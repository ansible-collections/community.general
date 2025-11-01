# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


import json


from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


pipx_common_argspec = {
    "global": dict(type="bool", default=False),
    "executable": dict(type="path"),
}


_state_map = dict(
    install="install",
    install_all="install-all",
    present="install",
    uninstall="uninstall",
    absent="uninstall",
    uninstall_all="uninstall-all",
    inject="inject",
    uninject="uninject",
    upgrade="upgrade",
    upgrade_shared="upgrade-shared",
    upgrade_all="upgrade-all",
    reinstall="reinstall",
    reinstall_all="reinstall-all",
    pin="pin",
    unpin="unpin",
)


def pipx_runner(module, command, **kwargs):
    arg_formats = dict(
        state=cmd_runner_fmt.as_map(_state_map),
        name=cmd_runner_fmt.as_list(),
        name_source=cmd_runner_fmt.as_func(cmd_runner_fmt.unpack_args(lambda n, s: [s] if s else [n])),
        install_apps=cmd_runner_fmt.as_bool("--include-apps"),
        install_deps=cmd_runner_fmt.as_bool("--include-deps"),
        inject_packages=cmd_runner_fmt.as_list(),
        force=cmd_runner_fmt.as_bool("--force"),
        include_injected=cmd_runner_fmt.as_bool("--include-injected"),
        index_url=cmd_runner_fmt.as_opt_val("--index-url"),
        python=cmd_runner_fmt.as_opt_val("--python"),
        system_site_packages=cmd_runner_fmt.as_bool("--system-site-packages"),
        _list=cmd_runner_fmt.as_fixed(["list", "--include-injected", "--json"]),
        editable=cmd_runner_fmt.as_bool("--editable"),
        pip_args=cmd_runner_fmt.as_opt_eq_val("--pip-args"),
        suffix=cmd_runner_fmt.as_opt_val("--suffix"),
        spec_metadata=cmd_runner_fmt.as_list(),
        version=cmd_runner_fmt.as_fixed("--version"),
    )
    arg_formats["global"] = cmd_runner_fmt.as_bool("--global")

    runner = CmdRunner(
        module,
        command=command,
        arg_formats=arg_formats,
        environ_update={"USE_EMOJI": "0", "PIPX_USE_EMOJI": "0"},
        check_rc=True,
        **kwargs,
    )
    return runner


def _make_entry(venv_name, venv, include_injected, include_deps):
    entry = {
        "name": venv_name,
        "version": venv["metadata"]["main_package"]["package_version"],
        "pinned": venv["metadata"]["main_package"].get("pinned"),
    }
    if include_injected:
        entry["injected"] = {k: v["package_version"] for k, v in venv["metadata"]["injected_packages"].items()}
    if include_deps:
        entry["dependencies"] = list(venv["metadata"]["main_package"]["app_paths_of_dependencies"])
    return entry


def make_process_dict(include_injected, include_deps=False):
    def process_dict(rc, out, err):
        if not out:
            return {}

        results = {}
        raw_data = json.loads(out)
        for venv_name, venv in raw_data["venvs"].items():
            results[venv_name] = _make_entry(venv_name, venv, include_injected, include_deps)

        return results, raw_data

    return process_dict


def make_process_list(mod_helper, **kwargs):
    #
    # ATTENTION!
    #
    # The function `make_process_list()` is deprecated and will be removed in community.general 13.0.0
    #
    process_dict = make_process_dict(mod_helper, **kwargs)

    def process_list(rc, out, err):
        res_dict, raw_data = process_dict(rc, out, err)

        if kwargs.get("include_raw"):
            mod_helper.vars.raw_output = raw_data

        return [entry for name, entry in res_dict.items() if name == kwargs.get("name")]

    return process_list

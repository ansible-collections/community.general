# -*- coding: utf-8 -*-
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import json


from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


pipx_common_argspec = {
    "global": dict(type='bool', default=False),
    "executable": dict(type='path'),
}


_state_map = dict(
    install='install',
    install_all='install-all',
    present='install',
    uninstall='uninstall',
    absent='uninstall',
    uninstall_all='uninstall-all',
    inject='inject',
    uninject='uninject',
    upgrade='upgrade',
    upgrade_shared='upgrade-shared',
    upgrade_all='upgrade-all',
    reinstall='reinstall',
    reinstall_all='reinstall-all',
    pin='pin',
    unpin='unpin',
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
        index_url=cmd_runner_fmt.as_opt_val('--index-url'),
        python=cmd_runner_fmt.as_opt_val('--python'),
        system_site_packages=cmd_runner_fmt.as_bool("--system-site-packages"),
        _list=cmd_runner_fmt.as_fixed(['list', '--include-injected', '--json']),
        editable=cmd_runner_fmt.as_bool("--editable"),
        pip_args=cmd_runner_fmt.as_opt_eq_val('--pip-args'),
        suffix=cmd_runner_fmt.as_opt_val('--suffix'),
        spec_metadata=cmd_runner_fmt.as_list(),
        version=cmd_runner_fmt.as_fixed('--version'),
    )
    arg_formats["global"] = cmd_runner_fmt.as_bool("--global")

    runner = CmdRunner(
        module,
        command=command,
        arg_formats=arg_formats,
        environ_update={'USE_EMOJI': '0'},
        check_rc=True,
        **kwargs
    )
    return runner


def make_process_list(mod_helper, **kwargs):
    def process_list(rc, out, err):
        if not out:
            return []

        results = []
        raw_data = json.loads(out)
        if kwargs.get("include_raw"):
            mod_helper.vars.raw_output = raw_data

        if kwargs["name"]:
            if kwargs["name"] in raw_data['venvs']:
                data = {kwargs["name"]: raw_data['venvs'][kwargs["name"]]}
            else:
                data = {}
        else:
            data = raw_data['venvs']

        for venv_name, venv in data.items():
            entry = {
                'name': venv_name,
                'version': venv['metadata']['main_package']['package_version'],
                'pinned': venv['metadata']['main_package'].get('pinned'),
            }
            if kwargs.get("include_injected"):
                entry['injected'] = {k: v['package_version'] for k, v in venv['metadata']['injected_packages'].items()}
            if kwargs.get("include_deps"):
                entry['dependencies'] = list(venv['metadata']['main_package']['app_paths_of_dependencies'])
            results.append(entry)

        return results

    return process_list

# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import typing as t

from ansible_collections.community.general.plugins.module_utils._cmd_runner import CmdRunner, cmd_runner_fmt

if t.TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule


def getfattr_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    return CmdRunner(
        module,
        command="getfattr",
        arg_formats=dict(
            absolute_names=cmd_runner_fmt.as_fixed("--absolute-names"),
            follow=cmd_runner_fmt.as_bool_not("-h"),
            dump=cmd_runner_fmt.as_fixed("-d"),
            match=cmd_runner_fmt.as_opt_val("-m"),
            attr_name=cmd_runner_fmt.as_opt_val("-n"),
            path=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def setfattr_runner(module: AnsibleModule, **kwargs) -> CmdRunner:
    return CmdRunner(
        module,
        command="setfattr",
        arg_formats=dict(
            follow=cmd_runner_fmt.as_bool_not("-h"),
            attr_name=cmd_runner_fmt.as_opt_val("-n"),
            value=cmd_runner_fmt.as_opt_val("-v"),
            remove=cmd_runner_fmt.as_opt_val("-x"),
            path=cmd_runner_fmt.as_list(),
        ),
        **kwargs,
    )


def full_key(namespace: str | None, key: str) -> str:
    if not namespace or (namespace == "user" and key.startswith("user.")):
        return key
    return f"{namespace}.{key}"


def parse_getfattr(out: str) -> dict[str, str]:
    result = {}
    for line in out.splitlines():
        if line.startswith("#") or line == "":
            continue
        name, dummy, value = line.partition("=")
        result[name] = value.strip('"')
    return result

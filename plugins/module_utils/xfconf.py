# -*- coding: utf-8 -*-
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.parsing.convert_bool import boolean
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


@cmd_runner_fmt.unpack_args
def _values_fmt(values, value_types):
    result = []
    for value, value_type in zip(values, value_types):
        if value_type == 'bool':
            value = 'true' if boolean(value) else 'false'
        result.extend(['--type', '{0}'.format(value_type), '--set', '{0}'.format(value)])
    return result


def xfconf_runner(module, **kwargs):
    runner = CmdRunner(
        module,
        command='xfconf-query',
        arg_formats=dict(
            channel=cmd_runner_fmt.as_opt_val("--channel"),
            property=cmd_runner_fmt.as_opt_val("--property"),
            force_array=cmd_runner_fmt.as_bool("--force-array"),
            reset=cmd_runner_fmt.as_bool("--reset"),
            create=cmd_runner_fmt.as_bool("--create"),
            list_arg=cmd_runner_fmt.as_bool("--list"),
            values_and_types=_values_fmt,
            version=cmd_runner_fmt.as_fixed("--version"),
        ),
        **kwargs
    )
    return runner


def get_xfconf_version(runner):
    with runner("version") as ctx:
        rc, out, err = ctx.run()
        return out.splitlines()[0].split()[1]

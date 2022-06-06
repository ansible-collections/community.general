# -*- coding: utf-8 -*-
# (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.parsing.convert_bool import boolean
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt as fmt


@fmt.unpack_args
def _values_fmt(values, value_types):
    result = []
    for value, value_type in zip(values, value_types):
        if value_type == 'bool':
            value = boolean(value)
        result.extend(['--type', '{0}'.format(value_type), '--set', '{0}'.format(value)])
    return result


def xfconf_runner(module, **kwargs):
    runner = CmdRunner(
        module,
        command='xfconf-query',
        arg_formats=dict(
            channel=fmt.as_opt_val("--channel"),
            property=fmt.as_opt_val("--property"),
            force_array=fmt.as_bool("--force-array"),
            reset=fmt.as_bool("--reset"),
            create=fmt.as_bool("--create"),
            list_arg=fmt.as_bool("--list"),
            values_and_types=fmt.as_func(_values_fmt),
        ),
        **kwargs
    )
    return runner

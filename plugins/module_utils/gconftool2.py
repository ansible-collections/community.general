# -*- coding: utf-8 -*-
# (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt as fmt


def gconftool2_runner(module, **kwargs):
    return CmdRunner(
        module,
        command='gconftool-2',
        arg_formats=dict(
            key=fmt.as_list(),
            value_type=fmt.as_opt_val("--type"),
            value=fmt.as_list(),
            direct=fmt.as_bool("--direct"),
            config_source=fmt.as_opt_val("--config-source"),
            get=fmt.as_bool("--get"),
            set_arg=fmt.as_bool("--set"),
            unset=fmt.as_bool("--unset"),
        ),
        **kwargs
    )

# -*- coding: utf-8 -*-
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


def gio_mime_runner(module, **kwargs):
    return CmdRunner(
        module,
        command=['gio', 'mime'],
        arg_formats=dict(
            mime_type=cmd_runner_fmt.as_list(),
            handler=cmd_runner_fmt.as_list(),
        ),
        **kwargs
    )


def gio_mime_get(runner, mime_type):
    def process(rc, out, err):
        if err.startswith("No default applications for"):
            return None
        out = out.splitlines()[0]
        return out.split()[-1]

    with runner("mime_type", output_process=process) as ctx:
        return ctx.run(mime_type=mime_type)

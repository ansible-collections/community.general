#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: gio_mime
author:
  - "Alexei Znamensky (@russoz)"
short_description: Set default handler for MIME type, for applications using Gnome GIO
version_added: 7.5.0
description:
  - This module allows configuring the default handler for a specific MIME type, to be used by applications built with the
    Gnome GIO API.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  mime_type:
    description:
      - MIME type for which a default handler is set.
    type: str
    required: true
  handler:
    description:
      - Default handler set for the MIME type.
    type: str
    required: true
notes:
  - This module is a thin wrapper around the C(gio mime) command (and subcommand).
  - See man gio(1) for more details.
seealso:
  - name: C(gio) command manual page
    description: Manual page for the command.
    link: https://man.archlinux.org/man/gio.1
  - name: GIO Documentation
    description: Reference documentation for the GIO API..
    link: https://docs.gtk.org/gio/
"""

EXAMPLES = r"""
- name: Set chrome as the default handler for https
  community.general.gio_mime:
    mime_type: x-scheme-handler/https
    handler: google-chrome.desktop
  register: result
"""

RETURN = r"""
handler:
  description:
    - The handler set as default.
  returned: success
  type: str
  sample: google-chrome.desktop
version:
  description: Version of gio.
  type: str
  returned: always
  sample: "2.80.0"
  version_added: 10.0.0
"""

from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.gio_mime import gio_mime_runner, gio_mime_get


class GioMime(ModuleHelper):
    output_params = ['handler']
    module = dict(
        argument_spec=dict(
            mime_type=dict(type='str', required=True),
            handler=dict(type='str', required=True),
        ),
        supports_check_mode=True,
    )
    use_old_vardict = False

    def __init_module__(self):
        self.runner = gio_mime_runner(self.module, check_rc=True)
        with self.runner("version") as ctx:
            rc, out, err = ctx.run()
            self.vars.version = out.strip()
        self.vars.set_meta("handler", initial_value=gio_mime_get(self.runner, self.vars.mime_type), diff=True, change=True)

    def __run__(self):
        check_mode_return = (0, 'Module executed in check mode', '')
        if self.vars.has_changed:
            with self.runner.context(args_order="mime mime_type handler", check_mode_skip=True, check_mode_return=check_mode_return) as ctx:
                rc, out, err = ctx.run()
                self.vars.stdout = out
                self.vars.stderr = err
                self.vars.set("run_info", ctx.run_info, verbosity=4)


def main():
    GioMime.execute()


if __name__ == '__main__':
    main()

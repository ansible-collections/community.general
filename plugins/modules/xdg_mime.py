#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Marcos Alano <marcoshalano@gmail.com>
# Based on gio_mime module. Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: xdg_mime
author:
  - "Marcos Alano (@mhalano)"
short_description: Set default handler for MIME type, for applications using XDG tools
version_added: 10.6.0
description:
  - This module allows configuring the default handler for a specific MIME type, to be used by applications that use XDG.
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
      - MIME type for which a default handler will be set.
    type: str
    required: true
  handler:
    description:
      - Default handler will be set for the MIME type.
      - The desktop file must be installed in the system
    type: str
    required: true
notes:
  - This module is a thin wrapper around xdg-mime tool.
  - See man xdg-mime(1) for more details.
seealso:
  - name: C(xdg-mime) command manual page
    description: Manual page for the command.
    link: https://portland.freedesktop.org/doc/xdg-mime.html
  - name: xdg-utils Documentation
    description: Reference documentation for xdg-utils.
    link: https://www.freedesktop.org/wiki/Software/xdg-utils/
"""

EXAMPLES = r"""
- name: Set chrome as the default handler for https
  community.general.xdg_mime:
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
stdout:
  description:
    - The output of the C(xdg-mime) command.
  returned: success
  type: str
  sample: ''
stderr:
  description:
    - The error output of the C(xdg-mime) command.
  returned: failure
  type: str
  sample: ''
version:
  description: Version of xdg-mime.
  type: str
  returned: always
  sample: "xdg-mime 1.2.1"
"""

from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.xdg_mime import xdg_mime_runner, xdg_mime_get


class XdgMime(ModuleHelper):
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
        self.runner = xdg_mime_runner(self.module, check_rc=True)
        with self.runner("version") as ctx:
            rc, out, err = ctx.run()
            self.vars.version = out.replace("xdg-mime ", "").strip()
        self.vars.set_meta("handler", initial_value=xdg_mime_get(self.runner, self.vars.mime_type), diff=True, change=True)

    def __run__(self):
        check_mode_return = (0, 'Module executed in check mode', '')
        if self.vars.has_changed:
            with self.runner.context(args_order="default handler mime_type", check_mode_skip=True, check_mode_return=check_mode_return) as ctx:
                rc, out, err = ctx.run()
                self.vars.stdout = out
                self.vars.stderr = err
                self.vars.set("run_info", ctx.run_info, verbosity=4)


def main():
    XdgMime.execute()


if __name__ == '__main__':
    main()

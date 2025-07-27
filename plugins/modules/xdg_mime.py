#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2025, Marcos Alano <marcoshalano@gmail.com>
# Based on gio_mime module. Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# In memory: This code is dedicated to my late grandmother, Maria Marlene. 1936-2025. Rest in peace, grandma.
# -Marcos Alano-

# TODO: Add support for diff mode

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: xdg_mime
author:
  - "Marcos Alano (@mhalano)"
short_description: Set default handler for MIME types, for applications using XDG tools
version_added: 10.7.0
description:
  - This module allows configuring the default handler for specific MIME types when you use applications that rely on XDG.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  mime_types:
    description:
      - One or more MIME types for which a default handler is set.
    type: list
    elements: str
    required: true
  handler:
    description:
      - Sets the default handler for the specified MIME types.
      - The desktop file must be installed in the system. If the desktop file is not installed, the module does not fail,
        but the handler is not set either.
      - You must pass a handler in the form V(*.desktop), otherwise the module fails.
    type: str
    required: true
notes:
  - This module is a thin wrapper around C(xdg-mime) tool.
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
- name: Set Chrome as the default handler for HTTPS
  community.general.xdg_mime:
    mime_types: x-scheme-handler/https
    handler: google-chrome.desktop
  register: result

- name: Set Chrome as the default handler for both HTTP and HTTPS
  community.general.xdg_mime:
    mime_types:
      - x-scheme-handler/http
      - x-scheme-handler/https
    handler: google-chrome.desktop
  register: result
"""

RETURN = r"""
current_handlers:
  description:
    - Currently set handlers for the passed MIME types.
  returned: success
  type: list
  elements: str
  sample:
    - google-chrome.desktop
    - firefox.desktop
version:
  description: Version of the C(xdg-mime) tool.
  type: str
  returned: always
  sample: "1.2.1"
"""

from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.xdg_mime import xdg_mime_runner, xdg_mime_get


class XdgMime(ModuleHelper):
    output_params = ['handler']

    module = dict(
        argument_spec=dict(
            mime_types=dict(type='list', elements='str', required=True),
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

        if not self.vars.handler.endswith(".desktop"):
            self.do_raise(msg="Handler must be a .desktop file")

        self.vars.current_handlers = []
        for mime in self.vars.mime_types:
            handler_value = xdg_mime_get(self.runner, mime)
            if not handler_value:
                handler_value = ''
            self.vars.current_handlers.append(handler_value)

    def __run__(self):
        check_mode_return = (0, 'Module executed in check mode', '')

        if any(h != self.vars.handler for h in self.vars.current_handlers):
            self.changed = True

        if self.has_changed():
            with self.runner.context(args_order="default handler mime_types", check_mode_skip=True, check_mode_return=check_mode_return) as ctx:
                rc, out, err = ctx.run()
                self.vars.stdout = out
                self.vars.stderr = err
                self.vars.set("run_info", ctx.run_info, verbosity=1)


def main():
    XdgMime.execute()


if __name__ == '__main__':
    main()

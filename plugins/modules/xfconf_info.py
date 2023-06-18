#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: xfconf_info
author:
  - "Alexei Znamensky (@russoz)"
short_description: Retrieve XFCE4 configurations
version_added: 3.5.0
description:
  - This module allows retrieving Xfce 4 configurations with the help of C(xfconf-query).
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
attributes:
  check_mode:
    version_added: 3.3.0
    # This was backported to 2.5.4 and 1.3.11 as well, since this was a bugfix
options:
  channel:
    description:
    - >
      A Xfconf preference channel is a top-level tree key, inside of the
      Xfconf repository that corresponds to the location for which all
      application properties/keys are stored.
    - If not provided, the module will list all available channels.
    type: str
  property:
    description:
    - >
      A Xfce preference key is an element in the Xfconf repository
      that corresponds to an application preference.
    - If provided, then O(channel) is required.
    - If not provided and a O(channel) is provided, then the module will list all available properties in that O(channel).
    type: str
notes:
  - See man xfconf-query(1) for more details.
'''

EXAMPLES = """
- name: Get list of all available channels
  community.general.xfconf_info: {}
  register: result

- name: Get list of all properties in a specific channel
  community.general.xfconf_info:
    channel: xsettings
  register: result

- name: Retrieve the DPI value
  community.general.xfconf_info:
    channel: xsettings
    property: /Xft/DPI
  register: result

- name: Get workspace names (4)
  community.general.xfconf_info:
    channel: xfwm4
    property: /general/workspace_names
  register: result
"""

RETURN = '''
  channels:
    description:
      - List of available channels.
      - Returned when the module receives no parameter at all.
    returned: success
    type: list
    elements: str
    sample:
    - xfce4-desktop
    - displays
    - xsettings
    - xfwm4
  properties:
    description:
      - List of available properties for a specific channel.
      - Returned by passing only the O(channel) parameter to the module.
    returned: success
    type: list
    elements: str
    sample:
      - /Gdk/WindowScalingFactor
      - /Gtk/ButtonImages
      - /Gtk/CursorThemeSize
      - /Gtk/DecorationLayout
      - /Gtk/FontName
      - /Gtk/MenuImages
      - /Gtk/MonospaceFontName
      - /Net/DoubleClickTime
      - /Net/IconThemeName
      - /Net/ThemeName
      - /Xft/Antialias
      - /Xft/Hinting
      - /Xft/HintStyle
      - /Xft/RGBA
  is_array:
    description:
      - Flag indicating whether the property is an array or not.
    returned: success
    type: bool
  value:
    description:
      - The value of the property. Empty if the property is of array type.
    returned: success
    type: str
    sample: Monospace 10
  value_array:
    description:
      - The array value of the property. Empty if the property is not of array type.
    returned: success
    type: list
    elements: str
    sample:
      - Main
      - Work
      - Tmp
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.xfconf import xfconf_runner


class XFConfInfo(ModuleHelper):
    module = dict(
        argument_spec=dict(
            channel=dict(type='str'),
            property=dict(type='str'),
        ),
        required_by=dict(
            property=['channel']
        ),
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.runner = xfconf_runner(self.module, check_rc=True)
        self.vars.set("list_arg", False, output=False)
        self.vars.set("is_array", False)

    def process_command_output(self, rc, out, err):
        result = out.rstrip()
        if "Value is an array with" in result:
            result = result.split("\n")
            result.pop(0)
            result.pop(0)
            self.vars.is_array = True

        return result

    def _process_list_properties(self, rc, out, err):
        return out.splitlines()

    def _process_list_channels(self, rc, out, err):
        lines = out.splitlines()
        lines.pop(0)
        lines = [s.lstrip() for s in lines]
        return lines

    def __run__(self):
        self.vars.list_arg = not (bool(self.vars.channel) and bool(self.vars.property))
        output = 'value'
        proc = self.process_command_output
        if self.vars.channel is None:
            output = 'channels'
            proc = self._process_list_channels
        elif self.vars.property is None:
            output = 'properties'
            proc = self._process_list_properties

        with self.runner.context('list_arg channel property', output_process=proc) as ctx:
            result = ctx.run(**self.vars)

        if not self.vars.list_arg and self.vars.is_array:
            output = "value_array"
        self.vars.set(output, result)


def main():
    XFConfInfo.execute()


if __name__ == '__main__':
    main()

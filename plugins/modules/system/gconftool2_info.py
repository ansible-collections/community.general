#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2021, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
    - If provided, then I(channel) is required.
    - If not provided and a I(channel) is provided, then the module will list all available properties in that I(channel).
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
        - Returned by passed only the I(channel) parameter to the module.
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
from ansible_collections.community.general.plugins.module_utils.gconftool2 import gconftool2_runner


class GConftoolInfo(ModuleHelper):
    output_params = ['key']
    module = dict(
        argument_spec=dict(
            key=dict(type='str', required=True),
        ),
        supports_check_mode=True,
    )

    def __init_module__(self):
        self.runner = gconftool2_runner(self.module, check_rc=True)

    def process_command_output(self, rc, out, err):
        return out.rstrip()

    def __run__(self):
        with self.runner.context(args_order=["get", "key"], output_process=self.process_command_output) as ctx:
            self.vars.value = ctx.run(get=True)


def main():
    xfconf = GConftoolInfo()
    xfconf.run()


if __name__ == '__main__':
    main()

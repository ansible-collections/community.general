# -*- coding: utf-8 -*-

# Copyright (c) 2025, Marco Noce <nce.marco@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  unitname:
    description:
      - List of unit names to process.
      - It supports .service, .target, .socket, and .mount units type.
      - Each name must correspond to the full name of the systemd unit.
    type: list
    elements: str
    default: []
  extra_properties:
    description:
      - Additional properties to retrieve (appended to the default ones).
      - Each property is case-sensitive and must follow the exact systemd syntax.
    type: list
    elements: str
    default: []
notes:
  - Regardless of whether the property is default or extra, it will be output in lowercase once extracted.
  - Default properties depend on the type of systemd unit.
  - service properties V(name), V(loadstate), V(activestate), V(substate), V(fragmentpath), V(unitfilepreset), V(unitfilestate), V(mainpid), V(execmainpid).
  - target properties V(name), V(loadstate), V(activestate), V(substate), V(fragmentpath), V(unitfilepreset), V(unitfilestate).
  - socket properties V(name), V(loadstate), V(activestate), V(substate), V(fragmentpath), V(unitfilepreset), V(unitfilestate).
  - mount properties V(name), V(loadstate), V(activestate), V(substate), V(what), V(where), V(type), V(options).
"""

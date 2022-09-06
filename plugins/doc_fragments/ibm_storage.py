# -*- coding: utf-8 -*-

# Copyright (c) 2018, IBM CORPORATION
# Author(s): Tzur Eliyahu <tzure@il.ibm.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleDocFragment(object):

    # ibm_storage documentation fragment
    DOCUMENTATION = r'''
options:
    username:
        description:
            - Management user on the spectrum accelerate storage system.
        type: str
        required: true
    password:
        description:
            - Password for username on the spectrum accelerate storage system.
        type: str
        required: true
    endpoints:
        description:
            - The hostname or management IP of Spectrum Accelerate storage system.
        type: str
        required: true
notes:
  - This module requires pyxcli python library.
    Use 'pip install pyxcli' in order to get pyxcli.
requirements:
  - python >= 2.7
  - pyxcli
'''

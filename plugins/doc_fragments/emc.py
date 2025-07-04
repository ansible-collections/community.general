# -*- coding: utf-8 -*-

# Copyright (c) 2018, Luca Lorenzetto (@remix_tj) <lorenzetto.luca@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Documentation fragment for VNX (emc_vnx)
    EMC_VNX = r'''
options:
  sp_address:
    description:
      - Address of the SP of target/secondary storage.
    type: str
    required: true
  sp_user:
    description:
      - Username for accessing SP.
    type: str
    default: sysadmin
  sp_password:
    description:
      - password for accessing SP.
    type: str
    default: sysadmin
requirements:
  - An EMC VNX Storage device.
  - storops (0.5.10 or greater). Install using C(pip install storops).
notes:
  - The modules prefixed with C(emc_vnx) are built to support the EMC VNX storage platform.
'''

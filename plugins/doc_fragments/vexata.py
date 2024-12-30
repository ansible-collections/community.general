# -*- coding: utf-8 -*-
#
# Copyright (c) 2019, Sandeep Kasargod <sandeep@vexata.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Documentation fragment for Vexata VX100 series
    VX100 = r'''
options:
  array:
    description:
      - Vexata VX100 array hostname or IPv4 Address.
    required: true
    type: str
  user:
    description:
      - Vexata API user with administrative privileges.
      - Uses the E(VEXATA_USER) environment variable as a fallback.
    required: false
    type: str
  password:
    description:
      - Vexata API user password.
      - Uses the E(VEXATA_PASSWORD) environment variable as a fallback.
    required: false
    type: str
  validate_certs:
    description:
      - Allows connection when SSL certificates are not valid. Set to V(false) when certificates are not trusted.
      - If set to V(true), please make sure Python >= 2.7.9 is installed on the given machine.
    required: false
    type: bool
    default: false

requirements:
  - Vexata VX100 storage array with VXOS >= v3.5.0 on storage array
  - vexatapi >= 0.0.1
  - E(VEXATA_USER) and E(VEXATA_PASSWORD) environment variables must be set if
    user and password arguments are not passed to the module directly.
'''

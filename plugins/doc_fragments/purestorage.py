# -*- coding: utf-8 -*-

# Copyright (c) 2017, Simon Dodsley <simon@purestorage.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard Pure Storage documentation fragment
    DOCUMENTATION = r'''
options:
  - See separate platform section for more details
requirements:
  - See separate platform section for more details
notes:
  - Ansible modules are available for the following Pure Storage products: FlashArray, FlashBlade
'''

    # Documentation fragment for FlashBlade
    FB = r'''
options:
  fb_url:
    description:
      - FlashBlade management IP address or Hostname.
    type: str
  api_token:
    description:
      - FlashBlade API token for admin privileged user.
    type: str
notes:
  - This module requires the C(purity_fb) Python library.
  - You must set E(PUREFB_URL) and E(PUREFB_API) environment variables
    if O(fb_url) and O(api_token) arguments are not passed to the module directly.
requirements:
  - purity_fb >= 1.1
'''

    # Documentation fragment for FlashArray
    FA = r'''
options:
  fa_url:
    description:
      - FlashArray management IPv4 address or Hostname.
    type: str
    required: true
  api_token:
    description:
      - FlashArray API token for admin privileged user.
    type: str
    required: true
notes:
  - This module requires the C(purestorage) Python library.
  - You must set E(PUREFA_URL) and E(PUREFA_API) environment variables
    if O(fa_url) and O(api_token) arguments are not passed to the module directly.
requirements:
  - purestorage
'''

# -*- coding: utf-8 -*-

# Copyright (C) 2017 Lenovo, Inc.
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Standard Pylxca documentation fragment
    DOCUMENTATION = r'''
author:
  - Naval Patel (@navalkp)
  - Prashant Bhosale (@prabhosa)

options:
  login_user:
    description:
    - The username for use in HTTP basic authentication.
    type: str
    required: true

  login_password:
    description:
    - The password for use in HTTP basic authentication.
    type: str
    required: true

  auth_url:
    description:
    - lxca HTTPS full web address.
    type: str
    required: true

requirements:
  - pylxca

notes:
  - Additional detail about pylxca can be found at U(https://github.com/lenovo/pylxca).
  - Playbooks using these modules can be found at U(https://github.com/lenovo/ansible.lenovo-lxca).
'''

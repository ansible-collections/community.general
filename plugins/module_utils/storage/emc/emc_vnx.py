# -*- coding: utf-8 -*-
# Copyright (c) 2018 Luca 'remix_tj' Lorenzetto
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


emc_vnx_argument_spec = {
    'sp_address': dict(type='str', required=True),
    'sp_user': dict(type='str', required=False, default='sysadmin'),
    'sp_password': dict(type='str', required=False, default='sysadmin',
                        no_log=True),
}

# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# (c) 2018 Luca 'remix_tj' Lorenzetto
#
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


emc_vnx_argument_spec = {
    'sp_address': dict(type='str', required=True),
    'sp_user': dict(type='str', required=False, default='sysadmin'),
    'sp_password': dict(type='str', required=False, default='sysadmin',
                        no_log=True),
}

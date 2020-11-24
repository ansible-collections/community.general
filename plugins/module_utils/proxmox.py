# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, Tristan Le Guern <tleguern at bouledef.eu>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import atexit
import time
import re
import traceback

PROXMOXER_IMP_ERR = None
try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False
    PROXMOXER_IMP_ERR = traceback.format_exc()


from ansible.module_utils.basic import env_fallback, missing_required_lib


def proxmox_auth_argument_spec():
    return dict(
        api_host=dict(type='str',
                      required=True,
                      fallback=(env_fallback, ['PROXMOX_HOST'])
                      ),
        api_user=dict(type='str',
                      required=True,
                      fallback=(env_fallback, ['PROXMOX_USER'])
                      ),
        api_password=dict(type='str',
                          no_log=True,
                          fallback=(env_fallback, ['PROXMOX_PASSWORD'])
                          ),
        api_token_id=dict(type='str',
                          no_log=False
                          ),
        api_token_secret=dict(type='str',
                              no_log=True
                              ),
        validate_certs=dict(type='bool',
                            default=False
                            ),
    )


def proxmox_to_ansible_bool(value):
    '''Convert Proxmox representation of a boolean to be ansible-friendly'''
    return True if value == 1 else False


class ProxmoxAnsible(object):
    """Base class for Proxmox modules"""
    def __init__(self, module):
        self.module = module
        self.proxmox_api = self._connect()
        # Test token validity
        try:
            self.proxmox_api.version.get()
        except Exception as e:
            module.fail_json(msg='%s' % e, exception=traceback.format_exc())

    def _connect(self):
        api_host = self.module.params['api_host']
        api_user = self.module.params['api_user']
        api_password = self.module.params['api_password']
        api_token_id = self.module.params['api_token_id']
        api_token_secret = self.module.params['api_token_secret']
        validate_certs = self.module.params['validate_certs']

        auth_args = {'user': api_user}
        if api_password:
            auth_args['password'] = api_password
        else:
            auth_args['token_name'] = api_token_id
            auth_args['token_value'] = api_token_secret

        try:
            return ProxmoxAPI(api_host, verify_ssl=validate_certs, **auth_args)
        except Exception as e:
            self.module.fail_json(msg='%s' % e, exception=traceback.format_exc())

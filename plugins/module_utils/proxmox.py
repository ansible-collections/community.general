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
from ansible.module_utils.common.text.converters import to_native
from ansible_collections.community.general.plugins.module_utils.version import LooseVersion


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


def ansible_to_proxmox_bool(value):
    '''Convert Ansible representation of a boolean to be proxmox-friendly'''
    if value is None:
        return None

    if not isinstance(value, bool):
        raise ValueError("%s must be of type bool not %s" % (value, type(value)))

    return 1 if value else 0


class ProxmoxAnsible(object):
    """Base class for Proxmox modules"""
    def __init__(self, module):
        if not HAS_PROXMOXER:
            module.fail_json(msg=missing_required_lib('proxmoxer'), exception=PROXMOXER_IMP_ERR)

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

    def version(self):
        apireturn = self.proxmox_api.version.get()
        return LooseVersion(apireturn['version'])

    def get_node(self, node):
        nodes = [n for n in self.proxmox_api.nodes.get() if n['node'] == node]
        return nodes[0] if nodes else None

    def get_nextvmid(self):
        vmid = self.proxmox_api.cluster.nextid.get()
        return vmid

    def get_vmid(self, name, ignore_missing=False, choose_first_if_multiple=False):
        vms = [vm['vmid'] for vm in self.proxmox_api.cluster.resources.get(type='vm') if vm.get('name') == name]

        if not vms:
            if ignore_missing:
                return None

            self.module.fail_json(msg='No VM with name %s found' % name)
        elif len(vms) > 1:
            if choose_first_if_multiple:
                self.module.deprecate(
                    'Multiple VMs with name %s found, choosing the first one. ' % name +
                    'This will be an error in the future. To ensure the correct VM is used, ' +
                    'also pass the vmid parameter.',
                    version='5.0.0', collection_name='community.general')
            else:
                self.module.fail_json(msg='Multiple VMs with name %s found, provide vmid instead' % name)

        return vms[0]

    def get_vm(self, vmid, ignore_missing=False):
        vms = [vm for vm in self.proxmox_api.cluster.resources.get(type='vm') if vm['vmid'] == int(vmid)]

        if vms:
            return vms[0]
        else:
            if ignore_missing:
                return None

            self.module.fail_json(msg='VM with vmid %s does not exist in cluster' % vmid)

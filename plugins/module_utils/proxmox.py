# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Tristan Le Guern <tleguern at bouledef.eu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import traceback

PROXMOXER_IMP_ERR = None
try:
    from proxmoxer import ProxmoxAPI
    from proxmoxer import __version__ as proxmoxer_version
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False
    PROXMOXER_IMP_ERR = traceback.format_exc()


from ansible.module_utils.basic import env_fallback, missing_required_lib
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


class ProxmoxStorage:
    def __init__(self, storage):
        self.storage = storage
        # Convert proxmox representation of lists, dicts and boolean for easier
        # manipulation within ansible.
        if "shared" in self.storage:
            self.storage["shared"] = proxmox_to_ansible_bool(self.storage["shared"])
        if "content" in self.storage:
            self.storage["content"] = self.storage["content"].split(",")
        if "nodes" in self.storage:
            self.storage["nodes"] = self.storage["nodes"].split(",")
        if "prune-backups" in storage:
            options = storage["prune-backups"].split(",")
            self.storage["prune-backups"] = dict()
            for option in options:
                k, v = option.split("=")
                self.storage["prune-backups"][k] = v


class ProxmoxAnsible(object):
    """Base class for Proxmox modules"""
    def __init__(self, module):
        if not HAS_PROXMOXER:
            module.fail_json(msg=missing_required_lib('proxmoxer'), exception=PROXMOXER_IMP_ERR)

        self.module = module
        self.proxmoxer_version = proxmoxer_version
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
            if self.proxmoxer_version < LooseVersion('1.1.0'):
                self.module.fail_json('Using "token_name" and "token_value" require proxmoxer>=1.1.0')
            auth_args['token_name'] = api_token_id
            auth_args['token_value'] = api_token_secret

        try:
            return ProxmoxAPI(api_host, verify_ssl=validate_certs, **auth_args)
        except Exception as e:
            self.module.fail_json(msg='%s' % e, exception=traceback.format_exc())

    def version(self):
        try:
            apiversion = self.proxmox_api.version.get()
            return LooseVersion(apiversion['version'])
        except Exception as e:
            self.module.fail_json(msg='Unable to retrieve Proxmox VE version: %s' % e)

    def get_node(self, node):
        try:
            nodes = [n for n in self.proxmox_api.nodes.get() if n['node'] == node]
        except Exception as e:
            self.module.fail_json(msg='Unable to retrieve Proxmox VE node: %s' % e)
        return nodes[0] if nodes else None

    def get_nextvmid(self):
        try:
            return self.proxmox_api.cluster.nextid.get()
        except Exception as e:
            self.module.fail_json(msg='Unable to retrieve next free vmid: %s' % e)

    def get_vmid(self, name, ignore_missing=False, choose_first_if_multiple=False):
        try:
            vms = [vm['vmid'] for vm in self.proxmox_api.cluster.resources.get(type='vm') if vm.get('name') == name]
        except Exception as e:
            self.module.fail_json(msg='Unable to retrieve list of VMs filtered by name %s: %s' % (name, e))

        if not vms:
            if ignore_missing:
                return None

            self.module.fail_json(msg='No VM with name %s found' % name)
        elif len(vms) > 1:
            self.module.fail_json(msg='Multiple VMs with name %s found, provide vmid instead' % name)

        return vms[0]

    def get_vm(self, vmid, ignore_missing=False):
        try:
            vms = [vm for vm in self.proxmox_api.cluster.resources.get(type='vm') if vm['vmid'] == int(vmid)]
        except Exception as e:
            self.module.fail_json(msg='Unable to retrieve list of VMs filtered by vmid %s: %s' % (vmid, e))

        if vms:
            return vms[0]
        else:
            if ignore_missing:
                return None

            self.module.fail_json(msg='VM with vmid %s does not exist in cluster' % vmid)

    def api_task_ok(self, node, taskid):
        try:
            status = self.proxmox_api.nodes(node).tasks(taskid).status.get()
            return status['status'] == 'stopped' and status['exitstatus'] == 'OK'
        except Exception as e:
            self.module.fail_json(msg='Unable to retrieve API task ID from node %s: %s' % (node, e))

    def get_pool(self, poolid):
        """Retrieve pool information

        :param poolid: str - name of the pool
        :return: dict - pool information
        """
        try:
            return self.proxmox_api.pools(poolid).get()
        except Exception as e:
            self.module.fail_json(msg="Unable to retrieve pool %s information: %s" % (poolid, e))

    def get_storage(self, storage):
        try:
            storage = self.proxmox_api.storage.get(storage)
        except Exception:
            self.module.fail_json(msg="Storage '%s' does not exist" % storage)
        return ProxmoxStorage(storage)

    def get_storages(self, type):
        """Retrieve storages information

        :param type: str, optional - type of storages
        :return: list of dicts - array of storages
        """
        try:
            return self.proxmox_api.storage.get(type=type)
        except Exception as e:
            self.module.fail_json(
                msg="Unable to retrieve storages information with type %s: %s"
                % (type, e)
            )

    def get_storages_as_objects(self, type):
        """Retrieve storages information

        :param type: str, optional - type of storages
        :return: list of ProxmoxStorage - array of storages
        """
        storages = self.get_storage(type)
        return [ProxmoxStorage(storage) for storage in storages]

    def get_storage_content(self, node, storage, content=None, vmid=None):
        try:
            return (
                self.proxmox_api.nodes(node)
                .storage(storage)
                .content()
                .get(content=content, vmid=vmid)
            )
        except Exception as e:
            self.module.fail_json(
                msg="Unable to list content on %s, %s for %s and %s: %s"
                % (node, storage, content, vmid, e)
            )

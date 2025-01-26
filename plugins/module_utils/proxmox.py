# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Tristan Le Guern <tleguern at bouledef.eu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import traceback
from time import sleep

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
        api_port=dict(type='int',
                      fallback=(env_fallback, ['PROXMOX_PORT'])
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
    TASK_TIMED_OUT = 'timeout expired'

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
        api_port = self.module.params['api_port']
        api_user = self.module.params['api_user']
        api_password = self.module.params['api_password']
        api_token_id = self.module.params['api_token_id']
        api_token_secret = self.module.params['api_token_secret']
        validate_certs = self.module.params['validate_certs']

        auth_args = {'user': api_user}

        if api_port:
            auth_args['port'] = api_port

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
        elif len(vms) > 1 and not choose_first_if_multiple:
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

    def api_task_failed(self, node, taskid):
        """ Explicitly check if the task stops but exits with a failed status
        """
        try:
            status = self.proxmox_api.nodes(node).tasks(taskid).status.get()
            return status['status'] == 'stopped' and status['exitstatus'] != 'OK'
        except Exception as e:
            self.module.fail_json(msg='Unable to retrieve API task ID from node %s: %s' % (node, e))

    def api_task_complete(self, node_name, task_id, timeout):
        """Wait until the task stops or times out.

        :param node_name: Proxmox node name where the task is running.
        :param task_id: ID of the running task.
        :param timeout: Timeout in seconds to wait for the task to complete.
        :return: Task completion status (True/False) and ``exitstatus`` message when status=False.
        """
        status = {}
        while timeout:
            try:
                status = self.proxmox_api.nodes(node_name).tasks(task_id).status.get()
            except Exception as e:
                self.module.fail_json(msg='Unable to retrieve API task ID from node %s: %s' % (node_name, e))

            if status['status'] == 'stopped':
                if status['exitstatus'] == 'OK':
                    return True, None
                else:
                    return False, status['exitstatus']
            else:
                timeout -= 1
                if timeout <= 0:
                    return False, ProxmoxAnsible.TASK_TIMED_OUT
                sleep(1)

    def get_pool(self, poolid):
        """Retrieve pool information

        :param poolid: str - name of the pool
        :return: dict - pool information
        """
        try:
            return self.proxmox_api.pools(poolid).get()
        except Exception as e:
            self.module.fail_json(msg="Unable to retrieve pool %s information: %s" % (poolid, e))

    def get_storages(self, type):
        """Retrieve storages information

        :param type: str, optional - type of storages
        :return: list of dicts - array of storages
        """
        try:
            return self.proxmox_api.storage.get(type=type)
        except Exception as e:
            self.module.fail_json(msg="Unable to retrieve storages information with type %s: %s" % (type, e))

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

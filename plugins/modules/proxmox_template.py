#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: proxmox_template
short_description: Management of OS templates in Proxmox VE cluster
description:
  - allows you to upload/delete templates in Proxmox VE cluster
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  node:
    description:
      - Proxmox VE node on which to operate.
    type: str
  src:
    description:
      - Path to uploaded file.
      - Required only for I(state=present).
    type: path
  template:
    description:
      - The template name.
      - Required for I(state=absent) to delete a template.
      - Required for I(state=present) to download an appliance container template (pveam).
    type: str
  content_type:
    description:
      - Content type.
      - Required only for I(state=present).
    type: str
    default: 'vztmpl'
    choices: ['vztmpl', 'iso']
  storage:
    description:
      - Target storage.
    type: str
    default: 'local'
  timeout:
    description:
      - Timeout for operations.
    type: int
    default: 30
  force:
    description:
      - It can only be used with I(state=present), existing template will be overwritten.
    type: bool
    default: false
  state:
    description:
     - Indicate desired state of the template.
    type: str
    choices: ['present', 'absent']
    default: present
notes:
  - Requires C(proxmoxer) and C(requests) modules on host. This modules can be installed with M(ansible.builtin.pip).
author: Sergei Antipov (@UnderGreen)
extends_documentation_fragment:
  - community.general.proxmox.documentation
  - community.general.attributes
'''

EXAMPLES = '''
- name: Upload new openvz template with minimal options
  community.general.proxmox_template:
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    src: ~/ubuntu-14.04-x86_64.tar.gz

- name: >
    Upload new openvz template with minimal options use environment
    PROXMOX_PASSWORD variable(you should export it before)
  community.general.proxmox_template:
    node: uk-mc02
    api_user: root@pam
    api_host: node1
    src: ~/ubuntu-14.04-x86_64.tar.gz

- name: Upload new openvz template with all options and force overwrite
  community.general.proxmox_template:
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    storage: local
    content_type: vztmpl
    src: ~/ubuntu-14.04-x86_64.tar.gz
    force: true

- name: Delete template with minimal options
  community.general.proxmox_template:
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    template: ubuntu-14.04-x86_64.tar.gz
    state: absent

- name: Download proxmox appliance container template
  community.general.proxmox_template:
    node: uk-mc02
    api_user: root@pam
    api_password: 1q2w3e
    api_host: node1
    storage: local
    content_type: vztmpl
    template: ubuntu-20.04-standard_20.04-1_amd64.tar.gz
'''

import os
import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.proxmox import (proxmox_auth_argument_spec, ProxmoxAnsible)


class ProxmoxTemplateAnsible(ProxmoxAnsible):
    def get_template(self, node, storage, content_type, template):
        return [True for tmpl in self.proxmox_api.nodes(node).storage(storage).content.get()
                if tmpl['volid'] == '%s:%s/%s' % (storage, content_type, template)]

    def task_status(self, node, taskid, timeout):
        """
        Check the task status and wait until the task is completed or the timeout is reached.
        """
        while timeout:
            if self.api_task_ok(node, taskid):
                return True
            timeout = timeout - 1
            if timeout == 0:
                self.module.fail_json(msg='Reached timeout while waiting for uploading/downloading template. Last line in task before timeout: %s' %
                                      self.proxmox_api.node(node).tasks(taskid).log.get()[:1])

            time.sleep(1)
        return False

    def upload_template(self, node, storage, content_type, realpath, timeout):
        taskid = self.proxmox_api.nodes(node).storage(storage).upload.post(content=content_type, filename=open(realpath, 'rb'))
        return self.task_status(node, taskid, timeout)

    def download_template(self, node, storage, template, timeout):
        taskid = self.proxmox_api.nodes(node).aplinfo.post(storage=storage, template=template)
        return self.task_status(node, taskid, timeout)

    def delete_template(self, node, storage, content_type, template, timeout):
        volid = '%s:%s/%s' % (storage, content_type, template)
        self.proxmox_api.nodes(node).storage(storage).content.delete(volid)
        while timeout:
            if not self.get_template(node, storage, content_type, template):
                return True
            timeout = timeout - 1
            if timeout == 0:
                self.module.fail_json(msg='Reached timeout while waiting for deleting template.')

            time.sleep(1)
        return False


def main():
    module_args = proxmox_auth_argument_spec()
    template_args = dict(
        node=dict(),
        src=dict(type='path'),
        template=dict(),
        content_type=dict(default='vztmpl', choices=['vztmpl', 'iso']),
        storage=dict(default='local'),
        timeout=dict(type='int', default=30),
        force=dict(type='bool', default=False),
        state=dict(default='present', choices=['present', 'absent']),
    )
    module_args.update(template_args)

    module = AnsibleModule(
        argument_spec=module_args,
        required_together=[('api_token_id', 'api_token_secret')],
        required_one_of=[('api_password', 'api_token_id')],
        required_if=[('state', 'absent', ['template'])]
    )

    proxmox = ProxmoxTemplateAnsible(module)

    state = module.params['state']
    node = module.params['node']
    storage = module.params['storage']
    timeout = module.params['timeout']

    if state == 'present':
        try:
            content_type = module.params['content_type']
            src = module.params['src']

            # download appliance template
            if content_type == 'vztmpl' and not src:
                template = module.params['template']

                if not template:
                    module.fail_json(msg='template param for downloading appliance template is mandatory')

                if proxmox.get_template(node, storage, content_type, template) and not module.params['force']:
                    module.exit_json(changed=False, msg='template with volid=%s:%s/%s already exists' % (storage, content_type, template))

                if proxmox.download_template(node, storage, template, timeout):
                    module.exit_json(changed=True, msg='template with volid=%s:%s/%s downloaded' % (storage, content_type, template))

            template = os.path.basename(src)
            if proxmox.get_template(node, storage, content_type, template) and not module.params['force']:
                module.exit_json(changed=False, msg='template with volid=%s:%s/%s is already exists' % (storage, content_type, template))
            elif not src:
                module.fail_json(msg='src param to uploading template file is mandatory')
            elif not (os.path.exists(src) and os.path.isfile(src)):
                module.fail_json(msg='template file on path %s not exists' % src)

            if proxmox.upload_template(node, storage, content_type, src, timeout):
                module.exit_json(changed=True, msg='template with volid=%s:%s/%s uploaded' % (storage, content_type, template))
        except Exception as e:
            module.fail_json(msg="uploading/downloading of template %s failed with exception: %s" % (template, e))

    elif state == 'absent':
        try:
            content_type = module.params['content_type']
            template = module.params['template']

            if not proxmox.get_template(node, storage, content_type, template):
                module.exit_json(changed=False, msg='template with volid=%s:%s/%s is already deleted' % (storage, content_type, template))

            if proxmox.delete_template(node, storage, content_type, template, timeout):
                module.exit_json(changed=True, msg='template with volid=%s:%s/%s deleted' % (storage, content_type, template))
        except Exception as e:
            module.fail_json(msg="deleting of template %s failed with exception: %s" % (template, e))


if __name__ == '__main__':
    main()

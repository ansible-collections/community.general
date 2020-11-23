#!/usr/bin/python
#
# Copyright: Ansible Project
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: proxmox_template
short_description: management of OS templates in Proxmox VE cluster
description:
  - allows you to upload/delete templates in Proxmox VE cluster
options:
  api_host:
    description:
      - the host of the Proxmox VE cluster
    type: str
    required: true
  api_user:
    description:
      - the user to authenticate with
    type: str
    required: true
  api_password:
    description:
      - the password to authenticate with
      - you can use PROXMOX_PASSWORD environment variable
    type: str
  api_token_id:
    description:
      - Specify the token ID.
    type: str
    version_added: 1.3.0
  api_token_secret:
    description:
      - Specify the token secret.
    type: str
    version_added: 1.3.0
  validate_certs:
    description:
      - enable / disable https certificate verification
    default: 'no'
    type: bool
  node:
    description:
      - Proxmox VE node, when you will operate with template
    type: str
  src:
    description:
      - path to uploaded file
      - required only for C(state=present)
    type: path
  template:
    description:
      - the template name
      - Required for state C(absent) to delete a template.
      - Required for state C(present) to download an appliance container template (pveam).
    type: str
  content_type:
    description:
      - content type
      - required only for C(state=present)
    type: str
    default: 'vztmpl'
    choices: ['vztmpl', 'iso']
  storage:
    description:
      - target storage
    type: str
    default: 'local'
  timeout:
    description:
      - timeout for operations
    type: int
    default: 30
  force:
    description:
      - can be used only with C(state=present), exists template will be overwritten
    type: bool
    default: 'no'
  state:
    description:
     - Indicate desired state of the template
    type: str
    choices: ['present', 'absent']
    default: present
notes:
  - Requires proxmoxer and requests modules on host. This modules can be installed with pip.
requirements: [ "proxmoxer", "requests" ]
author: Sergei Antipov (@UnderGreen)
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
    force: yes

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

try:
    from proxmoxer import ProxmoxAPI
    HAS_PROXMOXER = True
except ImportError:
    HAS_PROXMOXER = False

from ansible.module_utils.basic import AnsibleModule


def get_template(proxmox, node, storage, content_type, template):
    return [True for tmpl in proxmox.nodes(node).storage(storage).content.get()
            if tmpl['volid'] == '%s:%s/%s' % (storage, content_type, template)]


def task_status(module, proxmox, node, taskid, timeout):
    """
    Check the task status and wait until the task is completed or the timeout is reached.
    """
    while timeout:
        task_status = proxmox.nodes(node).tasks(taskid).status.get()
        if task_status['status'] == 'stopped' and task_status['exitstatus'] == 'OK':
            return True
        timeout = timeout - 1
        if timeout == 0:
            module.fail_json(msg='Reached timeout while waiting for uploading/downloading template. Last line in task before timeout: %s'
                                 % proxmox.node(node).tasks(taskid).log.get()[:1])

        time.sleep(1)
    return False


def upload_template(module, proxmox, node, storage, content_type, realpath, timeout):
    taskid = proxmox.nodes(node).storage(storage).upload.post(content=content_type, filename=open(realpath, 'rb'))
    return task_status(module, proxmox, node, taskid, timeout)


def download_template(module, proxmox, node, storage, template, timeout):
    taskid = proxmox.nodes(node).aplinfo.post(storage=storage, template=template)
    return task_status(module, proxmox, node, taskid, timeout)


def delete_template(module, proxmox, node, storage, content_type, template, timeout):
    volid = '%s:%s/%s' % (storage, content_type, template)
    proxmox.nodes(node).storage(storage).content.delete(volid)
    while timeout:
        if not get_template(proxmox, node, storage, content_type, template):
            return True
        timeout = timeout - 1
        if timeout == 0:
            module.fail_json(msg='Reached timeout while waiting for deleting template.')

        time.sleep(1)
    return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_host=dict(required=True),
            api_password=dict(no_log=True),
            api_token_id=dict(no_log=True),
            api_token_secret=dict(no_log=True),
            api_user=dict(required=True),
            validate_certs=dict(type='bool', default=False),
            node=dict(),
            src=dict(type='path'),
            template=dict(),
            content_type=dict(default='vztmpl', choices=['vztmpl', 'iso']),
            storage=dict(default='local'),
            timeout=dict(type='int', default=30),
            force=dict(type='bool', default=False),
            state=dict(default='present', choices=['present', 'absent']),
        )
    )

    if not HAS_PROXMOXER:
        module.fail_json(msg='proxmoxer required for this module')

    state = module.params['state']
    api_host = module.params['api_host']
    api_password = module.params['api_password']
    api_token_id = module.params['api_token_id']
    api_token_secret = module.params['api_token_secret']
    api_user = module.params['api_user']
    validate_certs = module.params['validate_certs']
    node = module.params['node']
    storage = module.params['storage']
    timeout = module.params['timeout']

    auth_args = {'user': api_user}
    if not (api_token_id and api_token_secret):
        # If password not set get it from PROXMOX_PASSWORD env
        if not api_password:
            try:
                api_password = os.environ['PROXMOX_PASSWORD']
            except KeyError as e:
                module.fail_json(msg='You should set api_password param or use PROXMOX_PASSWORD environment variable')
        auth_args['password'] = api_password
    else:
        auth_args['token_name'] = api_token_id
        auth_args['token_value'] = api_token_secret

    try:
        proxmox = ProxmoxAPI(api_host, verify_ssl=validate_certs, **auth_args)
        # Used to test the validity of the token if given
        proxmox.version.get()
    except Exception as e:
        module.fail_json(msg='authorization on proxmox cluster failed with exception: %s' % e)

    if state == 'present':
        try:
            content_type = module.params['content_type']
            src = module.params['src']

            # download appliance template
            if content_type == 'vztmpl' and not src:
                template = module.params['template']

                if not template:
                    module.fail_json(msg='template param for downloading appliance template is mandatory')

                if get_template(proxmox, node, storage, content_type, template) and not module.params['force']:
                    module.exit_json(changed=False, msg='template with volid=%s:%s/%s already exists' % (storage, content_type, template))

                if download_template(module, proxmox, node, storage, template, timeout):
                    module.exit_json(changed=True, msg='template with volid=%s:%s/%s downloaded' % (storage, content_type, template))

            template = os.path.basename(src)
            if get_template(proxmox, node, storage, content_type, template) and not module.params['force']:
                module.exit_json(changed=False, msg='template with volid=%s:%s/%s is already exists' % (storage, content_type, template))
            elif not src:
                module.fail_json(msg='src param to uploading template file is mandatory')
            elif not (os.path.exists(src) and os.path.isfile(src)):
                module.fail_json(msg='template file on path %s not exists' % src)

            if upload_template(module, proxmox, node, storage, content_type, src, timeout):
                module.exit_json(changed=True, msg='template with volid=%s:%s/%s uploaded' % (storage, content_type, template))
        except Exception as e:
            module.fail_json(msg="uploading/downloading of template %s failed with exception: %s" % (template, e))

    elif state == 'absent':
        try:
            content_type = module.params['content_type']
            template = module.params['template']

            if not template:
                module.fail_json(msg='template param is mandatory')
            elif not get_template(proxmox, node, storage, content_type, template):
                module.exit_json(changed=False, msg='template with volid=%s:%s/%s is already deleted' % (storage, content_type, template))

            if delete_template(module, proxmox, node, storage, content_type, template, timeout):
                module.exit_json(changed=True, msg='template with volid=%s:%s/%s deleted' % (storage, content_type, template))
        except Exception as e:
            module.fail_json(msg="deleting of template %s failed with exception: %s" % (template, e))


if __name__ == '__main__':
    main()

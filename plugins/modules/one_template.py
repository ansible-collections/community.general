#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Jyrki Gadinger <nilsding@nilsding.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
module: one_template

short_description: Manages OpenNebula templates

version_added: 2.4.0

requirements:
  - pyone

description:
  - Manages OpenNebula templates.
attributes:
  check_mode:
    support: partial
    details:
      - Note that check mode always returns C(changed=true) for existing templates, even if the template would not actually
        change.
  diff_mode:
    support: none

options:
  id:
    description:
      - A O(id) of the template you would like to manage. If not set then a new template will be created with the given O(name).
    type: int
  name:
    description:
      - A O(name) of the template you would like to manage. If a template with the given name does not exist it will be created,
        otherwise it will be managed by this module.
    type: str
  template:
    description:
      - A string containing the template contents.
    type: str
  state:
    description:
      - V(present) - state that is used to manage the template.
      - V(absent) - delete the template.
    choices: ["present", "absent"]
    default: present
    type: str
  filter:
    description:
      - V(user_primary_group) - Resources belonging to the user's primary group.
      - V(user) - Resources belonging to the user.
      - V(all) - All resources.
      - V(user_groups) - Resources belonging to the user and any of his groups.
    choices: [user_primary_group, user, all, user_groups]
    default: user
    type: str
    version_added: 10.3.0

extends_documentation_fragment:
  - community.general.opennebula
  - community.general.attributes

author:
  - "Jyrki Gadinger (@nilsding)"
"""

EXAMPLES = r"""
- name: Fetch the TEMPLATE by id
  community.general.one_template:
    id: 6459
  register: result

- name: Print the TEMPLATE properties
  ansible.builtin.debug:
    var: result

- name: Fetch the TEMPLATE by name
  community.general.one_template:
    name: tf-prd-users-workerredis-p6379a
  register: result

- name: Create a new or update an existing TEMPLATE
  community.general.one_template:
    name: generic-opensuse
    template: |
      CONTEXT = [
        HOSTNAME = "generic-opensuse"
      ]
      CPU = "1"
      CUSTOM_ATTRIBUTE = ""
      DISK = [
        CACHE = "writeback",
        DEV_PREFIX = "sd",
        DISCARD = "unmap",
        IMAGE = "opensuse-leap-15.2",
        IMAGE_UNAME = "oneadmin",
        IO = "threads",
        SIZE = "" ]
      MEMORY = "2048"
      NIC = [
        MODEL = "virtio",
        NETWORK = "testnet",
        NETWORK_UNAME = "oneadmin" ]
      OS = [
        ARCH = "x86_64",
        BOOT = "disk0" ]
      SCHED_REQUIREMENTS = "CLUSTER_ID=\\"100\\""
      VCPU = "2"

- name: Delete the TEMPLATE by id
  community.general.one_template:
    id: 6459
    state: absent
"""

RETURN = r"""
id:
  description: Template ID.
  type: int
  returned: when O(state=present)
  sample: 153
name:
  description: Template name.
  type: str
  returned: when O(state=present)
  sample: app1
template:
  description: The parsed template.
  type: dict
  returned: when O(state=present)
group_id:
  description: Template's group ID.
  type: int
  returned: when O(state=present)
  sample: 1
group_name:
  description: Template's group name.
  type: str
  returned: when O(state=present)
  sample: one-users
owner_id:
  description: Template's owner ID.
  type: int
  returned: when O(state=present)
  sample: 143
owner_name:
  description: Template's owner name.
  type: str
  returned: when O(state=present)
  sample: ansible-test
"""


from ansible_collections.community.general.plugins.module_utils.opennebula import OpenNebulaModule


class TemplateModule(OpenNebulaModule):
    def __init__(self):
        argument_spec = dict(
            id=dict(type='int', required=False),
            name=dict(type='str', required=False),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            template=dict(type='str', required=False),
            filter=dict(type='str', required=False, choices=['user_primary_group', 'user', 'all', 'user_groups'], default='user'),
        )

        mutually_exclusive = [
            ['id', 'name']
        ]

        required_one_of = [('id', 'name')]

        required_if = [
            ['state', 'present', ['template']]
        ]

        OpenNebulaModule.__init__(self,
                                  argument_spec,
                                  supports_check_mode=True,
                                  mutually_exclusive=mutually_exclusive,
                                  required_one_of=required_one_of,
                                  required_if=required_if)

    def run(self, one, module, result):
        params = module.params
        id = params.get('id')
        name = params.get('name')
        desired_state = params.get('state')
        template_data = params.get('template')
        filter = params.get('filter')

        self.result = {}

        template = self.get_template_instance(id, name, filter)
        needs_creation = False
        if not template and desired_state != 'absent':
            if id:
                module.fail_json(msg="There is no template with id=" + str(id))
            else:
                needs_creation = True

        if desired_state == 'absent':
            self.result = self.delete_template(template)
        else:
            if needs_creation:
                self.result = self.create_template(name, template_data, filter)
            else:
                self.result = self.update_template(template, template_data, filter)

        self.exit()

    def get_template(self, predicate, filter):
        # filter was included, for discussions see:
        # Issue: https://github.com/ansible-collections/community.general/issues/9278
        # PR: https://github.com/ansible-collections/community.general/pull/9547
        # the other two parameters are used for pagination, -1 for both essentially means "return all"
        filter_values = {'user_primary_group': -4, 'user': -3, 'all': -2, 'user_groups': -1}
        pool = self.one.templatepool.info(filter_values[filter], -1, -1)

        for template in pool.VMTEMPLATE:
            if predicate(template):
                return template

        return None

    def get_template_by_id(self, template_id, filter):
        return self.get_template(lambda template: (template.ID == template_id), filter)

    def get_template_by_name(self, name, filter):
        return self.get_template(lambda template: (template.NAME == name), filter)

    def get_template_instance(self, requested_id, requested_name, filter):
        if requested_id:
            return self.get_template_by_id(requested_id, filter)
        else:
            return self.get_template_by_name(requested_name, filter)

    def get_template_info(self, template):
        info = {
            'id': template.ID,
            'name': template.NAME,
            'template': template.TEMPLATE,
            'user_name': template.UNAME,
            'user_id': template.UID,
            'group_name': template.GNAME,
            'group_id': template.GID,
        }

        return info

    def create_template(self, name, template_data, filter):
        if not self.module.check_mode:
            self.one.template.allocate("NAME = \"" + name + "\"\n" + template_data)

        result = self.get_template_info(self.get_template_by_name(name, filter))
        result['changed'] = True

        return result

    def update_template(self, template, template_data, filter):
        if not self.module.check_mode:
            # 0 = replace the whole template
            self.one.template.update(template.ID, template_data, 0)

        result = self.get_template_info(self.get_template_by_id(template.ID, filter))
        if self.module.check_mode:
            # Unfortunately it is not easy to detect if the template would have changed, therefore always report a change here.
            result['changed'] = True
        else:
            # if the previous parsed template data is not equal to the updated one, this has changed
            result['changed'] = template.TEMPLATE != result['template']

        return result

    def delete_template(self, template):
        if not template:
            return {'changed': False}

        if not self.module.check_mode:
            self.one.template.delete(template.ID)

        return {'changed': True}


def main():
    TemplateModule().run_module()


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022, Håkon Lerring
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: consul_policy
short_description: Manipulate Consul policies
version_added: 7.2.0
description:
 - Allows the addition, modification and deletion of policies in a consul
   cluster via the agent. For more details on using and configuring ACLs,
   see U(https://www.consul.io/docs/guides/acl.html).
author:
  - Håkon Lerring (@Hakon)
extends_documentation_fragment:
  - community.general.consul
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  state:
    description:
      - Whether the policy should be present or absent.
    choices: ['present', 'absent']
    default: present
    type: str
  valid_datacenters:
    description:
      - Valid datacenters for the policy. All if list is empty.
    default: []
    type: list
    elements: str
  name:
    description:
      - The name that should be associated with the policy, this is opaque
        to Consul.
    required: true
    type: str
  description:
    description:
      - Description of the policy.
    type: str
    default: ''
  rules:
    type: str
    description:
      - Rule document that should be associated with the current policy.
'''

EXAMPLES = """
- name: Create a policy with rules
  community.general.consul_policy:
    host: consul1.example.com
    token: some_management_acl
    name: foo-access
    rules: |
        key "foo" {
            policy = "read"
        }
        key "private/foo" {
            policy = "deny"
        }

- name: Update the rules associated to a policy
  community.general.consul_policy:
    host: consul1.example.com
    token: some_management_acl
    name: foo-access
    rules: |
        key "foo" {
            policy = "read"
        }
        key "private/foo" {
            policy = "deny"
        }
        event "bbq" {
            policy = "write"
        }

- name: Remove a policy
  community.general.consul_policy:
    host: consul1.example.com
    token: some_management_acl
    name: foo-access
    state: absent
"""

RETURN = """
operation:
    description: The operation performed on the policy.
    returned: changed
    type: str
    sample: update
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.consul import (
    _ConsulModule, auth_argument_spec)

NAME_PARAMETER_NAME = "name"
DESCRIPTION_PARAMETER_NAME = "description"
RULES_PARAMETER_NAME = "rules"
VALID_DATACENTERS_PARAMETER_NAME = "valid_datacenters"
STATE_PARAMETER_NAME = "state"


PRESENT_STATE_VALUE = "present"
ABSENT_STATE_VALUE = "absent"

REMOVE_OPERATION = "remove"
UPDATE_OPERATION = "update"
CREATE_OPERATION = "create"

_ARGUMENT_SPEC = {
    NAME_PARAMETER_NAME: dict(required=True),
    DESCRIPTION_PARAMETER_NAME: dict(required=False, type='str', default=''),
    RULES_PARAMETER_NAME: dict(type='str'),
    VALID_DATACENTERS_PARAMETER_NAME: dict(type='list', elements='str', default=[]),
    STATE_PARAMETER_NAME: dict(default=PRESENT_STATE_VALUE, choices=[PRESENT_STATE_VALUE, ABSENT_STATE_VALUE])
}
_ARGUMENT_SPEC.update(auth_argument_spec())


def update_policy(policy, configuration, consul_module):
    updated_policy = consul_module.put(('acl', 'policy', policy['ID']), data={
        'Name': configuration.name,  # should be equal at this point.
        'Description': configuration.description,
        'Rules': configuration.rules,
        'Datacenters': configuration.valid_datacenters
    })

    changed = (
        policy.get('Rules', "") != updated_policy.get('Rules', "") or
        policy.get('Description', "") != updated_policy.get('Description', "") or
        policy.get('Datacenters', []) != updated_policy.get('Datacenters', [])
    )

    return Output(changed=changed, operation=UPDATE_OPERATION, policy=updated_policy)


def create_policy(configuration, consul_module):
    created_policy = consul_module.put('acl/policy', data={
        'Name': configuration.name,
        'Description': configuration.description,
        'Rules': configuration.rules,
        'Datacenters': configuration.valid_datacenters
    })
    return Output(changed=True, operation=CREATE_OPERATION, policy=created_policy)


def remove_policy(configuration, consul_module):
    policies = get_policies(consul_module)

    if configuration.name in policies:

        policy_id = policies[configuration.name]['ID']
        policy = get_policy(policy_id, consul_module)
        consul_module.delete(('acl', 'policy', policy['ID']))

        changed = True
    else:
        changed = False
    return Output(changed=changed, operation=REMOVE_OPERATION)


def get_policies(consul_module):
    policies = consul_module.get('acl/policies')
    existing_policies_mapped_by_name = dict(
        (policy['Name'], policy) for policy in policies if policy['Name'] is not None)
    return existing_policies_mapped_by_name


def get_policy(id, consul_module):
    return consul_module.get(('acl', 'policy', id))


def set_policy(configuration, consul_module):
    policies = get_policies(consul_module)

    if configuration.name in policies:
        index_policy_object = policies[configuration.name]
        policy_id = policies[configuration.name]['ID']
        rest_policy_object = get_policy(policy_id, consul_module)
        # merge dicts as some keys are only available in the partial policy
        policy = index_policy_object.copy()
        policy.update(rest_policy_object)
        return update_policy(policy, configuration, consul_module)
    else:
        return create_policy(configuration, consul_module)


class Configuration:
    """
    Configuration for this module.
    """

    def __init__(self, name=None, description=None, rules=None, valid_datacenters=None, state=None):
        self.name = name                            # type: str
        self.description = description              # type: str
        self.rules = rules                          # type: str
        self.valid_datacenters = valid_datacenters  # type: str
        self.state = state                          # type: str


class Output:
    """
    Output of an action of this module.
    """

    def __init__(self, changed=None, operation=None, policy=None):
        self.changed = changed      # type: bool
        self.operation = operation  # type: str
        self.policy = policy        # type: dict


def main():
    """
    Main method.
    """
    module = AnsibleModule(_ARGUMENT_SPEC, supports_check_mode=False)
    consul_module = _ConsulModule(module)

    configuration = Configuration(
        name=module.params.get(NAME_PARAMETER_NAME),
        description=module.params.get(DESCRIPTION_PARAMETER_NAME),
        rules=module.params.get(RULES_PARAMETER_NAME),
        valid_datacenters=module.params.get(VALID_DATACENTERS_PARAMETER_NAME),
        state=module.params.get(STATE_PARAMETER_NAME),
    )

    if configuration.state == PRESENT_STATE_VALUE:
        output = set_policy(configuration, consul_module)
    else:
        output = remove_policy(configuration, consul_module)

    return_values = dict(changed=output.changed, operation=output.operation, policy=output.policy)
    module.exit_json(**return_values)


if __name__ == "__main__":
    main()

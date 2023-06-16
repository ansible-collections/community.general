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
    required: false
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
    required: false
    type: str
    default: ''
  rules:
    type: str
    description:
      - Rule document that should be associated with the current policy.
    required: false
  host:
    description:
      - Host of the consul agent, defaults to localhost.
    required: false
    default: localhost
    type: str
  port:
    type: int
    description:
      - The port on which the consul agent is running.
    required: false
    default: 8500
  scheme:
    description:
      - The protocol scheme on which the consul agent is running.
    required: false
    default: http
    type: str
  token:
    description:
      - A management token is required to manipulate the policies.
    type: str
  validate_certs:
    type: bool
    description:
      - Whether to verify the TLS certificate of the consul agent or not.
    required: false
    default: true
requirements:
  - requests
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

try:
    from requests.exceptions import ConnectionError
    import requests
    has_requests = True
except ImportError:
    has_requests = False


TOKEN_PARAMETER_NAME = "token"
HOST_PARAMETER_NAME = "host"
SCHEME_PARAMETER_NAME = "scheme"
VALIDATE_CERTS_PARAMETER_NAME = "validate_certs"
NAME_PARAMETER_NAME = "name"
DESCRIPTION_PARAMETER_NAME = "description"
PORT_PARAMETER_NAME = "port"
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
    PORT_PARAMETER_NAME: dict(default=8500, type='int'),
    RULES_PARAMETER_NAME: dict(type='str'),
    VALID_DATACENTERS_PARAMETER_NAME: dict(type='list', elements='str', default=[]),
    HOST_PARAMETER_NAME: dict(default='localhost'),
    SCHEME_PARAMETER_NAME: dict(default='http'),
    TOKEN_PARAMETER_NAME: dict(no_log=True),
    VALIDATE_CERTS_PARAMETER_NAME: dict(type='bool', default=True),
    STATE_PARAMETER_NAME: dict(default=PRESENT_STATE_VALUE, choices=[PRESENT_STATE_VALUE, ABSENT_STATE_VALUE]),
}


def get_consul_url(configuration):
    return '%s://%s:%s/v1' % (configuration.scheme,
                              configuration.host, configuration.port)


def get_auth_headers(configuration):
    if configuration.token is None:
        return {}
    else:
        return {'X-Consul-Token': configuration.token}


class RequestError(Exception):
    pass


def handle_consul_response_error(response):
    if 400 <= response.status_code < 600:
        raise RequestError('%d %s' % (response.status_code, response.content))


def update_policy(policy, configuration):
    url = '%s/acl/policy/%s' % (get_consul_url(configuration), policy['ID'])
    headers = get_auth_headers(configuration)
    response = requests.put(url, headers=headers, json={
        'Name': configuration.name,  # should be equal at this point.
        'Description': configuration.description,
        'Rules': configuration.rules,
        'Datacenters': configuration.valid_datacenters
    }, verify=configuration.validate_certs)
    handle_consul_response_error(response)

    updated_policy = response.json()

    changed = (
        policy.get('Rules', "") != updated_policy.get('Rules', "") or
        policy.get('Description', "") != updated_policy.get('Description', "") or
        policy.get('Datacenters', []) != updated_policy.get('Datacenters', [])
    )

    return Output(changed=changed, operation=UPDATE_OPERATION, policy=updated_policy)


def create_policy(configuration):
    url = '%s/acl/policy' % get_consul_url(configuration)
    headers = get_auth_headers(configuration)
    response = requests.put(url, headers=headers, json={
        'Name': configuration.name,
        'Description': configuration.description,
        'Rules': configuration.rules,
        'Datacenters': configuration.valid_datacenters
    }, verify=configuration.validate_certs)
    handle_consul_response_error(response)

    created_policy = response.json()

    return Output(changed=True, operation=CREATE_OPERATION, policy=created_policy)


def remove_policy(configuration):
    policies = get_policies(configuration)

    if configuration.name in policies:

        policy_id = policies[configuration.name]['ID']
        policy = get_policy(policy_id, configuration)

        url = '%s/acl/policy/%s' % (get_consul_url(configuration),
                                    policy['ID'])
        headers = get_auth_headers(configuration)
        response = requests.delete(url, headers=headers, verify=configuration.validate_certs)
        handle_consul_response_error(response)

        changed = True
    else:
        changed = False
    return Output(changed=changed, operation=REMOVE_OPERATION)


def get_policies(configuration):
    url = '%s/acl/policies' % get_consul_url(configuration)
    headers = get_auth_headers(configuration)
    response = requests.get(url, headers=headers, verify=configuration.validate_certs)
    handle_consul_response_error(response)
    policies = response.json()
    existing_policies_mapped_by_name = dict(
        (policy['Name'], policy) for policy in policies if policy['Name'] is not None)
    return existing_policies_mapped_by_name


def get_policy(id, configuration):
    url = '%s/acl/policy/%s' % (get_consul_url(configuration), id)
    headers = get_auth_headers(configuration)
    response = requests.get(url, headers=headers, verify=configuration.validate_certs)
    handle_consul_response_error(response)
    return response.json()


def set_policy(configuration):
    policies = get_policies(configuration)

    if configuration.name in policies:
        index_policy_object = policies[configuration.name]
        policy_id = policies[configuration.name]['ID']
        rest_policy_object = get_policy(policy_id, configuration)
        # merge dicts as some keys are only available in the partial policy
        policy = index_policy_object.copy()
        policy.update(rest_policy_object)
        return update_policy(policy, configuration)
    else:
        return create_policy(configuration)


class Configuration:
    """
    Configuration for this module.
    """

    def __init__(self, token=None, host=None, scheme=None, validate_certs=None, name=None, description=None, port=None,
                 rules=None, valid_datacenters=None, state=None):
        self.token = token                          # type: str
        self.host = host                            # type: str
        self.scheme = scheme                        # type: str
        self.validate_certs = validate_certs        # type: bool
        self.name = name                            # type: str
        self.description = description              # type: str
        self.port = port                            # type: int
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


def check_dependencies():
    """
    Checks that the required dependencies have been imported.
    :exception ImportError: if it is detected that any of the required dependencies have not been imported
    """

    if not has_requests:
        raise ImportError(
            "requests required for this module. See https://pypi.org/project/requests/")


def main():
    """
    Main method.
    """
    module = AnsibleModule(_ARGUMENT_SPEC, supports_check_mode=False)

    try:
        check_dependencies()
    except ImportError as e:
        module.fail_json(msg=str(e))

    configuration = Configuration(
        token=module.params.get(TOKEN_PARAMETER_NAME),
        host=module.params.get(HOST_PARAMETER_NAME),
        scheme=module.params.get(SCHEME_PARAMETER_NAME),
        validate_certs=module.params.get(VALIDATE_CERTS_PARAMETER_NAME),
        name=module.params.get(NAME_PARAMETER_NAME),
        description=module.params.get(DESCRIPTION_PARAMETER_NAME),
        port=module.params.get(PORT_PARAMETER_NAME),
        rules=module.params.get(RULES_PARAMETER_NAME),
        valid_datacenters=module.params.get(VALID_DATACENTERS_PARAMETER_NAME),
        state=module.params.get(STATE_PARAMETER_NAME),
    )

    try:
        if configuration.state == PRESENT_STATE_VALUE:
            output = set_policy(configuration)
        else:
            output = remove_policy(configuration)
    except ConnectionError as e:
        module.fail_json(msg='Could not connect to consul agent at %s:%s, error was %s' % (
            configuration.host, configuration.port, str(e)))
        raise

    return_values = dict(changed=output.changed, operation=output.operation, policy=output.policy)
    module.exit_json(**return_values)


if __name__ == "__main__":
    main()

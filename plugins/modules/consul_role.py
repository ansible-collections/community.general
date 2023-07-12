#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022, Håkon Lerring
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
module: consul_role
short_description: Manipulate Consul roles
version_added: 7.2.0
description:
 - Allows the addition, modification and deletion of roles in a consul
   cluster via the agent. For more details on using and configuring ACLs,
   see https://www.consul.io/docs/guides/acl.html.
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
  name:
    description:
      - A name used to identify the role.
    required: true
    type: str
  state:
    description:
      - whether the role should be present or absent.
    required: false
    choices: ['present', 'absent']
    default: present
    type: str
  description:
    description:
      - Description of the role.
    required: false
    type: str
    default: ''
  policies:
    type: list
    elements: dict
    description:
      - List of policies to attach to the role.
      - Each element must have a "name" or "id" (or both) to identify the policy. See consul_policy for more info.
    required: false
    default: []
  service_identities:
    type: list
    elements: dict
    description:
      - List of service identities to attach to the role.
      - Each element must have a "name" and optionally a "datacenters" list of datacenters the policy is valid for.
      - An empty datacenters list allows all datacenters
    required: false
    default: []
  node_identities:
    type: list
    elements: dict
    description:
      - List of node identities to attach to the role.
      - Each element must have a "name" and optionally a "datacenter" the policy is valid for. An empty datacenter allows all datacenters
    required: false
    default: []
  host:
    description:
      - host of the consul agent, defaults to localhost.
    required: false
    default: localhost
    type: str
  port:
    type: int
    description:
      - the port on which the consul agent is running.
    required: false
    default: 8500
  scheme:
    description:
      - the protocol scheme on which the consul agent is running.
    required: false
    default: http
    type: str
  token:
    description:
      - a management token is required to manipulate the roles.
    type: str
  validate_certs:
    type: bool
    description:
      - whether to verify the tls certificate of the consul agent
    required: false
    default: True
requirements:
  - requests
'''

EXAMPLES = """
- name: Create a role with 2 policies
  community.general.consul_role:
    host: consul1.example.com
    token: some_management_acl
    name: foo-role
    policies:
      - id: 783beef3-783f-f41f-7422-7087dc272765
      - name: "policy-1"
- name: Create a role with service identity
  community.general.consul_role:
    host: consul1.example.com
    token: some_management_acl
    name: foo-role-2
    service_identities:
      - name: web
        datacenters:
          - dc1
- name: Create a role with node identity
  community.general.consul_role:
    host: consul1.example.com
    token: some_management_acl
    name: foo-role-3
    node_identities:
      - name: node-1
        datacenter: dc2
- name: Remove a role
  community.general.consul_role:
    host: consul1.example.com
    token: some_management_acl
    name: foo-role-3
    state: absent
"""

RETURN = """
role:
    description: The role object
    returned: success
    type: str
    sample: |
        {
            "CreateIndex": 39,
            "Description": "",
            "Hash": "Trt0QJtxVEfvTTIcdTUbIJRr6Dsi6E4EcwSFxx9tCYM=",
            "ID": "9a300b8d-48db-b720-8544-a37c0f5dafb5",
            "ModifyIndex": 39,
            "Name": "foo-role",
            "Policies": [
                {"ID": "b1a00172-d7a1-0e66-a12e-7a4045c4b774", "Name": "foo-access"}
            ]
        }
operation:
    description: the operation performed on the role
    returned: changed
    type: str
    sample: update
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib
from ansible_collections.community.general.plugins.module_utils.consul import (
    get_consul_url, get_auth_headers, RequestError, handle_consul_response_error)
import traceback

REQUESTS_IMP_ERR = None

try:
    from requests.exceptions import ConnectionError
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    REQUESTS_IMP_ERR = traceback.format_exc()

TOKEN_PARAMETER_NAME = "token"
HOST_PARAMETER_NAME = "host"
SCHEME_PARAMETER_NAME = "scheme"
VALIDATE_CERTS_PARAMETER_NAME = "validate_certs"
NAME_PARAMETER_NAME = "name"
DESCRIPTION_PARAMETER_NAME = "description"
PORT_PARAMETER_NAME = "port"
POLICIES_PARAMETER_NAME = "policies"
SERVICE_IDENTITIES_PARAMETER_NAME = "service_identities"
NODE_IDENTITIES_PARAMETER_NAME = "node_identities"
STATE_PARAMETER_NAME = "state"

PRESENT_STATE_VALUE = "present"
ABSENT_STATE_VALUE = "absent"

REMOVE_OPERATION = "remove"
UPDATE_OPERATION = "update"
CREATE_OPERATION = "create"

_ARGUMENT_SPEC = {
    TOKEN_PARAMETER_NAME: dict(no_log=True),
    PORT_PARAMETER_NAME: dict(default=8500, type='int'),
    HOST_PARAMETER_NAME: dict(default='localhost'),
    SCHEME_PARAMETER_NAME: dict(default='http'),
    VALIDATE_CERTS_PARAMETER_NAME: dict(type='bool', default=True),
    NAME_PARAMETER_NAME: dict(required=True),
    DESCRIPTION_PARAMETER_NAME: dict(required=False, type='str', default=''),
    POLICIES_PARAMETER_NAME: dict(type='list', elements='dict', default=[]),
    SERVICE_IDENTITIES_PARAMETER_NAME: dict(type='list', elements='dict', default=[]),
    NODE_IDENTITIES_PARAMETER_NAME: dict(type='list', elements='dict', default=[]),
    STATE_PARAMETER_NAME: dict(default=PRESENT_STATE_VALUE, choices=[PRESENT_STATE_VALUE, ABSENT_STATE_VALUE]),
}


def update_role(role, configuration):
    url = '%s/acl/role/%s' % (get_consul_url(configuration),
                              role['Name'])
    headers = get_auth_headers(configuration)

    update_role_data = {
        'Description': configuration.description,
        'Policies': [x.to_dict() for x in configuration.policies],
    }

    if configuration.version >= ConsulVersion("1.5.0"):
        update_role_data["ServiceIdentities"] = [
            x.to_dict() for x in configuration.service_identities]

    if configuration.version >= ConsulVersion("1.8.0"):
        update_role_data["NodeIdentities"] = [
            x.to_dict() for x in configuration.node_identities]

    response = requests.put(url, headers=headers, json=update_role_data, verify=configuration.validate_certs)
    handle_consul_response_error(response)

    resulting_role = response.json()
    changed = (
        role['Description'] != resulting_role['Description'] or
        role.get('Policies', None) != resulting_role.get('Policies', None) or
        role.get('ServiceIdentities', None) != resulting_role.get('ServiceIdentities', None) or
        role.get('NodeIdentities', None) != resulting_role.get('NodeIdentities', None)
    )

    return Output(changed=changed, operation=UPDATE_OPERATION, role=resulting_role)


def create_role(configuration):
    url = '%s/acl/role' % get_consul_url(configuration)
    headers = get_auth_headers(configuration)
    create_role_data = {
        'Name': configuration.name,
        'Description': configuration.description,
        'Policies': [x.to_dict() for x in configuration.policies],
    }
    if configuration.version >= ConsulVersion("1.5.0"):
        create_role_data["ServiceIdentities"] = [x.to_dict() for x in configuration.service_identities]

    if configuration.version >= ConsulVersion("1.8.0"):
        create_role_data["NodeIdentities"] = [x.to_dict() for x in configuration.node_identities]

    response = requests.put(url, headers=headers, json=create_role_data, verify=configuration.validate_certs)
    handle_consul_response_error(response)

    resulting_role = response.json()

    return Output(changed=True, operation=CREATE_OPERATION, role=resulting_role)


def remove_role(configuration):
    roles = get_roles(configuration)

    if configuration.name in roles:

        role_id = roles[configuration.name]['ID']

        url = '%s/acl/role/%s' % (get_consul_url(configuration), role_id)
        headers = get_auth_headers(configuration)
        response = requests.delete(url, headers=headers, verify=configuration.validate_certs)
        handle_consul_response_error(response)

        changed = True
    else:
        changed = False
    return Output(changed=changed, operation=REMOVE_OPERATION)


def get_roles(configuration):
    url = '%s/acl/roles' % get_consul_url(configuration)
    headers = get_auth_headers(configuration)
    response = requests.get(url, headers=headers, verify=configuration.validate_certs)
    handle_consul_response_error(response)
    roles = response.json()
    existing_roles_mapped_by_id = dict((role['Name'], role) for role in roles if role['Name'] is not None)
    return existing_roles_mapped_by_id


def get_consul_version(configuration):
    url = '%s/agent/self' % get_consul_url(configuration)
    headers = get_auth_headers(configuration)
    response = requests.get(url, headers=headers, verify=configuration.validate_certs)
    handle_consul_response_error(response)
    config = response.json()["Config"]
    return ConsulVersion(config["Version"])


def set_role(configuration):
    roles = get_roles(configuration)

    if configuration.name in roles:
        role = roles[configuration.name]
        return update_role(role, configuration)
    else:
        return create_role(configuration)


class ConsulVersion:
    def __init__(self, version_string):
        split = version_string.split('.')
        self.major = split[0]
        self.minor = split[1]
        self.patch = split[2]

    def __ge__(self, other):
        return int(self.major + self.minor +
                   self.patch) >= int(other.major + other.minor + other.patch)

    def __le__(self, other):
        return int(self.major + self.minor +
                   self.patch) <= int(other.major + other.minor + other.patch)


class ServiceIdentity:
    def __init__(self, input):
        if not isinstance(input, dict) or 'name' not in input:
            raise ValueError(
                "Each element of service_identities must be a dict with the keys name and optionally datacenters")
        self.name = input["name"]
        self.datacenters = input["datacenters"] if "datacenters" in input else None

    def to_dict(self):
        return {
            "ServiceName": self.name,
            "Datacenters": self.datacenters
        }


class NodeIdentity:
    def __init__(self, input):
        if not isinstance(input, dict) or 'name' not in input:
            raise ValueError(
                "Each element of node_identities must be a dict with the keys name and optionally datacenter")
        self.name = input["name"]
        self.datacenter = input["datacenter"] if "datacenter" in input else None

    def to_dict(self):
        return {
            "NodeName": self.name,
            "Datacenter": self.datacenter
        }


class RoleLink:
    def __init__(self, dict):
        self.id = dict.get("id", None)
        self.name = dict.get("name", None)

    def to_dict(self):
        return {
            "ID": self.id,
            "Name": self.name
        }


class PolicyLink:
    def __init__(self, dict):
        self.id = dict.get("id", None)
        self.name = dict.get("name", None)

    def to_dict(self):
        return {
            "ID": self.id,
            "Name": self.name
        }


class Configuration:
    """
    Configuration for this module.
    """

    def __init__(self, token=None, host=None, scheme=None, validate_certs=None, name=None, description=None, port=None,
                 policies=None, service_identities=None, node_identities=None, state=None):
        self.token = token                                    # type: str
        self.host = host                                                            # type: str
        self.port = port                                                            # type: int
        self.scheme = scheme                                                        # type: str
        self.validate_certs = validate_certs                                        # type: bool
        self.name = name                                                            # type: str
        self.description = description                                              # type: str
        self.policies = [PolicyLink(p) for p in policies]                           # type: list(PolicyLink)
        self.service_identities = [ServiceIdentity(s) for s in service_identities]  # type: list(ServiceIdentity)
        self.node_identities = [NodeIdentity(n) for n in node_identities]           # type: list(NodeIdentity)
        self.state = state                                                          # type: str


class Output:
    """
    Output of an action of this module.
    """

    def __init__(self, changed=None, operation=None, role=None):
        self.changed = changed      # type: bool
        self.operation = operation  # type: str
        self.role = role          # type: dict


def main():
    """
    Main method.
    """
    module = AnsibleModule(_ARGUMENT_SPEC, supports_check_mode=False)

    if not HAS_REQUESTS:
        module.fail_json(msg=missing_required_lib("requests"),
                         exception=REQUESTS_IMP_ERR)

    try:
        configuration = Configuration(
            token=module.params.get(TOKEN_PARAMETER_NAME),
            host=module.params.get(HOST_PARAMETER_NAME),
            port=module.params.get(PORT_PARAMETER_NAME),
            scheme=module.params.get(SCHEME_PARAMETER_NAME),
            validate_certs=module.params.get(VALIDATE_CERTS_PARAMETER_NAME),
            name=module.params.get(NAME_PARAMETER_NAME),
            description=module.params.get(DESCRIPTION_PARAMETER_NAME),
            policies=module.params.get(POLICIES_PARAMETER_NAME),
            service_identities=module.params.get(SERVICE_IDENTITIES_PARAMETER_NAME),
            node_identities=module.params.get(NODE_IDENTITIES_PARAMETER_NAME),
            state=module.params.get(STATE_PARAMETER_NAME),

        )
    except ValueError as err:
        module.fail_json(msg='Configuration error: %s' % str(err))
        return

    try:

        version = get_consul_version(configuration)
        configuration.version = version
        if configuration.state == PRESENT_STATE_VALUE:
            output = set_role(configuration)
        else:
            output = remove_role(configuration)
    except ConnectionError as e:
        module.fail_json(msg='Could not connect to consul agent at %s:%s, error was %s' % (
            configuration.host, configuration.port, str(e)))
        raise

    return_values = dict(changed=output.changed, operation=output.operation, role=output.role)
    module.exit_json(**return_values)


if __name__ == "__main__":
    main()

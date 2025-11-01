#!/usr/bin/python

# Copyright (c) 2024, Michael Ilg
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: consul_agent_service
short_description: Add, modify and delete services within a Consul cluster
version_added: 9.1.0
description:
  - Allows the addition, modification and deletion of services in a Consul cluster using the agent.
  - There are currently no plans to create services and checks in one. This is because the Consul API does not provide checks
    for a service and the checks themselves do not match the module parameters. Therefore, only a service without checks can
    be created in this module.
author:
  - Michael Ilg (@Ilgmi)
extends_documentation_fragment:
  - community.general.consul
  - community.general.consul.actiongroup_consul
  - community.general.consul.token
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: partial
    details:
      - In check mode the diff misses operational attributes.
options:
  state:
    description:
      - Whether the service should be present or absent.
    choices: ['present', 'absent']
    default: present
    type: str
  name:
    description:
      - Unique name for the service on a node, must be unique per node, required if registering a service.
    type: str
  id:
    description:
      - Specifies a unique ID for this service. This must be unique per agent. This defaults to the O(name) parameter if not
        provided. If O(state=absent), defaults to the service name if supplied.
    type: str
  tags:
    description:
      - Tags that are attached to the service registration.
    type: list
    elements: str
  address:
    description:
      - The address to advertise that the service listens on. This value is passed as the C(address) parameter to Consul's
        C(/v1/agent/service/register) API method, so refer to the Consul API documentation for further details.
    type: str
  meta:
    description:
      - Optional meta data used for filtering. For keys, the characters C(A-Z), C(a-z), C(0-9), C(_), C(-) are allowed. Not
        allowed characters are replaced with underscores.
    type: dict
  service_port:
    description:
      - The port on which the service is listening. Can optionally be supplied for registration of a service, that is if O(name)
        or O(id) is set.
    type: int
  enable_tag_override:
    description:
      - Specifies to disable the anti-entropy feature for this service's tags. If C(EnableTagOverride) is set to true then
        external agents can update this service in the catalog and modify the tags.
    type: bool
    default: false
  weights:
    description:
      - Specifies weights for the service.
    type: dict
    suboptions:
      passing:
        description:
          - Weights for passing.
        type: int
        default: 1
      warning:
        description:
          - Weights for warning.
        type: int
        default: 1
    default: {"passing": 1, "warning": 1}
"""

EXAMPLES = r"""
- name: Register nginx service with the local Consul agent
  community.general.consul_agent_service:
    host: consul1.example.com
    token: some_management_acl
    name: nginx
    service_port: 80

- name: Register nginx with a tcp check
  community.general.consul_agent_service:
    host: consul1.example.com
    token: some_management_acl
    name: nginx
    service_port: 80

- name: Register nginx with an http check
  community.general.consul_agent_service:
    host: consul1.example.com
    token: some_management_acl
    name: nginx
    service_port: 80

- name: Register external service nginx available at 10.1.5.23
  community.general.consul_agent_service:
    host: consul1.example.com
    token: some_management_acl
    name: nginx
    service_port: 80
    address: 10.1.5.23

- name: Register nginx with some service tags
  community.general.consul_agent_service:
    host: consul1.example.com
    token: some_management_acl
    name: nginx
    service_port: 80
    tags:
      - prod
      - webservers

- name: Register nginx with some service meta
  community.general.consul_agent_service:
    host: consul1.example.com
    token: some_management_acl
    name: nginx
    service_port: 80
    meta:
      nginx_version: 1.25.3

- name: Remove nginx service
  community.general.consul_agent_service:
    host: consul1.example.com
    token: some_management_acl
    service_id: nginx
    state: absent

- name: Register celery worker service
  community.general.consul_agent_service:
    host: consul1.example.com
    token: some_management_acl
    name: celery-worker
    tags:
      - prod
      - worker
"""

RETURN = r"""
service:
  description: The service as returned by the Consul HTTP API.
  returned: always
  type: dict
  sample:
    ID: nginx
    Service: nginx
    Address: localhost
    Port: 80
    Tags:
      - http
    Meta:
      - nginx_version: 1.23.3
    Datacenter: dc1
    Weights:
      Passing: 1
      Warning: 1
    ContentHash: 61a245cd985261ac
    EnableTagOverride: false
operation:
  description: The operation performed.
  returned: changed
  type: str
  sample: update
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.consul import (
    AUTH_ARGUMENTS_SPEC,
    OPERATION_CREATE,
    OPERATION_UPDATE,
    OPERATION_DELETE,
    _ConsulModule,
)

_CHECK_MUTUALLY_EXCLUSIVE = [("args", "ttl", "tcp", "http")]
_CHECK_REQUIRED_BY = {
    "args": "interval",
    "http": "interval",
    "tcp": "interval",
}

_ARGUMENT_SPEC = {
    "state": dict(default="present", choices=["present", "absent"]),
    "name": dict(type="str"),
    "id": dict(type="str"),
    "tags": dict(type="list", elements="str"),
    "address": dict(type="str"),
    "meta": dict(type="dict"),
    "service_port": dict(type="int"),
    "enable_tag_override": dict(type="bool", default=False),
    "weights": dict(
        type="dict",
        options=dict(passing=dict(type="int", default=1, no_log=False), warning=dict(type="int", default=1)),
        default={"passing": 1, "warning": 1},
    ),
}

_REQUIRED_IF = [
    ("state", "present", ["name"]),
    ("state", "absent", ("id", "name"), True),
]

_ARGUMENT_SPEC.update(AUTH_ARGUMENTS_SPEC)


class ConsulAgentServiceModule(_ConsulModule):
    api_endpoint = "agent/service"
    result_key = "service"
    unique_identifiers = ["id", "name"]
    operational_attributes = {"Service", "ContentHash", "Datacenter"}

    def endpoint_url(self, operation, identifier=None):
        if operation in [OPERATION_CREATE, OPERATION_UPDATE]:
            return f"{self.api_endpoint}/register"
        if operation == OPERATION_DELETE:
            return f"{self.api_endpoint}/deregister/{identifier}"

        return super().endpoint_url(operation, identifier)

    def prepare_object(self, existing, obj):
        existing = super().prepare_object(existing, obj)
        if "ServicePort" in existing:
            existing["Port"] = existing.pop("ServicePort")

        if "ID" not in existing:
            existing["ID"] = existing["Name"]

        return existing

    def needs_update(self, api_obj, module_obj):
        obj = {}
        if "Service" in api_obj:
            obj["Service"] = api_obj["Service"]
        api_obj = self.prepare_object(api_obj, obj)

        if "Name" in module_obj:
            module_obj["Service"] = module_obj.pop("Name")
        if "ServicePort" in module_obj:
            module_obj["Port"] = module_obj.pop("ServicePort")

        return super().needs_update(api_obj, module_obj)

    def delete_object(self, obj):
        if not self._module.check_mode:
            url = self.endpoint_url(OPERATION_DELETE, self.id_from_obj(obj, camel_case=True))
            self.put(url)
        return {}


def main():
    module = AnsibleModule(
        _ARGUMENT_SPEC,
        required_if=_REQUIRED_IF,
        supports_check_mode=True,
    )

    consul_module = ConsulAgentServiceModule(module)
    consul_module.execute()


if __name__ == "__main__":
    main()

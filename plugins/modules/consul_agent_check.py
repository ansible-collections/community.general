#!/usr/bin/python

# Copyright (c) 2024, Michael Ilg
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: consul_agent_check
short_description: Add, modify, and delete checks within a Consul cluster
version_added: 9.1.0
description:
  - Allows the addition, modification and deletion of checks in a Consul cluster using the agent. For more details on using
    and configuring Checks, see U(https://developer.hashicorp.com/consul/api-docs/agent/check).
  - Currently, there is no complete way to retrieve the script, interval or TTL metadata for a registered check. Without this
    metadata it is not possible to tell if the data supplied with ansible represents a change to a check. As a result, the
    module does not attempt to determine changes and it always reports a changed occurred. An API method is planned to supply
    this metadata so at that stage change management is to be added.
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
    details:
      - The result is the object as it is defined in the module options and not the object structure of the Consul API. For
        a better overview of what the object structure looks like, take a look at U(https://developer.hashicorp.com/consul/api-docs/agent/check#list-checks).
  diff_mode:
    support: partial
    details:
      - In check mode the diff shows the object as it is defined in the module options and not the object structure of the
        Consul API.
options:
  state:
    description:
      - Whether the check should be present or absent.
    choices: ['present', 'absent']
    default: present
    type: str
  name:
    description:
      - Required name for the service check.
    type: str
  id:
    description:
      - Specifies a unique ID for this check on the node. This defaults to the O(name) parameter, but it may be necessary
        to provide an ID for uniqueness. This value is returned in the response as V(CheckId).
    type: str
  interval:
    description:
      - The interval at which the service check is run. This is a number with a V(s) or V(m) suffix to signify the units of
        seconds or minutes, for example V(15s) or V(1m). If no suffix is supplied V(s) is used by default, for example V(10)
        is equivalent to V(10s).
      - Required if one of the parameters O(args), O(http), or O(tcp) is specified.
    type: str
  notes:
    description:
      - Notes to attach to check when registering it.
    type: str
  args:
    description:
      - Specifies command arguments to run to update the status of the check.
      - Requires O(interval) to be provided.
      - Mutually exclusive with O(ttl), O(tcp) and O(http).
    type: list
    elements: str
  ttl:
    description:
      - Checks can be registered with a TTL instead of a O(args) and O(interval) this means that the service checks in with
        the agent before the TTL expires. If it does not the check is considered failed. Required if registering a check and
        the script an interval are missing Similar to the interval this is a number with a V(s) or V(m) suffix to signify
        the units of seconds or minutes, for example V(15s) or V(1m). If no suffix is supplied V(s) is used by default, for
        example V(10) is equivalent to V(10s).
      - Mutually exclusive with O(args), O(tcp) and O(http).
    type: str
  tcp:
    description:
      - Checks can be registered with a TCP port. This means that Consul will check if the connection attempt to that port
        is successful (that is, the port is currently accepting connections). The format is V(host:port), for example V(localhost:80).
      - Requires O(interval) to be provided.
      - Mutually exclusive with O(args), O(ttl) and O(http).
    type: str
    version_added: '1.3.0'
  http:
    description:
      - Checks can be registered with an HTTP endpoint. This means that Consul checks that the HTTP endpoint returns a successful
        HTTP status.
      - Requires O(interval) to be provided.
      - Mutually exclusive with O(args), O(ttl) and O(tcp).
    type: str
  timeout:
    description:
      - A custom HTTP check timeout. The Consul default is 10 seconds. Similar to the interval this is a number with a V(s)
        or V(m) suffix to signify the units of seconds or minutes, for example V(15s) or V(1m). If no suffix is supplied V(s)
        is used by default, for example V(10) is equivalent to V(10s).
    type: str
  service_id:
    description:
      - The ID for the service, must be unique per node. If O(state=absent), defaults to the service name if supplied.
    type: str
"""

EXAMPLES = r"""
- name: Register tcp check for service 'nginx'
  community.general.consul_agent_check:
    name: nginx_tcp_check
    service_id: nginx
    interval: 60s
    tcp: localhost:80
    notes: "Nginx Check"

- name: Register http check for service 'nginx'
  community.general.consul_agent_check:
    name: nginx_http_check
    service_id: nginx
    interval: 60s
    http: http://localhost:80/status
    notes: "Nginx Check"

- name: Remove check for service 'nginx'
  community.general.consul_agent_check:
    state: absent
    id: nginx_http_check
    service_id: "{{ nginx_service.ID }}"
"""

RETURN = r"""
check:
  description: The check as returned by the Consul HTTP API.
  returned: always
  type: dict
  sample:
    CheckID: nginx_check
    ServiceID: nginx
    Interval: 30s
    Type: http
    Notes: Nginx Check
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
    OPERATION_READ,
    _ConsulModule,
    validate_check,
)

_ARGUMENT_SPEC = {
    "state": dict(default="present", choices=["present", "absent"]),
    "name": dict(type="str"),
    "id": dict(type="str"),
    "interval": dict(type="str"),
    "notes": dict(type="str"),
    "args": dict(type="list", elements="str"),
    "http": dict(type="str"),
    "tcp": dict(type="str"),
    "ttl": dict(type="str"),
    "timeout": dict(type="str"),
    "service_id": dict(type="str"),
}

_MUTUALLY_EXCLUSIVE = [
    ("args", "ttl", "tcp", "http"),
]

_REQUIRED_IF = [
    ("state", "present", ["name"]),
    ("state", "absent", ("id", "name"), True),
]

_REQUIRED_BY = {
    "args": "interval",
    "http": "interval",
    "tcp": "interval",
}

_ARGUMENT_SPEC.update(AUTH_ARGUMENTS_SPEC)


class ConsulAgentCheckModule(_ConsulModule):
    api_endpoint = "agent/check"
    result_key = "check"
    unique_identifiers = ["id", "name"]
    operational_attributes = {
        "Node",
        "CheckID",
        "Output",
        "ServiceName",
        "ServiceTags",
        "Status",
        "Type",
        "ExposedPort",
        "Definition",
    }

    def endpoint_url(self, operation, identifier=None):
        if operation == OPERATION_READ:
            return "agent/checks"
        if operation in [OPERATION_CREATE, OPERATION_UPDATE]:
            return f"{self.api_endpoint}/register"
        if operation == OPERATION_DELETE:
            return f"{self.api_endpoint}/deregister/{identifier}"

        return super().endpoint_url(operation, identifier)

    def read_object(self):
        url = self.endpoint_url(OPERATION_READ)
        checks = self.get(url)
        identifier = self.id_from_obj(self.params)
        if identifier in checks:
            return checks[identifier]
        return None

    def prepare_object(self, existing, obj):
        existing = super().prepare_object(existing, obj)
        validate_check(existing)
        return existing

    def delete_object(self, obj):
        if not self._module.check_mode:
            self.put(self.endpoint_url(OPERATION_DELETE, obj.get("CheckID")))
        return {}


def main():
    module = AnsibleModule(
        _ARGUMENT_SPEC,
        mutually_exclusive=_MUTUALLY_EXCLUSIVE,
        required_if=_REQUIRED_IF,
        required_by=_REQUIRED_BY,
        supports_check_mode=True,
    )

    consul_module = ConsulAgentCheckModule(module)
    consul_module.execute()


if __name__ == "__main__":
    main()

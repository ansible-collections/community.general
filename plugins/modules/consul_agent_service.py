#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Michael Ilg
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
module: consul_agent_service
short_description: Add, modify and delete services within a consul cluster
version_added: 8.4.0
description:
 - Allows the addition, modification and deletion of services in a consul
   cluster via the agent. For more details on using and configuring Checks,
   see U(https://developer.hashicorp.com/consul/api-docs/agent/service).
 - "Checks may also be registered per node e.g. disk usage, or cpu usage and
   notify the health of the entire node to the cluster.
   Service level checks do not require a check name or id as these are derived
   by Consul from the Service name and id respectively by appending 'service:'
   Node level checks require a O(checks[].name) and optionally a O(checks[].check_id)."
 - Currently, there is no complete way to retrieve the script, interval or TTL
   metadata for a registered check. Without this metadata it is not possible to
   tell if the data supplied with ansible represents a change to a check. As a
   result this does not attempt to determine changes and will always report a
   changed occurred. An API method is planned to supply this metadata so at that
   stage change management will be added.
author:
  - Florian Apolloner (@apollo13)
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
      - In check mode the diff will miss operational attributes.
options:
  state:
    description:
      - Whether the service should be present or absent.
    choices: ['present', 'absent']
    default: present
    type: str
  name:
    description:
      - Unique name for the service on a node, must be unique per node,
        required if registering a service. May be omitted if registering
        a node level check.
    type: str
  id:
    description:
      - The ID for the service, must be unique per node. If O(state=absent),
        defaults to the service name if supplied.
    type: str
  tags:
    description:
      - Tags that will be attached to the service registration.
    type: list
    elements: str
  address:
    description:
      - The address to advertise that the service will be listening on.
        This value will be passed as the C(address) parameter to Consul's
        C(/v1/agent/service/register) API method, so refer to the Consul API
        documentation for further details.
    type: str
  meta:
    description:
      - Optional meta data used for filtering.
        For key are the characters "A-Z, a-z, 0-9, _, -" allowed
             Not allowed characters are replaced with underscores
    type: dict
  service_port:
    description:
      - The port on which the service is listening. Can optionally be supplied for
        registration of a service, that is if O(name) or O(id) is set.
    type: int
  checks:
    description:
      - Checks to
    type: list
    elements: dict
    suboptions:
      name:
        description:
        - Required name for the service check.
        type: str
      check_id:
        description:
          - An unique ID for the service check.
        type: str
      interval:
        description:
          - The interval at which the service check will be run.
            This is a number with a V(s) or V(m) suffix to signify the units of seconds or minutes, for example V(15s) or V(1m).
            If no suffix is supplied V(s) will be used by default, for example V(10) will be V(10s).
          - Required if one of the parameters O(checks[].args), O(checks[].http), or O(checks[].tcp) is specified.
        type: str
      notes:
        description:
          - Notes to attach to check when registering it.
        type: str
      args:
        description:
          - Specifies command arguments to run to update the status of the check.
          - Requires O(checks[].interval) to be provided.
          - Mutually exclusive with O(checks[].ttl), O(checks[].tcp) and O(checks[].http).
          - "There is an issue with args. It throws an 'Invalid check: TTL must be > 0 for TTL checks'"
          - See U(https://github.com/hashicorp/consul/issues/6923#issuecomment-564476529) for more details
        type: list
        elements: str
      ttl:
        description:
          - Checks can be registered with a TTL instead of a O(checks[].args) and O(checks[].interval)
            this means that the service will check in with the agent before the
            TTL expires. If it doesn't the check will be considered failed.
            Required if registering a check and the script an interval are missing
            Similar to the interval this is a number with a V(s) or V(m) suffix to
            signify the units of seconds or minutes, for example V(15s) or V(1m).
            If no suffix is supplied V(s) will be used by default, for example V(10) will be V(10s).
          - Mutually exclusive with O(checks[].args), O(checks[].tcp) and O(checks[].http).
        type: str
      tcp:
        description:
          - Checks can be registered with a TCP port. This means that consul
            will check if the connection attempt to that port is successful (that is, the port is currently accepting connections).
            The format is V(host:port), for example V(localhost:80).
          - Requires O(checks[].interval) to be provided.
          - Mutually exclusive with O(checks[].args), O(checks[].ttl) and O(checks[].http).
        type: str
        version_added: '1.3.0'
      http:
        description:
          - Checks can be registered with an HTTP endpoint. This means that consul
            will check that the http endpoint returns a successful HTTP status.
          - Requires O(checks[].interval) to be provided.
          - Mutually exclusive with O(checks[].args), O(checks[].ttl) and O(checks[].tcp).
        type: str
      timeout:
        description:
          - A custom HTTP check timeout. The consul default is 10 seconds.
            Similar to the interval this is a number with a V(s) or V(m) suffix to
            signify the units of seconds or minutes, for example V(15s) or V(1m).
            If no suffix is supplied V(s) will be used by default, for example V(10) will be V(10s).
        type: str
'''

EXAMPLES = '''
- name: Register nginx service with the local consul agent
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
    checks:
      - name: nginx-check2
        interval: 60s
        tcp: localhost:80

- name: Register nginx with an http check
  community.general.consul_agent_service:
    host: consul1.example.com
    token: some_management_acl
    name: nginx
    service_port: 80
    checks:
      - name: nginx-check2
        interval: 60s
        http: http://localhost:80/status

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
'''

RETURN = """
service:
    description: The alert policy information
    returned: success
    type: dict
    sample:
        Address: localhost
        ContentHash: 61a245cd985261ac
        Datacenter: dc1
        EnableTagOverride: false
        ID: nginx
        Meta:
            - nginx_version: 1.23.3
        Port: 80
        Service: nginx
        Tags:
            - http
        Weights:
            Passing: 1
            Warning: 1
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
    camel_case_key,
    validate_check,
)

_CHECK_MUTUALLY_EXCLUSIVE = [('args', 'ttl', 'tcp', 'http')]
_CHECK_REQUIRED_BY = {
    'args': 'interval',
    'http': 'interval',
    'tcp': 'interval',
}

_ARGUMENT_SPEC = {
    "state": dict(default="present", choices=["present", "absent"]),
    "name": dict(type='str'),
    "id": dict(type='str'),
    "tags": dict(type='list', elements='str'),
    "address": dict(type='str'),
    "meta": dict(type='dict'),
    "service_port": dict(type='int'),
    "checks": dict(
        type='list',
        elements='dict',
        options=dict(
            name=dict(type='str'),
            check_id=dict(type='str'),
            interval=dict(type='str'),
            notes=dict(type='str'),
            args=dict(type='list', elements='str'),
            http=dict(type='str'),
            tcp=dict(type='str'),
            ttl=dict(type='str'),
            timeout=dict(type='str'),
        ),
        mutually_exclusive=_CHECK_MUTUALLY_EXCLUSIVE,
        required_by=_CHECK_REQUIRED_BY
    ),
}

_REQUIRED_IF = [
    ('state', 'present', ['name']),
    ('state', 'absent', ('id', 'name'), True),
]

_ARGUMENT_SPEC.update(AUTH_ARGUMENTS_SPEC)


class ConsulAgentServiceModule(_ConsulModule):
    api_endpoint = "agent/service"
    result_key = "service"
    unique_identifiers = ["id", "name"]

    def endpoint_url(self, operation, identifier=None):

        if operation in [OPERATION_CREATE, OPERATION_UPDATE]:
            return "/".join([self.api_endpoint, "register"])
        if operation == OPERATION_DELETE:
            if identifier is None and self.params["name"] is not None:
                return [self.api_endpoint, "deregister", self.params["name"]]
            return "/".join([self.api_endpoint, "deregister", identifier])

        return super(ConsulAgentServiceModule, self).endpoint_url(operation, identifier)

    def prepare_object(self, existing, obj):
        existing = super(ConsulAgentServiceModule, self).prepare_object(existing, obj)

        operational_attributes = {"Service", "ContentHash", "Datacenter"}
        existing = {
            k: v for k, v in existing.items() if k not in operational_attributes
        }

        if existing['ServicePort']:
            existing['Port'] = existing['ServicePort']
            del existing['ServicePort']

        if existing['Checks']:
            for check in existing['Checks']:
                validate_check(check)

        return existing

    def delete_object(self, obj):
        if not self._module.check_mode:
            url = self.endpoint_url(
                OPERATION_DELETE, obj.get("ID")
            )
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

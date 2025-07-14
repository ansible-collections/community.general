#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2015, Steve Gargan <steve.gargan@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: consul
short_description: Add, modify & delete services within a Consul cluster
description:
  - Registers services and checks for an agent with a Consul cluster. A service is some process running on the agent node
    that should be advertised by Consul's discovery mechanism. It may optionally supply a check definition, a periodic service
    test to notify the Consul cluster of service's health.
  - Checks may also be registered per node, for example disk usage, or cpu usage and notify the health of the entire node
    to the cluster. Service level checks do not require a check name or ID as these are derived by Consul from the Service
    name and ID respectively by appending V(service:) Node level checks require a O(check_name) and optionally a O(check_id).
  - Currently, there is no complete way to retrieve the script, interval or TTL metadata for a registered check. Without this
    metadata it is not possible to tell if the data supplied with ansible represents a change to a check. As a result this
    does not attempt to determine changes and it always reports a changed occurred. An API method is planned to supply this
    metadata so at that stage change management is to be added.
  - See U(http://consul.io) for more details.
requirements:
  - python-consul
  - requests
author: "Steve Gargan (@sgargan)"
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  state:
    type: str
    description:
      - Register or deregister the Consul service, defaults to present.
    default: present
    choices: ['present', 'absent']
  service_name:
    type: str
    description:
      - Unique name for the service on a node, must be unique per node, required if registering a service. May be omitted
        if registering a node level check.
  service_id:
    type: str
    description:
      - The ID for the service, must be unique per node. If O(state=absent), defaults to the service name if supplied.
  host:
    type: str
    description:
      - Host of the Consul agent defaults to localhost.
    default: localhost
  port:
    type: int
    description:
      - The port on which the Consul agent is running.
    default: 8500
  scheme:
    type: str
    description:
      - The protocol scheme on which the Consul agent is running.
    default: http
  validate_certs:
    description:
      - Whether to verify the TLS certificate of the Consul agent.
    type: bool
    default: true
  notes:
    type: str
    description:
      - Notes to attach to check when registering it.
  service_port:
    type: int
    description:
      - The port on which the service is listening. Can optionally be supplied for registration of a service, that is if O(service_name)
        or O(service_id) is set.
  service_address:
    type: str
    description:
      - The address to advertise that the service is listening on. This value is passed as the C(address) parameter to Consul's
        C(/v1/agent/service/register) API method, so refer to the Consul API documentation for further details.
  tags:
    type: list
    elements: str
    description:
      - Tags that are attached to the service registration.
  script:
    type: str
    description:
      - The script/command that is run periodically to check the health of the service.
      - Requires O(interval) to be provided.
      - Mutually exclusive with O(ttl), O(tcp) and O(http).
  interval:
    type: str
    description:
      - The interval at which the service check is run. This is a number with a V(s) or V(m) suffix to signify the units of
        seconds or minutes, for example V(15s) or V(1m). If no suffix is supplied V(s) is used by default, for example V(10)
        is V(10s).
      - Required if one of the parameters O(script), O(http), or O(tcp) is specified.
  check_id:
    type: str
    description:
      - An ID for the service check. If O(state=absent), defaults to O(check_name). Ignored if part of a service definition.
  check_name:
    type: str
    description:
      - Name for the service check. Required if standalone, ignored if part of service definition.
  check_node:
    description:
      - Node name.
    type: str
  check_host:
    description:
      - Host name.
    type: str
  ttl:
    type: str
    description:
      - Checks can be registered with a TTL instead of a O(script) and O(interval) this means that the service checks in with
        the agent before the TTL expires. If it does not the check is considered failed. Required if registering a check and
        the script an interval are missing Similar to the interval this is a number with a V(s) or V(m) suffix to signify
        the units of seconds or minutes, for example V(15s) or V(1m). If no suffix is supplied V(s) is used by default, for
        example V(10) is equivalent to V(10s).
      - Mutually exclusive with O(script), O(tcp) and O(http).
  tcp:
    type: str
    description:
      - Checks can be registered with a TCP port. This means that Consul checks if the connection attempt to that port is
        successful (that is, the port is currently accepting connections). The format is V(host:port), for example V(localhost:80).
      - Requires O(interval) to be provided.
      - Mutually exclusive with O(script), O(ttl) and O(http).
    version_added: '1.3.0'
  http:
    type: str
    description:
      - Checks can be registered with an HTTP endpoint. This means that Consul checks that the http endpoint returns a successful
        HTTP status.
      - Requires O(interval) to be provided.
      - Mutually exclusive with O(script), O(ttl) and O(tcp).
  timeout:
    type: str
    description:
      - A custom HTTP check timeout. The Consul default is 10 seconds. Similar to the interval this is a number with a V(s)
        or V(m) suffix to signify the units of seconds or minutes, for example V(15s) or V(1m). If no suffix is supplied V(s)
        is used by default, for example V(10) is equivalent to V(10s).
  token:
    type: str
    description:
      - The token key identifying an ACL rule set. May be required to register services.
"""

EXAMPLES = r"""
- name: Register nginx service with the local Consul agent
  community.general.consul:
    service_name: nginx
    service_port: 80

- name: Register nginx service with curl check
  community.general.consul:
    service_name: nginx
    service_port: 80
    script: curl http://localhost
    interval: 60s

- name: register nginx with a tcp check
  community.general.consul:
    service_name: nginx
    service_port: 80
    interval: 60s
    tcp: localhost:80

- name: Register nginx with an http check
  community.general.consul:
    service_name: nginx
    service_port: 80
    interval: 60s
    http: http://localhost:80/status

- name: Register external service nginx available at 10.1.5.23
  community.general.consul:
    service_name: nginx
    service_port: 80
    service_address: 10.1.5.23

- name: Register nginx with some service tags
  community.general.consul:
    service_name: nginx
    service_port: 80
    tags:
      - prod
      - webservers

- name: Remove nginx service
  community.general.consul:
    service_name: nginx
    state: absent

- name: Register celery worker service
  community.general.consul:
    service_name: celery-worker
    tags:
      - prod
      - worker

- name: Create a node level check to test disk usage
  community.general.consul:
    check_name: Disk usage
    check_id: disk_usage
    script: /opt/disk_usage.py
    interval: 5m

- name: Register an http check against a service that's already registered
  community.general.consul:
    check_name: nginx-check2
    check_id: nginx-check2
    service_id: nginx
    interval: 60s
    http: http://localhost:80/morestatus
"""

try:
    import consul
    from requests.exceptions import ConnectionError

    class PatchedConsulAgentService(consul.Consul.Agent.Service):
        def deregister(self, service_id, token=None):
            params = {}
            if token:
                params['token'] = token
            return self.agent.http.put(consul.base.CB.bool(),
                                       '/v1/agent/service/deregister/%s' % service_id,
                                       params=params)

    python_consul_installed = True
except ImportError:
    python_consul_installed = False

import re
from ansible.module_utils.basic import AnsibleModule


def register_with_consul(module):
    state = module.params['state']

    if state == 'present':
        add(module)
    else:
        remove(module)


def add(module):
    ''' adds a service or a check depending on supplied configuration'''
    check = parse_check(module)
    service = parse_service(module)

    if not service and not check:
        module.fail_json(msg='a name and port are required to register a service')

    if service:
        if check:
            service.add_check(check)
        add_service(module, service)
    elif check:
        add_check(module, check)


def remove(module):
    ''' removes a service or a check '''
    service_id = module.params['service_id'] or module.params['service_name']
    check_id = module.params['check_id'] or module.params['check_name']
    if service_id:
        remove_service(module, service_id)
    else:
        remove_check(module, check_id)


def add_check(module, check):
    ''' registers a check with the given agent. currently there is no way
    retrieve the full metadata of an existing check  through the consul api.
    Without this we can't compare to the supplied check and so we must assume
    a change. '''
    if not check.name and not check.service_id:
        module.fail_json(msg='a check name is required for a node level check, one not attached to a service')

    consul_api = get_consul_api(module)
    check.register(consul_api)

    module.exit_json(changed=True,
                     check_id=check.check_id,
                     check_name=check.name,
                     script=check.script,
                     interval=check.interval,
                     ttl=check.ttl,
                     tcp=check.tcp,
                     http=check.http,
                     timeout=check.timeout,
                     service_id=check.service_id)


def remove_check(module, check_id):
    ''' removes a check using its id '''
    consul_api = get_consul_api(module)

    if check_id in consul_api.agent.checks():
        consul_api.agent.check.deregister(check_id)
        module.exit_json(changed=True, id=check_id)

    module.exit_json(changed=False, id=check_id)


def add_service(module, service):
    ''' registers a service with the current agent '''
    result = service
    changed = False

    consul_api = get_consul_api(module)
    existing = get_service_by_id_or_name(consul_api, service.id)

    # there is no way to retrieve the details of checks so if a check is present
    # in the service it must be re-registered
    if service.has_checks() or not existing or not existing == service:

        service.register(consul_api)
        # check that it registered correctly
        registered = get_service_by_id_or_name(consul_api, service.id)
        if registered:
            result = registered
            changed = True

    module.exit_json(changed=changed,
                     service_id=result.id,
                     service_name=result.name,
                     service_port=result.port,
                     checks=[check.to_dict() for check in service.checks()],
                     tags=result.tags)


def remove_service(module, service_id):
    ''' deregister a service from the given agent using its service id '''
    consul_api = get_consul_api(module)
    service = get_service_by_id_or_name(consul_api, service_id)
    if service:
        consul_api.agent.service.deregister(service_id, token=module.params['token'])
        module.exit_json(changed=True, id=service_id)

    module.exit_json(changed=False, id=service_id)


def get_consul_api(module):
    consulClient = consul.Consul(host=module.params['host'],
                                 port=module.params['port'],
                                 scheme=module.params['scheme'],
                                 verify=module.params['validate_certs'],
                                 token=module.params['token'])
    consulClient.agent.service = PatchedConsulAgentService(consulClient)
    return consulClient


def get_service_by_id_or_name(consul_api, service_id_or_name):
    ''' iterate the registered services and find one with the given id '''
    for dummy, service in consul_api.agent.services().items():
        if service_id_or_name in (service['ID'], service['Service']):
            return ConsulService(loaded=service)


def parse_check(module):
    if module.params['check_id'] or any(module.params[p] is not None for p in ('script', 'ttl', 'tcp', 'http')):
        return ConsulCheck(
            module.params['check_id'],
            module.params['check_name'],
            module.params['check_node'],
            module.params['check_host'],
            module.params['script'],
            module.params['interval'],
            module.params['ttl'],
            module.params['notes'],
            module.params['tcp'],
            module.params['http'],
            module.params['timeout'],
            module.params['service_id'],
        )


def parse_service(module):
    return ConsulService(
        module.params['service_id'],
        module.params['service_name'],
        module.params['service_address'],
        module.params['service_port'],
        module.params['tags'],
    )


class ConsulService(object):

    def __init__(self, service_id=None, name=None, address=None, port=-1,
                 tags=None, loaded=None):
        self.id = self.name = name
        if service_id:
            self.id = service_id
        self.address = address
        self.port = port
        self.tags = tags
        self._checks = []
        if loaded:
            self.id = loaded['ID']
            self.name = loaded['Service']
            self.port = loaded['Port']
            self.tags = loaded['Tags']

    def register(self, consul_api):
        optional = {}

        if self.port:
            optional['port'] = self.port

        if len(self._checks) > 0:
            optional['check'] = self._checks[0].check

        consul_api.agent.service.register(
            self.name,
            service_id=self.id,
            address=self.address,
            tags=self.tags,
            **optional)

    def add_check(self, check):
        self._checks.append(check)

    def checks(self):
        return self._checks

    def has_checks(self):
        return len(self._checks) > 0

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.id == other.id and
                self.name == other.name and
                self.port == other.port and
                self.tags == other.tags)

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self):
        data = {'id': self.id, "name": self.name}
        if self.port:
            data['port'] = self.port
        if self.tags and len(self.tags) > 0:
            data['tags'] = self.tags
        if len(self._checks) > 0:
            data['check'] = self._checks[0].to_dict()
        return data


class ConsulCheck(object):

    def __init__(self, check_id, name, node=None, host='localhost',
                 script=None, interval=None, ttl=None, notes=None, tcp=None, http=None, timeout=None, service_id=None):
        self.check_id = self.name = name
        if check_id:
            self.check_id = check_id
        self.service_id = service_id
        self.notes = notes
        self.node = node
        self.host = host

        self.interval = self.validate_duration('interval', interval)
        self.ttl = self.validate_duration('ttl', ttl)
        self.script = script
        self.tcp = tcp
        self.http = http
        self.timeout = self.validate_duration('timeout', timeout)

        self.check = None

        if script:
            self.check = consul.Check.script(script, self.interval)

        if ttl:
            self.check = consul.Check.ttl(self.ttl)

        if http:
            self.check = consul.Check.http(http, self.interval, self.timeout)

        if tcp:
            regex = r"(?P<host>.*):(?P<port>(?:[0-9]+))$"
            match = re.match(regex, tcp)

            if not match:
                raise Exception('tcp check must be in host:port format')

            self.check = consul.Check.tcp(match.group('host').strip('[]'), int(match.group('port')), self.interval)

    def validate_duration(self, name, duration):
        if duration:
            duration_units = ['ns', 'us', 'ms', 's', 'm', 'h']
            if not any(duration.endswith(suffix) for suffix in duration_units):
                duration = "{0}s".format(duration)
        return duration

    def register(self, consul_api):
        consul_api.agent.check.register(self.name, check_id=self.check_id, service_id=self.service_id,
                                        notes=self.notes,
                                        check=self.check)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.check_id == other.check_id and
                self.service_id == other.service_id and
                self.name == other.name and
                self.script == other.script and
                self.interval == other.interval)

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self):
        data = {}
        self._add(data, 'id', attr='check_id')
        self._add(data, 'name', attr='check_name')
        self._add(data, 'script')
        self._add(data, 'node')
        self._add(data, 'notes')
        self._add(data, 'host')
        self._add(data, 'interval')
        self._add(data, 'ttl')
        self._add(data, 'tcp')
        self._add(data, 'http')
        self._add(data, 'timeout')
        self._add(data, 'service_id')
        return data

    def _add(self, data, key, attr=None):
        try:
            if attr is None:
                attr = key
            data[key] = getattr(self, attr)
        except Exception:
            pass


def test_dependencies(module):
    if not python_consul_installed:
        module.fail_json(msg="python-consul required for this module. see https://python-consul.readthedocs.io/en/latest/#installation")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(default='localhost'),
            port=dict(default=8500, type='int'),
            scheme=dict(default='http'),
            validate_certs=dict(default=True, type='bool'),
            check_id=dict(),
            check_name=dict(),
            check_node=dict(),
            check_host=dict(),
            notes=dict(),
            script=dict(),
            service_id=dict(),
            service_name=dict(),
            service_address=dict(type='str'),
            service_port=dict(type='int'),
            state=dict(default='present', choices=['present', 'absent']),
            interval=dict(type='str'),
            ttl=dict(type='str'),
            tcp=dict(type='str'),
            http=dict(type='str'),
            timeout=dict(type='str'),
            tags=dict(type='list', elements='str'),
            token=dict(no_log=True),
        ),
        mutually_exclusive=[
            ('script', 'ttl', 'tcp', 'http'),
        ],
        required_if=[
            ('state', 'present', ['service_name']),
            ('state', 'absent', ['service_id', 'service_name', 'check_id', 'check_name'], True),
        ],
        required_by={
            'script': 'interval',
            'http': 'interval',
            'tcp': 'interval',
        },
        supports_check_mode=False,
    )
    p = module.params

    test_dependencies(module)
    if p['state'] == 'absent' and any(p[x] for x in ['script', 'ttl', 'tcp', 'http', 'interval']):
        module.fail_json(
            msg="The use of parameters 'script', 'ttl', 'tcp', 'http', 'interval' along with 'state=absent' is no longer allowed."
        )

    try:
        register_with_consul(module)
    except SystemExit:
        raise
    except ConnectionError as e:
        module.fail_json(msg='Could not connect to consul agent at %s:%s, error was %s' % (p['host'], p['port'], str(e)))
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: ovh_ip_loadbalancing_backend
short_description: Manage OVH IP LoadBalancing backends
description:
  - Manage OVH (French European hosting provider) LoadBalancing IP backends.
author: Pascal Heraud (@pascalheraud)
notes:
  - Uses the Python OVH API U(https://github.com/ovh/python-ovh). You have to create an application (a key and secret) with
    a consumer key as described into U(https://docs.ovh.com/gb/en/customer/first-steps-with-ovh-api/).
requirements:
  - ovh > 0.3.5
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  name:
    required: true
    description:
      - Name of the LoadBalancing internal name (V(ip-X.X.X.X)).
    type: str
  backend:
    required: true
    description:
      - The IP address of the backend to update / modify / delete.
    type: str
  state:
    default: present
    choices: ['present', 'absent']
    description:
      - Determines whether the backend is to be created/modified or deleted.
    type: str
  probe:
    default: 'none'
    choices: ['none', 'http', 'icmp', 'oco']
    description:
      - Determines the type of probe to use for this backend.
    type: str
  weight:
    default: 8
    description:
      - Determines the weight for this backend.
    type: int
  endpoint:
    required: true
    description:
      - The endpoint to use (for instance V(ovh-eu)).
    type: str
  application_key:
    required: true
    description:
      - The applicationKey to use.
    type: str
  application_secret:
    required: true
    description:
      - The application secret to use.
    type: str
  consumer_key:
    required: true
    description:
      - The consumer key to use.
    type: str
  timeout:
    default: 120
    description:
      - The timeout in seconds used to wait for a task to be completed.
    type: int
"""

EXAMPLES = r"""
- name: Adds or modify the backend '212.1.1.1' to a loadbalancing 'ip-1.1.1.1'
  ovh_ip_loadbalancing:
    name: ip-1.1.1.1
    backend: 212.1.1.1
    state: present
    probe: none
    weight: 8
    endpoint: ovh-eu
    application_key: yourkey
    application_secret: yoursecret
    consumer_key: yourconsumerkey

- name: Removes a backend '212.1.1.1' from a loadbalancing 'ip-1.1.1.1'
  ovh_ip_loadbalancing:
    name: ip-1.1.1.1
    backend: 212.1.1.1
    state: absent
    endpoint: ovh-eu
    application_key: yourkey
    application_secret: yoursecret
    consumer_key: yourconsumerkey
"""

RETURN = r"""
"""

import time

try:
    import ovh
    import ovh.exceptions
    from ovh.exceptions import APIError
    HAS_OVH = True
except ImportError:
    HAS_OVH = False

from ansible.module_utils.basic import AnsibleModule


def getOvhClient(ansibleModule):
    endpoint = ansibleModule.params.get('endpoint')
    application_key = ansibleModule.params.get('application_key')
    application_secret = ansibleModule.params.get('application_secret')
    consumer_key = ansibleModule.params.get('consumer_key')

    return ovh.Client(
        endpoint=endpoint,
        application_key=application_key,
        application_secret=application_secret,
        consumer_key=consumer_key
    )


def waitForNoTask(client, name, timeout):
    currentTimeout = timeout
    while len(client.get('/ip/loadBalancing/{0}/task'.format(name))) > 0:
        time.sleep(1)  # Delay for 1 sec
        currentTimeout -= 1
        if currentTimeout < 0:
            return False
    return True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            backend=dict(required=True),
            weight=dict(default=8, type='int'),
            probe=dict(default='none',
                       choices=['none', 'http', 'icmp', 'oco']),
            state=dict(default='present', choices=['present', 'absent']),
            endpoint=dict(required=True),
            application_key=dict(required=True, no_log=True),
            application_secret=dict(required=True, no_log=True),
            consumer_key=dict(required=True, no_log=True),
            timeout=dict(default=120, type='int')
        )
    )

    if not HAS_OVH:
        module.fail_json(msg='ovh-api python module'
                         'is required to run this module ')

    # Get parameters
    name = module.params.get('name')
    state = module.params.get('state')
    backend = module.params.get('backend')
    weight = module.params.get('weight')
    probe = module.params.get('probe')
    timeout = module.params.get('timeout')

    # Connect to OVH API
    client = getOvhClient(module)

    # Check that the load balancing exists
    try:
        loadBalancings = client.get('/ip/loadBalancing')
    except APIError as apiError:
        module.fail_json(
            msg='Unable to call OVH api for getting the list of loadBalancing, '
                'check application key, secret, consumerkey and parameters. '
                'Error returned by OVH api was : {0}'.format(apiError))

    if name not in loadBalancings:
        module.fail_json(msg='IP LoadBalancing {0} does not exist'.format(name))

    # Check that no task is pending before going on
    try:
        if not waitForNoTask(client, name, timeout):
            module.fail_json(
                msg='Timeout of {0} seconds while waiting for no pending '
                    'tasks before executing the module '.format(timeout))
    except APIError as apiError:
        module.fail_json(
            msg='Unable to call OVH api for getting the list of pending tasks '
                'of the loadBalancing, check application key, secret, consumerkey '
                'and parameters. Error returned by OVH api was : {0}'
                .format(apiError))

    try:
        backends = client.get('/ip/loadBalancing/{0}/backend'.format(name))
    except APIError as apiError:
        module.fail_json(
            msg='Unable to call OVH api for getting the list of backends '
                'of the loadBalancing, check application key, secret, consumerkey '
                'and parameters. Error returned by OVH api was : {0}'
            .format(apiError))

    backendExists = backend in backends
    moduleChanged = False
    if state == "absent":
        if backendExists:
            # Remove backend
            try:
                client.delete(
                    '/ip/loadBalancing/{0}/backend/{1}'.format(name, backend))
                if not waitForNoTask(client, name, timeout):
                    module.fail_json(
                        msg='Timeout of {0} seconds while waiting for completion '
                            'of removing backend task'.format(timeout))
            except APIError as apiError:
                module.fail_json(
                    msg='Unable to call OVH api for deleting the backend, '
                        'check application key, secret, consumerkey and '
                        'parameters. Error returned by OVH api was : {0}'
                        .format(apiError))
            moduleChanged = True
    else:
        if backendExists:
            # Get properties
            try:
                backendProperties = client.get(
                    '/ip/loadBalancing/{0}/backend/{1}'.format(name, backend))
            except APIError as apiError:
                module.fail_json(
                    msg='Unable to call OVH api for getting the backend properties, '
                        'check application key, secret, consumerkey and '
                        'parameters. Error returned by OVH api was : {0}'
                        .format(apiError))

            if (backendProperties['weight'] != weight):
                # Change weight
                try:
                    client.post(
                        '/ip/loadBalancing/{0}/backend/{1}/setWeight'
                        .format(name, backend), weight=weight)
                    if not waitForNoTask(client, name, timeout):
                        module.fail_json(
                            msg='Timeout of {0} seconds while waiting for completion '
                                'of setWeight to backend task'
                                .format(timeout))
                except APIError as apiError:
                    module.fail_json(
                        msg='Unable to call OVH api for updating the weight of the '
                            'backend, check application key, secret, consumerkey '
                            'and parameters. Error returned by OVH api was : {0}'
                            .format(apiError))
                moduleChanged = True

            if (backendProperties['probe'] != probe):
                # Change probe
                backendProperties['probe'] = probe
                try:
                    client.put(
                        '/ip/loadBalancing/{0}/backend/{1}'
                        .format(name, backend), probe=probe)
                    if not waitForNoTask(client, name, timeout):
                        module.fail_json(
                            msg='Timeout of {0} seconds while waiting for completion of '
                                'setProbe to backend task'
                                .format(timeout))
                except APIError as apiError:
                    module.fail_json(
                        msg='Unable to call OVH api for updating the probe of '
                            'the backend, check application key, secret, '
                            'consumerkey and parameters. Error returned by OVH api '
                            'was : {0}'
                            .format(apiError))
                moduleChanged = True

        else:
            # Creates backend
            try:
                try:
                    client.post('/ip/loadBalancing/{0}/backend'.format(name),
                                ipBackend=backend, probe=probe, weight=weight)
                except APIError as apiError:
                    module.fail_json(
                        msg='Unable to call OVH api for creating the backend, check '
                            'application key, secret, consumerkey and parameters. '
                            'Error returned by OVH api was : {0}'
                            .format(apiError))

                if not waitForNoTask(client, name, timeout):
                    module.fail_json(
                        msg='Timeout of {0} seconds while waiting for completion of '
                            'backend creation task'.format(timeout))
            except APIError as apiError:
                module.fail_json(
                    msg='Unable to call OVH api for creating the backend, check '
                        'application key, secret, consumerkey and parameters. '
                        'Error returned by OVH api was : {0}'.format(apiError))
            moduleChanged = True

    module.exit_json(changed=moduleChanged)


if __name__ == '__main__':
    main()

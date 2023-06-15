#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018, Jean-Philippe Evrard <jean-philippe@evrard.me>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: etcd3
short_description: Set or delete key value pairs from an etcd3 cluster
requirements:
  - etcd3
description:
  - Sets or deletes values in etcd3 cluster using its v3 api.
  - Needs python etcd3 lib to work
extends_documentation_fragment:
  - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    key:
        type: str
        description:
            - the key where the information is stored in the cluster
        required: true
    value:
        type: str
        description:
            - the information stored
        required: true
    host:
        type: str
        description:
            - the IP address of the cluster
        default: 'localhost'
    port:
        type: int
        description:
            - the port number used to connect to the cluster
        default: 2379
    state:
        type: str
        description:
            - the state of the value for the key.
            - can be present or absent
        required: true
        choices: [ present, absent ]
    user:
        type: str
        description:
            - The etcd user to authenticate with.
    password:
        type: str
        description:
            - The password to use for authentication.
            - Required if O(user) is defined.
    ca_cert:
        type: path
        description:
            - The Certificate Authority to use to verify the etcd host.
            - Required if O(client_cert) and O(client_key) are defined.
    client_cert:
        type: path
        description:
            - PEM formatted certificate chain file to be used for SSL client authentication.
            - Required if O(client_key) is defined.
    client_key:
        type: path
        description:
            - PEM formatted file that contains your private key to be used for SSL client authentication.
            - Required if O(client_cert) is defined.
    timeout:
        type: int
        description:
            - The socket level timeout in seconds.
author:
    - Jean-Philippe Evrard (@evrardjp)
    - Victor Fauth (@vfauth)
'''

EXAMPLES = """
- name: Store a value "bar" under the key "foo" for a cluster located "http://localhost:2379"
  community.general.etcd3:
    key: "foo"
    value: "baz3"
    host: "localhost"
    port: 2379
    state: "present"

- name: Authenticate using user/password combination with a timeout of 10 seconds
  community.general.etcd3:
    key: "foo"
    value: "baz3"
    state: "present"
    user: "someone"
    password: "password123"
    timeout: 10

- name: Authenticate using TLS certificates
  community.general.etcd3:
    key: "foo"
    value: "baz3"
    state: "present"
    ca_cert: "/etc/ssl/certs/CA_CERT.pem"
    client_cert: "/etc/ssl/certs/cert.crt"
    client_key: "/etc/ssl/private/key.pem"
"""

RETURN = '''
key:
    description: The key that was queried
    returned: always
    type: str
old_value:
    description: The previous value in the cluster
    returned: always
    type: str
'''

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


try:
    import etcd3
    HAS_ETCD = True
    ETCD_IMP_ERR = None
except ImportError:
    ETCD_IMP_ERR = traceback.format_exc()
    HAS_ETCD = False


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        key=dict(type='str', required=True, no_log=False),
        value=dict(type='str', required=True),
        host=dict(type='str', default='localhost'),
        port=dict(type='int', default=2379),
        state=dict(type='str', required=True, choices=['present', 'absent']),
        user=dict(type='str'),
        password=dict(type='str', no_log=True),
        ca_cert=dict(type='path'),
        client_cert=dict(type='path'),
        client_key=dict(type='path'),
        timeout=dict(type='int'),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_together=[['client_cert', 'client_key'], ['user', 'password']],
    )

    # It is possible to set `ca_cert` to verify the server identity without
    # setting `client_cert` or `client_key` to authenticate the client
    # so required_together is enough
    # Due to `required_together=[['client_cert', 'client_key']]`, checking the presence
    # of either `client_cert` or `client_key` is enough
    if module.params['ca_cert'] is None and module.params['client_cert'] is not None:
        module.fail_json(msg="The 'ca_cert' parameter must be defined when 'client_cert' and 'client_key' are present.")

    result['key'] = module.params.get('key')
    module.params['cert_cert'] = module.params.pop('client_cert')
    module.params['cert_key'] = module.params.pop('client_key')

    if not HAS_ETCD:
        module.fail_json(msg=missing_required_lib('etcd3'), exception=ETCD_IMP_ERR)

    allowed_keys = ['host', 'port', 'ca_cert', 'cert_cert', 'cert_key',
                    'timeout', 'user', 'password']
    # TODO(evrardjp): Move this back to a dict comprehension when python 2.7 is
    # the minimum supported version
    # client_params = {key: value for key, value in module.params.items() if key in allowed_keys}
    client_params = dict()
    for key, value in module.params.items():
        if key in allowed_keys:
            client_params[key] = value
    try:
        etcd = etcd3.client(**client_params)
    except Exception as exp:
        module.fail_json(msg='Cannot connect to etcd cluster: %s' % (to_native(exp)),
                         exception=traceback.format_exc())
    try:
        cluster_value = etcd.get(module.params['key'])
    except Exception as exp:
        module.fail_json(msg='Cannot reach data: %s' % (to_native(exp)),
                         exception=traceback.format_exc())

    # Make the cluster_value[0] a string for string comparisons
    result['old_value'] = to_native(cluster_value[0])

    if module.params['state'] == 'absent':
        if cluster_value[0] is not None:
            if module.check_mode:
                result['changed'] = True
            else:
                try:
                    etcd.delete(module.params['key'])
                except Exception as exp:
                    module.fail_json(msg='Cannot delete %s: %s' % (module.params['key'], to_native(exp)),
                                     exception=traceback.format_exc())
                else:
                    result['changed'] = True
    elif module.params['state'] == 'present':
        if result['old_value'] != module.params['value']:
            if module.check_mode:
                result['changed'] = True
            else:
                try:
                    etcd.put(module.params['key'], module.params['value'])
                except Exception as exp:
                    module.fail_json(msg='Cannot add or edit key %s: %s' % (module.params['key'], to_native(exp)),
                                     exception=traceback.format_exc())
                else:
                    result['changed'] = True
    else:
        module.fail_json(msg="State not recognized")

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

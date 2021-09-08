#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: redis_set
short_description: Set key value pairs in Redis
description:
   - Set key value pairs in Redis database.
author: "Andreas Botzner (@paginabianca)"
options:
    key:
        description:
            - Database key.
        required: True
        type: str
    value:
        description:
            - Value that key should be set to.
        required: False
        type: str
    expiration:
        description:
            - Expiration time in milliseconds.
        required: False
        type: int
    non_existing:
        description:
            - Only set key if it does not already exist.
        required: False
        type: bool
    existing:
        description:
            - Only set key if it already exists.
        required: False
        type: bool
    keep_ttl:
        description:
            - Retain the time to live associated with the key.
        required: False
        type: bool
    state:
        description:
            - State of the key.
        default: present
        type: str
        choices:
            - present
            - absent

extends_documentation_fragment:
  - community.general.redis.documentation

seealso:
    - module: community.general.redis_data_info
    - module: community.general.redis_incr
    - module: community.general.redis
'''

EXAMPLES = '''
- name: Set key foo=bar on loalhost with no username
  community.general.redis_set:
    login_host: localhost
    login_password: supersecret
    key: foo
    value: bar
    state: present

- name: Set key foo=bar if non existing with expiration of 30s
  community.general.redis_set:
    login_host: localhost
    login_password: supersecret
    key: foo
    value: bar
    non_existing: true
    expiration: 30000
    state: present

- name: Set key foo=bar if existing and keep current TTL
  community.general.redis_set:
    login_host: localhost
    login_pasword: supersecret
    key: foo
    value: bar
    existing: yes
    keep_ttl: yes

- name: Set key foo=bar on redishost with custom ca-cert file
  community.general.redis:
    login_host: redishost
    login_password: supersecret
    login_user: somuser
    validate_certs: yes
    ssl_ca_certs: /path/to/ca/certs
    key: foo
    value: bar

- name: Delete key foo=bar on loalhost with no username
  community.general.redis_set:
    login_host: localhost
    login_password: supersecret
    key: foo
    state: absent
'''

RETURN = '''
old_value:
  description: Value of key before setting.
  returned: always
  type: str
  sample: 'old_value_of_key'
value:
  description: Value key was set to
  returned: on success
  type: str
  sample: 'new_value_of_key'
msg:
  description: A short message.
  returned: always
  type: str
  sample: ''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.redis import (
    fail_imports, redis_auth_argument_spec, RedisAnsible)


def main():
    redis_auth_args = redis_auth_argument_spec()
    module_args = dict(
        key=dict(type='str', required=True, no_log=False),
        value=dict(type='str', required=False),
        expiration=dict(type='int', required=False),
        non_existing=dict(type='bool', required=False),
        existing=dict(type='bool', required=False),
        keep_ttl=dict(type='bool', required=False),
        state=dict(type='str', default='present',
                   choices=['present', 'absent']),
    )
    module_args.update(redis_auth_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        required_if=[('state', 'present', ('value',))],
        mutually_exclusive=[['non_existing', 'existing'],
                            ['keep_ttl', 'expiration']],)
    import_errors = fail_imports()
    if len(import_errors) != 0:
        module.fail_json(msg=import_errors)

    redis = RedisAnsible(module)

    key = module.params['key']
    value = module.params['value']
    px = module.params['expiration']
    nx = module.params['non_existing']
    xx = module.params['existing']
    keepttl = module.params['keep_ttl']
    state = module.params['state']
    set_args = {'name': key, 'value': value, 'px': px,
                'nx': nx, 'xx': xx, 'keepttl': keepttl}

    result = {'changed': False}

    if state == 'absent':
        try:
            ret = redis.connection.delete(key)
            if ret == 0:
                msg = 'Key: {0} not present'.format(key)
                result['msg'] = msg
                module.exit_json(**result)
            else:
                msg = 'Deleted key: {0}'.format(key)
                result['msg'] = msg
                result['changed'] = True
                module.exit_json(**result)
        except Exception as e:
            msg = 'Failed to delete key: {0} with exception: {1}'.format(
                key, str(e))
            result['msg'] = msg
            module.fail_json(**result)

    old_value = None
    try:
        old_value = redis.connection.get(key)
    except Exception as e:
        msg = 'Failed to get value of key: {0} with exception: {1}'.format(
            key, str(e))
        result['msg'] = msg
        module.fail_json(**result)

    result['old_value'] = old_value
    result['value'] = value
    if old_value == value:
        msg = 'Key: {0} had value: {1} now has value {2}'.format(
            key, old_value, value)
        result['msg'] = msg
        module.exit_json(**result)
    try:
        ret = redis.connection.set(**set_args)
        if ret is None:
            if nx:
                msg = 'Could not set key: {0} to {1}. Key already present.'.format(
                    key, value)
            else:
                msg = 'Could not set key: {0} to {1}. Key not present.'.format(
                    key, value)
            result['msg'] = msg
            module.fail_json(**result)
        msg = 'Set key: {0} to {1}'.format(key, value)
        result['msg'] = msg
        result['changed'] = True
        module.exit_json(**result)
    except Exception as e:
        msg = 'Failed to set key: {0} to value: {1} with exception: {2}'.format(
            key, value, str(e))
        result['msg'] = msg
        module.fail_json(**result)


if __name__ == '__main__':
    main()

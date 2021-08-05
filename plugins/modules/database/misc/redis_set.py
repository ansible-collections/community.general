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
        required: True
        type: str
notes:
   - Requires the redis-py Python package on the remote host. You can
     install it with pip (pip install redis) or with a package manager.
     https://github.com/andymccurdy/redis-py

extends_documentation_fragment:
  - community.general.redis.documentation

seealso:
    - module: community.general.redis_info
    - module: community.general.redis
'''

EXAMPLES = '''
- name: Set key foo=bar on loalhost with no username
  community.general.redis_set:
    login_host: localhost
    login_password: supersecret
    key: foo
    value: bar

- name: Set key foo=bar on redishost with custom ca-cert file
  community.general.redis:
    login_host: redishost
    login_password: supersecret
    login_user: somuser
    validate_certs: yes
    ssl_ca_certs: /path/to/ca/certs
    key: foo
    value: bar
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
        value=dict(type='str', required=True)
    )
    module_args.update(redis_auth_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )
    import_errors = fail_imports()
    if len(import_errors) != 0:
        module.fail_json(msg=import_errors)

    redis = RedisAnsible(module)

    key = module.params['key']
    value = module.params['value']

    result = {'changed': False}

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
    if module.check_mode or old_value == value:
        msg = 'Key: {0} had value: {1} now has value {2}'.format(
            key, old_value, value)
        result['msg'] = msg
        module.exit_json(**result)
    try:
        redis.connection.set(key, value)
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

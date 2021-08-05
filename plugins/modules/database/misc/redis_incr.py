#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: redis_incr
short_description: Increment keys in Redis
description:
   - Increment integer keys in Redis database by 1 and get new value.
author: "Andreas Botzner (@paginabianca)"
options:
  key:
    description:
      - Database key.
    type: str
    required: True
  increment:
    description:
      - Amount to increment by. Can be integer of float.
    required: False
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
- name: Incr key foo on loalhost with no username and print new value
  community.general.redis_incr:
    login_host: localhost
    login_password: supersecret
    key: foo
  register: result
- name: Print new value
  debug:
    var: result.value
- name: Increment key foo by 20.4
  community.general.redis_incr:
    login_host: redishost
    login_user: redisuser
    login_password: somepass
    key: foo
    increment: '20.4'
'''

RETURN = '''
value:
  description: Incremented value of key
  returned: on success
  type: str
  sample: '4039.4'
msg:
  description: A short message.
  returned: always
  type: str
  sample: 'Incremented key: foo by 20.4 to 65.9'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.redis import (
    fail_imports, redis_auth_argument_spec, RedisAnsible)


def main():
    redis_auth_args = redis_auth_argument_spec()
    module_args = dict(
        key=dict(type='str', required=True, no_log=False),
        increment=dict(type='str', required=False),
    )
    module_args.update(redis_auth_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
    )
    import_errors = fail_imports()
    if len(import_errors) != 0:
        module.fail_json(msg=import_errors)

    redis = RedisAnsible(module)
    key = module.params['key']
    increment = module.params['increment']

    result = {'changed': False}
    if increment is not None:
        try:
            increment = float(increment)
        except ValueError:
            msg = "Increment: {0} is not a number".format(increment)
            result['msg'] = msg
            module.fail_json(**result)
        if increment.is_integer():
            try:
                increment = int(increment)
                value = redis.connection.incrby(key, increment)
                msg = 'Incremented key: {0} by {1} to {2}'.format(
                    key, increment, value)
                result['msg'] = msg
                result['value'] = str(value)
                result['changed'] = True
                module.exit_json(**result)
            except Exception as e:
                msg = 'Failed to increment key: {0} by {1} with exception: {2}'.format(
                    key, increment, str(e))
                result['msg'] = msg
                module.fail_json(**result)
                pass
        else:
            try:
                value = redis.connection.incrbyfloat(key, increment)
                msg = 'Incremented key: {0} by {1} to {2}'.format(
                    key, increment, value)
                result['msg'] = msg
                result['value'] = str(value)
                result['changed'] = True
                module.exit_json(**result)
            except Exception as e:
                msg = 'Failed to increment key: {0} by {1} with exception: {2}'.format(
                    key, increment, str(e))
                result['msg'] = msg
                module.fail_json(**result)
                pass
            pass
    else:
        try:
            value = redis.connection.incr(key)
            msg = 'Incremented key: {0} to {1}'.format(key, value)
            result['msg'] = msg
            result['value'] = str(value)
            result['changed'] = True
            module.exit_json(**result)
        except Exception as e:
            msg = 'Failed to increment key: {0} with exception: {1}'.format(
                key, str(e))
            result['msg'] = msg
            module.fail_json(**result)


if __name__ == '__main__':
    main()

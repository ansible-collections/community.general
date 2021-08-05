#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: redis_data_info
short_description: Get value of key in Redis database
description:
  - Get value of keys in Redis database
author: "Andreas Botzner (@botzner_andreas)"
options:
  key:
    description:
      - Database key.
    type: str
    required: True
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
value:
  description: Value key was set to
  returned: on success
  type: str
  sample: 'value_of_some_key'
msg:
  description: A short message.
  returned: always
  type: str
  sample: 'Got key: foo with value: bar'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.redis import (
    fail_imports, redis_auth_argument_spec, RedisAnsible)


def main():
    redis_auth_args = redis_auth_argument_spec()
    module_args = dict(
        key=dict(type='str', required=True, no_log=False),
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
    result = {'changed': False}

    value = None
    try:
        value = redis.connection.get(key)
        msg = 'Got key: {0} with value: {1}'.format(key, value)
        result['msg'] = msg
        result['value'] = value
        module.exit_json(**result)
    except Exception as e:
        msg = 'Failed to get value of key: {0} with exception: {1}'.format(
            key, str(e))
        result['msg'] = msg
        module.fail_json(**result)


if __name__ == '__main__':
    main()

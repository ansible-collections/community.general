#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: redis_data_info
short_description: Get value of key in Redis database
version_added: 3.7.0
description:
  - Get value of keys in Redis database.
author: "Andreas Botzner (@paginabianca)"
options:
  key:
    description:
      - Database key.
    type: str
    required: true

extends_documentation_fragment:
  - community.general.redis
  - community.general.attributes
  - community.general.attributes.info_module

seealso:
  - module: community.general.redis_data
  - module: community.general.redis_data_incr
  - module: community.general.redis_info
  - module: community.general.redis
'''

EXAMPLES = '''
- name: Get key foo=bar from loalhost with no username
  community.general.redis_data_info:
    login_host: localhost
    login_password: supersecret
    key: foo

- name: Get key foo=bar on redishost with custom ca-cert file
  community.general.redis_data_info:
    login_host: redishost
    login_password: supersecret
    login_user: somuser
    validate_certs: true
    ssl_ca_certs: /path/to/ca/certs
    key: foo
'''

RETURN = '''
exists:
  description: If they key exists in the database.
  returned: on success
  type: bool
value:
  description: Value key was set to.
  returned: if existing
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
        supports_check_mode=True,
    )
    fail_imports(module)

    redis = RedisAnsible(module)

    key = module.params['key']
    result = {'changed': False}

    value = None
    try:
        value = redis.connection.get(key)
    except Exception as e:
        msg = 'Failed to get value of key "{0}" with exception: {1}'.format(
            key, str(e))
        result['msg'] = msg
        module.fail_json(**result)

    if value is None:
        msg = 'Key "{0}" does not exist in database'.format(key)
        result['exists'] = False
    else:
        msg = 'Got key "{0}"'.format(key)
        result['value'] = value
        result['exists'] = True
    result['msg'] = msg
    module.exit_json(**result)


if __name__ == '__main__':
    main()

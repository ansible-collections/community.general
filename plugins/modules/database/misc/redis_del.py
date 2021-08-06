#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: redis_del
short_description: Delete key from Redis
description:
   - Delete a key from a Redis database
author: "Andreas Botzner (@paginabianca)"
options:
    key:
        description:
            - Database key.
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
- name: Delete key foo=bar on loalhost with no username
  community.general.redis_del:
    login_host: localhost
    login_password: supersecret
    key: foo
'''

RETURN = '''
msg:
  description: A short message.
  returned: always
  type: str
  sample: 'Deleted key: foo'
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
        supports_check_mode=False,)
    import_errors = fail_imports()
    if len(import_errors):
        module.fail_json(msg=import_errors)

    redis = RedisAnsible(module)
    key = module.params['key']
    result = {'changed': False}

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


if __name__ == '__main__':
    main()

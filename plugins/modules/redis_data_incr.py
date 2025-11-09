#!/usr/bin/python

# Copyright (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: redis_data_incr
short_description: Increment keys in Redis
version_added: 4.0.0
description:
  - Increment integers or float keys in Redis database and get new value.
  - Default increment for all keys is V(1). For specific increments use the O(increment_int) and O(increment_float) options.
author: "Andreas Botzner (@paginabianca)"
attributes:
  check_mode:
    support: partial
    details:
      - For C(check_mode) to work, the specified O(login_user) needs permission to run the C(GET) command on the key, otherwise
        the module fails.
      - When using C(check_mode) the module tries to calculate the value that Redis would return. If the key is not present,
        V(0.0) is used as value.
  diff_mode:
    support: none
options:
  key:
    description:
      - Database key.
    type: str
    required: true
  increment_int:
    description:
      - Integer amount to increment the key by.
    type: int
  increment_float:
    description:
      - Float amount to increment the key by.
      - This only works with keys that contain float values in their string representation.
    type: float


extends_documentation_fragment:
  - community.general.redis.documentation
  - community.general.attributes

seealso:
  - module: community.general.redis_data
  - module: community.general.redis_data_info
  - module: community.general.redis
"""

EXAMPLES = r"""
- name: Increment integer key foo on localhost with no username and print new value
  community.general.redis_data_incr:
    login_host: localhost
    login_password: supersecret
    key: foo
    increment_int: 1
  register: result
- name: Print new value
  debug:
    var: result.value

- name: Increment float key foo by 20.4
  community.general.redis_data_incr:
    login_host: redishost
    login_user: redisuser
    login_password: somepass
    key: foo
    increment_float: '20.4'
"""

RETURN = r"""
value:
  description: Incremented value of key.
  returned: on success
  type: float
  sample: '4039.4'
msg:
  description: A short message.
  returned: always
  type: str
  sample: 'Incremented key: foo by 20.4 to 65.9'
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.redis import (
    fail_imports,
    redis_auth_argument_spec,
    RedisAnsible,
)


def main():
    redis_auth_args = redis_auth_argument_spec()
    module_args = dict(
        key=dict(type="str", required=True, no_log=False),
        increment_int=dict(type="int"),
        increment_float=dict(type="float"),
    )
    module_args.update(redis_auth_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[["increment_int", "increment_float"]],
    )
    fail_imports(module)

    redis = RedisAnsible(module)
    key = module.params["key"]
    increment_float = module.params["increment_float"]
    increment_int = module.params["increment_int"]
    increment = 1
    if increment_float is not None:
        increment = increment_float
    elif increment_int is not None:
        increment = increment_int

    result = {"changed": False}
    if module.check_mode:
        value = 0.0
        try:
            res = redis.connection.get(key)
            if res is not None:
                value = float(res)
        except ValueError:
            msg = f"Value: {res} of key: {key} is not incrementable(int or float)"
            result["msg"] = msg
            module.fail_json(**result)
        except Exception as e:
            msg = f"Failed to get value of key: {key} with exception: {e}"
            result["msg"] = msg
            module.fail_json(**result)
        msg = f"Incremented key: {key} by {increment} to {value + increment}"
        result["msg"] = msg
        result["value"] = float(value + increment)
        module.exit_json(**result)

    if increment_float is not None:
        try:
            value = redis.connection.incrbyfloat(key, increment)
            msg = f"Incremented key: {key} by {increment} to {value}"
            result["msg"] = msg
            result["value"] = float(value)
            result["changed"] = True
            module.exit_json(**result)
        except Exception as e:
            msg = f"Failed to increment key: {key} by {increment} with exception: {e}"
            result["msg"] = msg
            module.fail_json(**result)
    elif increment_int is not None:
        try:
            value = redis.connection.incrby(key, increment)
            msg = f"Incremented key: {key} by {increment} to {value}"
            result["msg"] = msg
            result["value"] = float(value)
            result["changed"] = True
            module.exit_json(**result)
        except Exception as e:
            msg = f"Failed to increment key: {key} by {increment} with exception: {e}"
            result["msg"] = msg
            module.fail_json(**result)
    else:
        try:
            value = redis.connection.incr(key)
            msg = f"Incremented key: {key} to {value}"
            result["msg"] = msg
            result["value"] = float(value)
            result["changed"] = True
            module.exit_json(**result)
        except Exception as e:
            msg = f"Failed to increment key: {key} with exception: {e}"
            result["msg"] = msg
            module.fail_json(**result)


if __name__ == "__main__":
    main()

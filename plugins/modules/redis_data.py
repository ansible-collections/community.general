#!/usr/bin/python

# Copyright (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: redis_data
short_description: Set key value pairs in Redis
version_added: 3.7.0
description:
  - Set key value pairs in Redis database.
author: "Andreas Botzner (@paginabianca)"
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  key:
    description:
      - Database key.
    required: true
    type: str
  value:
    description:
      - Value that key should be set to.
    type: str
  expiration:
    description:
      - Expiration time in milliseconds. Setting this option always results in a change in the database.
    type: int
  non_existing:
    description:
      - Only set key if it does not already exist.
    type: bool
  existing:
    description:
      - Only set key if it already exists.
    type: bool
  keep_ttl:
    description:
      - Retain the time to live associated with the key.
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
  - community.general.attributes

seealso:
  - module: community.general.redis_data_incr
  - module: community.general.redis_data_info
  - module: community.general.redis
"""

EXAMPLES = r"""
- name: Set key foo=bar on localhost with no username
  community.general.redis_data:
    login_host: localhost
    login_password: supersecret
    key: foo
    value: bar
    state: present

- name: Set key foo=bar if non existing with expiration of 30s
  community.general.redis_data:
    login_host: localhost
    login_password: supersecret
    key: foo
    value: bar
    non_existing: true
    expiration: 30000
    state: present

- name: Set key foo=bar if existing and keep current TTL
  community.general.redis_data:
    login_host: localhost
    login_password: supersecret
    key: foo
    value: bar
    existing: true
    keep_ttl: true

- name: Set key foo=bar on redishost with custom ca-cert file
  community.general.redis_data:
    login_host: redishost
    login_password: supersecret
    login_user: someuser
    validate_certs: true
    ssl_ca_certs: /path/to/ca/certs
    key: foo
    value: bar

- name: Delete key foo on localhost with no username
  community.general.redis_data:
    login_host: localhost
    login_password: supersecret
    key: foo
    state: absent
"""

RETURN = r"""
old_value:
  description: Value of key before setting.
  returned: on_success if O(state=present) and key exists in database.
  type: str
  sample: 'old_value_of_key'
value:
  description: Value key was set to.
  returned: on success if O(state=present).
  type: str
  sample: 'new_value_of_key'
msg:
  description: A short message.
  returned: always
  type: str
  sample: 'Set key: foo to bar'
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
        value=dict(type="str"),
        expiration=dict(type="int"),
        non_existing=dict(type="bool"),
        existing=dict(type="bool"),
        keep_ttl=dict(type="bool"),
        state=dict(type="str", default="present", choices=["present", "absent"]),
    )
    module_args.update(redis_auth_args)

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[("state", "present", ("value",))],
        mutually_exclusive=[["non_existing", "existing"], ["keep_ttl", "expiration"]],
    )
    fail_imports(module)

    redis = RedisAnsible(module)

    key = module.params["key"]
    value = module.params["value"]
    px = module.params["expiration"]
    nx = module.params["non_existing"]
    xx = module.params["existing"]
    keepttl = module.params["keep_ttl"]
    state = module.params["state"]
    set_args = {"name": key, "value": value, "px": px, "nx": nx, "xx": xx, "keepttl": keepttl}

    result = {"changed": False}

    old_value = None
    try:
        old_value = redis.connection.get(key)
    except Exception as e:
        msg = f"Failed to get value of key: {key} with exception: {e}"
        result["msg"] = msg
        module.fail_json(**result)

    if state == "absent":
        if module.check_mode:
            if old_value is None:
                msg = f"Key: {key} not present"
                result["msg"] = msg
                module.exit_json(**result)
            else:
                msg = f"Deleted key: {key}"
                result["msg"] = msg
                module.exit_json(**result)
        try:
            ret = redis.connection.delete(key)
            if ret == 0:
                msg = f"Key: {key} not present"
                result["msg"] = msg
                module.exit_json(**result)
            else:
                msg = f"Deleted key: {key}"
                result["msg"] = msg
                result["changed"] = True
                module.exit_json(**result)
        except Exception as e:
            msg = f"Failed to delete key: {key} with exception: {e}"
            result["msg"] = msg
            module.fail_json(**result)

    old_value = None
    try:
        old_value = redis.connection.get(key)
    except Exception as e:
        msg = f"Failed to get value of key: {key} with exception: {e}"
        result["msg"] = msg
        module.fail_json(**result)

    result["old_value"] = old_value
    if old_value == value and keepttl is not False and px is None:
        msg = f"Key {key} already has desired value"
        result["msg"] = msg
        result["value"] = value
        module.exit_json(**result)
    if module.check_mode:
        result["msg"] = f"Set key: {key}"
        result["value"] = value
        module.exit_json(**result)
    try:
        ret = redis.connection.set(**set_args)
        if ret is None:
            if nx:
                msg = f"Could not set key: {key}. Key already present."
            else:
                msg = f"Could not set key: {key}. Key not present."
            result["msg"] = msg
            module.fail_json(**result)
        msg = f"Set key: {key}"
        result["msg"] = msg
        result["changed"] = True
        result["value"] = value
        module.exit_json(**result)
    except Exception as e:
        msg = f"Failed to set key: {key} with exception: {e}"
        result["msg"] = msg
        module.fail_json(**result)


if __name__ == "__main__":
    main()

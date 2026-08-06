#!/usr/bin/python
#
# Copyright (c) 2026, Shreyash Bhosale <shrbhosa@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: consul_kv_info
short_description: Retrieve entries from the key/value store of a Consul cluster
version_added: 13.3.0
description:
  - Retrieve one or more key/value entries from a Consul cluster.
  - See U(https://developer.hashicorp.com/consul/api-docs/kv) for more details.
author:
  - Shreyash Bhosale (@Shreyashxredhat)
extends_documentation_fragment:
  - community.general._consul
  - community.general._consul.actiongroup_consul
  - community.general._consul.token
  - community.general._attributes
  - community.general._attributes.info_module
options:
  key:
    description:
      - The key to retrieve.
      - When O(recurse) is V(true), this is treated as a prefix.
    type: str
    required: true
  recurse:
    description:
      - If V(true), retrieve all entries sharing the prefix specified by O(key).
    type: bool
    default: false
  datacenter:
    description:
      - The name of the datacenter to query. If unspecified, the query defaults to the datacenter of the Consul agent
        on O(host).
    type: str
"""

EXAMPLES = r"""
- name: Retrieve a single key
  community.general.consul_kv_info:
    key: somekey
  register: result

- name: Display the value
  ansible.builtin.debug:
    msg: "{{ result.data }}"

- name: Retrieve all keys under a prefix
  community.general.consul_kv_info:
    key: app/config/
    recurse: true
  register: result
"""

RETURN = r"""
data:
  description:
    - The list of KV entries matching the query.
    - Each element is a dictionary with the keys C(Key), C(Value), C(Flags), and others returned by the Consul API.
    - The list is empty if the key does not exist.
  returned: always
  type: list
  elements: dict
index:
  description:
    - The Consul index value from the C(X-Consul-Index) response header.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._consul import (
    AUTH_ARGUMENTS_SPEC,
    RequestError,
    _ConsulModule,
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            datacenter=dict(type="str"),
            key=dict(type="str", required=True, no_log=False),
            recurse=dict(type="bool", default=False),
            **AUTH_ARGUMENTS_SPEC,
        ),
        supports_check_mode=True,
    )
    consul_module = _ConsulModule(module)

    try:
        index, data = consul_module.kv_get(
            module.params["key"],
            recurse=module.params["recurse"],
            dc=module.params["datacenter"],
        )
        if data is None:
            data = []
        elif not isinstance(data, list):
            data = [data]
        module.exit_json(changed=False, index=index, data=data)
    except RequestError as e:
        body = e.response_data
        if isinstance(body, bytes):
            body = body.decode("utf-8", errors="replace")
        body = (body or "").strip()
        module.fail_json(msg=body or f"HTTP {e.status}")
    except Exception as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()

#!/usr/bin/python
#
# Copyright (c) 2015, Steve Gargan <steve.gargan@gmail.com>
# Copyright (c) 2018 Genome Research Ltd.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: consul_kv
short_description: Manipulate entries in the key/value store of a Consul cluster
description:
  - Allows the retrieval, addition, modification and deletion of key/value entries in a Consul cluster using the agent. The
    entire contents of the record, including the indices, flags and session are returned as RV(ignore:value).
  - If the O(key) represents a prefix then note that when a value is removed, the existing value if any is returned as part
    of the results.
  - See http://www.consul.io/docs/agent/http.html#kv for more details.
author:
  - Steve Gargan (@sgargan)
  - Colin Nolan (@colin-nolan)
extends_documentation_fragment:
  - community.general._consul
  - community.general._consul.actiongroup_consul
  - community.general._consul.token
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  action_group:
    version_added: 13.2.0
options:
  state:
    description:
      - The action to take with the supplied key and value. If the state is V(present) and O(value) is set, the key contents
        is set to the value supplied and RV(ignore:changed) is set to V(true) only if the value was different to the current contents.
        If the state is V(present) and O(value) is not set, the existing value associated to the key is returned. The state
        V(absent) is used to remove the key/value pair, again RV(ignore:changed) is set to V(true) only if the key actually existed
        prior to the removal. An attempt can be made to obtain or free the lock associated with a key/value pair with the
        states V(acquire) or V(release) respectively. A valid session must be supplied to make the attempt RV(ignore:changed) is V(true)
        if the attempt is successful, V(false) otherwise.
    type: str
    choices: [absent, acquire, present, release]
    default: present
  key:
    description:
      - The key at which the value should be stored.
    type: str
    required: true
  value:
    description:
      - The value should be associated with the given key, required if O(state) is V(present).
    type: str
  recurse:
    description:
      - If the key represents a prefix, each entry with the prefix can be retrieved by setting this to V(true).
    type: bool
  retrieve:
    description:
      - If the O(state) is V(present) and O(value) is set, perform a read after setting the value and return this value.
    default: true
    type: bool
  session:
    description:
      - The session that should be used to acquire or release a lock associated with a key/value pair.
    type: str
  cas:
    description:
      - Used when acquiring a lock with a session. If the O(cas) is V(0), then Consul only puts the key if it does not already
        exist. If the O(cas) value is non-zero, then the key is only set if the index matches the ModifyIndex of that key.
    type: str
  flags:
    description:
      - Opaque positive integer value that can be passed when setting a value.
    type: str
  datacenter:
    description:
      - The name of the datacenter to query. If unspecified, the query defaults to the datacenter of the Consul agent on O(host).
    type: str
    version_added: 10.0.0
"""


EXAMPLES = r"""
# If the key does not exist, the value associated to the "data" property in `retrieved_key` will be `None`
# If the key value is empty string, `retrieved_key["data"]["Value"]` will be `None`
- name: Retrieve a value from the key/value store
  community.general.consul_kv:
    key: somekey
  register: retrieved_key

- name: Add or update the value associated with a key in the key/value store
  community.general.consul_kv:
    key: somekey
    value: somevalue

- name: Remove a key from the store
  community.general.consul_kv:
    key: somekey
    state: absent

- name: Add a node to an arbitrary group using Consul inventory (see consul.ini)
  community.general.consul_kv:
    key: ansible/groups/dc1/somenode
    value: top_secret

- name: Register a key/value pair with an associated session
  community.general.consul_kv:
    key: stg/node/server_birthday
    value: 20160509
    session: "{{ sessionid }}"
    state: acquire
"""

import base64
from http import HTTPStatus
from urllib.parse import quote

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text

from ansible_collections.community.general.plugins.module_utils._consul import (
    AUTH_ARGUMENTS_SPEC,
    RequestError,
    _ConsulModule,
)


def _decode_value(entry):
    if entry.get("Value") is not None:
        entry["Value"] = base64.b64decode(entry["Value"])


def _quote_key(key):
    # KV keys may contain characters that are not valid in a URL path
    # (spaces, non-ASCII, ...). Slashes are key separators and must stay raw.
    return quote(key, safe="/")


def _kv_get(consul_module, key, recurse=False, dc=None):
    params = {"dc": dc}
    if recurse:
        params["recurse"] = "true"
    try:
        body, headers = consul_module.request("GET", ("kv", _quote_key(key)), params=params)
    except RequestError as e:
        if e.status == HTTPStatus.NOT_FOUND:
            index = e.response_headers.get("X-Consul-Index") if e.response_headers else None
            return index, None
        raise
    index = headers.get("X-Consul-Index") if headers is not None else None
    if not body:
        return index, None
    for entry in body:
        _decode_value(entry)
    if recurse:
        return index, body
    return index, body[0]


def _kv_put(consul_module, key, value, cas=None, acquire=None, release=None, flags=None, dc=None):
    params = {"cas": cas, "acquire": acquire, "release": release, "flags": flags, "dc": dc}
    if value is not None:
        value = value.encode("utf-8")
    return consul_module.put(("kv", _quote_key(key)), data=value, params=params) is True


def _kv_delete(consul_module, key, recurse=False, dc=None):
    params = {"dc": dc}
    if recurse:
        params["recurse"] = "true"
    return consul_module.delete(("kv", _quote_key(key)), params=params) is True


def _has_value_changed(consul_module, key, target_value):
    index, existing = _kv_get(consul_module, key)
    if not existing:
        return index, True
    try:
        changed = to_text(existing["Value"], errors="surrogate_or_strict") != target_value
        return index, changed
    except UnicodeError:
        # Existing value was not decodable but all values we set are valid utf-8
        return index, True


def execute(module, consul_module):
    state = module.params["state"]

    if state == "acquire" or state == "release":
        lock(module, consul_module, state)
    elif state == "present":
        if module.params["value"] is None:
            get_value(module, consul_module)
        else:
            set_value(module, consul_module)
    elif state == "absent":
        remove_value(module, consul_module)
    else:
        module.exit_json(msg=f"Unsupported state: {state}")


def lock(module, consul_module, state):
    session = module.params["session"]
    key = module.params["key"]
    value = module.params["value"]
    dc = module.params["datacenter"]

    if not session:
        module.fail_json(msg=f"{state} of lock for {key} requested but no session supplied")

    index, changed = _has_value_changed(consul_module, key, value)

    if changed and not module.check_mode:
        kwargs = {
            "cas": module.params["cas"],
            "flags": module.params["flags"],
            "dc": dc,
        }
        if state == "acquire":
            kwargs["acquire"] = session
        else:
            kwargs["release"] = session
        changed = _kv_put(consul_module, key, value, **kwargs)

    module.exit_json(changed=changed, index=index, key=key)


def get_value(module, consul_module):
    key = module.params["key"]
    index, existing = _kv_get(
        consul_module,
        key,
        recurse=module.params["recurse"],
        dc=module.params["datacenter"],
    )
    module.exit_json(changed=False, index=index, data=existing)


def set_value(module, consul_module):
    key = module.params["key"]
    value = module.params["value"]
    dc = module.params["datacenter"]

    if value is None:
        raise AssertionError(f'Cannot set value of "{key}" to None')

    index, changed = _has_value_changed(consul_module, key, value)

    if changed and not module.check_mode:
        changed = _kv_put(
            consul_module,
            key,
            value,
            cas=module.params["cas"],
            flags=module.params["flags"],
            dc=dc,
        )

    stored = None
    if module.params["retrieve"]:
        index, stored = _kv_get(consul_module, key, dc=dc)

    module.exit_json(changed=changed, index=index, key=key, data=stored)


def remove_value(module, consul_module):
    """Remove the value associated with the given key. If the recurse parameter
    is set then any key prefixed with the given key will be removed."""
    key = module.params["key"]
    dc = module.params["datacenter"]
    recurse = module.params["recurse"]

    index, existing = _kv_get(consul_module, key, recurse=recurse, dc=dc)

    changed = existing is not None
    if changed and not module.check_mode:
        _kv_delete(consul_module, key, recurse=recurse, dc=dc)

    module.exit_json(changed=changed, index=index, key=key, data=existing)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cas=dict(type="str"),
            datacenter=dict(type="str"),
            flags=dict(type="str"),
            key=dict(type="str", required=True, no_log=False),
            recurse=dict(type="bool"),
            retrieve=dict(type="bool", default=True),
            state=dict(type="str", default="present", choices=["absent", "acquire", "present", "release"]),
            value=dict(type="str"),
            session=dict(type="str"),
            **AUTH_ARGUMENTS_SPEC,
        ),
        supports_check_mode=True,
    )
    consul_module = _ConsulModule(module)

    try:
        execute(module, consul_module)
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

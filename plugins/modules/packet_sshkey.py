#!/usr/bin/python
# Copyright 2016 Tomas Karasek <tom.to.the.k@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: packet_sshkey
short_description: Create/delete an SSH key in Packet host
description:
  - Create/delete an SSH key in Packet host.
  - API is documented at U(https://www.packet.net/help/api/#page:ssh-keys,header:ssh-keys-ssh-keys-post).
author: "Tomas Karasek (@t0mk) <tom.to.the.k@gmail.com>"
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  state:
    description:
      - Indicate desired state of the target.
    default: present
    choices: ['present', 'absent']
    type: str
  auth_token:
    description:
      - Packet API token. You can also supply it in environment variable E(PACKET_API_TOKEN).
    type: str
  label:
    description:
      - Label for the key. If you keep it empty, it is read from key string.
    type: str
    aliases: [name]
  id:
    description:
      - UUID of the key which you want to remove.
    type: str
  fingerprint:
    description:
      - Fingerprint of the key which you want to remove.
    type: str
  key:
    description:
      - Public Key string (V({type} {base64 encoded key} {description})).
    type: str
  key_file:
    description:
      - File with the public key.
    type: path

requirements:
  - packet-python
"""

EXAMPLES = r"""
# All the examples assume that you have your Packet API token in env var PACKET_API_TOKEN.
# You can also pass the api token in module param auth_token.

- name: Create sshkey from string
  hosts: localhost
  tasks:
    community.general.packet_sshkey:
      key: "{{ lookup('file', 'my_packet_sshkey.pub') }}"

- name: Create sshkey from file
  hosts: localhost
  tasks:
    community.general.packet_sshkey:
      label: key from file
      key_file: ~/ff.pub

- name: Remove sshkey by id
  hosts: localhost
  tasks:
    community.general.packet_sshkey:
      state: absent
      id: eef49903-7a09-4ca1-af67-4087c29ab5b6
"""

RETURN = r"""
sshkeys:
  description: Information about sshkeys that were created/removed.
  type: list
  sample:
    [
      {
        "fingerprint": "5c:93:74:7c:ed:07:17:62:28:75:79:23:d6:08:93:46",
        "id": "41d61bd8-3342-428b-a09c-e67bdd18a9b7",
        "key": "ssh-dss AAAAB3NzaC1kc3MAAACBA ... MdDxfmcsCslJKgoRKSmQpCwXQtN2g== user@server",
        "label": "mynewkey33"
      }
    ]
  returned: always
"""

import os
import uuid

from ansible.module_utils.basic import AnsibleModule

HAS_PACKET_SDK = True
try:
    import packet
except ImportError:
    HAS_PACKET_SDK = False


PACKET_API_TOKEN_ENV_VAR = "PACKET_API_TOKEN"


def serialize_sshkey(sshkey):
    sshkey_data = {}
    copy_keys = ["id", "key", "label", "fingerprint"]
    for name in copy_keys:
        sshkey_data[name] = getattr(sshkey, name)
    return sshkey_data


def is_valid_uuid(myuuid):
    try:
        val = uuid.UUID(myuuid, version=4)
    except ValueError:
        return False
    return str(val) == myuuid


def load_key_string(key_str):
    ret_dict = {}
    key_str = key_str.strip()
    ret_dict["key"] = key_str
    cut_key = key_str.split()
    if len(cut_key) in [2, 3]:
        if len(cut_key) == 3:
            ret_dict["label"] = cut_key[2]
    else:
        raise Exception(f"Public key {key_str} is in wrong format")
    return ret_dict


def get_sshkey_selector(module):
    key_id = module.params.get("id")
    if key_id:
        if not is_valid_uuid(key_id):
            raise Exception(f"sshkey ID {key_id} is not valid UUID")
    selecting_fields = ["label", "fingerprint", "id", "key"]
    select_dict = {}
    for f in selecting_fields:
        if module.params.get(f) is not None:
            select_dict[f] = module.params.get(f)

    if module.params.get("key_file"):
        with open(module.params.get("key_file")) as _file:
            loaded_key = load_key_string(_file.read())
        select_dict["key"] = loaded_key["key"]
        if module.params.get("label") is None:
            if loaded_key.get("label"):
                select_dict["label"] = loaded_key["label"]

    def selector(k):
        if "key" in select_dict:
            # if key string is specified, compare only the key strings
            return k.key == select_dict["key"]
        else:
            # if key string not specified, all the fields must match
            return all(select_dict[f] == getattr(k, f) for f in select_dict)

    return selector


def act_on_sshkeys(target_state, module, packet_conn):
    selector = get_sshkey_selector(module)
    existing_sshkeys = packet_conn.list_ssh_keys()
    matching_sshkeys = list(filter(selector, existing_sshkeys))
    changed = False
    if target_state == "present":
        if matching_sshkeys == []:
            # there is no key matching the fields from module call
            # => create the key, label and
            newkey = {}
            if module.params.get("key_file"):
                with open(module.params.get("key_file")) as f:
                    newkey = load_key_string(f.read())
            if module.params.get("key"):
                newkey = load_key_string(module.params.get("key"))
            if module.params.get("label"):
                newkey["label"] = module.params.get("label")
            for param in ("label", "key"):
                if param not in newkey:
                    _msg = (
                        "If you want to ensure a key is present, you must "
                        "supply both a label and a key string, either in "
                        f"module params, or in a key file. {param} is missing"
                    )
                    raise Exception(_msg)
            matching_sshkeys = []
            new_key_response = packet_conn.create_ssh_key(newkey["label"], newkey["key"])
            changed = True

            matching_sshkeys.append(new_key_response)
    else:
        # state is 'absent' => delete matching keys
        for k in matching_sshkeys:
            try:
                k.delete()
                changed = True
            except Exception as e:
                _msg = f"while trying to remove sshkey {k.label}, id {k.id} {target_state}, got error: {e}"
                raise Exception(_msg)

    return {"changed": changed, "sshkeys": [serialize_sshkey(k) for k in matching_sshkeys]}


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(choices=["present", "absent"], default="present"),
            auth_token=dict(default=os.environ.get(PACKET_API_TOKEN_ENV_VAR), no_log=True),
            label=dict(type="str", aliases=["name"]),
            id=dict(type="str"),
            fingerprint=dict(type="str"),
            key=dict(type="str", no_log=True),
            key_file=dict(type="path"),
        ),
        mutually_exclusive=[
            ("label", "id"),
            ("label", "fingerprint"),
            ("id", "fingerprint"),
            ("key", "fingerprint"),
            ("key", "id"),
            ("key_file", "key"),
        ],
    )

    if not HAS_PACKET_SDK:
        module.fail_json(msg="packet required for this module")

    if not module.params.get("auth_token"):
        _fail_msg = f"if Packet API token is not in environment variable {PACKET_API_TOKEN_ENV_VAR}, the auth_token parameter is required"
        module.fail_json(msg=_fail_msg)

    auth_token = module.params.get("auth_token")

    packet_conn = packet.Manager(auth_token=auth_token)

    state = module.params.get("state")

    if state in ["present", "absent"]:
        try:
            module.exit_json(**act_on_sshkeys(state, module, packet_conn))
        except Exception as e:
            module.fail_json(msg=f"failed to set sshkey state: {e}")
    else:
        module.fail_json(msg=f"{state} is not a valid state for this module")


if __name__ == "__main__":
    main()

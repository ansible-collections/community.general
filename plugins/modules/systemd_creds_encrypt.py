#!/usr/bin/python

# Copyright (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: systemd_creds_encrypt
short_description: C(systemd)'s C(systemd-creds encrypt) plugin
description:
  - This module encrypts input using C(systemd)'s C(systemd-creds encrypt).
author:
  - Thomas Sjögren (@konstruktoid)
version_added: '10.2.0'
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
    details:
      - This action does not modify state.
  diff_mode:
    support: N/A
    details:
      - This action does not modify state.
options:
  name:
    description:
      - The credential name to embed in the encrypted credential data.
    type: str
  not_after:
    description:
      - The time when the credential shall not be used anymore.
      - Takes a timestamp specification in the format described in V(systemd.time(7\)).
    type: str
  pretty:
    description:
      - Pretty print the output so that it may be pasted directly into a unit file.
    type: bool
    default: false
  secret:
    description:
      - The secret to encrypt.
    type: str
    required: true
  timestamp:
    description:
      - The timestamp to embed into the encrypted credential.
      - Takes a timestamp specification in the format described in V(systemd.time(7\)).
    type: str
  user:
    description:
      - A user name or numeric UID to encrypt the credential for.
      - If set to the special string V(self) it sets the user to the user of the calling process.
      - Requires C(systemd) 256 or later.
    type: str
notes:
  - C(systemd-creds) requires C(systemd) 250 or later.
"""

EXAMPLES = r"""
- name: Encrypt secret
  become: true
  community.general.systemd_creds_encrypt:
    name: db
    not_after: +48hr
    secret: access_token
  register: encrypted_secret

- name: Print the encrypted secret
  ansible.builtin.debug:
    msg: "{{ encrypted_secret }}"
"""

RETURN = r"""
value:
  description: The Base64 encoded encrypted secret.
  type: str
  returned: always
  sample: "WhQZht+JQJax1aZemmGLxmAAAA..."
"""

from ansible.module_utils.basic import AnsibleModule


def main():
    """Encrypt secret using systemd-creds."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str"),
            not_after=dict(type="str"),
            pretty=dict(type="bool", default=False),
            secret=dict(type="str", required=True, no_log=True),
            timestamp=dict(type="str"),
            user=dict(type="str"),
        ),
        supports_check_mode=True,
    )

    cmd = module.get_bin_path("systemd-creds", required=True)

    name = module.params["name"]
    not_after = module.params["not_after"]
    pretty = module.params["pretty"]
    secret = module.params["secret"]
    timestamp = module.params["timestamp"]
    user = module.params["user"]

    encrypt_cmd = [cmd, "encrypt"]
    if name:
        encrypt_cmd.append(f"--name={name}")
    else:
        encrypt_cmd.append("--name=")
    if not_after:
        encrypt_cmd.append(f"--not-after={not_after}")
    if pretty:
        encrypt_cmd.append("--pretty")
    if timestamp:
        encrypt_cmd.append(f"--timestamp={timestamp}")
    if user:
        encrypt_cmd.append(f"--uid={user}")
    encrypt_cmd.extend(["-", "-"])

    rc, stdout, stderr = module.run_command(encrypt_cmd, data=secret, binary_data=True)

    module.exit_json(
        changed=False,
        value=stdout,
        rc=rc,
        stderr=stderr,
    )


if __name__ == "__main__":
    main()

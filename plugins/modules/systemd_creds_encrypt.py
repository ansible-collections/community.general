#!/usr/bin/python

# Copyright (c) 2024, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type


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
        When using the O(dest) option, you can set this to an empty
        string ("") to prevent C(systemd-creds encrypt) from using
        filename from O(dest) as the credential name. Conversely,
        leave out the O(name) option to let C(systemd-creds encrypt)
        use the filename from O(dest) as the credential name.
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
  dest:
    description:
      - The destination for the credential file.
    type: path
    version_added: 11.3.0
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

- name: Create a credential file
  become: true
  community.general.systemd_creds_encrypt:
    name: db
    secret: access_token
    dest: /etc/credstore.encrypted/db.cred
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
            dest=dict(type="path"),
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['pretty', 'dest']
        ]
    )

    cmd = module.get_bin_path("systemd-creds", required=True)

    name = module.params["name"]
    not_after = module.params["not_after"]
    pretty = module.params["pretty"]
    secret = module.params["secret"]
    timestamp = module.params["timestamp"]
    user = module.params["user"]
    dest = module.params["dest"]

    encrypt_cmd = [cmd, "encrypt"]
    if name is not None:
        encrypt_cmd.append("--name=" + name)
    elif not dest:
        encrypt_cmd.append("--name=")
    if not_after:
        encrypt_cmd.append("--not-after=" + not_after)
    if pretty:
        encrypt_cmd.append("--pretty")
    if timestamp:
        encrypt_cmd.append("--timestamp=" + timestamp)
    if user:
        encrypt_cmd.append("--uid=" + user)

    encrypt_cmd.append("-")

    if dest and not module.check_mode:
        encrypt_cmd.append(dest)
    else:
        encrypt_cmd.append("-")

    rc, stdout, stderr = module.run_command(encrypt_cmd, data=secret, binary_data=True)

    module.exit_json(
        changed=False,
        value=stdout if not dest else None,
        rc=rc,
        stderr=stderr,
    )


if __name__ == "__main__":
    main()

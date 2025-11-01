#!/usr/bin/python

# Copyright (c) 2019, George Rawlinson <george@rawlinson.net.nz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: pacman_key
author:
  - George Rawlinson (@grawlinson)
version_added: "3.2.0"
short_description: Manage pacman's list of trusted keys
description:
  - Add or remove gpg keys from the pacman keyring.
notes:
  - Use full-length key ID (40 characters).
  - Keys are verified when using O(data), O(file), or O(url) unless O(verify) is overridden.
  - Keys are locally signed after being imported into the keyring.
  - If the key ID exists in the keyring, the key is not added unless O(force_update) is specified.
  - O(data), O(file), O(url), and O(keyserver) are mutually exclusive.
requirements:
  - gpg
  - pacman-key
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  id:
    description:
      - The 40 character identifier of the key.
      - Including this allows check mode to correctly report the changed state.
      - Do not specify a subkey ID, instead specify the primary key ID.
    required: true
    type: str
  data:
    description:
      - The keyfile contents to add to the keyring.
      - Must be of C(PGP PUBLIC KEY BLOCK) type.
    type: str
  file:
    description:
      - The path to a keyfile on the remote server to add to the keyring.
      - Remote file must be of C(PGP PUBLIC KEY BLOCK) type.
    type: path
  url:
    description:
      - The URL to retrieve keyfile from.
      - Remote file must be of C(PGP PUBLIC KEY BLOCK) type.
    type: str
  keyserver:
    description:
      - The keyserver used to retrieve key from.
    type: str
  verify:
    description:
      - Whether or not to verify the keyfile's key ID against specified key ID.
    type: bool
    default: true
  force_update:
    description:
      - This forces the key to be updated if it already exists in the keyring.
    type: bool
    default: false
  keyring:
    description:
      - The full path to the keyring folder on the remote server.
      - If not specified, module uses pacman's default (V(/etc/pacman.d/gnupg)).
      - Useful if the remote system requires an alternative gnupg directory.
    type: path
    default: /etc/pacman.d/gnupg
  state:
    description:
      - Ensures that the key is V(present) (added) or V(absent) (revoked).
    default: present
    choices: [absent, present]
    type: str
  ensure_trusted:
    description:
      - Ensure that the key is trusted (signed by the Pacman machine key and not expired).
    type: bool
    default: false
    version_added: 11.0.0
"""

EXAMPLES = r"""
- name: Import a key via local file
  community.general.pacman_key:
    id: 01234567890ABCDE01234567890ABCDE12345678
    data: "{{ lookup('file', 'keyfile.asc') }}"
    state: present

- name: Import a key via remote file
  community.general.pacman_key:
    id: 01234567890ABCDE01234567890ABCDE12345678
    file: /tmp/keyfile.asc
    state: present

- name: Import a key via url
  community.general.pacman_key:
    id: 01234567890ABCDE01234567890ABCDE12345678
    url: https://domain.tld/keys/keyfile.asc
    state: present

- name: Import a key via keyserver
  community.general.pacman_key:
    id: 01234567890ABCDE01234567890ABCDE12345678
    keyserver: keyserver.domain.tld

- name: Import a key into an alternative keyring
  community.general.pacman_key:
    id: 01234567890ABCDE01234567890ABCDE12345678
    file: /tmp/keyfile.asc
    keyring: /etc/pacman.d/gnupg-alternative

- name: Remove a key from the keyring
  community.general.pacman_key:
    id: 01234567890ABCDE01234567890ABCDE12345678
    state: absent
"""

RETURN = r""" # """

import os.path
import tempfile
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.common.text.converters import to_native


class GpgListResult:
    """Wraps gpg --list-* output."""

    def __init__(self, line):
        self._parts = line.split(":")

    @property
    def kind(self):
        return self._parts[0]

    @property
    def valid(self):
        return self._parts[1]

    @property
    def is_fully_valid(self):
        return self.valid == "f"

    @property
    def key(self):
        return self._parts[4]

    @property
    def user_id(self):
        return self._parts[9]


def gpg_get_first_attr_of_kind(lines, kind, attr):
    for line in lines:
        glr = GpgListResult(line)
        if glr.kind == kind:
            return getattr(glr, attr)


def gpg_get_all_attrs_of_kind(lines, kind, attr):
    result = []
    for line in lines:
        glr = GpgListResult(line)
        if glr.kind == kind:
            result.append(getattr(glr, attr))
    return result


class PacmanKey:
    def __init__(self, module):
        self.module = module
        # obtain binary paths for gpg & pacman-key
        self.gpg_binary = module.get_bin_path("gpg", required=True)
        self.pacman_key_binary = module.get_bin_path("pacman-key", required=True)

        # obtain module parameters
        keyid = module.params["id"]
        url = module.params["url"]
        data = module.params["data"]
        file = module.params["file"]
        keyserver = module.params["keyserver"]
        verify = module.params["verify"]
        force_update = module.params["force_update"]
        keyring = module.params["keyring"]
        state = module.params["state"]
        ensure_trusted = module.params["ensure_trusted"]
        self.keylength = 40

        # sanitise key ID & check if key exists in the keyring
        keyid = self.sanitise_keyid(keyid)
        key_validity = self.key_validity(keyring, keyid)
        key_present = len(key_validity) > 0
        key_valid = any(key_validity)

        # check mode
        if module.check_mode:
            if state == "present":
                changed = (key_present and force_update) or not key_present
                if not changed and ensure_trusted:
                    changed = not (key_valid and self.key_is_trusted(keyring, keyid))
                module.exit_json(changed=changed)
            if state == "absent":
                module.exit_json(changed=key_present)

        if state == "present":
            trusted = key_valid and self.key_is_trusted(keyring, keyid)
            if not force_update and key_present and (not ensure_trusted or trusted):
                module.exit_json(changed=False)
            changed = False
            if data:
                file = self.save_key(data)
                self.add_key(keyring, file, keyid, verify)
                changed = True
            elif file:
                self.add_key(keyring, file, keyid, verify)
                changed = True
            elif url:
                data = self.fetch_key(url)
                file = self.save_key(data)
                self.add_key(keyring, file, keyid, verify)
                changed = True
            elif keyserver:
                self.recv_key(keyring, keyid, keyserver)
                changed = True
            if changed or (ensure_trusted and not trusted):
                self.lsign_key(keyring=keyring, keyid=keyid)
                changed = True
            module.exit_json(changed=changed)
        elif state == "absent":
            if key_present:
                self.remove_key(keyring, keyid)
                module.exit_json(changed=True)
            module.exit_json(changed=False)

    def gpg(self, args, keyring=None, **kwargs):
        cmd = [self.gpg_binary]
        if keyring:
            cmd.append(f"--homedir={keyring}")
        cmd.extend(["--no-permission-warning", "--with-colons", "--quiet", "--batch", "--no-tty"])
        return self.module.run_command(cmd + args, **kwargs)

    def pacman_key(self, args, keyring, **kwargs):
        return self.module.run_command([self.pacman_key_binary, "--gpgdir", keyring] + args, **kwargs)

    def pacman_machine_key(self, keyring):
        unused_rc, stdout, unused_stderr = self.gpg(["--list-secret-key"], keyring=keyring)
        return gpg_get_first_attr_of_kind(stdout.splitlines(), "sec", "key")

    def is_hexadecimal(self, string):
        """Check if a given string is valid hexadecimal"""
        try:
            int(string, 16)
        except ValueError:
            return False
        return True

    def sanitise_keyid(self, keyid):
        """Sanitise given key ID.

        Strips whitespace, uppercases all characters, and strips leading `0X`.
        """
        sanitised_keyid = keyid.strip().upper().replace(" ", "").replace("0X", "")
        if len(sanitised_keyid) != self.keylength:
            self.module.fail_json(msg=f"key ID is not full-length: {sanitised_keyid}")
        if not self.is_hexadecimal(sanitised_keyid):
            self.module.fail_json(msg=f"key ID is not hexadecimal: {sanitised_keyid}")
        return sanitised_keyid

    def fetch_key(self, url):
        """Downloads a key from url"""
        response, info = fetch_url(self.module, url)
        if info["status"] != 200:
            self.module.fail_json(msg=f"failed to fetch key at {url}, error was {info['msg']}")
        return to_native(response.read())

    def recv_key(self, keyring, keyid, keyserver):
        """Receives key via keyserver"""
        self.pacman_key(["--keyserver", keyserver, "--recv-keys", keyid], keyring=keyring, check_rc=True)

    def lsign_key(self, keyring, keyid):
        """Locally sign key"""
        self.pacman_key(["--lsign-key", keyid], keyring=keyring, check_rc=True)

    def save_key(self, data):
        "Saves key data to a temporary file"
        tmpfd, tmpname = tempfile.mkstemp()
        self.module.add_cleanup_file(tmpname)
        tmpfile = os.fdopen(tmpfd, "w")
        tmpfile.write(data)
        tmpfile.close()
        return tmpname

    def add_key(self, keyring, keyfile, keyid, verify):
        """Add key to pacman's keyring"""
        if verify:
            self.verify_keyfile(keyfile, keyid)
        self.pacman_key(["--add", keyfile], keyring=keyring, check_rc=True)

    def remove_key(self, keyring, keyid):
        """Remove key from pacman's keyring"""
        self.pacman_key(["--delete", keyid], keyring=keyring, check_rc=True)

    def verify_keyfile(self, keyfile, keyid):
        """Verify that keyfile matches the specified key ID"""
        if keyfile is None:
            self.module.fail_json(msg="expected a key, got none")
        elif keyid is None:
            self.module.fail_json(msg="expected a key ID, got none")

        rc, stdout, stderr = self.gpg(
            ["--with-fingerprint", "--show-keys", keyfile],
            check_rc=True,
        )

        extracted_keyid = gpg_get_first_attr_of_kind(stdout.splitlines(), "fpr", "user_id")
        if extracted_keyid != keyid:
            self.module.fail_json(msg=f"key ID does not match. expected {keyid}, got {extracted_keyid}")

    def key_validity(self, keyring, keyid):
        "Check if the key ID is in pacman's keyring and not expired"
        rc, stdout, stderr = self.gpg(["--no-default-keyring", "--list-keys", keyid], keyring=keyring, check_rc=False)
        if rc != 0:
            if stderr.find("No public key") >= 0:
                return []
            else:
                self.module.fail_json(msg=f"gpg returned an error: {stderr}")
        return gpg_get_all_attrs_of_kind(stdout.splitlines(), "uid", "is_fully_valid")

    def key_is_trusted(self, keyring, keyid):
        """Check if key is signed and not expired."""
        unused_rc, stdout, unused_stderr = self.gpg(["--check-signatures", keyid], keyring=keyring)
        return self.pacman_machine_key(keyring) in gpg_get_all_attrs_of_kind(stdout.splitlines(), "sig", "key")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            id=dict(type="str", required=True),
            data=dict(type="str"),
            file=dict(type="path"),
            url=dict(type="str"),
            keyserver=dict(type="str"),
            verify=dict(type="bool", default=True),
            force_update=dict(type="bool", default=False),
            keyring=dict(type="path", default="/etc/pacman.d/gnupg"),
            ensure_trusted=dict(type="bool", default=False),
            state=dict(type="str", default="present", choices=["absent", "present"]),
        ),
        supports_check_mode=True,
        mutually_exclusive=(("data", "file", "url", "keyserver"),),
        required_if=[("state", "present", ("data", "file", "url", "keyserver"), True)],
    )
    PacmanKey(module)


if __name__ == "__main__":
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, George Rawlinson <george@rawlinson.net.nz>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: pacman_key
author:
- George Rawlinson (@grawlinson)
version_added: "1.3.0"
short_description: Manage pacman's list of trusted keys
description:
- Add or remove gpg keys from the pacman keyring.
notes:
- Use full-length identifier (40 characters) for key ID and fingerprint to avoid key collisions.
- If you specify both the key id and the URL with C(state=present), the task can verify or add the key as needed.
- By default, keys will be locally signed after being imported into the keyring.
- If the specified key id exists in the keyring, the key will not be added.
- I(data), I(file), and I(url) are mutually exclusive.
- Supports C(check_mode).
requirements:
- gpg
- pacman-key
options:
    id:
        description:
            - The 40 character identifier of the key.
            - Including this allows check mode to correctly report the changed state.
            - Do not specify a subkey id, instead specify the master key id.
        required: yes
        type: str
    data:
        description:
            - The keyfile contents to add to the keyring.
            - Must be of "PGP PUBLIC KEY BLOCK" type.
        type: str
    file:
        description:
            - The path to a keyfile on the remote server to add to the keyring.
            - Remote file should be of "PGP PUBLIC KEY BLOCK" type.
        type: path
    url:
        description:
            - The URL to retrieve keyfile from.
            - Remote file should be of "PGP PUBLIC KEY BLOCK" type.
        type: str
    keyserver:
        description:
            - The keyserver used to retrieve key from.
        type: str
    fingerprint:
        description:
            - 40 character fingerprint of the key.
            - When specified, it is used for verification.
        type: str
    force_update:
        description:
            - This forces the key to be updated if it already exists in the keyring.
        type: bool
        default: no
    keyring:
        description:
            - The full path to the keyring folder on the remote server.
            - If not specified, module will use pacman's default (/etc/pacman.d/gnupg).
            - Useful if the remote system requires an alternative gnupg directory.
        type: path
    state:
        description:
            - Ensures that the key is present (added) or absent (revoked).
        default: present
        choices: [ absent, present ]
        type: str
'''

EXAMPLES = '''
- name: Import a key via local file
  community.general.pacman_key:
    data: "{{ lookup('file', 'keyfile.asc') }}"
    state: present

- name: Import a key via remote file
  community.general.pacman_key:
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
'''

RETURN = r''' # '''

import os.path
import tempfile
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_native


class PacmanKey(object):
    def __init__(self, module):
        self.module = module
        self.gpg = module.get_bin_path('gpg', required=True)
        self.pacman_key = module.get_bin_path('pacman-key', required=True)
        keyid = module.params['id']
        url = module.params['url']
        data = module.params['data']
        file = module.params['file']
        keyserver = module.params['keyserver']
        fingerprint = module.params['fingerprint']
        force_update = module.params['force_update']
        keyring = module.params['keyring']
        state = module.params['state']
        self.keylength = 40

        keyid = self.sanitise_identifier(keyid)
        if fingerprint:
            fingerprint = self.sanitise_identifier(fingerprint)
        key_present = self.key_in_keyring(keyid, keyring)

        if (
            state == "present"
            and data is None
            and file is None
            and url is None
            and keyserver is None
        ):
            module.fail_json(msg="expected one of: data, file, url, keyserver. got none")

        if module.check_mode:
            if state == "present":
                if (key_present and force_update) or not key_present:
                    module.exit_json(changed=True)
                module.exit_json(changed=False)
            elif state == "absent":
                if key_present:
                    module.exit_json(changed=True)
                module.exit_json(changed=False)

        if state == "present":
            if key_present and not force_update:
                module.exit_json(changed=False)

            if data:
                file = self.save_key(data)
                self.add_key(keyring, file, keyid, fingerprint)
                module.exit_json(changed=True)
            elif file:
                self.add_key(keyring, file, keyid, fingerprint)
                module.exit_json(changed=True)
            elif url:
                data = self.fetch_key(url)
                file = self.save_key(data)
                self.add_key(keyring, file, keyid, fingerprint)
                module.exit_json(changed=True)
            elif keyserver:
                self.recv_key(keyring, keyid, keyserver)
                module.exit_json(changed=True)
        elif state == "absent":
            if key_present:
                self.remove_key(keyring, keyid)
                module.exit_json(changed=True)
            module.exit_json(changed=False)

    def is_hexadecimal(self, string):
        """Check if a given string is valid hexadecimal"""
        try:
            int(string, 16)
        except ValueError:
            return False
        return True

    def sanitise_identifier(self, identifier):
        """Sanitise given key id or fingerprint.

        Strips whitespace, uppercases all characters, and strips leading `0X`.
        """
        identifier = identifier.strip().upper().replace(' ', '').replace('0X', '')
        if len(identifier) != self.keylength:
            self.module.fail_json(msg="identifier is not full-length: %s" % identifier)
        if not self.is_hexadecimal(identifier):
            self.module.fail_json(msg="identifier is not hexadecimal: %s" % identifier)
        return identifier

    def fetch_key(self, url):
        """Downloads a key from url"""
        response, info = fetch_url(self.module, url)
        if info['status'] != 200:
            self.module.fail_json(msg="failed to fetch key at %s, error was %s" % (url, info['msg']))
        return to_native(response.read())

    def recv_key(self, keyring, keyid, keyserver=None):
        """Receives key via keyserver"""
        cmd = [self.pacman_key, '--gpgdir', keyring]
        if keyserver is not None:
            cmd.extend(['--keyserver', keyserver])
        self.module.run_command(cmd + ['--recv-keys', keyid], check_rc=True)
        self.lsign_key(keyid, keyring)

    def lsign_key(self, keyring, keyid):
        """Locally sign key"""
        cmd = [self.pacman_key, '--gpgdir', keyring]
        self.module.run_command(cmd + ['--lsign-key', keyid], check_rc=True)

    def save_key(self, data):
        "Saves key data to a temporary file"
        tmpfd, tmpname = tempfile.mkstemp()
        self.module.add_cleanup_file(tmpname)
        tmpfile = os.fdopen(tmpfd, "w")
        tmpfile.write(data)
        tmpfile.close()
        return tmpname

    def add_key(self, keyring, keyfile, keyid, fingerprint=None):
        """Add key to pacman's keyring"""
        cmd = [self.pacman_key, '--gpgdir', keyring]
        if fingerprint is not None:
            self.verify_keyfile(keyfile, keyid, fingerprint)
        self.module.run_command(cmd + ['--add', keyfile], check_rc=True)
        self.lsign_key(keyid, keyring)

    def remove_key(self, keyring, keyid):
        """Remove key from pacman's keyring"""
        cmd = [self.pacman_key, '--gpgdir', keyring]
        self.module.run_command(cmd + ['--delete', keyid], check_rc=True)

    def verify_keyfile(self, keyfile, keyid, fingerprint):
        """Verify that keyfile matches the specified keyid & fingerprint"""
        if keyfile is None:
            self.module.fail_json(msg="expected a key, got none")
        elif keyid is None:
            self.module.fail_json(msg="expected a keyid, got none")
        elif fingerprint is None:
            self.module.fail_json(msg="expected a fingerprint, got none")

        _, stdout, _ = self.module.run_command([self.gpg, '--with-colons', '--with-fingerprint', '--batch', '--no-tty', '--show-keys', keyfile], check_rc=True)

        extracted_keyid = extracted_fingerprint = None
        for line in stdout.splitlines():
            if line.startswith('pub:'):
                extracted_keyid = line.split(':')[4]
            elif line.startswith('fpr:'):
                extracted_fingerprint = line.split(':')[9]
                break

        if extracted_keyid != keyid:
            self.module.fail_json(msg="keyid does not match. expected %s, got %s" % (keyid, extracted_keyid))
        elif extracted_fingerprint != fingerprint:
            self.module.fail_json(msg="fingerprint does not match. expected %s, got %s" % (fingerprint, extracted_fingerprint))

    def key_in_keyring(self, keyring, keyid):
        "Check if the keyid is in pacman's keyring"
        rc, _, stderr = self.module.run_command(
            [self.gpg, '--with-colons', '--batch', '--no-tty',
                '--no-default-keyring', '--keyring=' + keyring + '/pubring.gpg',
                '--list-keys', keyid])
        if rc != 0:
            if stderr.find("No public key") >= 0:
                return False
            else:
                self.module.fail_json(msg="gpg returned an error: %s" % stderr)
        return True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            id=dict(type='str', required=True),
            data=dict(type='str'),
            file=dict(type='path'),
            url=dict(type='str'),
            keyserver=dict(type='str'),
            fingerprint=dict(type='str'),
            force_update=dict(type='bool', default=False),
            keyring=dict(type='path', default='/etc/pacman.d/gnupg'),
            state=dict(type='str', default='present', choices=['absent', 'present']),
        ),
        supports_check_mode=True,
        mutually_exclusive=(('data', 'file', 'url', 'keyserver'),),
    )
    PacmanKey(module)


if __name__ == '__main__':
    main()

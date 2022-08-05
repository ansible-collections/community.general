#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, George Rawlinson <george@rawlinson.net.nz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: pacman_key
author:
- George Rawlinson (@grawlinson)
version_added: "3.2.0"
short_description: Manage pacman's list of trusted keys
description:
- Add or remove gpg keys from the pacman keyring.
notes:
- Use full-length key ID (40 characters).
- Keys will be verified when using I(data), I(file), or I(url) unless I(verify) is overridden.
- Keys will be locally signed after being imported into the keyring.
- If the key ID exists in the keyring, the key will not be added unless I(force_update) is specified.
- I(data), I(file), I(url), and I(keyserver) are mutually exclusive.
- Supports C(check_mode).
requirements:
- gpg
- pacman-key
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
            - If not specified, module will use pacman's default (C(/etc/pacman.d/gnupg)).
            - Useful if the remote system requires an alternative gnupg directory.
        type: path
        default: /etc/pacman.d/gnupg
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
from ansible.module_utils.common.text.converters import to_native


class PacmanKey(object):
    def __init__(self, module):
        self.module = module
        # obtain binary paths for gpg & pacman-key
        self.gpg = module.get_bin_path('gpg', required=True)
        self.pacman_key = module.get_bin_path('pacman-key', required=True)

        # obtain module parameters
        keyid = module.params['id']
        url = module.params['url']
        data = module.params['data']
        file = module.params['file']
        keyserver = module.params['keyserver']
        verify = module.params['verify']
        force_update = module.params['force_update']
        keyring = module.params['keyring']
        state = module.params['state']
        self.keylength = 40

        # sanitise key ID & check if key exists in the keyring
        keyid = self.sanitise_keyid(keyid)
        key_present = self.key_in_keyring(keyring, keyid)

        # check mode
        if module.check_mode:
            if state == "present":
                changed = (key_present and force_update) or not key_present
                module.exit_json(changed=changed)
            elif state == "absent":
                if key_present:
                    module.exit_json(changed=True)
                module.exit_json(changed=False)

        if state == "present":
            if key_present and not force_update:
                module.exit_json(changed=False)

            if data:
                file = self.save_key(data)
                self.add_key(keyring, file, keyid, verify)
                module.exit_json(changed=True)
            elif file:
                self.add_key(keyring, file, keyid, verify)
                module.exit_json(changed=True)
            elif url:
                data = self.fetch_key(url)
                file = self.save_key(data)
                self.add_key(keyring, file, keyid, verify)
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

    def sanitise_keyid(self, keyid):
        """Sanitise given key ID.

        Strips whitespace, uppercases all characters, and strips leading `0X`.
        """
        sanitised_keyid = keyid.strip().upper().replace(' ', '').replace('0X', '')
        if len(sanitised_keyid) != self.keylength:
            self.module.fail_json(msg="key ID is not full-length: %s" % sanitised_keyid)
        if not self.is_hexadecimal(sanitised_keyid):
            self.module.fail_json(msg="key ID is not hexadecimal: %s" % sanitised_keyid)
        return sanitised_keyid

    def fetch_key(self, url):
        """Downloads a key from url"""
        response, info = fetch_url(self.module, url)
        if info['status'] != 200:
            self.module.fail_json(msg="failed to fetch key at %s, error was %s" % (url, info['msg']))
        return to_native(response.read())

    def recv_key(self, keyring, keyid, keyserver):
        """Receives key via keyserver"""
        cmd = [self.pacman_key, '--gpgdir', keyring, '--keyserver', keyserver, '--recv-keys', keyid]
        self.module.run_command(cmd, check_rc=True)
        self.lsign_key(keyring, keyid)

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

    def add_key(self, keyring, keyfile, keyid, verify):
        """Add key to pacman's keyring"""
        if verify:
            self.verify_keyfile(keyfile, keyid)
        cmd = [self.pacman_key, '--gpgdir', keyring, '--add', keyfile]
        self.module.run_command(cmd, check_rc=True)
        self.lsign_key(keyring, keyid)

    def remove_key(self, keyring, keyid):
        """Remove key from pacman's keyring"""
        cmd = [self.pacman_key, '--gpgdir', keyring, '--delete', keyid]
        self.module.run_command(cmd, check_rc=True)

    def verify_keyfile(self, keyfile, keyid):
        """Verify that keyfile matches the specified key ID"""
        if keyfile is None:
            self.module.fail_json(msg="expected a key, got none")
        elif keyid is None:
            self.module.fail_json(msg="expected a key ID, got none")

        rc, stdout, stderr = self.module.run_command(
            [
                self.gpg,
                '--with-colons',
                '--with-fingerprint',
                '--batch',
                '--no-tty',
                '--show-keys',
                keyfile
            ],
            check_rc=True,
        )

        extracted_keyid = None
        for line in stdout.splitlines():
            if line.startswith('fpr:'):
                extracted_keyid = line.split(':')[9]
                break

        if extracted_keyid != keyid:
            self.module.fail_json(msg="key ID does not match. expected %s, got %s" % (keyid, extracted_keyid))

    def key_in_keyring(self, keyring, keyid):
        "Check if the key ID is in pacman's keyring"
        rc, stdout, stderr = self.module.run_command(
            [
                self.gpg,
                '--with-colons',
                '--batch',
                '--no-tty',
                '--no-default-keyring',
                '--keyring=%s/pubring.gpg' % keyring,
                '--list-keys', keyid
            ],
            check_rc=False,
        )
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
            verify=dict(type='bool', default=True),
            force_update=dict(type='bool', default=False),
            keyring=dict(type='path', default='/etc/pacman.d/gnupg'),
            state=dict(type='str', default='present', choices=['absent', 'present']),
        ),
        supports_check_mode=True,
        mutually_exclusive=(('data', 'file', 'url', 'keyserver'),),
        required_if=[('state', 'present', ('data', 'file', 'url', 'keyserver'), True)],
    )
    PacmanKey(module)


if __name__ == '__main__':
    main()

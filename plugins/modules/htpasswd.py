#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Nimbis Services, Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: htpasswd
short_description: Manage user files for basic authentication
description:
  - Add and remove username/password entries in a password file using htpasswd.
  - This is used by web servers such as Apache and Nginx for basic authentication.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  path:
    type: path
    required: true
    aliases: [dest, destfile]
    description:
      - Path to the file that contains the usernames and passwords.
  name:
    type: str
    required: true
    aliases: [username]
    description:
      - User name to add or remove.
  password:
    type: str
    required: false
    description:
      - Password associated with user.
      - Must be specified if user does not exist yet.
  hash_scheme:
    type: str
    required: false
    default: "apr_md5_crypt"
    description:
      - Hashing scheme to be used. As well as the four choices listed here, you can also use any other hash supported by passlib,
        such as V(portable_apache22) and V(host_apache24); or V(md5_crypt) and V(sha256_crypt), which are Linux passwd hashes.
        Only some schemes in addition to the four choices below are compatible with Apache or Nginx, and supported schemes
        depend on C(passlib) version and its dependencies.
      - See U(https://passlib.readthedocs.io/en/stable/lib/passlib.apache.html#passlib.apache.HtpasswdFile) parameter C(default_scheme).
      - 'Some of the available choices might be: V(apr_md5_crypt), V(des_crypt), V(ldap_sha1), V(plaintext).'
      - 'B(WARNING): The module has no mechanism to determine the O(hash_scheme) of an existing entry, therefore, it does
        not detect whether the O(hash_scheme) has changed. If you want to change the scheme, you must remove the existing
        entry and then create a new one using the new scheme.'
    aliases: [crypt_scheme]
  state:
    type: str
    required: false
    choices: [present, absent]
    default: "present"
    description:
      - Whether the user entry should be present or not.
  create:
    required: false
    type: bool
    default: true
    description:
      - Used with O(state=present). If V(true), the file is created if it does not exist. Conversely, if set to V(false) and
        the file does not exist, it fails.
notes:
  - This module depends on the C(passlib) Python library, which needs to be installed on all target systems.
  - 'On Debian < 11, Ubuntu <= 20.04, or Fedora: install C(python-passlib).'
  - 'On Debian, Ubuntu: install C(python3-passlib).'
  - 'On RHEL or CentOS: Enable EPEL, then install C(python-passlib).'
requirements: [passlib>=1.6]
author: "Ansible Core Team"
extends_documentation_fragment:
  - files
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Add a user to a password file and ensure permissions are set
  community.general.htpasswd:
    path: /etc/nginx/passwdfile
    name: janedoe
    password: '9s36?;fyNp'
    owner: root
    group: www-data
    mode: '0640'

- name: Remove a user from a password file
  community.general.htpasswd:
    path: /etc/apache2/passwdfile
    name: foobar
    state: absent

- name: Add a user to a password file suitable for use by libpam-pwdfile
  community.general.htpasswd:
    path: /etc/mail/passwords
    name: alex
    password: oedu2eGh
    hash_scheme: md5_crypt
"""


import os
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils import deps
from ansible.module_utils.common.text.converters import to_native


with deps.declare("passlib"):
    from passlib.apache import HtpasswdFile, htpasswd_context
    from passlib.context import CryptContext


apache_hashes = ["apr_md5_crypt", "des_crypt", "ldap_sha1", "plaintext"]


def create_missing_directories(dest):
    destpath = os.path.dirname(dest)
    if not os.path.exists(destpath):
        os.makedirs(destpath)


def present(dest, username, password, hash_scheme, create, check_mode):
    """ Ensures user is present

    Returns (msg, changed) """
    if hash_scheme in apache_hashes:
        context = htpasswd_context
    else:
        context = CryptContext(schemes=[hash_scheme] + apache_hashes)
    if not os.path.exists(dest):
        if not create:
            raise ValueError('Destination %s does not exist' % dest)
        if check_mode:
            return ("Create %s" % dest, True)
        create_missing_directories(dest)
        ht = HtpasswdFile(dest, new=True, default_scheme=hash_scheme, context=context)
        ht.set_password(username, password)
        ht.save()
        return ("Created %s and added %s" % (dest, username), True)
    else:
        ht = HtpasswdFile(dest, new=False, default_scheme=hash_scheme, context=context)

        found = ht.check_password(username, password)

        if found:
            return ("%s already present" % username, False)
        else:
            if not check_mode:
                ht.set_password(username, password)
                ht.save()
            return ("Add/update %s" % username, True)


def absent(dest, username, check_mode):
    """ Ensures user is absent

    Returns (msg, changed) """
    ht = HtpasswdFile(dest, new=False)

    if username not in ht.users():
        return ("%s not present" % username, False)
    else:
        if not check_mode:
            ht.delete(username)
            ht.save()
        return ("Remove %s" % username, True)


def check_file_attrs(module, changed, message):

    file_args = module.load_file_common_arguments(module.params)
    if module.set_fs_attributes_if_different(file_args, False):

        if changed:
            message += " and "
        changed = True
        message += "ownership, perms or SE linux context changed"

    return message, changed


def main():
    arg_spec = dict(
        path=dict(type='path', required=True, aliases=["dest", "destfile"]),
        name=dict(type='str', required=True, aliases=["username"]),
        password=dict(type='str', no_log=True),
        hash_scheme=dict(type='str', default="apr_md5_crypt", aliases=["crypt_scheme"]),
        state=dict(type='str', default="present", choices=["present", "absent"]),
        create=dict(type='bool', default=True),

    )
    module = AnsibleModule(argument_spec=arg_spec,
                           add_file_common_args=True,
                           supports_check_mode=True)

    path = module.params['path']
    username = module.params['name']
    password = module.params['password']
    hash_scheme = module.params['hash_scheme']
    state = module.params['state']
    create = module.params['create']
    check_mode = module.check_mode

    deps.validate(module)

    # TODO double check if this hack below is still needed.
    # Check file for blank lines in effort to avoid "need more than 1 value to unpack" error.
    try:
        with open(path, "r") as f:
            lines = f.readlines()

        # If the file gets edited, it returns true, so only edit the file if it has blank lines
        strip = False
        for line in lines:
            if not line.strip():
                strip = True
                break

        if strip:
            # If check mode, create a temporary file
            if check_mode:
                temp = tempfile.NamedTemporaryFile()
                path = temp.name
            with open(path, "w") as f:
                f.writelines(line for line in lines if line.strip())

    except IOError:
        # No preexisting file to remove blank lines from
        pass

    try:
        if state == 'present':
            (msg, changed) = present(path, username, password, hash_scheme, create, check_mode)
        elif state == 'absent':
            if not os.path.exists(path):
                module.warn("%s does not exist" % path)
                module.exit_json(msg="%s not present" % username, changed=False)
            (msg, changed) = absent(path, username, check_mode)
        else:
            module.fail_json(msg="Invalid state: %s" % state)
            return  # needed to make pylint happy

        (msg, changed) = check_file_attrs(module, changed, msg)
        module.exit_json(msg=msg, changed=changed)
    except Exception as e:
        module.fail_json(msg=to_native(e))


if __name__ == '__main__':
    main()

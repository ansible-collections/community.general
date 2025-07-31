#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022, Alexander Hussey <ahussey@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Ansible Module - community.general.keyring
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: keyring
version_added: 5.2.0
author:
  - Alexander Hussey (@ahussey-redhat)
short_description: Set or delete a passphrase using the Operating System's native keyring
description: >-
  This module uses the L(keyring Python library, https://pypi.org/project/keyring/) to set or delete passphrases for a given
  service and username from the OS' native keyring.
requirements:
  - keyring (Python library)
  - gnome-keyring (application - required for headless Gnome keyring access)
  - dbus-run-session (application - required for headless Gnome keyring access)
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  service:
    description: The name of the service.
    required: true
    type: str
  username:
    description: The user belonging to the service.
    required: true
    type: str
  user_password:
    description: The password to set.
    required: false
    type: str
    aliases:
      - password
  keyring_password:
    description: Password to unlock keyring.
    required: true
    type: str
  state:
    description: Whether the password should exist.
    required: false
    default: present
    type: str
    choices:
      - present
      - absent
"""

EXAMPLES = r"""
- name: Set a password for test/test1
  community.general.keyring:
    service: test
    username: test1
    user_password: "{{ user_password }}"
    keyring_password: "{{ keyring_password }}"

- name: Delete the password for test/test1
  community.general.keyring:
    service: test
    username: test1
    user_password: "{{ user_password }}"
    keyring_password: "{{ keyring_password }}"
    state: absent
"""

try:
    from shlex import quote
except ImportError:
    from pipes import quote
import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

try:
    import keyring

    HAS_KEYRING = True
    KEYRING_IMP_ERR = None
except ImportError:
    HAS_KEYRING = False
    KEYRING_IMP_ERR = traceback.format_exc()


def del_passphrase(module):
    """
    Attempt to delete a passphrase in the keyring using the Python API and fallback to using a shell.
    """
    if module.check_mode:
        return None
    try:
        keyring.delete_password(module.params["service"], module.params["username"])
        return None
    except keyring.errors.KeyringLocked:
        delete_argument = (
            'echo "%s" | gnome-keyring-daemon --unlock\nkeyring del %s %s\n'
            % (
                quote(module.params["keyring_password"]),
                quote(module.params["service"]),
                quote(module.params["username"]),
            )
        )
        dummy, dummy, stderr = module.run_command(
            "dbus-run-session -- /bin/bash",
            use_unsafe_shell=True,
            data=delete_argument,
            encoding=None,
        )

        if not stderr.decode("UTF-8"):
            return None
        return stderr.decode("UTF-8")


def set_passphrase(module):
    """
    Attempt to set passphrase in the keyring using the Python API and fallback to using a shell.
    """
    if module.check_mode:
        return None
    try:
        keyring.set_password(
            module.params["service"],
            module.params["username"],
            module.params["user_password"],
        )
        return None
    except keyring.errors.KeyringLocked:
        set_argument = (
            'echo "%s" | gnome-keyring-daemon --unlock\nkeyring set %s %s\n%s\n'
            % (
                quote(module.params["keyring_password"]),
                quote(module.params["service"]),
                quote(module.params["username"]),
                quote(module.params["user_password"]),
            )
        )
        dummy, dummy, stderr = module.run_command(
            "dbus-run-session -- /bin/bash",
            use_unsafe_shell=True,
            data=set_argument,
            encoding=None,
        )
        if not stderr.decode("UTF-8"):
            return None
        return stderr.decode("UTF-8")


def get_passphrase(module):
    """
    Attempt to retrieve passphrase from keyring using the Python API and fallback to using a shell.
    """
    try:
        passphrase = keyring.get_password(
            module.params["service"], module.params["username"]
        )
        return passphrase
    except keyring.errors.KeyringLocked:
        pass
    except keyring.errors.InitError:
        pass
    except AttributeError:
        pass
    get_argument = 'echo "%s" | gnome-keyring-daemon --unlock\nkeyring get %s %s\n' % (
        quote(module.params["keyring_password"]),
        quote(module.params["service"]),
        quote(module.params["username"]),
    )
    dummy, stdout, dummy = module.run_command(
        "dbus-run-session -- /bin/bash",
        use_unsafe_shell=True,
        data=get_argument,
        encoding=None,
    )
    try:
        return stdout.decode("UTF-8").splitlines()[1]  # Only return the line containing the password
    except IndexError:
        return None


def run_module():
    """
    Attempts to retrieve a passphrase from a keyring.
    """
    result = dict(
        changed=False,
        msg="",
    )

    module_args = dict(
        service=dict(type="str", required=True),
        username=dict(type="str", required=True),
        keyring_password=dict(type="str", required=True, no_log=True),
        user_password=dict(
            type="str", no_log=True, aliases=["password"]
        ),
        state=dict(
            type="str", default="present", choices=["absent", "present"]
        ),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if not HAS_KEYRING:
        module.fail_json(msg=missing_required_lib("keyring"), exception=KEYRING_IMP_ERR)

    passphrase = get_passphrase(module)
    if module.params["state"] == "present":
        if passphrase is not None:
            if passphrase == module.params["user_password"]:
                result["msg"] = "Passphrase already set for %s@%s" % (
                    module.params["service"],
                    module.params["username"],
                )
            if passphrase != module.params["user_password"]:
                set_result = set_passphrase(module)
                if set_result is None:
                    result["changed"] = True
                    result["msg"] = "Passphrase has been updated for %s@%s" % (
                        module.params["service"],
                        module.params["username"],
                    )
                if set_result is not None:
                    module.fail_json(msg=set_result)
        if passphrase is None:
            set_result = set_passphrase(module)
            if set_result is None:
                result["changed"] = True
                result["msg"] = "Passphrase has been updated for %s@%s" % (
                    module.params["service"],
                    module.params["username"],
                )
            if set_result is not None:
                module.fail_json(msg=set_result)

    if module.params["state"] == "absent":
        if not passphrase:
            result["result"] = "Passphrase already absent for %s@%s" % (
                module.params["service"],
                module.params["username"],
            )
        if passphrase:
            del_result = del_passphrase(module)
            if del_result is None:
                result["changed"] = True
                result["msg"] = "Passphrase has been removed for %s@%s" % (
                    module.params["service"],
                    module.params["username"],
                )
            if del_result is not None:
                module.fail_json(msg=del_result)

    module.exit_json(**result)


def main():
    """
    main module loop
    """
    run_module()


if __name__ == "__main__":
    main()

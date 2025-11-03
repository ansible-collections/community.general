#!/usr/bin/python

# Copyright (c) 2022, Alexander Hussey <ahussey@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Ansible Module - community.general.keyring_info
"""

from __future__ import annotations


DOCUMENTATION = r"""
module: keyring_info
version_added: 5.2.0
author:
  - Alexander Hussey (@ahussey-redhat)
short_description: Get a passphrase using the Operating System's native keyring
description: >-
  This module uses the L(keyring Python library, https://pypi.org/project/keyring/) to retrieve passphrases for a given service
  and username from the OS' native keyring.
requirements:
  - keyring (Python library)
  - gnome-keyring (application - required for headless Linux keyring access)
  - dbus-run-session (application - required for headless Linux keyring access)
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
options:
  service:
    description: The name of the service.
    required: true
    type: str
  username:
    description: The user belonging to the service.
    required: true
    type: str
  keyring_password:
    description: Password to unlock keyring.
    required: true
    type: str
"""

EXAMPLES = r"""
- name: Retrieve password for service_name/user_name
  community.general.keyring_info:
    service: test
    username: test1
    keyring_password: "{{ keyring_password }}"
  register: test_password

- name: Display password
  ansible.builtin.debug:
    msg: "{{ test_password.passphrase }}"
"""

RETURN = r"""
passphrase:
  description: A string containing the password.
  returned: success and the password exists
  type: str
  sample: Password123
"""

from shlex import quote
import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

try:
    import keyring

    HAS_KEYRING = True
    KEYRING_IMP_ERR = None
except ImportError:
    HAS_KEYRING = False
    KEYRING_IMP_ERR = traceback.format_exc()


def _alternate_retrieval_method(module):
    get_argument = (
        f'echo "{quote(module.params["keyring_password"])}" | gnome-keyring-daemon --unlock\n'
        f"keyring get {quote(module.params['service'])} {quote(module.params['username'])}\n"
    )
    dummy, stdout, dummy = module.run_command(
        "dbus-run-session -- /bin/bash",
        use_unsafe_shell=True,
        data=get_argument,
        encoding=None,
    )
    try:
        return stdout.decode("UTF-8").splitlines()[1]
    except IndexError:
        return None


def run_module():
    """
    Attempts to retrieve a passphrase from a keyring.
    """
    result = dict(changed=False, msg="")

    module_args = dict(
        service=dict(type="str", required=True),
        username=dict(type="str", required=True),
        keyring_password=dict(type="str", required=True, no_log=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    if not HAS_KEYRING:
        module.fail_json(msg=missing_required_lib("keyring"), exception=KEYRING_IMP_ERR)
    try:
        passphrase = keyring.get_password(module.params["service"], module.params["username"])
    except keyring.errors.KeyringLocked:
        pass
    except keyring.errors.InitError:
        pass
    except AttributeError:
        pass

    if passphrase is None:
        passphrase = _alternate_retrieval_method(module)

    if passphrase is not None:
        result["msg"] = f"Successfully retrieved password for {module.params['service']}@{module.params['username']}"
        result["passphrase"] = passphrase
    if passphrase is None:
        result["msg"] = f"Password for {module.params['service']}@{module.params['username']} does not exist."
    module.exit_json(**result)


def main():
    """
    main module loop
    """
    run_module()


if __name__ == "__main__":
    main()

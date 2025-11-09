#!/usr/bin/python
#
# Copyright (C) 2013, Peter Sprygada <sprygada@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: ejabberd_user
author: "Peter Sprygada (@privateip)"
short_description: Manages users for ejabberd servers
requirements:
  - ejabberd with mod_admin_extra
description:
  - This module provides user management for ejabberd servers.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  username:
    type: str
    description:
      - The name of the user to manage.
    required: true
  host:
    type: str
    description:
      - The ejabberd host associated with this username.
    required: true
  password:
    type: str
    description:
      - The password to assign to the username.
  state:
    type: str
    description:
      - Describe the desired state of the user to be managed.
    default: 'present'
    choices: ['present', 'absent']
notes:
  - Password parameter is required for O(state=present) only.
  - Passwords must be stored in clear text for this release.
  - The ejabberd configuration file must include mod_admin_extra as a module.
"""
EXAMPLES = r"""
# Example playbook entries using the ejabberd_user module to manage users state.

- name: Create a user if it does not exist
  community.general.ejabberd_user:
    username: test
    host: server
    password: password

- name: Delete a user if it exists
  community.general.ejabberd_user:
    username: test
    host: server
    state: absent
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


class EjabberdUser:
    """This object represents a user resource for an ejabberd server.   The
    object manages user creation and deletion using ejabberdctl.  The following
    commands are currently supported:
        * ejabberdctl register
        * ejabberdctl unregister
    """

    def __init__(self, module):
        self.module = module
        self.state = module.params.get("state")
        self.host = module.params.get("host")
        self.user = module.params.get("username")
        self.pwd = module.params.get("password")
        self.runner = CmdRunner(
            module,
            command="ejabberdctl",
            arg_formats=dict(
                cmd=cmd_runner_fmt.as_list(),
                host=cmd_runner_fmt.as_list(),
                user=cmd_runner_fmt.as_list(),
                pwd=cmd_runner_fmt.as_list(),
            ),
            check_rc=False,
        )

    @property
    def changed(self):
        """This method will check the current user and see if the password has
        changed.   It will return True if the user does not match the supplied
        credentials and False if it does not
        """
        return self.run_command("check_password", "user host pwd", (lambda rc, out, err: bool(rc)))

    @property
    def exists(self):
        """This method will check to see if the supplied username exists for
        host specified.  If the user exists True is returned, otherwise False
        is returned
        """
        return self.run_command("check_account", "user host", (lambda rc, out, err: not bool(rc)))

    def log(self, entry):
        """This method does nothing"""
        pass

    def run_command(self, cmd, options, process=None):
        """This method will run the any command specified and return the
        returns using the Ansible common module
        """

        def _proc(*a):
            return a

        if process is None:
            process = _proc

        with self.runner(f"cmd {options}", output_process=process) as ctx:
            res = ctx.run(cmd=cmd, host=self.host, user=self.user, pwd=self.pwd)
            self.log(f"command: {' '.join(ctx.run_info['cmd'])}")
        return res

    def update(self):
        """The update method will update the credentials for the user provided"""
        return self.run_command("change_password", "user host pwd")

    def create(self):
        """The create method will create a new user on the host with the
        password provided
        """
        return self.run_command("register", "user host pwd")

    def delete(self):
        """The delete method will delete the user from the host"""
        return self.run_command("unregister", "user host")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True, type="str"),
            username=dict(required=True, type="str"),
            password=dict(type="str", no_log=True),
            state=dict(default="present", choices=["present", "absent"]),
        ),
        required_if=[
            ("state", "present", ["password"]),
        ],
        supports_check_mode=True,
    )

    obj = EjabberdUser(module)

    rc = None
    result = dict(changed=False)

    if obj.state == "absent":
        if obj.exists:
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = obj.delete()
            if rc != 0:
                module.fail_json(msg=err, rc=rc)

    elif obj.state == "present":
        if not obj.exists:
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = obj.create()
        elif obj.changed:
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = obj.update()
        if rc is not None and rc != 0:
            module.fail_json(msg=err, rc=rc)

    if rc is None:
        result["changed"] = False
    else:
        result["changed"] = True

    module.exit_json(**result)


if __name__ == "__main__":
    main()

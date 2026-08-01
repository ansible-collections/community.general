#!/usr/bin/python
# Copyright (c) 2016, Werner Dijkerman (ikben@werner-dijkerman.nl)
# Copyright (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: opendj_backendprop
short_description: Update the backend configuration of OpenDJ using the dsconfig set-backend-prop command
description:
  - This module updates settings for OpenDJ with the command C(set-backend-prop).
  - It checks first using C(get-backend-prop) if configuration needs to be applied.
author:
  - Werner Dijkerman (@dj-wasabi)
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  opendj_bindir:
    description:
      - The path to the bin directory of OpenDJ.
    default: /opt/opendj/bin
    type: path
  hostname:
    description:
      - The hostname of the OpenDJ server.
    required: true
    type: str
  port:
    description:
      - The Admin port on which the OpenDJ instance is available.
    required: true
    type: str
  username:
    description:
      - The username to connect with.
    default: cn=Directory Manager
    type: str
  password:
    description:
      - The password for O(username).
      - Either O(password) or O(passwordfile) is needed.
    type: str
  passwordfile:
    description:
      - Location to the password file which holds the password for O(username).
      - Either O(password) or O(passwordfile) is needed.
    type: path
  backend:
    description:
      - The name of the backend on which the property needs to be updated.
    required: true
    type: str
  name:
    description:
      - The configuration setting to update.
    required: true
    type: str
  value:
    description:
      - The value for the configuration item.
    required: true
    type: str
  state:
    description:
      - If configuration needs to be added/updated.
    default: "present"
    type: str
"""

EXAMPLES = r"""
- name: Add or update OpenDJ backend properties
  opendj_backendprop:
    hostname: localhost
    port: 4444
    username: "cn=Directory Manager"
    password: password
    backend: userRoot
    name: index-entry-limit
    value: 5000
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._cmd_runner import CmdRunner, cmd_runner_fmt


class BackendProp:
    def __init__(self, module):
        self._module = module
        self.runner = CmdRunner(
            module,
            command=f"{module.params['opendj_bindir']}/dsconfig",
            arg_formats=dict(
                get_cmd=cmd_runner_fmt.as_fixed(["get-backend-prop", "-n", "-X", "-s"]),
                set_cmd=cmd_runner_fmt.as_fixed(["set-backend-prop", "-n", "-X"]),
                hostname=cmd_runner_fmt.as_opt_val("-h"),
                port=cmd_runner_fmt.as_opt_val("--port"),
                username=cmd_runner_fmt.as_opt_val("--bindDN"),
                password=cmd_runner_fmt.as_opt_val("-w"),
                passwordfile=cmd_runner_fmt.as_opt_val("-j"),
                backend=cmd_runner_fmt.as_opt_val("--backend-name"),
                set_prop=cmd_runner_fmt.as_func(cmd_runner_fmt.unpack_args(lambda n, v: ["--set", f"{n}:{v}"])),
            ),
        )

    def get_property(self):
        with self.runner(
            "get_cmd hostname port username password passwordfile backend",
            check_rc=True,
        ) as ctx:
            rc, stdout, stderr = ctx.run()
        return stdout

    def set_property(self, name, value):
        with self.runner(
            "set_cmd hostname port username password passwordfile backend set_prop",
            check_rc=True,
        ) as ctx:
            ctx.run(set_prop=[name, value])

    def validate_data(self, data, name, value):
        for config_line in data.splitlines():
            if config_line:
                split_line = config_line.split()
                if split_line[0] == name:
                    if split_line[1] == value:
                        return True
        return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            opendj_bindir=dict(default="/opt/opendj/bin", type="path"),
            hostname=dict(required=True),
            port=dict(required=True),
            username=dict(default="cn=Directory Manager"),
            password=dict(no_log=True),
            passwordfile=dict(type="path"),
            backend=dict(required=True),
            name=dict(required=True),
            value=dict(required=True),
            state=dict(default="present"),
        ),
        supports_check_mode=True,
        mutually_exclusive=[["password", "passwordfile"]],
        required_one_of=[["password", "passwordfile"]],
    )

    opendj = BackendProp(module)
    stdout = opendj.get_property()

    if stdout and not opendj.validate_data(data=stdout, name=module.params["name"], value=module.params["value"]):
        if module.check_mode:
            module.exit_json(changed=True)
        opendj.set_property(module.params["name"], module.params["value"])
        module.exit_json(changed=True)
    else:
        module.exit_json(changed=False)


if __name__ == "__main__":
    main()

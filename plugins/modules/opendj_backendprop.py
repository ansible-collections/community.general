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
  - community.general.attributes
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


class BackendProp:
    def __init__(self, module):
        self._module = module

    def get_property(self, opendj_bindir, hostname, port, username, password_method, backend_name):
        my_command = [
            f"{opendj_bindir}/dsconfig",
            "get-backend-prop",
            "-h",
            hostname,
            "--port",
            str(port),
            "--bindDN",
            username,
            "--backend-name",
            backend_name,
            "-n",
            "-X",
            "-s",
        ] + password_method
        rc, stdout, stderr = self._module.run_command(my_command, check_rc=True)
        return stdout

    def set_property(self, opendj_bindir, hostname, port, username, password_method, backend_name, name, value):
        my_command = [
            f"{opendj_bindir}/dsconfig",
            "set-backend-prop",
            "-h",
            hostname,
            "--port",
            str(port),
            "--bindDN",
            username,
            "--backend-name",
            backend_name,
            "--set",
            f"{name}:{value}",
            "-n",
            "-X",
        ] + password_method
        self._module.run_command(my_command, check_rc=True)
        return True

    def validate_data(self, data=None, name=None, value=None):
        for config_line in data.split("\n"):
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

    opendj_bindir = module.params["opendj_bindir"]
    hostname = module.params["hostname"]
    port = module.params["port"]
    username = module.params["username"]
    password = module.params["password"]
    passwordfile = module.params["passwordfile"]
    backend_name = module.params["backend"]
    name = module.params["name"]
    value = module.params["value"]
    # state = module.params["state"]  TODO - ???

    if module.params["password"] is not None:
        password_method = ["-w", password]
    elif module.params["passwordfile"] is not None:
        password_method = ["-j", passwordfile]

    opendj = BackendProp(module)
    validate = opendj.get_property(
        opendj_bindir=opendj_bindir,
        hostname=hostname,
        port=port,
        username=username,
        password_method=password_method,
        backend_name=backend_name,
    )

    if validate:
        if not opendj.validate_data(data=validate, name=name, value=value):
            if module.check_mode:
                module.exit_json(changed=True)
            if opendj.set_property(
                opendj_bindir=opendj_bindir,
                hostname=hostname,
                port=port,
                username=username,
                password_method=password_method,
                backend_name=backend_name,
                name=name,
                value=value,
            ):
                module.exit_json(changed=True)
            else:
                module.exit_json(changed=False)
        else:
            module.exit_json(changed=False)
    else:
        module.exit_json(changed=False)


if __name__ == "__main__":
    main()

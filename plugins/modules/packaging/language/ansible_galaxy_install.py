#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2021, Alexei Znamensky <russoz@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: ansible_galaxy_install
author:
    - "Alexei Znamensky (@russoz)"
short_description: Install Ansible roles or collections using ansible-galaxy
description:
  - This module allows the installation of Ansible collections or roles using C(ansible-galaxy).
options:
  type:
    description:
    - The type of installation performed by C(ansible-galaxy).
    - If I(type) is C(both), then I(requirements_file) must be passed and it may contain both roles and collections.
    type: str
    choices: [collection, role, both]
    required: yes
  name:
    description:
    - Name of the collection or role being installed.
    - Versions can be specified with C(ansible-galaxy) usual formats. For example, C(community.docker:1.6.1) or C(ansistrano.deploy,3.8.0).
    - I(name) and I(requirements_file) are mutually exclusive.
    type: str
  requirements_file:
    description:
    - Path to a file containing a list of requirements to be installed.
    - It works for I(type) equals to C(collection) and C(role).
    - I(name) and I(requirements_file) are mutually exclusive.
    type: path
  dest:
    description:
    - The path to the directory containing your collections or roles, according to the value of I(type).
    - >
      Please notice that C(ansible-galaxy) will not install collections with I(type) C(both), when I(requirements_file)
      contains both roles and collections and I(dest) is specified.
    type: path
  force:
    description:
    - Force overwriting an existing role or collection.
    - Using I(force) as C(true) is mandatory when downgrading.
    type: bool
    default: no
"""

EXAMPLES = """
- name: Install collection community.network
  community.general.ansible_galaxy_install:
    type: collection
    name: community.network

- name: Install role at specific path
  community.general.ansible_galaxy_install:
    type: role
    name: ansistrano.deploy
    dest: /ansible/roles

- name: Install collections and roles together
  community.general.ansible_galaxy_install:
    type: both
    requirements_file: requirements.yml

- name: Force-install collection community.network at specific version
  community.general.ansible_galaxy_install:
    type: collection
    name: community.network:3.0.2
    force: yes

"""

RETURN = """
  installed:
    description: Collections and roles effectively installed
    returned: success
    type: complex
    contains:
      collections:
        description: Collections and versions installed
        returned: success
        type: dict
      roles:
        description: Roles and versions installed
        returned: success
        type: dict
    sample:
      collections:
        community.general: 3.1.0
        community.docker: 1.6.1
      roles:
        ansistrano.deploy: 3.8.0
        baztian.xfce: v0.0.3
  type:
    description: The value of the I(type) parameter.
    type: str
    returned: always
  name:
    description: The value of the I(name) parameter.
    type: str
    returned: always
  dest:
    description: The value of the I(dest) parameter.
    type: str
    returned: always
  requirements_file:
    description: The value of the I(requirements_file) parameter.
    type: str
    returned: always
  force:
    description: The value of the I(force) parameter.
    type: bool
    returned: always
  roles:
    description:
    - If I(requirements_file) is specified instead, returns dictionary with all the roles installed per path.
    - If I(name) is specified, returns that role name and the version installed per path.
    type: dict
    returned: always when installing roles
    contains:
      "<path>":
        description: Roles and versions for that path
        type: dict
    sample:
      /home/az/.ansible/roles:
        ansistrano.deploy: 3.9.0
        baztian.xfce: v0.0.3
      /custom/ansible/roles:
        ansistrano.deploy: 3.8.0
  collections:
    description:
    - If I(requirements_file) is specified instead, returns dictionary with all the collections installed per path.
    - If I(name) is specified, returns that collection name and the version installed per path.
    type: dict
    returned: always when installing collections
    contains:
      "<path>":
        description: Collections and versions for that path
        type: dict
    sample:
      /home/az/.ansible/collections/ansible_collections:
        community.docker: 1.6.0
        community.general: 3.0.2
      /custom/ansible/ansible_collections:
        community.general: 3.1.0
"""

import re
import json

from ansible_collections.community.general.plugins.module_utils.module_helper import CmdModuleHelper, ArgFormat


class AnsibleGalaxyInstall(CmdModuleHelper):
    output_params = ('type', 'name', 'dest', 'requirements_file', 'force')
    module = dict(
        argument_spec=dict(
            type=dict(type='str', choices=('collection', 'role', 'both'), required=True),
            name=dict(type='str'),
            requirements_file=dict(type='path'),
            dest=dict(type='path'),
            force=dict(type='bool', default=False),
        ),
        mutually_exclusive=[('name', 'requirements_file')],
        required_one_of=[('name', 'requirements_file')],
        required_if=[('type', 'both', ['requirements_file'])],
        supports_check_mode=False,
    )

    command = 'ansible-galaxy'
    command_args_formats = dict(
        type=dict(fmt=lambda v: [] if v == 'both' else [v]),
        galaxy_cmd=dict(),
        requirements_file=dict(fmt=('-r', '{0}'),),
        dest=dict(fmt=('-p', '{0}'),),
        force=dict(fmt="--force", style=ArgFormat.BOOLEAN),
        format=dict(fmt=["--format", "json"], style=ArgFormat.BOOLEAN),
    )
    check_rc = True

    def __list_collections__(self):
        params = ({'type': 'collection'}, {'galaxy_cmd': 'list'}, 'dest', 'format')
        collections = self.run_command(params=params, process_output=lambda rc, out, err: out)
        collections = json.loads(collections)
        if self.vars.dest in collections:
            collections = {self.vars.det: collections[self.vars.dest]}

        if self.vars.name:
            for path in collections:
                c = {}
                if self.vars.name in collections[path]:
                    c[self.vars.name] = collections[path][self.vars.name]
                collections[path] = c

        for path in collections:
            collections[path] = dict((k, v['version']) for k, v in collections[path].items())
        return collections

    def __list_roles__(self):
        params = ({'type': 'role'}, {'galaxy_cmd': 'list'}, 'dest')
        roles = self.run_command(params=params, process_output=lambda rc, out, err: out)
        roles_dict = {}
        current_path = None

        re_rolepath = re.compile(r'^# (?P<path>.*)$')
        re_role = re.compile(r'^- (?P<role>\w+\.\w+), (?P<version>[\d\.]+)$')
        for line in roles.splitlines():
            if line.startswith("#"):
                match = re_rolepath.match(line)
                if not match:
                    continue
                if self.vars.dest and match.group('path') != self.vars.dest:
                    current_path = None
                    continue
                current_path = match.group('path') if match else None

            elif current_path is not None:
                match = re_role.match(line)
                if not match or (self.vars.name and match.group('role') != self.vars.name):
                    continue
                roles_dict[current_path][match.group('role')] = match.group('version')
        return roles_dict

    def __run__(self):
        self.vars.installed = {'collections': {}, 'roles': {}}
        if self.vars.type != "collection":
            self.vars.set("roles", self.__list_roles__(), change=True)
        if self.vars.type != "roles":
            self.vars.set("collections", self.__list_collections__(), change=True)
        params = ('type', {'galaxy_cmd': 'install'}, 'force', 'dest', 'requirements_file', 'name')
        self.run_command(params=params)
        if self.vars.type != "collection":
            self.vars.roles = self.__list_roles__()
        if self.vars.type != "roles":
            self.vars.collections = self.__list_collections__()

    def process_command_output(self, rc, out, err):
        re_patt = re.compile(r'^(?:(?P<collection>\w+\.\w+):(?P<cversion>[\d\.]+)'
                             r'|- (?P<role>\w+\.\w+) \((?P<rversion>[\d\.]+))'
                             r' was installed successfully$')
        self.vars.installed = {}
        for line in out.splitlines():
            match = re_patt.match(line)
            if not match:
                continue
            if match.group("collection"):
                self.vars.installed['collections'][match.group("collection")] = match.group("cversion")
            else:
                self.vars.installed['roles'][match.group("role")] = match.group("rversion")


def main():
    galaxy = AnsibleGalaxyInstall()
    galaxy.run()


if __name__ == '__main__':
    main()

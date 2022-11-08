#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Eric D Helms <ericdhelms@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: foreman
short_description: Manage Foreman Resources
deprecated:
    removed_in: 2.0.0  # was Ansible 2.12
    why: "Replaced by re-designed individual modules living at https://github.com/theforeman/foreman-ansible-modules"
    alternative: https://github.com/theforeman/foreman-ansible-modules
description:
    - Allows the management of Foreman resources inside your Foreman server.
author:
- Eric D Helms (@ehelms)
requirements:
    - nailgun >= 0.28.0
    - python >= 2.6
    - datetime
options:
    server_url:
        description:
            - URL of Foreman server.
        required: true
    username:
        description:
            - Username on Foreman server.
        required: true
    verify_ssl:
        description:
            - Whether to verify an SSL connection to Foreman server.
        type: bool
        default: False
    password:
        description:
            - Password for user accessing Foreman server.
        required: true
    entity:
        description:
            - The Foreman resource that the action will be performed on (e.g. organization, host).
        required: true
    params:
        description:
            - Parameters associated to the entity resource to set or edit in dictionary format (e.g. name, description).
        required: true
'''

EXAMPLES = '''
- name: Create CI Organization
  community.general.foreman:
    username: admin
    password: admin
    server_url: https://fakeserver.com
    entity: organization
    params:
      name: My Cool New Organization
  delegate_to: localhost
'''

RETURN = '''# '''

import traceback

try:
    from nailgun import entities
    from nailgun.config import ServerConfig
    HAS_NAILGUN_PACKAGE = True
except Exception:
    HAS_NAILGUN_PACKAGE = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native


class NailGun(object):
    def __init__(self, server, entities, module):
        self._server = server
        self._entities = entities
        self._module = module

    def find_organization(self, name, **params):
        org = self._entities.Organization(self._server, name=name, **params)
        response = org.search(set(), {'search': 'name={0}'.format(name)})

        if len(response) == 1:
            return response[0]

        return None

    def organization(self, params):
        name = params['name']
        del params['name']
        org = self.find_organization(name, **params)

        if org:
            org = self._entities.Organization(self._server, name=name, id=org.id, **params)
            org.update()
        else:
            org = self._entities.Organization(self._server, name=name, **params)
            org.create()

        return True


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(type='str', required=True),
            username=dict(type='str', required=True, no_log=True),
            password=dict(type='str', required=True, no_log=True),
            entity=dict(type='str', required=True),
            verify_ssl=dict(type='bool', default=False),
            params=dict(type='dict', required=True, no_log=True),
        ),
        supports_check_mode=True,
    )

    if not HAS_NAILGUN_PACKAGE:
        module.fail_json(msg="Missing required nailgun module (check docs or install with: pip install nailgun")

    server_url = module.params['server_url']
    username = module.params['username']
    password = module.params['password']
    entity = module.params['entity']
    params = module.params['params']
    verify_ssl = module.params['verify_ssl']

    server = ServerConfig(
        url=server_url,
        auth=(username, password),
        verify=verify_ssl
    )
    ng = NailGun(server, entities, module)

    # Lets make an connection to the server with username and password
    try:
        org = entities.Organization(server)
        org.search()
    except Exception as e:
        module.fail_json(msg="Failed to connect to Foreman server: %s " % to_native(e),
                         exception=traceback.format_exc())

    if entity == 'organization':
        ng.organization(params)
        module.exit_json(changed=True, result="%s updated" % entity)
    else:
        module.fail_json(changed=False, result="Unsupported entity supplied")


if __name__ == '__main__':
    main()

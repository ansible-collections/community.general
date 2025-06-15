#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023, Pedro Nascimento <apecnascimento@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: nomad_token
author: Pedro Nascimento (@apecnascimento)
version_added: "8.1.0"
short_description: Manage Nomad ACL tokens
description:
  - This module allows to create Bootstrap tokens, create ACL tokens, update ACL tokens, and delete ACL tokens.
requirements:
  - python-nomad
extends_documentation_fragment:
  - community.general.nomad
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  name:
    description:
      - Name of ACL token to create.
    type: str
  token_type:
    description:
      - The type of the token can be V(client), V(management), or V(bootstrap).
    choices: ["client", "management", "bootstrap"]
    type: str
    default: "client"
  policies:
    description:
      - A list of the policies assigned to the token.
    type: list
    elements: str
    default: []
  global_replicated:
    description:
      - Indicates whether or not the token was created with the C(--global).
    type: bool
    default: false
  state:
    description:
      - Create or remove ACL token.
    choices: ["present", "absent"]
    required: true
    type: str

seealso:
  - name: Nomad ACL documentation
    description: Complete documentation for Nomad API ACL.
    link: https://developer.hashicorp.com/nomad/api-docs/acl/tokens
"""

EXAMPLES = r"""
- name: Create boostrap token
  community.general.nomad_token:
    host: localhost
    token_type: bootstrap
    state: present

- name: Create ACL token
  community.general.nomad_token:
    host: localhost
    name: "Dev token"
    token_type: client
    policies:
      - readonly
    global_replicated: false
    state: absent

- name: Update ACL token Dev token
  community.general.nomad_token:
    host: localhost
    name: "Dev token"
    token_type: client
    policies:
      - readonly
      - devpolicy
    global_replicated: false
    state: absent

- name: Delete ACL token
  community.general.nomad_token:
    host: localhost
    name: "Dev token"
    state: absent
"""

RETURN = r"""
result:
  description: Result returned by nomad.
  returned: always
  type: dict
  sample:
    {
      "accessor_id": "0d01c55f-8d63-f832-04ff-1866d4eb594e",
      "create_index": 14,
      "create_time": "2023-11-12T18:48:34.248857001Z",
      "expiration_time": null,
      "expiration_ttl": "",
      "global": true,
      "hash": "eSn8H8RVqh8As8WQNnC2vlBRqXy6DECogc5umzX0P30=",
      "modify_index": 836,
      "name": "devs",
      "policies": [
        "readonly"
      ],
      "roles": null,
      "secret_id": "12e878ab-e1f6-e103-b4c4-3b5173bb4cea",
      "type": "client"
    }
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

import_nomad = None

try:
    import nomad

    import_nomad = True
except ImportError:
    import_nomad = False


def get_token(name, nomad_client):
    tokens = nomad_client.acl.get_tokens()
    token = next((token for token in tokens
                  if token.get('Name') == name), None)
    return token


def transform_response(nomad_response):
    transformed_response = {
        "accessor_id": nomad_response['AccessorID'],
        "create_index": nomad_response['CreateIndex'],
        "create_time": nomad_response['CreateTime'],
        "expiration_ttl": nomad_response['ExpirationTTL'],
        "expiration_time": nomad_response['ExpirationTime'],
        "global": nomad_response['Global'],
        "hash": nomad_response['Hash'],
        "modify_index": nomad_response['ModifyIndex'],
        "name": nomad_response['Name'],
        "policies": nomad_response['Policies'],
        "roles": nomad_response['Roles'],
        "secret_id": nomad_response['SecretID'],
        "type": nomad_response['Type']
    }

    return transformed_response


argument_spec = dict(
    host=dict(required=True, type='str'),
    port=dict(type='int', default=4646),
    state=dict(required=True, choices=['present', 'absent']),
    use_ssl=dict(type='bool', default=True),
    timeout=dict(type='int', default=5),
    validate_certs=dict(type='bool', default=True),
    client_cert=dict(type='path'),
    client_key=dict(type='path'),
    namespace=dict(type='str'),
    token=dict(type='str', no_log=True),
    name=dict(type='str'),
    token_type=dict(choices=['client', 'management', 'bootstrap'], default='client'),
    policies=dict(type='list', elements='str', default=[]),
    global_replicated=dict(type='bool', default=False),
)


def setup_module_object():
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_one_of=[
            ['name', 'token_type']
        ],
        required_if=[
            ('token_type', 'client', ('name',)),
            ('token_type', 'management', ('name',)),
        ],
    )
    return module


def setup_nomad_client(module):
    if not import_nomad:
        module.fail_json(msg=missing_required_lib("python-nomad"))

    certificate_ssl = (module.params.get('client_cert'), module.params.get('client_key'))

    nomad_client = nomad.Nomad(
        host=module.params.get('host'),
        port=module.params.get('port'),
        secure=module.params.get('use_ssl'),
        timeout=module.params.get('timeout'),
        verify=module.params.get('validate_certs'),
        cert=certificate_ssl,
        namespace=module.params.get('namespace'),
        token=module.params.get('token')
    )

    return nomad_client


def run(module):
    nomad_client = setup_nomad_client(module)

    msg = ""
    result = {}
    changed = False
    if module.params.get('state') == "present":

        if module.params.get('token_type') == 'bootstrap':
            try:
                current_token = get_token('Bootstrap Token', nomad_client)
                if current_token:
                    msg = "ACL bootstrap already exist."
                else:
                    nomad_result = nomad_client.acl.generate_bootstrap()
                    msg = "Boostrap token created."
                    result = transform_response(nomad_result)
                    changed = True

            except nomad.api.exceptions.URLNotAuthorizedNomadException:
                try:
                    nomad_result = nomad_client.acl.generate_bootstrap()
                    msg = "Boostrap token created."
                    result = transform_response(nomad_result)
                    changed = True

                except Exception as e:
                    module.fail_json(msg=to_native(e))
        else:
            try:
                token_info = {
                    "Name": module.params.get('name'),
                    "Type": module.params.get('token_type'),
                    "Policies": module.params.get('policies'),
                    "Global": module.params.get('global_replicated')
                }

                current_token = get_token(token_info['Name'], nomad_client)

                if current_token:
                    token_info['AccessorID'] = current_token['AccessorID']
                    nomad_result = nomad_client.acl.update_token(current_token['AccessorID'], token_info)
                    msg = "ACL token updated."
                    result = transform_response(nomad_result)
                    changed = True

                else:
                    nomad_result = nomad_client.acl.create_token(token_info)
                    msg = "ACL token Created."
                    result = transform_response(nomad_result)
                    changed = True

            except Exception as e:
                module.fail_json(msg=to_native(e))

    if module.params.get('state') == "absent":

        if not module.params.get('name'):
            module.fail_json(msg="name is needed to delete token.")

        if module.params.get('token_type') == 'bootstrap' or module.params.get('name') == 'Bootstrap Token':
            module.fail_json(msg="Delete ACL bootstrap token is not allowed.")

        try:
            token = get_token(module.params.get('name'), nomad_client)
            if token:
                nomad_client.acl.delete_token(token.get('AccessorID'))
                msg = 'ACL token deleted.'
                changed = True
            else:
                msg = "No token with name '{0}' found".format(module.params.get('name'))

        except Exception as e:
            module.fail_json(msg=to_native(e))

    module.exit_json(changed=changed, msg=msg, result=result)


def main():
    module = setup_module_object()
    run(module)


if __name__ == "__main__":
    main()

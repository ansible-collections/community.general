#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, FERREIRA Christophe <christophe.ferreira@cnaf.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


import_nomad = None


try:
    import nomad
    import_nomad = True
except ImportError:
    import_nomad = False


DOCUMENTATION = '''
---
module: nomad_acl
author: Pedro Nascimento(@apecnascimento)
version_added: "1.0.0"
short_description: Manage Nomad ACL tokens
description:
  - Create Bootstrap token
  - Create ACL token.
  - Update ACL token.
  - Delete ACL token
requirements:
  - python-nomad
extends_documentation_fragment:
  - community.general.nomad
  - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    name:
      description:
        - Name of acl token to create.
      type: str
    token_type:
      description:
        - The type of the token can be "client", "management" or bootstrap.
      choices: ["client", "management", "bootstrap"]
      type: str
      default: "client"
    policies:
      description:
        - A list of the policies assigned to the token.
      type: list
      default: []
    global_token:
      description:
        - indicates whether or not the token was created with the --global.
      type: bool
      default: false
    state:
      description:
        - Create or remove acl token.
      choices: ["present", "absent"]
      required: true
      type: str

seealso:
  - name: Nomad acl documentation
    description: Complete documentation for Nomad API acl.
    link: https://developer.hashicorp.com/nomad/api-docs/acl
'''

EXAMPLES = '''
- name: Create boostrap token
  community.general.nomad_acl:
    host: localhost
    token_type: bootstrap
    state: present

- name: Create acl token
  community.general.nomad_acl:
    host: localhost
    name: "Dev token"
    token_type: client
    policies:
    - readonly
    global_token: false
    state: absent

- name: "Update acl token Dev token""
  community.general.nomad_acl:
    host: localhost
    name: "Dev token"
    token_type: client
    policies: 
    - readonly
    - devpolicy
    global_token: false
    state: absent

- name: Delete acl token
  community.general.nomad_acl:
    host: localhost
    name: "Dev token"
    state: absent

'''

RETURN = '''
msg:
  description: friendly result message
  type: str
  sample: "ACL bootstrap already exist."
result:
  token:
  description: Acl token object
  type: dict
  sample: "ACL bootstrap already exist."
  contains:
    accessor_id:
      description: token accessor ID.
      type: str
    create_index:
      description: token create index.
      type: int
    create_time:
      description: token createtion time.
      type: str
    expiration_ttl:
      description: token expiration ttl.
      type: str
    expiration_time:
      description: token expiration time.
      type: str
    global:
      description: Global token identifier.
      type: bool
    hash:
      description: Token hash.
      type: str
    modify_index:
      description: Token modify index.
      type: int
    name:
      description: Token name.
      type: str
    policies:
      description: Token policies list.
      type: list
      elements: str
    roles:
      description: Token roles list.
      type: list
      elements: str
    secret_id:
      description: Token secret ID.
      type: str
    type:
      description: Token type
      type: str
'''


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


def run():

    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True, type='str'),
            port=dict(type='int', default=4646),
            state=dict(required=True, choices=['present', 'absent']),
            use_ssl=dict(type='bool', default=False),
            timeout=dict(type='int', default=5),
            validate_certs=dict(type='bool', default=False),
            client_cert=dict(type='path'),
            client_key=dict(type='path'),
            token=dict(type='str', no_log=True),
            name=dict(type='str'),
            token_type=dict(choices=['client', 'management', 'bootstrap'], default='client'),
            policies=dict(type=list, default=[]),
            global_token=dict(type=bool, default=False),
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ["name"]
        ],
        required_one_of=[
            ['name', 'token_type']
        ]
    )

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

    changed = False
    result = {}
    if module.params.get('state') == "present":

        if module.params.get('token_type') == 'bootstrap':
            try:
                current_token = get_token('Bootstrap Token', nomad_client)
                if current_token:
                    result = {"msg": "ACL bootstrap already exist.", "token": {}}

            except nomad.api.exceptions.URLNotAuthorizedNomadException:
                try:
                    nomad_result = nomad_client.acl.generate_bootstrap()
                    result = {'msg': "Boostrap token created.",
                              "token": transform_response(nomad_result)}
                    changed = True
                except Exception as e:
                    module.fail_json(msg=to_native(e))
        else:
            try:
                token_info = {
                  "Name": module.params.get('name'),
                  "Type": module.params.get('token_type'),
                  "Policies": module.params.get('policies'),
                  "Global": module.params.get('global_token')
                }

                current_token = get_token(token_info['Name'], nomad_client)

                if  current_token:
                    token_info['AccessorID'] = current_token['AccessorID']
                    nomad_result = nomad_client.acl.update_token(current_token['AccessorID'],
                                                                 token_info)
                    result = {"msg": "Acl token updated.",
                              "token": transform_response(nomad_result)}

                else:
                    nomad_result = nomad_client.acl.create_token(token_info)
                    result = {"msg": "Acl token Created.",
                              "token": transform_response(nomad_result)}
                    changed = True
            except Exception as e:
                module.fail_json(msg=to_native(e))

    if module.params.get('state') == "absent":
        if module.params.get('token_type') == 'bootstrap':
            module.fail_json(msg="Delete ACL bootstrap token is not allowed.")

        if not module.params.get('name'):
            module.fail_json(msg="name is needed to delete token.")

        try:
            token = get_token(module.params.get('name'), nomad_client)
            if token:
                nomad_client.acl.delete_token(token.get('AccessorID'))
                result = {'msg': "Acl token deleted.', ", token: {}}
                changed = True
            else:
                result = {'msg': f"Not found token with name '{module.params.get('name')}'",
                          token: {}}

        except Exception as e:
            module.fail_json(msg=to_native(e))

    module.exit_json(changed=changed, result=result)


def main():
    run()


if __name__ == "__main__":
    main()

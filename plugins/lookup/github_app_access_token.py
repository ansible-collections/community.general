# -*- coding: utf-8 -*-
# Copyright (c) 2023, Poh Wei Sheng <weisheng-p@hotmail.sg>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: github_app_access_token
    author:
      - Poh Wei Sheng (@weisheng-p)
    short_description: Obtain short-lived Github App Access tokens
    version_added: '8.2.0'
    requirements:
      - jwt (https://github.com/GehirnInc/python-jwt)
    description:
      - This generates a Github access token that can be used with a C(git) command, if you use a Github App.
    options:
      key_path:
        description:
        - Path to your private key.
        required: true
        type: path
      app_id:
        description:
        - Your GitHub App ID, you can find this in the Settings page.
        required: true
        type: str
      installation_id:
        description:
        - The installation ID that contains the git repository you would like access to.
        - As of 2023-12-24, this can be found via Settings page > Integrations > Application. The last part of the URL in the
          configure button is the installation ID.
        - Alternatively, you can use PyGithub (U(https://github.com/PyGithub/PyGithub)) to get your installation ID.
        required: true
        type: str
      token_expiry:
        description:
        - How long the token should last for in seconds.
        default: 600
        type: int
'''

EXAMPLES = '''
- name: Get access token to be used for git checkout with app_id=123456, installation_id=64209
  ansible.builtin.git:
    repo: >-
      https://x-access-token:{{ github_token }}@github.com/hidden_user/super-secret-repo.git
    dest: /srv/checkout
  vars:
    github_token: >-
      lookup('community.general.github_app_access_token', key_path='/home/to_your/key',
             app_id='123456', installation_id='64209')
'''

RETURN = '''
  _raw:
    description: A one-element list containing your GitHub access token.
    type: list
    elements: str
'''


try:
    from jwt import JWT, jwk_from_pem
    HAS_JWT = True
except ImportError:
    HAS_JWT = False

import time
import json
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

if HAS_JWT:
    jwt_instance = JWT()
else:
    jwk_from_pem = None
    jwt_instance = None

display = Display()


def read_key(path):
    try:
        with open(path, 'rb') as pem_file:
            return jwk_from_pem(pem_file.read())
    except Exception as e:
        raise AnsibleError("Error while parsing key file: {0}".format(e))


def encode_jwt(app_id, jwk, exp=600):
    now = int(time.time())
    payload = {
        'iat': now,
        'exp': now + exp,
        'iss': app_id,
    }
    try:
        return jwt_instance.encode(payload, jwk, alg='RS256')
    except Exception as e:
        raise AnsibleError("Error while encoding jwt: {0}".format(e))


def post_request(generated_jwt, installation_id):
    github_api_url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
    headers = {
        "Authorization": f'Bearer {generated_jwt}',
        "Accept": "application/vnd.github.v3+json",
    }
    try:
        response = open_url(github_api_url, headers=headers, method='POST')
    except HTTPError as e:
        try:
            error_body = json.loads(e.read().decode())
            display.vvv("Error returned: {0}".format(error_body))
        except Exception:
            error_body = {}
        if e.code == 404:
            raise AnsibleError("Github return error. Please confirm your installationd_id value is valid")
        elif e.code == 401:
            raise AnsibleError("Github return error. Please confirm your private key is valid")
        raise AnsibleError("Unexpected data returned: {0} -- {1}".format(e, error_body))
    response_body = response.read()
    try:
        json_data = json.loads(response_body.decode('utf-8'))
    except json.decoder.JSONDecodeError as e:
        raise AnsibleError("Error while dencoding JSON respone from github: {0}".format(e))
    return json_data.get('token')


def get_token(key_path, app_id, installation_id, expiry=600):
    jwk = read_key(key_path)
    generated_jwt = encode_jwt(app_id, jwk, exp=expiry)
    return post_request(generated_jwt, installation_id)


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        if not HAS_JWT:
            raise AnsibleError('Python jwt library is required. '
                               'Please install using "pip install jwt"')

        self.set_options(var_options=variables, direct=kwargs)

        t = get_token(
            self.get_option('key_path'),
            self.get_option('app_id'),
            self.get_option('installation_id'),
            self.get_option('token_expiry'),
        )

        return [t]

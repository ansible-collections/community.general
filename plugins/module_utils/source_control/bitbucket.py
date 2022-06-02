# -*- coding: utf-8 -*-

# Simplified BSD License (see simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.urls import fetch_url, basic_auth_header


class BitbucketHelper:
    BITBUCKET_API_URL = 'https://api.bitbucket.org'

    def __init__(self, module):
        self.module = module
        self.access_token = None

    @staticmethod
    def bitbucket_argument_spec():
        return dict(
            client_id=dict(type='str', fallback=(env_fallback, ['BITBUCKET_CLIENT_ID'])),
            client_secret=dict(type='str', no_log=True, fallback=(env_fallback, ['BITBUCKET_CLIENT_SECRET'])),
            # TODO:
            # - Rename user to username once current usage of username is removed
            # - Alias user to username and deprecate it
            user=dict(type='str', fallback=(env_fallback, ['BITBUCKET_USERNAME'])),
            password=dict(type='str', no_log=True, fallback=(env_fallback, ['BITBUCKET_PASSWORD'])),
        )

    @staticmethod
    def bitbucket_required_one_of():
        return [['client_id', 'client_secret', 'user', 'password']]

    @staticmethod
    def bitbucket_required_together():
        return [['client_id', 'client_secret'], ['user', 'password']]

    def fetch_access_token(self):
        if self.module.params['client_id'] and self.module.params['client_secret']:
            headers = {
                'Authorization': basic_auth_header(self.module.params['client_id'], self.module.params['client_secret']),
            }

            info, content = self.request(
                api_url='https://bitbucket.org/site/oauth2/access_token',
                method='POST',
                data='grant_type=client_credentials',
                headers=headers,
            )

            if info['status'] == 200:
                self.access_token = content['access_token']
            else:
                self.module.fail_json(msg='Failed to retrieve access token: {0}'.format(info))

    def request(self, api_url, method, data=None, headers=None):
        headers = headers or {}

        if self.access_token:
            headers.update({
                'Authorization': 'Bearer {0}'.format(self.access_token),
            })
        elif self.module.params['user'] and self.module.params['password']:
            headers.update({
                'Authorization': basic_auth_header(self.module.params['user'], self.module.params['password']),
            })

        if isinstance(data, dict):
            data = self.module.jsonify(data)
            headers.update({
                'Content-type': 'application/json',
            })

        response, info = fetch_url(
            module=self.module,
            url=api_url,
            method=method,
            headers=headers,
            data=data,
            force=True,
        )

        content = {}

        if response is not None:
            body = to_text(response.read())
            if body:
                content = json.loads(body)

        return info, content

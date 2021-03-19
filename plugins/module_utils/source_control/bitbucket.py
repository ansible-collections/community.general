# -*- coding: utf-8 -*-

# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.urls import fetch_url, basic_auth_header


class BitbucketHelper:
    BITBUCKET_API_URL = 'https://api.bitbucket.org'

    error_messages = {
        'credentials_required': '`client_id`/`client_secret` or `username`/`password` must be specified as a parameter',
    }

    def __init__(self, module):
        self.module = module
        self.access_token = None
        self.username = None
        self.password = None

    @staticmethod
    def bitbucket_argument_spec():
        return dict(
            client_id=dict(type='str', no_log=False, fallback=(env_fallback, ['BITBUCKET_CLIENT_ID'])),
            client_secret=dict(type='str', no_log=True, fallback=(env_fallback, ['BITBUCKET_CLIENT_SECRET'])),
            username=dict(type='str', no_log=False, fallback=(env_fallback, ['BITBUCKET_USERNAME'])),
            password=dict(type='str', no_log=True, fallback=(env_fallback, ['BITBUCKET_PASSWORD'])),
        )

    def check_arguments(self):
        if self.module.params['client_id'] is None and self.module.params['client_secret'] is None or \
           self.module.params['username'] is None and self.module.params['password'] is None:
            self.module.fail_json(msg=self.error_messages['required_client_id'])

    def fetch_access_token(self):
        self.check_arguments()

        if 'client_id' in self.module.params and 'client_secret' in self.module.params:
            headers = {
                'Authorization': basic_auth_header(self.module.params['client_id'], self.module.params['client_secret'])
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
        elif self.username and self.password:
            headers.update({
                'Authorization': basic_auth_header(self.username, self.password)
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

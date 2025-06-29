# -*- coding: utf-8 -*-
# Copyright (c) 2015, Ensighten <infra@ensighten.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
author: Unknown (!UNKNOWN)
name: credstash
short_description: Retrieve secrets from Credstash on AWS
requirements:
  - credstash (python library)
description:
  - "Credstash is a small utility for managing secrets using AWS's KMS and DynamoDB: https://github.com/fugue/credstash."
options:
  _terms:
    description: Term or list of terms to lookup in the credit store.
    type: list
    elements: string
    required: true
  table:
    description: Name of the credstash table to query.
    type: str
    default: 'credential-store'
  version:
    description: Credstash version.
    type: str
    default: ''
  region:
    description: AWS region.
    type: str
  profile_name:
    description: AWS profile to use for authentication.
    type: str
    env:
      - name: AWS_PROFILE
  aws_access_key_id:
    description: AWS access key ID.
    type: str
    env:
      - name: AWS_ACCESS_KEY_ID
  aws_secret_access_key:
    description: AWS access key.
    type: str
    env:
      - name: AWS_SECRET_ACCESS_KEY
  aws_session_token:
    description: AWS session token.
    type: str
    env:
      - name: AWS_SESSION_TOKEN
"""

EXAMPLES = r"""
- name: first use credstash to store your secrets
  ansible.builtin.shell: credstash put my-github-password secure123

- name: "Test credstash lookup plugin -- get my github password"
  ansible.builtin.debug:
    msg: "Credstash lookup! {{ lookup('community.general.credstash', 'my-github-password') }}"

- name: "Test credstash lookup plugin -- get my other password from us-west-1"
  ansible.builtin.debug:
    msg: "Credstash lookup! {{ lookup('community.general.credstash', 'my-other-password', region='us-west-1') }}"

- name: "Test credstash lookup plugin -- get the company's github password"
  ansible.builtin.debug:
    msg: "Credstash lookup! {{ lookup('community.general.credstash', 'company-github-password', table='company-passwords') }}"

- name: Example play using the 'context' feature
  hosts: localhost
  vars:
    context:
      app: my_app
      environment: production
  tasks:

    - name: "Test credstash lookup plugin -- get the password with a context passed as a variable"
      ansible.builtin.debug:
        msg: "{{ lookup('community.general.credstash', 'some-password', context=context) }}"

    - name: "Test credstash lookup plugin -- get the password with a context defined here"
      ansible.builtin.debug:
        msg: "{{ lookup('community.general.credstash', 'some-password', context=dict(app='my_app', environment='production')) }}"
"""

RETURN = r"""
_raw:
  description:
    - Value(s) stored in Credstash.
  type: str
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase

CREDSTASH_INSTALLED = False

try:
    import credstash
    CREDSTASH_INSTALLED = True
except ImportError:
    CREDSTASH_INSTALLED = False


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        if not CREDSTASH_INSTALLED:
            raise AnsibleError('The credstash lookup plugin requires credstash to be installed.')

        self.set_options(var_options=variables, direct=kwargs)

        version = self.get_option('version')
        region = self.get_option('region')
        table = self.get_option('table')
        profile_name = self.get_option('profile_name')
        aws_access_key_id = self.get_option('aws_access_key_id')
        aws_secret_access_key = self.get_option('aws_secret_access_key')
        aws_session_token = self.get_option('aws_session_token')

        context = {
            k: v for k, v in kwargs.items()
            if k not in ('version', 'region', 'table', 'profile_name', 'aws_access_key_id', 'aws_secret_access_key', 'aws_session_token')
        }

        kwargs_pass = {
            'profile_name': profile_name,
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            'aws_session_token': aws_session_token,
        }

        ret = []
        for term in terms:
            try:
                ret.append(credstash.getSecret(term, version, region, table, context=context, **kwargs_pass))
            except credstash.ItemNotFound:
                raise AnsibleError(f'Key {term} not found')
            except Exception as e:
                raise AnsibleError(f'Encountered exception while fetching {term}: {e}')

        return ret

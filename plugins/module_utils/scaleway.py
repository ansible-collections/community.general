# -*- coding: utf-8 -*-
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import re
import sys
import datetime
import time
import traceback

from ansible.module_utils.basic import env_fallback, missing_required_lib
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six.moves.urllib.parse import urlencode

SCALEWAY_SECRET_IMP_ERR = None
try:
    from passlib.hash import argon2
    HAS_SCALEWAY_SECRET_PACKAGE = True
except Exception:
    argon2 = None
    SCALEWAY_SECRET_IMP_ERR = traceback.format_exc()
    HAS_SCALEWAY_SECRET_PACKAGE = False


def scaleway_argument_spec():
    return dict(
        api_token=dict(required=True, fallback=(env_fallback, ['SCW_TOKEN', 'SCW_API_KEY', 'SCW_OAUTH_TOKEN', 'SCW_API_TOKEN']),
                       no_log=True, aliases=['oauth_token']),
        api_url=dict(fallback=(env_fallback, ['SCW_API_URL']), default='https://api.scaleway.com', aliases=['base_url']),
        api_timeout=dict(type='int', default=30, aliases=['timeout']),
        query_parameters=dict(type='dict', default={}),
        validate_certs=dict(default=True, type='bool'),
    )


def scaleway_waitable_resource_argument_spec():
    return dict(
        wait=dict(type="bool", default=True),
        wait_timeout=dict(type="int", default=300),
        wait_sleep_time=dict(type="int", default=3),
    )


def payload_from_object(scw_object):
    return dict(
        (k, v)
        for k, v in scw_object.items()
        if k != 'id' and v is not None
    )


class ScalewayException(Exception):

    def __init__(self, message):
        self.message = message


# Specify a complete Link header, for validation purposes
R_LINK_HEADER = r'''<[^>]+>;\srel="(first|previous|next|last)"
    (,<[^>]+>;\srel="(first|previous|next|last)")*'''
# Specify a single relation, for iteration and string extraction purposes
R_RELATION = r'</?(?P<target_IRI>[^>]+)>; rel="(?P<relation>first|previous|next|last)"'


def parse_pagination_link(header):
    if not re.match(R_LINK_HEADER, header, re.VERBOSE):
        raise ScalewayException('Scaleway API answered with an invalid Link pagination header')
    else:
        relations = header.split(',')
        parsed_relations = {}
        rc_relation = re.compile(R_RELATION)
        for relation in relations:
            match = rc_relation.match(relation)
            if not match:
                raise ScalewayException('Scaleway API answered with an invalid relation in the Link pagination header')
            data = match.groupdict()
            parsed_relations[data['relation']] = data['target_IRI']
        return parsed_relations


def filter_sensitive_attributes(container, attributes):
    '''
    WARNING: This function is effectively private, **do not use it**!
    It will be removed or renamed once changing its name no longer triggers a pylint bug.
    '''
    for attr in attributes:
        container[attr] = "SENSITIVE_VALUE"

    return container


class SecretVariables(object):
    @staticmethod
    def ensure_scaleway_secret_package(module):
        if not HAS_SCALEWAY_SECRET_PACKAGE:
            module.fail_json(
                msg=missing_required_lib("passlib[argon2]", url='https://passlib.readthedocs.io/en/stable/'),
                exception=SCALEWAY_SECRET_IMP_ERR
            )

    @staticmethod
    def dict_to_list(source_dict):
        return [
            dict(key=var[0], value=var[1])
            for var in source_dict.items()
        ]

    @staticmethod
    def list_to_dict(source_list, hashed=False):
        key_value = 'hashed_value' if hashed else 'value'
        return dict(
            (var['key'], var[key_value])
            for var in source_list
        )

    @classmethod
    def decode(cls, secrets_list, values_list):
        secrets_dict = cls.list_to_dict(secrets_list, hashed=True)
        values_dict = cls.list_to_dict(values_list, hashed=False)
        for key in values_dict:
            if key in secrets_dict:
                if argon2.verify(values_dict[key], secrets_dict[key]):
                    secrets_dict[key] = values_dict[key]
                else:
                    secrets_dict[key] = secrets_dict[key]

        return cls.dict_to_list(secrets_dict)


def resource_attributes_should_be_changed(target, wished, verifiable_mutable_attributes, mutable_attributes):
    diff = dict()
    for attr in verifiable_mutable_attributes:
        if wished[attr] is not None and target[attr] != wished[attr]:
            diff[attr] = wished[attr]

    if diff:
        return dict((attr, wished[attr]) for attr in mutable_attributes)
    else:
        return diff


class Response(object):

    def __init__(self, resp, info):
        self.body = None
        if resp:
            self.body = resp.read()
        self.info = info

    @property
    def json(self):
        if not self.body:
            if "body" in self.info:
                return json.loads(self.info["body"])
            return None
        try:
            return json.loads(self.body)
        except ValueError:
            return None

    @property
    def status_code(self):
        return self.info["status"]

    @property
    def ok(self):
        return self.status_code in (200, 201, 202, 204)


class Scaleway(object):

    def __init__(self, module):
        self.module = module
        self.headers = {
            'X-Auth-Token': self.module.params.get('api_token'),
            'User-Agent': self.get_user_agent_string(module),
            'Content-Type': 'application/json',
        }
        self.name = None

    def get_resources(self):
        results = self.get('/%s' % self.name)

        if not results.ok:
            raise ScalewayException('Error fetching {0} ({1}) [{2}: {3}]'.format(
                self.name, '%s/%s' % (self.module.params.get('api_url'), self.name),
                results.status_code, results.json['message']
            ))

        return results.json.get(self.name)

    def _url_builder(self, path, params):
        d = self.module.params.get('query_parameters')
        if params is not None:
            d.update(params)
        query_string = urlencode(d, doseq=True)

        if path[0] == '/':
            path = path[1:]
        return '%s/%s?%s' % (self.module.params.get('api_url'), path, query_string)

    def send(self, method, path, data=None, headers=None, params=None):
        url = self._url_builder(path=path, params=params)
        self.warn(url)

        if headers is not None:
            self.headers.update(headers)

        if self.headers['Content-Type'] == "application/json":
            data = self.module.jsonify(data)

        resp, info = fetch_url(
            self.module, url, data=data, headers=self.headers, method=method,
            timeout=self.module.params.get('api_timeout')
        )

        # Exceptions in fetch_url may result in a status -1, the ensures a proper error to the user in all cases
        if info['status'] == -1:
            self.module.fail_json(msg=info['msg'])

        return Response(resp, info)

    @staticmethod
    def get_user_agent_string(module):
        return "ansible %s Python %s" % (module.ansible_version, sys.version.split(' ', 1)[0])

    def get(self, path, data=None, headers=None, params=None):
        return self.send(method='GET', path=path, data=data, headers=headers, params=params)

    def put(self, path, data=None, headers=None, params=None):
        return self.send(method='PUT', path=path, data=data, headers=headers, params=params)

    def post(self, path, data=None, headers=None, params=None):
        return self.send(method='POST', path=path, data=data, headers=headers, params=params)

    def delete(self, path, data=None, headers=None, params=None):
        return self.send(method='DELETE', path=path, data=data, headers=headers, params=params)

    def patch(self, path, data=None, headers=None, params=None):
        return self.send(method="PATCH", path=path, data=data, headers=headers, params=params)

    def update(self, path, data=None, headers=None, params=None):
        return self.send(method="UPDATE", path=path, data=data, headers=headers, params=params)

    def warn(self, x):
        self.module.warn(str(x))

    def fetch_state(self, resource):
        self.module.debug("fetch_state of resource: %s" % resource["id"])
        response = self.get(path=self.api_path + "/%s" % resource["id"])

        if response.status_code == 404:
            return "absent"

        if not response.ok:
            msg = 'Error during state fetching: (%s) %s' % (response.status_code, response.json)
            self.module.fail_json(msg=msg)

        try:
            self.module.debug("Resource %s in state: %s" % (resource["id"], response.json["status"]))
            return response.json["status"]
        except KeyError:
            self.module.fail_json(msg="Could not fetch state in %s" % response.json)

    def fetch_paginated_resources(self, resource_key, **pagination_kwargs):
        response = self.get(
            path=self.api_path,
            params=pagination_kwargs)

        status_code = response.status_code
        if not response.ok:
            self.module.fail_json(msg='Error getting {0} [{1}: {2}]'.format(
                resource_key,
                response.status_code, response.json['message']))

        return response.json[resource_key]

    def fetch_all_resources(self, resource_key, **pagination_kwargs):
        resources = []

        result = [None]
        while len(result) != 0:
            result = self.fetch_paginated_resources(resource_key, **pagination_kwargs)
            resources += result
            if 'page' in pagination_kwargs:
                pagination_kwargs['page'] += 1
            else:
                pagination_kwargs['page'] = 2

        return resources

    def wait_to_complete_state_transition(self, resource, stable_states, force_wait=False):
        wait = self.module.params["wait"]

        if not (wait or force_wait):
            return

        wait_timeout = self.module.params["wait_timeout"]
        wait_sleep_time = self.module.params["wait_sleep_time"]

        # Prevent requesting the resource status too soon
        time.sleep(wait_sleep_time)

        start = datetime.datetime.utcnow()
        end = start + datetime.timedelta(seconds=wait_timeout)

        while datetime.datetime.utcnow() < end:
            self.module.debug("We are going to wait for the resource to finish its transition")

            state = self.fetch_state(resource)
            if state in stable_states:
                self.module.debug("It seems that the resource is not in transition anymore.")
                self.module.debug("load-balancer in state: %s" % self.fetch_state(resource))
                break

            time.sleep(wait_sleep_time)
        else:
            self.module.fail_json(msg="Server takes too long to finish its transition")


SCALEWAY_LOCATION = {
    'par1': {
        'name': 'Paris 1',
        'country': 'FR',
        'api_endpoint': 'https://api.scaleway.com/instance/v1/zones/fr-par-1',
        'api_endpoint_vpc': 'https://api.scaleway.com/vpc/v1/zones/fr-par-1'
    },

    'EMEA-FR-PAR1': {
        'name': 'Paris 1',
        'country': 'FR',
        'api_endpoint': 'https://api.scaleway.com/instance/v1/zones/fr-par-1',
        'api_endpoint_vpc': 'https://api.scaleway.com/vpc/v1/zones/fr-par-1'
    },

    'par2': {
        'name': 'Paris 2',
        'country': 'FR',
        'api_endpoint': 'https://api.scaleway.com/instance/v1/zones/fr-par-2',
        'api_endpoint_vpc': 'https://api.scaleway.com/vpc/v1/zones/fr-par-2'
    },

    'EMEA-FR-PAR2': {
        'name': 'Paris 2',
        'country': 'FR',
        'api_endpoint': 'https://api.scaleway.com/instance/v1/zones/fr-par-2',
        'api_endpoint_vpc': 'https://api.scaleway.com/vpc/v1/zones/fr-par-2'
    },

    'ams1': {
        'name': 'Amsterdam 1',
        'country': 'NL',
        'api_endpoint': 'https://api.scaleway.com/instance/v1/zones/nl-ams-1',
        'api_endpoint_vpc': 'https://api.scaleway.com/vpc/v1/zones/nl-ams-10'
    },

    'EMEA-NL-EVS': {
        'name': 'Amsterdam 1',
        'country': 'NL',
        'api_endpoint': 'https://api.scaleway.com/instance/v1/zones/nl-ams-1',
        'api_endpoint_vpc': 'https://api.scaleway.com/vpc/v1/zones/nl-ams-1'
    },

    'waw1': {
        'name': 'Warsaw 1',
        'country': 'PL',
        'api_endpoint': 'https://api.scaleway.com/instance/v1/zones/pl-waw-1',
        'api_endpoint_vpc': 'https://api.scaleway.com/vpc/v1/zones/pl-waw-1'
    },

    'EMEA-PL-WAW1': {
        'name': 'Warsaw 1',
        'country': 'PL',
        'api_endpoint': 'https://api.scaleway.com/instance/v1/zones/pl-waw-1',
        'api_endpoint_vpc': 'https://api.scaleway.com/vpc/v1/zones/pl-waw-1'
    },
}

SCALEWAY_ENDPOINT = "https://api.scaleway.com"

SCALEWAY_REGIONS = [
    "fr-par",
    "nl-ams",
    "pl-waw",
]

SCALEWAY_ZONES = [
    "fr-par-1",
    "fr-par-2",
    "nl-ams-1",
    "pl-waw-1",
]

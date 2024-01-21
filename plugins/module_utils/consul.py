# -*- coding: utf-8 -*-

# Copyright (c) 2022, Håkon Lerring
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json

from ansible.module_utils.six.moves.urllib import error as urllib_error
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import open_url


def get_consul_url(configuration):
    return '%s://%s:%s/v1' % (configuration.scheme,
                              configuration.host, configuration.port)


def get_auth_headers(configuration):
    if configuration.token is None:
        return {}
    else:
        return {'X-Consul-Token': configuration.token}


class RequestError(Exception):
    pass


def handle_consul_response_error(response):
    if 400 <= response.status_code < 600:
        raise RequestError('%d %s' % (response.status_code, response.content))


def auth_argument_spec():
    return dict(
        host=dict(default="localhost"),
        port=dict(type="int", default=8500),
        scheme=dict(default="http"),
        validate_certs=dict(type="bool", default=True),
        token=dict(no_log=True),
        ca_path=dict(),
    )


class _ConsulModule:
    """Base class for Consul modules.

    This class is considered private, till the API is fully fleshed out.
    As such backwards incompatible changes can occur even in bugfix releases.
    """

    def __init__(self, module):
        self.module = module

    def _request(self, method, url_parts, data=None, params=None):
        module_params = self.module.params

        if isinstance(url_parts, str):
            url_parts = [url_parts]
        if params:
            # Remove values that are None
            params = {k: v for k, v in params.items() if v is not None}

        ca_path = module_params.get("ca_path")
        base_url = "%s://%s:%s/v1" % (
            module_params["scheme"],
            module_params["host"],
            module_params["port"],
        )
        url = "/".join([base_url] + list(url_parts))

        headers = {}
        token = self.module.params.get("token")
        if token:
            headers["X-Consul-Token"] = token

        try:
            if data:
                data = json.dumps(data)
                headers["Content-Type"] = "application/json"
            if params:
                url = "%s?%s" % (url, urlencode(params))
            response = open_url(
                url,
                method=method,
                data=data,
                headers=headers,
                validate_certs=module_params["validate_certs"],
                ca_path=ca_path,
            )
            response_data = response.read()
        except urllib_error.URLError as e:
            self.module.fail_json(
                msg="Could not connect to consul agent at %s:%s, error was %s"
                % (module_params["host"], module_params["port"], str(e))
            )
        else:
            status = (
                response.status if hasattr(response, "status") else response.getcode()
            )
            if 400 <= status < 600:
                raise RequestError("%d %s" % (status, response_data))

            return json.loads(response_data)

    def get(self, url_parts, **kwargs):
        return self._request("GET", url_parts, **kwargs)

    def put(self, url_parts, **kwargs):
        return self._request("PUT", url_parts, **kwargs)

    def delete(self, url_parts, **kwargs):
        return self._request("DELETE", url_parts, **kwargs)

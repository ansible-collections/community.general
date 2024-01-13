# -*- coding: utf-8 -*-

# Copyright (c) 2022, Håkon Lerring
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

import traceback

from ansible.module_utils.basic import missing_required_lib

__metaclass__ = type


REQUESTS_IMP_ERR = None
try:
    import requests
    from requests.exceptions import ConnectionError

    HAS_REQUESTS = True
except ImportError:
    requests = ConnectionError = None

    HAS_REQUESTS = False
    REQUESTS_IMP_ERR = traceback.format_exc()


class RequestError(Exception):
    pass


def auth_argument_spec():
    return dict(
        host=dict(default="localhost"),
        port=dict(type="int", default=8500),
        scheme=dict(choices=["http", "https"], default="http"),
        validate_certs=dict(type="bool", default=True),
        token=dict(no_log=True),
    )


class ConsulModule:
    """Base class for Consule modules"""

    def __init__(self, module):
        if not HAS_REQUESTS:
            module.fail_json(
                msg=missing_required_lib("requests"), exception=REQUESTS_IMP_ERR
            )

        self.module = module

    def _request(self, method, url_parts, data=None, params=None):
        module_params = self.module.params

        if isinstance(url_parts, str):
            url_parts = [url_parts]

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
            response = requests.request(
                method,
                url,
                params=params,
                json=data,
                headers=headers,
                verify=module_params["validate_certs"],
            )
        except ConnectionError as e:
            self.module.fail_json(
                msg="Could not connect to consul agent at %s:%s, error was %s"
                % (module_params["host"], module_params["port"], str(e))
            )
        else:
            if 400 <= response.status_code < 600:
                raise RequestError("%d %s" % (response.status_code, response.content))

            return response.json()

    def get(self, url_parts, **kwargs):
        return self._request("GET", url_parts, **kwargs)

    def put(self, url_parts, **kwargs):
        return self._request("PUT", url_parts, **kwargs)

    def delete(self, url_parts, **kwargs):
        return self._request("DELETE", url_parts, **kwargs)

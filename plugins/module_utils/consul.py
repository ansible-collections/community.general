# -*- coding: utf-8 -*-

# Copyright (c) 2022, Håkon Lerring
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import copy
import json
import re

from ansible.module_utils.six.moves.urllib import error as urllib_error
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import open_url


def get_consul_url(configuration):
    return "%s://%s:%s/v1" % (
        configuration.scheme,
        configuration.host,
        configuration.port,
    )


def get_auth_headers(configuration):
    if configuration.token is None:
        return {}
    else:
        return {"X-Consul-Token": configuration.token}


class RequestError(Exception):
    def __init__(self, status, response_data=None):
        self.status = status
        self.response_data = response_data

    def __str__(self):
        if self.response_data is None:
            # self.status is already the message (backwards compat)
            return self.status
        return "HTTP %d: %s" % (self.status, self.response_data)


def handle_consul_response_error(response):
    if 400 <= response.status_code < 600:
        raise RequestError("%d %s" % (response.status_code, response.content))


AUTH_ARGUMENTS_SPEC = dict(
    host=dict(default="localhost"),
    port=dict(type="int", default=8500),
    scheme=dict(default="http"),
    validate_certs=dict(type="bool", default=True),
    token=dict(no_log=True),
    ca_path=dict(),
)


def camel_case_key(key):
    parts = []
    for part in key.split("_"):
        if part in {"id", "ttl", "jwks", "jwt", "oidc", "iam", "sts"}:
            parts.append(part.upper())
        else:
            parts.append(part.capitalize())
    return "".join(parts)


def validate_check(check):
    validate_duration_keys = ['Interval', 'Ttl', 'Timeout']
    validate_tcp_regex = r"(?P<host>.*):(?P<port>(?:[0-9]+))$"
    if check.get('Tcp') is not None:
        match = re.match(validate_tcp_regex, check['Tcp'])
        if not match:
            raise Exception('tcp check must be in host:port format')
    for duration in validate_duration_keys:
        if duration in check and check[duration] is not None:
            check[duration] = validate_duration(check[duration])


def validate_duration(duration):
    if duration:
        if not re.search(r"\d+(?:ns|us|ms|s|m|h)", duration):
            duration = "{0}s".format(duration)
    return duration


STATE_PARAMETER = "state"
STATE_PRESENT = "present"
STATE_ABSENT = "absent"

OPERATION_READ = "read"
OPERATION_CREATE = "create"
OPERATION_UPDATE = "update"
OPERATION_DELETE = "remove"


def _normalize_params(params, arg_spec):
    final_params = {}
    for k, v in params.items():
        if k not in arg_spec or v is None:  # Alias
            continue
        spec = arg_spec[k]
        if (
            spec.get("type") == "list"
            and spec.get("elements") == "dict"
            and spec.get("options")
            and v
        ):
            v = [_normalize_params(d, spec["options"]) for d in v]
        elif spec.get("type") == "dict" and spec.get("options") and v:
            v = _normalize_params(v, spec["options"])
        final_params[k] = v
    return final_params


class _ConsulModule:
    """Base class for Consul modules.

    This class is considered private, till the API is fully fleshed out.
    As such backwards incompatible changes can occur even in bugfix releases.
    """

    api_endpoint = None  # type: str
    unique_identifiers = None  # type: list
    result_key = None  # type: str
    create_only_fields = set()
    operational_attributes = set()
    params = {}

    def __init__(self, module):
        self._module = module
        self.params = _normalize_params(module.params, module.argument_spec)
        self.api_params = {
            k: camel_case_key(k)
            for k in self.params
            if k not in STATE_PARAMETER and k not in AUTH_ARGUMENTS_SPEC
        }

        self.operational_attributes.update({"CreateIndex", "CreateTime", "Hash", "ModifyIndex"})

    def execute(self):
        obj = self.read_object()

        changed = False
        diff = {}
        if self.params[STATE_PARAMETER] == STATE_PRESENT:
            obj_from_module = self.module_to_obj(obj is not None)
            if obj is None:
                operation = OPERATION_CREATE
                new_obj = self.create_object(obj_from_module)
                diff = {"before": {}, "after": new_obj}
                changed = True
            else:
                operation = OPERATION_UPDATE
                if self._needs_update(obj, obj_from_module):
                    new_obj = self.update_object(obj, obj_from_module)
                    diff = {"before": obj, "after": new_obj}
                    changed = True
                else:
                    new_obj = obj
        elif self.params[STATE_PARAMETER] == STATE_ABSENT:
            operation = OPERATION_DELETE
            if obj is not None:
                self.delete_object(obj)
                changed = True
                diff = {"before": obj, "after": {}}
            else:
                diff = {"before": {}, "after": {}}
            new_obj = None
        else:
            raise RuntimeError("Unknown state supplied.")

        result = {"changed": changed}
        if changed:
            result["operation"] = operation
            if self._module._diff:
                result["diff"] = diff
        if self.result_key:
            result[self.result_key] = new_obj
        self._module.exit_json(**result)

    def module_to_obj(self, is_update):
        obj = {}
        for k, v in self.params.items():
            result = self.map_param(k, v, is_update)
            if result:
                obj[result[0]] = result[1]
        return obj

    def map_param(self, k, v, is_update):
        def helper(item):
            return {camel_case_key(k): v for k, v in item.items()}

        def needs_camel_case(k):
            spec = self._module.argument_spec[k]
            return (
                spec.get("type") == "list"
                and spec.get("elements") == "dict"
                and spec.get("options")
            ) or (spec.get("type") == "dict" and spec.get("options"))

        if k in self.api_params and v is not None:
            if isinstance(v, dict) and needs_camel_case(k):
                v = helper(v)
            elif isinstance(v, (list, tuple)) and needs_camel_case(k):
                v = [helper(i) for i in v]
            if is_update and k in self.create_only_fields:
                return
            return camel_case_key(k), v

    def _needs_update(self, api_obj, module_obj):
        api_obj = copy.deepcopy(api_obj)
        module_obj = copy.deepcopy(module_obj)
        return self.needs_update(api_obj, module_obj)

    def needs_update(self, api_obj, module_obj):
        for k, v in module_obj.items():
            if k not in api_obj:
                return True
            if api_obj[k] != v:
                return True
        return False

    def prepare_object(self, existing, obj):
        existing = {
            k: v for k, v in existing.items() if k not in self.operational_attributes
        }
        for k, v in obj.items():
            existing[k] = v
        return existing

    def id_from_obj(self, obj, camel_case=False):
        def key_func(key):
            return camel_case_key(key) if camel_case else key

        if self.unique_identifiers:
            for identifier in self.unique_identifiers:
                identifier = key_func(identifier)
                if identifier in obj:
                    return obj[identifier]
        return None

    def endpoint_url(self, operation, identifier=None):
        if operation == OPERATION_CREATE:
            return self.api_endpoint
        elif identifier:
            return "/".join([self.api_endpoint, identifier])
        raise RuntimeError("invalid arguments passed")

    def read_object(self):
        identifier = self.id_from_obj(self.params)
        url = self.endpoint_url(OPERATION_READ, identifier)
        try:
            return self.get(url)
        except RequestError as e:
            if e.status == 404:
                return
            elif e.status == 403 and b"ACL not found" in e.response_data:
                return
            raise

    def create_object(self, obj):
        if self._module.check_mode:
            return obj
        else:
            url = self.endpoint_url(OPERATION_CREATE)
            created_obj = self.put(url, data=self.prepare_object({}, obj))
            if created_obj is None:
                created_obj = self.read_object()
            return created_obj

    def update_object(self, existing, obj):
        merged_object = self.prepare_object(existing, obj)
        if self._module.check_mode:
            return merged_object
        else:
            url = self.endpoint_url(OPERATION_UPDATE, self.id_from_obj(existing, camel_case=True))
            updated_obj = self.put(url, data=merged_object)
            if updated_obj is None:
                updated_obj = self.read_object()
            return updated_obj

    def delete_object(self, obj):
        if self._module.check_mode:
            return {}
        else:
            url = self.endpoint_url(OPERATION_DELETE, self.id_from_obj(obj, camel_case=True))
            return self.delete(url)

    def _request(self, method, url_parts, data=None, params=None):
        module_params = self.params

        if not isinstance(url_parts, (tuple, list)):
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
        token = self.params.get("token")
        if token:
            headers["X-Consul-Token"] = token

        try:
            if data is not None:
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
            status = (
                response.status if hasattr(response, "status") else response.getcode()
            )

        except urllib_error.URLError as e:
            if isinstance(e, urllib_error.HTTPError):
                status = e.code
                response_data = e.fp.read()
            else:
                self._module.fail_json(
                    msg="Could not connect to consul agent at %s:%s, error was %s"
                    % (module_params["host"], module_params["port"], str(e))
                )
                raise

        if 400 <= status < 600:
            raise RequestError(status, response_data)

        if response_data:
            return json.loads(response_data)
        return None

    def get(self, url_parts, **kwargs):
        return self._request("GET", url_parts, **kwargs)

    def put(self, url_parts, **kwargs):
        return self._request("PUT", url_parts, **kwargs)

    def delete(self, url_parts, **kwargs):
        return self._request("DELETE", url_parts, **kwargs)

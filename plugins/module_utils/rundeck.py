# -*- coding: utf-8 -*-

# Copyright (c) 2021, Phillipe Smith <phsmithcc@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json

from ansible.module_utils.urls import fetch_url, url_argument_spec
from ansible.module_utils.common.text.converters import to_native


def api_argument_spec():
    '''
    Creates an argument spec that can be used with any module
    that will be requesting content via Rundeck API
    '''
    api_argument_spec = url_argument_spec()
    api_argument_spec.update(dict(
        url=dict(required=True, type="str"),
        api_version=dict(type="int", default=39),
        api_token=dict(required=True, type="str", no_log=True)
    ))

    return api_argument_spec


def api_request(module, endpoint, data=None, method="GET"):
    """Manages Rundeck API requests via HTTP(S)

    :arg module:   The AnsibleModule (used to get url, api_version, api_token, etc).
    :arg endpoint: The API endpoint to be used.
    :kwarg data:   The data to be sent (in case of POST/PUT).
    :kwarg method: "POST", "PUT", etc.

    :returns: A tuple of (**response**, **info**). Use ``response.read()`` to read the data.
        The **info** contains the 'status' and other meta data. When a HttpError (status >= 400)
        occurred then ``info['body']`` contains the error response data::

    Example::

        data={...}
        resp, info = fetch_url(module,
                               "http://rundeck.example.org",
                               data=module.jsonify(data),
                               method="POST")
        status_code = info["status"]
        body = resp.read()
        if status_code >= 400 :
            body = info['body']
    """

    response, info = fetch_url(
        module=module,
        url="%s/api/%s/%s" % (
            module.params["url"],
            module.params["api_version"],
            endpoint
        ),
        data=json.dumps(data),
        method=method,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Rundeck-Auth-Token": module.params["api_token"]
        }
    )

    if info["status"] == 403:
        module.fail_json(msg="Token authorization failed",
                         execution_info=json.loads(info["body"]))
    elif info["status"] == 404:
        return None, info
    elif info["status"] == 409:
        module.fail_json(msg="Job executions limit reached",
                         execution_info=json.loads(info["body"]))
    elif info["status"] >= 500:
        module.fail_json(msg="Rundeck API error",
                         execution_info=json.loads(info["body"]))

    try:
        content = response.read()

        if not content:
            return None, info
        else:
            json_response = json.loads(content)
            return json_response, info
    except AttributeError as error:
        module.fail_json(
            msg="Rundeck API request error",
            exception=to_native(error),
            execution_info=info
        )
    except ValueError as error:
        module.fail_json(
            msg="No valid JSON response",
            exception=to_native(error),
            execution_info=content
        )

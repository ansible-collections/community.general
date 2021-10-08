#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Phillipe Smith <phsmithcc@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: rundeck_job_executions_info
short_description: Rundeck job executions info
description:
    - This module gets the list of executions for a specified Rundeck job.
author: "Phillipe Smith (@phsmith)"
version_added: 3.8.0
options:
    url:
        type: str
        description:
            - Rundeck instance URL.
        required: True
    api_version:
        type: int
        description:
            - Rundeck API version to be used.
            - API version must be at least 14.
        default: 39
    api_token:
        type: str
        description:
            - Rundeck User API Token.
        required: True
    job_id:
        type: str
        description:
            - The job unique ID.
        required: True
    status:
        type: str
        description:
            - The job status to filter.
        required: False
        choices: [succeeded, failed, aborted, running]
    max:
        type: int
        description:
            - Max results to return.
        required: False
        default: 20
    offset:
        type: int
        description:
            - The start point to return the results.
        required: False
        default: 0
extends_documentation_fragment: url
'''

EXAMPLES = '''
- name: Get Rundeck job executions info
  community.general.rundeck_job_executions_info:
    url: "https://rundeck.example.org"
    api_version: 39
    api_token: "mytoken"
    job_id: "xxxxxxxxxxxxxxxxx"
  register: rundeck_job_executions_info

- name: Show Rundeck job executions info
  debug:
    var: rundeck_job_executions_info.executions
'''

RETURN = '''
paging:
    description: Results pagination info.
    returned: success
    type: dict
    sample: {
        "count": 20,
        "total": 100,
        "offset": 0,
        "max": 20
    }
executions:
    description: Job executions list.
    returned: success
    type: list
    elements: dict
    sample: [
        {
            "id": 1,
            "href": "https://rundeck.example.org/api/39/execution/1",
            "permalink": "https://rundeck.example.org/project/myproject/execution/show/1",
            "status": "succeeded",
            "project": "myproject",
            "executionType": "user",
            "user": "admin",
            "date-started": {
                "unixtime": 1633525515026,
                "date": "2021-10-06T13:05:15Z"
            },
            "date-ended": {
                "unixtime": 1633525518386,
                "date": "2021-10-06T13:05:18Z"
            },
            "job": {
                "id": "697af0c4-72d3-4c15-86a3-b5bfe3c6cb6a",
                "averageDuration": 6381,
                "name": "Test",
                "group": "",
                "project": "myproject",
                "description": "",
                "options": {
                    "exit_code": "0"
                },
                "href": "https://rundeck.example.org/api/39/job/697af0c4-72d3-4c15-86a3-b5bfe3c6cb6a",
                "permalink": "https://rundeck.example.org/project/myproject/job/show/697af0c4-72d3-4c15-86a3-b5bfe3c6cb6a"
            },
            "description": "Plugin[com.batix.rundeck.plugins.AnsiblePlaybookInlineWorkflowStep, nodeStep: false]",
            "argstring": "-exit_code 0",
            "serverUUID": "5b9a1438-fa3a-457e-b254-8f3d70338068"
        }
    ]
'''

# Modules import
import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.urls import fetch_url, url_argument_spec


class RundeckJobExecutionsInfo(object):
    def __init__(self, module):
        self.module = module
        self.url = self.module.params["url"]
        self.api_version = self.module.params["api_version"]
        self.job_id = self.module.params["job_id"]
        self.offset = self.module.params["offset"]
        self.max = self.module.params["max"]
        self.status = self.module.params.get("status") or ""
        self.__api_token = self.module.params["api_token"]

    def api_request(self, endpoint, data=None, method="GET"):
        response, info = fetch_url(
            module=self.module,
            url="%s/api/%s/%s" % (self.url, self.api_version, endpoint),
            data=json.dumps(data),
            method=method,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Rundeck-Auth-Token": self.__api_token
            }
        )

        if info["status"] == 403:
            self.module.fail_json(msg="Token authorization failed",
                                  execution_info=json.loads(info["body"]))
        if info["status"] == 409:
            self.module.fail_json(msg="Job executions limit reached",
                                  execution_info=json.loads(info["body"]))
        elif info["status"] >= 500:
            self.module.fail_json(msg="Rundeck API error",
                                  execution_info=json.loads(info["body"]))

        try:
            content = response.read()
            json_response = json.loads(content)
            return json_response, info
        except AttributeError as error:
            self.module.fail_json(msg="Rundeck API request error",
                                  exception=to_native(error),
                                  execution_info=info)
        except ValueError as error:
            self.module.fail_json(
                msg="No valid JSON response",
                exception=to_native(error),
                execution_info=content
            )

    def job_executions(self):
        response, info = self.api_request(
            endpoint="job/%s/executions?offset=%s&max=%s&status=%s"
                     % (self.job_id, self.offset, self.max, self.status),
            method="GET"
        )

        if info["status"] != 200:
            self.module.fail_json(
                msg=info["msg"],
                executions_info=response
            )

        self.module.exit_json(msg=response)


def main():
    argument_spec = url_argument_spec()
    argument_spec.update(dict(
        url=dict(required=True, type="str"),
        api_version=dict(type="int", default=39),
        api_token=dict(required=True, type="str", no_log=True),
        job_id=dict(required=True, type="str"),
        offset=dict(type="int", default=0),
        max=dict(type="int", default=20),
        status=dict(
            type="str",
            choices=["succeeded", "failed", "aborted", "running"]
        )
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    if module.params["api_version"] < 14:
        module.fail_json(msg="API version should be at least 14")

    rundeck = RundeckJobExecutionsInfo(module)
    rundeck.job_executions()


if __name__ == "__main__":
    main()

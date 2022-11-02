#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Phillipe Smith <phsmithcc@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: rundeck_job_executions_info
short_description: Query executions for a Rundeck job
description:
    - This module gets the list of executions for a specified Rundeck job.
author: "Phillipe Smith (@phsmith)"
version_added: 3.8.0
options:
    job_id:
        type: str
        description:
            - The job unique ID.
        required: true
    status:
        type: str
        description:
            - The job status to filter.
        choices: [succeeded, failed, aborted, running]
    max:
        type: int
        description:
            - Max results to return.
        default: 20
    offset:
        type: int
        description:
            - The start point to return the results.
        default: 0
extends_documentation_fragment:
  - community.general.rundeck
  - url
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
  ansible.builtin.debug:
    var: rundeck_job_executions_info.executions
'''

RETURN = '''
paging:
    description: Results pagination info.
    returned: success
    type: dict
    contains:
      count:
        description: Number of results in the response.
        type: int
        returned: success
      total:
        description: Total number of results.
        type: int
        returned: success
      offset:
        description: Offset from first of all results.
        type: int
        returned: success
      max:
        description: Maximum number of results per page.
        type: int
        returned: success
    sample: {
        "count": 20,
        "total": 100,
        "offset": 0,
        "max": 20
    }
executions:
    description: Job executions list.
    returned: always
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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible_collections.community.general.plugins.module_utils.rundeck import (
    api_argument_spec,
    api_request
)


class RundeckJobExecutionsInfo(object):
    def __init__(self, module):
        self.module = module
        self.url = self.module.params["url"]
        self.api_version = self.module.params["api_version"]
        self.job_id = self.module.params["job_id"]
        self.offset = self.module.params["offset"]
        self.max = self.module.params["max"]
        self.status = self.module.params["status"] or ""

    def job_executions(self):
        response, info = api_request(
            module=self.module,
            endpoint="job/%s/executions?offset=%s&max=%s&status=%s"
                     % (quote(self.job_id), self.offset, self.max, self.status),
            method="GET"
        )

        if info["status"] != 200:
            self.module.fail_json(
                msg=info["msg"],
                executions=response
            )

        self.module.exit_json(msg="Executions info result", **response)


def main():
    argument_spec = api_argument_spec()
    argument_spec.update(dict(
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

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Phillipe Smith <phsmithcc@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: rundeck_job_run
short_description: Run a Rundeck job
description:
    - This module runs a Rundeck job specified by ID.
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
    job_options:
        type: dict
        description:
            - The job options.
        required: False
        default: {}
    filter_nodes:
        type: str
        description:
            - Filter the nodes where the jobs must run.
            - See https://docs.rundeck.com/docs/manual/11-node-filters.html#node-filter-syntax.
        required: False
    run_at_time:
        type: str
        description:
            - Schedule the job execution to run at specific date and time.
            - ISO-8601 date and time format like 2021-10-05T15:45:00-03:00.
        required: False
    loglevel:
        type: str
        description:
            - Log level configuration.
        required: False
        choices: [debug, verbose, info, warn, error]
        default: info
    wait_execution:
        type: bool
        description:
            - Wait until the job finished the execution.
        required: False
        default: True
    wait_execution_timeout:
        type: int
        description:
            - Job execution wait timeout in seconds. 0 = no timeout.
            - If the timeout is reached, the job will be aborted.
            - Keep in mind that there is a sleep of 5s after each job status check
        required: False
        default: 0
extends_documentation_fragment: url
'''

EXAMPLES = '''
- name: Run a Rundeck job
  community.general.rundeck_job_run:
    url: "https://rundeck.example.org"
    api_version: 39
    api_token: "mytoken"
    job_id: "xxxxxxxxxxxxxxxxx"
  register: rundeck_job_run

- name: Show execution info
  debug:
    var: rundeck_job_run.execution_info

- name: Schedule a Rundeck job
  community.general.rundeck_job_run:
    url: "https://rundeck.example.org"
    api_version: 39
    api_token: "mytoken"
    job_id: "xxxxxxxxxxxxxxxxx"
    run_at_time: "2021-10-05T15:45:00-03:00"
  register: rundeck_job_schedule
'''

RETURN = '''
execution_info:
    description: Rundeck job execution metadata.
    returned: always
    type: dict
    sample: {
        "msg": "Job execution succeeded!",
        "execution_info": {
            "id": 1,
            "href": "https://rundeck.example.org/api/39/execution/1",
            "permalink": "https://rundeck.example.org/project/myproject/execution/show/1",
            "status": "succeeded",
            "project": "myproject",
            "executionType": "user",
            "user": "admin",
            "date-started": {
                "unixtime": 1633449020784,
                "date": "2021-10-05T15:50:20Z"
            },
            "date-ended": {
                "unixtime": 1633449026358,
                "date": "2021-10-05T15:50:26Z"
            },
            "job": {
                "id": "697af0c4-72d3-4c15-86a3-b5bfe3c6cb6a",
                "averageDuration": 4917,
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
            "description": "sleep 5 && echo 'Test!' && exit ${option.exit_code}",
            "argstring": "-exit_code 0",
            "serverUUID": "5b9a1438-fa3a-457e-b254-8f3d70338068",
            "successfulNodes": [
                "localhost"
            ],
            "output": "Test!"
        }
    }
'''

# Modules import
import json
from datetime import datetime
from time import sleep

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.urls import fetch_url, url_argument_spec


class RundeckJobRun(object):
    def __init__(self, module):
        self.module = module
        self.url = self.module.params["url"]
        self.api_version = self.module.params["api_version"]
        self.job_id = self.module.params["job_id"]
        self.job_options = self.module.params["job_options"]
        self.filter_nodes = self.module.params["filter_nodes"]
        self.run_at_time = self.module.params["run_at_time"]
        self.loglevel = self.module.params["loglevel"].upper()
        self.wait_execution = self.module.params['wait_execution']
        self.wait_execution_timeout = self.module.params['wait_execution_timeout']
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
        elif info["status"] == -1:
            self.module.fail_json(msg="Rundeck API request error",
                                  execution_info=info)

        response = response.read()

        try:
            json_response = json.loads(response)
            return json_response, info
        except ValueError as error:
            self.module.fail_json(
                msg="No valid JSON response",
                exception=to_native(error),
                execution_info=response
            )

    def job_status_check(self, execution_id):
        job_status_wait = True
        start_datetime = int(datetime.now().strftime("%s"))

        while job_status_wait:
            endpoint = "execution/%s" % execution_id
            response = self.api_request(endpoint)[0]
            datetime_after_start = int(datetime.now().strftime("%s"))
            output = self.api_request(endpoint="execution/%s/output" % execution_id)
            log_output = "\n".join([x["log"] for x in output[0]["entries"]])
            response.update({"output": log_output})

            if response["status"] == "scheduled":
                self.module.exit_json(msg="Job scheduled to run at %s" % self.run_at_time,
                                      execution_info=response,
                                      changed=True)
            elif response["status"] == "failed":
                self.module.fail_json(msg="Job execution failed",
                                      execution_info=response)
            elif response["status"] == "succeeded":
                self.module.exit_json(msg="Job execution succeeded!",
                                      execution_info=response)

            if self.wait_execution_timeout > 0:
                if (datetime_after_start - start_datetime) >= self.wait_execution_timeout:
                    job_status_wait = False
                    break

            # Wait for 5s before continue
            sleep(5)

        if not job_status_wait:
            response = self.api_request(
                "execution/%s/abort" % response['id'],
                method="GET"
            )

            self.module.fail_json(msg="Job execution aborted due the timeout specified",
                                  execution_info=response[0])

    def job_run(self):
        response, info = self.api_request(
            endpoint="job/%s/run" % self.job_id,
            method="POST",
            data={
                "loglevel": self.loglevel,
                "options": self.job_options,
                "runAtTime": self.run_at_time,
                "filter": self.filter_nodes
            }
        )

        if info["status"] != 200:
            self.module.fail_json(msg=info["msg"])

        if not self.wait_execution:
            self.module.exit_json(msg="Job run send successfully!",
                                  execution_info=response)

        self.job_status_check(response["id"])


def main():
    argument_spec = url_argument_spec()
    argument_spec.update(dict(
        url=dict(required=True, type="str"),
        api_version=dict(type="int", default=39),
        api_token=dict(required=True, type="str", no_log=True),
        job_id=dict(required=True, type="str"),
        job_options=dict(type="dict", default={}),
        filter_nodes=dict(type="str", default=""),
        run_at_time=dict(type="str", default=""),
        wait_execution=dict(type="bool", default=True),
        wait_execution_timeout=dict(type="int", default=0),
        loglevel=dict(
            type="str",
            choices=["debug", "verbose", "info", "warn", "error"],
            default="info"
        )
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False
    )

    if module.params["api_version"] < 14:
        module.fail_json(msg="API version should be at least 14")

    rundeck = RundeckJobRun(module)
    rundeck.job_run()


if __name__ == "__main__":
    main()

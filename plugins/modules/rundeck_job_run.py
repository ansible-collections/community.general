#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Phillipe Smith <phsmithcc@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none
options:
    job_id:
        type: str
        description:
            - The job unique ID.
        required: true
    job_options:
        type: dict
        description:
            - The job options for the steps.
            - Numeric values must be quoted.
    filter_nodes:
        type: str
        description:
            - Filter the nodes where the jobs must run.
            - See U(https://docs.rundeck.com/docs/manual/11-node-filters.html#node-filter-syntax).
    run_at_time:
        type: str
        description:
            - Schedule the job execution to run at specific date and time.
            - ISO-8601 date and time format like V(2021-10-05T15:45:00-03:00).
    loglevel:
        type: str
        description:
            - Log level configuration.
        choices: [debug, verbose, info, warn, error]
        default: info
    wait_execution:
        type: bool
        description:
            - Wait until the job finished the execution.
        default: true
    wait_execution_delay:
        type: int
        description:
            - Delay, in seconds, between job execution status check requests.
        default: 5
    wait_execution_timeout:
        type: int
        description:
            - Job execution wait timeout in seconds.
            - If the timeout is reached, the job will be aborted.
            - Keep in mind that there is a sleep based on O(wait_execution_delay) after each job status check.
        default: 120
    abort_on_timeout:
        type: bool
        description:
            - Send a job abort request if exceeded the O(wait_execution_timeout) specified.
        default: false
extends_documentation_fragment:
  - community.general.rundeck
  - ansible.builtin.url
  - community.general.attributes
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
  ansible.builtin.debug:
    var: rundeck_job_run.execution_info

- name: Run a Rundeck job with options
  community.general.rundeck_job_run:
    url: "https://rundeck.example.org"
    api_version: 39
    api_token: "mytoken"
    job_id: "xxxxxxxxxxxxxxxxx"
    job_options:
        option_1: "value_1"
        option_2: "value_3"
        option_3: "value_3"
  register: rundeck_job_run

- name: Run a Rundeck job with timeout, delay between status check and abort on timeout
  community.general.rundeck_job_run:
    url: "https://rundeck.example.org"
    api_version: 39
    api_token: "mytoken"
    job_id: "xxxxxxxxxxxxxxxxx"
    wait_execution_timeout: 30
    wait_execution_delay: 10
    abort_on_timeout: true
  register: rundeck_job_run

- name: Schedule a Rundeck job
  community.general.rundeck_job_run:
    url: "https://rundeck.example.org"
    api_version: 39
    api_token: "mytoken"
    job_id: "xxxxxxxxxxxxxxxxx"
    run_at_time: "2021-10-05T15:45:00-03:00"
  register: rundeck_job_schedule

- name: Fire-and-forget a Rundeck job
  community.general.rundeck_job_run:
    url: "https://rundeck.example.org"
    api_version: 39
    api_token: "mytoken"
    job_id: "xxxxxxxxxxxxxxxxx"
    wait_execution: false
  register: rundeck_job_run
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
from datetime import datetime, timedelta
from time import sleep

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible_collections.community.general.plugins.module_utils.rundeck import (
    api_argument_spec,
    api_request
)


class RundeckJobRun(object):
    def __init__(self, module):
        self.module = module
        self.url = self.module.params["url"]
        self.api_version = self.module.params["api_version"]
        self.job_id = self.module.params["job_id"]
        self.job_options = self.module.params["job_options"] or {}
        self.filter_nodes = self.module.params["filter_nodes"] or ""
        self.run_at_time = self.module.params["run_at_time"] or ""
        self.loglevel = self.module.params["loglevel"].upper()
        self.wait_execution = self.module.params['wait_execution']
        self.wait_execution_delay = self.module.params['wait_execution_delay']
        self.wait_execution_timeout = self.module.params['wait_execution_timeout']
        self.abort_on_timeout = self.module.params['abort_on_timeout']

        for k, v in self.job_options.items():
            if not isinstance(v, str):
                self.module.exit_json(
                    msg="Job option '%s' value must be a string" % k,
                    execution_info={}
                )

    def job_status_check(self, execution_id):
        response = dict()
        timeout = False
        due = datetime.now() + timedelta(seconds=self.wait_execution_timeout)

        while not timeout:
            endpoint = "execution/%d" % execution_id
            response = api_request(module=self.module, endpoint=endpoint)[0]
            output = api_request(module=self.module,
                                 endpoint="execution/%d/output" % execution_id)
            log_output = "\n".join([x["log"] for x in output[0]["entries"]])
            response.update({"output": log_output})

            if response["status"] == "aborted":
                break
            elif response["status"] == "scheduled":
                self.module.exit_json(msg="Job scheduled to run at %s" % self.run_at_time,
                                      execution_info=response,
                                      changed=True)
            elif response["status"] == "failed":
                self.module.fail_json(msg="Job execution failed",
                                      execution_info=response)
            elif response["status"] == "succeeded":
                self.module.exit_json(msg="Job execution succeeded!",
                                      execution_info=response)

            if datetime.now() >= due:
                timeout = True
                break

            # Wait for 5s before continue
            sleep(self.wait_execution_delay)

        response.update({"timed_out": timeout})
        return response

    def job_run(self):
        response, info = api_request(
            module=self.module,
            endpoint="job/%s/run" % quote(self.job_id),
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

        job_status = self.job_status_check(response["id"])

        if job_status["timed_out"]:
            if self.abort_on_timeout:
                api_request(
                    module=self.module,
                    endpoint="execution/%s/abort" % response['id'],
                    method="GET"
                )

                abort_status = self.job_status_check(response["id"])

                self.module.fail_json(msg="Job execution aborted due the timeout specified",
                                      execution_info=abort_status)

            self.module.fail_json(msg="Job execution timed out",
                                  execution_info=job_status)


def main():
    argument_spec = api_argument_spec()
    argument_spec.update(dict(
        job_id=dict(required=True, type="str"),
        job_options=dict(type="dict"),
        filter_nodes=dict(type="str"),
        run_at_time=dict(type="str"),
        wait_execution=dict(type="bool", default=True),
        wait_execution_delay=dict(type="int", default=5),
        wait_execution_timeout=dict(type="int", default=120),
        abort_on_timeout=dict(type="bool", default=False),
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

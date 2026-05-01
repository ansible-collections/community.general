#!/usr/bin/python

# Copyright (c) 2020, FERREIRA Christophe <christophe.ferreira@cnaf.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: nomad_job
author: FERREIRA Christophe (@chris93111)
version_added: "1.3.0"
short_description: Launch a Nomad Job
description:
  - Launch a Nomad job.
  - Stop a Nomad job.
  - Force start a Nomad job.
requirements:
  - python-nomad
extends_documentation_fragment:
  - community.general._nomad
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Name of job for delete, stop and start job without source.
      - Name of job for delete, stop and start job without source.
      - Either this or O(content) must be specified.
    type: str
  state:
    description:
      - Deploy or remove job.
    choices: ["present", "absent"]
    required: true
    type: str
  force_start:
    description:
      - Force job to started.
    type: bool
    default: false
  content:
    description:
      - Content of Nomad job.
      - Either this or O(name) must be specified.
    type: str
  content_format:
    description:
      - Type of content of Nomad job.
    choices: ["hcl", "json"]
    default: hcl
    type: str
seealso:
  - name: Nomad jobs documentation
    description: Complete documentation for Nomad API jobs.
    link: https://www.nomadproject.io/api-docs/jobs/
"""

EXAMPLES = r"""
- name: Create job
  community.general.nomad_job:
    host: localhost
    state: present
    content: "{{ lookup('ansible.builtin.file', 'job.hcl') }}"
    timeout: 120

- name: Connect with port to create job
  community.general.nomad_job:
    host: localhost
    port: 4645
    state: present
    content: "{{ lookup('ansible.builtin.file', 'job.hcl') }}"
    timeout: 120

- name: Stop job
  community.general.nomad_job:
    host: localhost
    state: absent
    name: api

- name: Force job to start
  community.general.nomad_job:
    host: localhost
    state: present
    name: api
    timeout: 120
    force_start: true
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils._nomad import argument_spec as nomad_argument_spec
from ansible_collections.community.general.plugins.module_utils._nomad import nomad, setup_nomad_client


def run():
    module = AnsibleModule(
        argument_spec={
            **nomad_argument_spec,
            "state": dict(required=True, choices=["present", "absent"]),
            "name": dict(type="str"),
            "content_format": dict(choices=["hcl", "json"], default="hcl"),
            "content": dict(type="str"),
            "force_start": dict(type="bool", default=False),
        },
        supports_check_mode=True,
        mutually_exclusive=[["name", "content"]],
        required_one_of=[["name", "content"]],
    )

    nomad_client = setup_nomad_client(module)

    if module.params["state"] == "present":
        if module.params["name"] and not module.params["force_start"]:
            module.fail_json(msg="For start job with name, force_start is needed")

        changed = False
        if module.params["content"]:
            if module.params["content_format"] == "json":
                job_json = module.params["content"]
                try:
                    job_json = json.loads(job_json)
                except ValueError as e:
                    module.fail_json(msg=f"{e}")
                job = {"job": job_json}
                try:
                    job_id = job_json.get("ID")
                    if job_id is None:
                        module.fail_json(msg="Cannot retrieve job with ID None")
                    plan = nomad_client.job.plan_job(job_id, job, diff=True)
                    if plan["Diff"].get("Type") != "None":
                        changed = True
                        if not module.check_mode:
                            result = nomad_client.jobs.register_job(job)
                        else:
                            result = plan
                    else:
                        result = plan
                except Exception as e:
                    module.fail_json(msg=f"{e}")

            if module.params["content_format"] == "hcl":
                try:
                    job_hcl = module.params["content"]
                    job_json = nomad_client.jobs.parse(job_hcl)
                    job = {"job": job_json}
                except nomad.api.exceptions.BadRequestNomadException as err:
                    module.fail_json(msg=f"{err.nomad_resp.reason} {err.nomad_resp.text}")
                try:
                    job_id = job_json.get("ID")
                    plan = nomad_client.job.plan_job(job_id, job, diff=True)
                    if plan["Diff"].get("Type") != "None":
                        changed = True
                        if not module.check_mode:
                            result = nomad_client.jobs.register_job(job)
                        else:
                            result = plan
                    else:
                        result = plan
                except Exception as e:
                    module.fail_json(msg=f"{e}")

        if module.params["force_start"]:
            try:
                if module.params["name"]:
                    job_name = module.params["name"]
                else:
                    job_name = job_json["Name"]
                job_json = nomad_client.job.get_job(job_name)
                if job_json["Status"] == "running":
                    result = job_json
                else:
                    job_json["Status"] = "running"
                    job_json["Stop"] = False
                    job = {"job": job_json}
                    if not module.check_mode:
                        result = nomad_client.jobs.register_job(job)
                    else:
                        result = nomad_client.validate.validate_job(job)
                        if result.status_code != 200:
                            module.fail_json(msg=to_native(result.text))
                        result = json.loads(result.text)
                    changed = True
            except Exception as e:
                module.fail_json(msg=f"{e}")

    if module.params["state"] == "absent":
        try:
            if module.params["name"] is not None:
                job_name = module.params["name"]
            else:
                if module.params["content_format"] == "hcl":
                    job_json = nomad_client.jobs.parse(module.params["content"])
                    job_name = job_json["Name"]
                if module.params["content_format"] == "json":
                    job_json = module.params["content"]
                    job_name = job_json["Name"]
            job = nomad_client.job.get_job(job_name)
            if job["Status"] == "dead":
                changed = False
                result = job
            else:
                if not module.check_mode:
                    result = nomad_client.job.deregister_job(job_name)
                else:
                    result = job
                changed = True
        except Exception as e:
            module.fail_json(msg=f"{e}")

    module.exit_json(changed=changed, result=result)


def main():
    run()


if __name__ == "__main__":
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2020, FERREIRA Christophe <christophe.ferreira@cnaf.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: nomad_job
author: FERREIRA Christophe (@chris93111)
version_added: "1.3.0"
short_description: Launch a Nomad Job
description:
    - Launch a Nomad job.
    - Stop a Nomad job.
    - Force start a Nomad job
requirements:
  - python-nomad
extends_documentation_fragment:
  - community.general.nomad
options:
    name:
      description:
        - Name of job for delete, stop and start job without source.
        - Name of job for delete, stop and start job without source.
        - Either this or I(content) must be specified.
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
        - Either this or I(name) must be specified.
      type: str
    content_format:
      description:
        - Type of content of Nomad job.
      choices: ["hcl", "json"]
      default: hcl
      type: str
notes:
  - C(check_mode) is supported.
seealso:
  - name: Nomad jobs documentation
    description: Complete documentation for Nomad API jobs.
    link: https://www.nomadproject.io/api-docs/jobs/
'''

EXAMPLES = '''
- name: Create job
  community.general.nomad_job:
    host: localhost
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
'''

import json

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

import_nomad = None
try:
    import nomad
    import_nomad = True
except ImportError:
    import_nomad = False


def run():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True, type='str'),
            state=dict(required=True, choices=['present', 'absent']),
            use_ssl=dict(type='bool', default=True),
            timeout=dict(type='int', default=5),
            validate_certs=dict(type='bool', default=True),
            client_cert=dict(type='path'),
            client_key=dict(type='path'),
            namespace=dict(type='str'),
            name=dict(type='str'),
            content_format=dict(choices=['hcl', 'json'], default='hcl'),
            content=dict(type='str'),
            force_start=dict(type='bool', default=False),
            token=dict(type='str', no_log=True)
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ["name", "content"]
        ],
        required_one_of=[
            ['name', 'content']
        ]
    )

    if not import_nomad:
        module.fail_json(msg=missing_required_lib("python-nomad"))

    certificate_ssl = (module.params.get('client_cert'), module.params.get('client_key'))

    nomad_client = nomad.Nomad(
        host=module.params.get('host'),
        secure=module.params.get('use_ssl'),
        timeout=module.params.get('timeout'),
        verify=module.params.get('validate_certs'),
        cert=certificate_ssl,
        namespace=module.params.get('namespace'),
        token=module.params.get('token')
    )

    if module.params.get('state') == "present":

        if module.params.get('name') and not module.params.get('force_start'):
            module.fail_json(msg='For start job with name, force_start is needed')

        changed = False
        if module.params.get('content'):

            if module.params.get('content_format') == 'json':

                job_json = module.params.get('content')
                try:
                    job_json = json.loads(job_json)
                except ValueError as e:
                    module.fail_json(msg=to_native(e))
                job = dict()
                job['job'] = job_json
                try:
                    job_id = job_json.get('ID')
                    if job_id is None:
                        module.fail_json(msg="Cannot retrieve job with ID None")
                    plan = nomad_client.job.plan_job(job_id, job, diff=True)
                    if not plan['Diff'].get('Type') == "None":
                        changed = True
                        if not module.check_mode:
                            result = nomad_client.jobs.register_job(job)
                        else:
                            result = plan
                    else:
                        result = plan
                except Exception as e:
                    module.fail_json(msg=to_native(e))

            if module.params.get('content_format') == 'hcl':

                try:
                    job_hcl = module.params.get('content')
                    job_json = nomad_client.jobs.parse(job_hcl)
                    job = dict()
                    job['job'] = job_json
                except nomad.api.exceptions.BadRequestNomadException as err:
                    msg = str(err.nomad_resp.reason) + " " + str(err.nomad_resp.text)
                    module.fail_json(msg=to_native(msg))
                try:
                    job_id = job_json.get('ID')
                    plan = nomad_client.job.plan_job(job_id, job, diff=True)
                    if not plan['Diff'].get('Type') == "None":
                        changed = True
                        if not module.check_mode:
                            result = nomad_client.jobs.register_job(job)
                        else:
                            result = plan
                    else:
                        result = plan
                except Exception as e:
                    module.fail_json(msg=to_native(e))

        if module.params.get('force_start'):

            try:
                job = dict()
                if module.params.get('name'):
                    job_name = module.params.get('name')
                else:
                    job_name = job_json['Name']
                job_json = nomad_client.job.get_job(job_name)
                if job_json['Status'] == 'running':
                    result = job_json
                else:
                    job_json['Status'] = 'running'
                    job_json['Stop'] = False
                    job['job'] = job_json
                    if not module.check_mode:
                        result = nomad_client.jobs.register_job(job)
                    else:
                        result = nomad_client.validate.validate_job(job)
                        if not result.status_code == 200:
                            module.fail_json(msg=to_native(result.text))
                        result = json.loads(result.text)
                    changed = True
            except Exception as e:
                module.fail_json(msg=to_native(e))

    if module.params.get('state') == "absent":

        try:
            if not module.params.get('name') is None:
                job_name = module.params.get('name')
            else:
                if module.params.get('content_format') == 'hcl':
                    job_json = nomad_client.jobs.parse(module.params.get('content'))
                    job_name = job_json['Name']
                if module.params.get('content_format') == 'json':
                    job_json = module.params.get('content')
                    job_name = job_json['Name']
            job = nomad_client.job.get_job(job_name)
            if job['Status'] == 'dead':
                changed = False
                result = job
            else:
                if not module.check_mode:
                    result = nomad_client.job.deregister_job(job_name)
                else:
                    result = job
                changed = True
        except Exception as e:
            module.fail_json(msg=to_native(e))

    module.exit_json(changed=changed, result=result)


def main():

    run()


if __name__ == "__main__":
    main()

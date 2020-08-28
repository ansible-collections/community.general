#!/usr/bin/python
# coding: utf-8 -*-

# (c) 2020, FERREIRA Christophe <christophe.ferreira@cnaf.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: nomad_job
author: "FERREIRA Christophe (@chris93111)"
version_added: "1.2.0"
short_description: Launch an Nomad Job.
description:
    - Launch an Nomad job. See
      U(https://www.nomadproject.io/api-docs/jobs/) for an overview.
options:
    host:
      description:
        - FQDN of nomad server.
      required: true
      type: str
    secure:
      description:
        - ssl connection.
      type: bool
      default: false
    timeout:
      description:
        - timeout of request nomad.
      type: int
      default: 5
    validate_certs:
      description:
        - skip validation cert.
      type: bool
      default: true
    cert:
      description:
        - path of certificate ssl.
      type: path
    key:
      description:
        - path of certificate key ssl.
      type: path
    namespace:
      description:
        - namespace for nomad.
      type: str
    token:
      description:
        - acl token for authentification.
      type: str
    name:
      description:
        - name of job for delete or stop job without source.
      type: str
    state:
      description:
        - type of request
      choices: ["present", "absent"]
      required: True
      type: str
    force_start:
      description:
        - force job to started
      type: bool
      default: false
    source_json:
      description:
        - source of json nomad job
      type: json
    source_hcl:
      description:
        - source of hcl nomad job
      type: str
'''

EXAMPLES = '''
- name: create job
  nomad_job:
    host: localhost
    state: present
    source_hcl: "{{ lookup('file', 'job.hcl') }}"
    timeout: 120

- name: stop job
  nomad_job:
    host: localhost
    state: absent
    name: api

- name: force job to start
  nomad_job:
    host: localhost
    state: present
    name: api
    timeout: 120
    force_start: true
'''


import os
import json

from ansible.module_utils.basic import AnsibleModule

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
            secure=dict(type='bool', default=False),
            timeout=dict(type='int', default=5),
            validate_certs=dict(type='bool', default=True),
            cert=dict(type='path', default=None),
            key=dict(type='path', default=None),
            namespace=dict(type='str', default=None),
            name=dict(type='str', default=None),
            source_json=dict(type='json', default=None),
            source_hcl=dict(type='str', default=None),
            force_start=dict(type='bool', default=False),
            token=dict(type='str', default=None, no_log=True)
        ),
        mutually_exclusive=[
            ["name", "source_json", "source_hcl"],
            ["source_json", "source_hcl"]
        ],
        required_one_of=[
            ['name', 'source_json', 'source_hcl']
        ]
    )

    if not import_nomad:
        module.fail_json(msg='python-nomad is required for nomad_job ')

    certificate_ssl = (module.params.get('cert'), module.params.get('key'))

    nomad_client = nomad.Nomad(
        host=module.params.get('host'),
        secure=module.params.get('secure'),
        timeout=module.params.get('timeout'),
        verify=module.params.get('validate_certs'),
        cert=certificate_ssl,
        namespace=module.params.get('namespace'),
        token=module.params.get('token')
    )

    if module.params.get('state') == "present":

        if module.params.get('name') and not module.params.get('force_start'):
            module.fail_json(msg='for start job with name, force_start is needed')

        changed = False
        if not module.params.get('source_json') is None:
            job_json = module.params.get('source_json')
            try:
                job_json = json.loads(job_json)
            except ValueError as e:
                module.fail_json(msg=str(e))
            job = dict()
            job['job'] = job_json
            try:
                result = nomad_client.jobs.register_job(job)
                changed = True
            except Exception as e:
                module.fail_json(msg=str(e))

        if not module.params.get('source_hcl') is None:

            try:
                job_hcl = module.params.get('source_hcl')
                job_json = nomad_client.jobs.parse(job_hcl)
                job = dict()
                job['job'] = job_json
            except nomad.api.exceptions.BadRequestNomadException as err:
                msg = str(err.nomad_resp.reason) + " " + str(err.nomad_resp.text)
                module.fail_json(msg=msg)
            try:
                result = nomad_client.jobs.register_job(job)
                changed = True
            except Exception as e:
                module.fail_json(msg=str(e))

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
                    result = nomad_client.jobs.register_job(job)
                    changed = True
            except Exception as e:
                module.fail_json(msg=str(e))

    if module.params.get('state') == "absent":

        try:
            if not module.params.get('name') is None:
                job_name = module.params.get('name')
            if not module.params.get('source_hcl') is None:
                job_json = nomad_client.jobs.parse(job_hcl)
                job_name = job_json['Name']
            if not module.params.get('source_json') is None:
                job_json = module.params.get('source_json')
                job_name = job_json['Name']
            job = nomad_client.job.get_job(job_name)
            if job['Status'] == 'dead':
                changed = False
                result = job
            else:
                result = nomad_client.job.deregister_job(job_name)
                changed = True
        except Exception as e:
            module.fail_json(msg=str(e))

    module.exit_json(changed=changed, result=result)


def main():

    run()


if __name__ == "__main__":
    main()

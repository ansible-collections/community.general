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
module: nomad_jobs
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
      type: ...
    secure:
      description:
        - ssl connection.
    timeout:
      description:
        - timeout of request nomad.
    validate_certs:
      description:
        - skip validation cert.
    cert:
      description:
        - path of certificate ssl.
    key:
      description:
        - path of certificate key ssl.
    namespace:
      description:
        - namespace for nomad.
    token:
      description:
        - acl token for authentification.
    name:
      description:
        - name of job for get|stop.
    state:
      description:
        - type of request
      choices: ["create", "stop", "get", "list"]
      required: True
    source:
      description:
        - path of json or hcl for create job
    source_json:
      description:
        - source of json nomad job
    source_hcl:
      description:
        - source of hcl nomad job
extends_documentation_fragment: nomad
'''

EXAMPLES = '''
# List jobs
- name: list jobs nomad
  nomad_job:
    nomad_server: localhost
    state: list
  register: jobs

- name: create job
  nomad_job:
    nomad_server: localhost
    state: create
    source: api.hcl
    source_type: hcl
    timeout: 120

- name: stop job
  nomad_job:
    nomad_server: localhost
    state: stop
    name: api

- name: get job
  nomad_job:
    nomad_server: localhost
    state: status
    name: api
'''


import os
import json

from ansible.module_utils.basic import *

try:
    import nomad
    import_nomad = True
except:
    import_nomad = False


def run():
    module = AnsibleModule(
        argument_spec = dict(
            host=dict(required=True, type='str'),
            state=dict(required=True, choices=['created', 'started', 'stopped'),
            secure=dict(type='bool', default=False),
            timeout=dict(type='int', default=5),
            validate_certs=dict(type='bool', default=True),
            cert=dict(type='path', default=None),
            key=dict(type='path', default=None),
            namespace=dict(type='str', default=None),
            name=dict(type='str', default=None),
            source_json=dict(type='json', default=None),
            source_hcl=dict(type='str', default=None),
            token=dict(type='str', default=None, no_log=True)
        ),
        mutually_exclusive = [["name", "source_json", "source_hcl"], ["source_json", "source_hcl"]],
        required_if = [
          ["state", "started", ["name"]],
          ["state", "stopped", ["name"]]
        ]
    )

    if not import_nomad:
        module.fail_json(msg='python-nomad is required for nomad_job ')

    if module.params.get('state') == 'created' and module.params.get('source_json') == None and module.params.get('source_hcl') == None:
       module.fail_json(msg='source hcl or json must be set ')

    certificate_ssl = (module.params.get('cert'), module.params.get('key'))

    nomad_client =  nomad.Nomad(
        host=module.params.get('host'), 
        secure=module.params.get('secure'),
        timeout=module.params.get('timeout'),
        verify=module.params.get('validate_certs'),
        cert=certificate_ssl,
        namespace=module.params.get('namespace'),
        token=module.params.get('token')
        )
    
    if module.params.get('state') == "created":

        if not module.params.get('source_json') == None:
            job_json = module.params.get('source_json')
            job_json = json.loads(job_json)
            job = dict()
            job['job'] = job_json
            try:
                result = nomad_client.jobs.register_job(job)
                changed = True
            except Exception as e:
                module.fail_json(msg=str(e))

        if not module.params.get('source_hcl') == None:

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
        
    if module.params.get('state') == "stopped":

        try:
            job_json = nomad_client.job.get_job(module.params.get('name'))
            if job_json['Status'] == 'dead':
                changed = False
                result = job_json
            else:
                result = nomad_client.job.deregister_job(module.params.get('name'))
                changed = True
        except Exception as e:
            module.fail_json(msg=str(e))

    if module.params.get('state') == "started":
    
        try:
            job = dict()
            job_json = nomad_client.job.get_job(module.params.get('name'))
            if job_json['Status'] == 'running':
                changed = False
                result = job_json
            else:
                job_json['Status'] = 'running'
                job_json['Stop'] = False
                job['job'] = job_json
                result = nomad_client.jobs.register_job(job)
                changed = True
        except Exception as e:
            module.fail_json(msg=str(e))


    module.exit_json(changed=changed, result=result)

def main():
    run()
if __name__ == "__main__":
    main()

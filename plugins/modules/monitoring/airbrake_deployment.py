#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Bruce Pennypacker <bruce@pennypacker.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: airbrake_deployment
author:
- "Bruce Pennypacker (@bpennypacker)"
- "Patrick Humpal (@phumpal)"
short_description: Notify airbrake about app deployments
description:
   - Notify airbrake about app deployments (see U(https://airbrake.io/docs/api/#deploys-v4)).
   - Parameter I(token) has been deprecated for community.general 0.2.0. Please remove entry.
options:
  project_id:
    description:
      - Airbrake PROJECT_ID
    required: false
    type: str
    version_added: '0.2.0'
  project_key:
    description:
      - Airbrake PROJECT_KEY.
    required: false
    type: str
    version_added: '0.2.0'
  environment:
    description:
      - The airbrake environment name, typically 'production', 'staging', etc.
    required: true
    type: str
  user:
    description:
      - The username of the person doing the deployment
    required: false
    type: str
  repo:
    description:
      - URL of the project repository
    required: false
    type: str
  revision:
    description:
      - A hash, number, tag, or other identifier showing what revision from version control was deployed
    required: false
    type: str
  version:
    description:
      - A string identifying what version was deployed
    required: false
    type: str
    version_added: '1.0.0'
  url:
    description:
      - Optional URL to submit the notification to. Use to send notifications to Airbrake-compliant tools like Errbit.
    required: false
    default: "https://api.airbrake.io/api/v4/projects/"
    type: str
  validate_certs:
    description:
      - If C(no), SSL certificates for the target url will not be validated. This should only be used
        on personally controlled sites using self-signed certificates.
    required: false
    default: 'yes'
    type: bool
  token:
     description:
      - This parameter (API token) has been deprecated in community.general 0.2.0. Please remove it from your tasks.
     required: false
     type: str

requirements: []
'''

EXAMPLES = '''
- name: Notify airbrake about an app deployment
  airbrake_deployment:
    project_id: '12345'
    project_key: 'AAAAAA'
    environment: staging
    user: ansible
    revision: '4.2'

- name: Notify airbrake about an app deployment, using git hash as revision
  airbrake_deployment:
    project_id: '12345'
    project_key: 'AAAAAA'
    environment: staging
    user: ansible
    revision: 'e54dd3a01f2c421b558ef33b5f79db936e2dcf15'
    version: '0.2.0'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six.moves.urllib.parse import urlencode


# ===========================================
# Module execution.
#

def main():

    module = AnsibleModule(
        argument_spec=dict(
            token=dict(required=False, no_log=True),
            project_id=dict(required=False, no_log=True),
            project_key=dict(required=False, no_log=True),
            environment=dict(required=True),
            user=dict(required=False),
            repo=dict(required=False),
            revision=dict(required=False),
            version=dict(required=False, type='str'),
            url=dict(required=False, default='https://api.airbrake.io/api/v4/projects/'),
            validate_certs=dict(default=True, type='bool'),
        ),
        supports_check_mode=True,
        required_together=[('project_id', 'project_key')],
        mutually_exclusive=[('project_id', 'token')],
    )

    # Build list of params
    params = {}

    # If we're in check mode, just exit pretending like we succeeded
    if module.check_mode:
        module.exit_json(changed=True)

    if module.params["token"]:
        # v2 API documented at https://airbrake.io/docs/legacy-xml-api/#tracking-deploys
        if module.params["environment"]:
            params["deploy[rails_env]"] = module.params["environment"]

        if module.params["user"]:
            params["deploy[local_username]"] = module.params["user"]

        if module.params["repo"]:
            params["deploy[scm_repository]"] = module.params["repo"]

        if module.params["revision"]:
            params["deploy[scm_revision]"] = module.params["revision"]

        # version not supported in v2 API; omit

        module.deprecate("Parameter 'token' is deprecated since community.general 0.2.0. Please remove "
                         "it and use 'project_id' and 'project_key' instead",
                         version='3.0.0', collection_name='community.general')  # was Ansible 2.14

        params["api_key"] = module.params["token"]

        # Allow sending to Airbrake compliant v2 APIs
        if module.params["url"] == 'https://api.airbrake.io/api/v4/projects/':
            url = 'https://api.airbrake.io/deploys.txt'
        else:
            url = module.params["url"]

        # Send the data to airbrake
        data = urlencode(params)
        response, info = fetch_url(module, url, data=data)

    if module.params["project_id"] and module.params["project_key"]:
        # v4 API documented at https://airbrake.io/docs/api/#create-deploy-v4
        if module.params["environment"]:
            params["environment"] = module.params["environment"]

        if module.params["user"]:
            params["username"] = module.params["user"]

        if module.params["repo"]:
            params["repository"] = module.params["repo"]

        if module.params["revision"]:
            params["revision"] = module.params["revision"]

        if module.params["version"]:
            params["version"] = module.params["version"]

        # Build deploy url
        url = module.params.get('url') + module.params["project_id"] + '/deploys?key=' + module.params["project_key"]
        json_body = module.jsonify(params)

        # Build header
        headers = {'Content-Type': 'application/json'}

        # Notify Airbrake of deploy
        response, info = fetch_url(module, url, data=json_body,
                                   headers=headers, method='POST')

    if info['status'] == 200 or info['status'] == 201:
        module.exit_json(changed=True)
    else:
        module.fail_json(msg="HTTP result code: %d connecting to %s" % (info['status'], url))


if __name__ == '__main__':
    main()

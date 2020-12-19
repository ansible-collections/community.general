#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Matt Coddington <coddington@gmail.com>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: newrelic_deployment
author:
    - "Davinder Pal (@116davinder)"
    - "Matt Coddington (@mcodd)"
short_description: Notify newrelic about app deployments
description:
   - Notify newrelic about app deployments
        (U(https://docs.newrelic.com/docs/apm/new-relic-apm/maintenance/record-deployments)).
options:
  token:
    description:
      - API token, to place in the x-api-key header.
    required: true
    type: str
  app_name:
    description:
      - The value of C(app_name) in the C(newrelic.yml) file used by the application.
      - Exactly one of I(app_name) or I(application_id) is required.
    required: false
    type: str
  application_id:
    description:
      - The I(application_id), found in the URL when viewing the application in RPM.
      - See U(https://rpm.newrelic.com/api/explore/applications/list).
      - Exactly one of I(app_name) or I(application_id) is required.
    required: false
    type: str
  changelog:
    description:
      - A list of changes for this deployment.
    required: false
    type: str
  description:
    description:
      - Text annotation for the deployment - notes for you.
    required: false
    type: str
  revision:
    description:
      - A revision number (for example, git commit SHA).
    required: true
    type: str
  appname:
    type: str
    description:
      - Name of the application. The value is not used for the v2 API.
      - This option has been deprecated and will be removed in community.general 4.0.0.
    required: false
  environment:
    type: str
    description:
      - Name of the environment for this deployment. The value is not used for the v2 API.
      - This option has been deprecated and will be removed in community.general 4.0.0.
    required: false
  validate_certs:
    description:
      - If C(no), SSL certificates will not be validated. The value is not used for the v2 API.
      - This should only be used on personally controlled sites using self-signed certificates.
      - This option has been deprecated and will be removed in community.general 4.0.0.
    required: false
    default: 'yes'
    type: bool
  user:
    description:
      - The name of the user/process that triggered this deployment
    required: false
    type: str
'''

EXAMPLES = '''
- name:  Notify newrelic about an app deployment
  community.general.newrelic_deployment:
    token: XXXXXXXXX
    app_name: ansible_app
    user: ansible_deployment_user
    revision: '1.X'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
import json


# ===========================================
# Module execution.
#

def main():

    module = AnsibleModule(
        argument_spec=dict(
            token=dict(required=True, no_log=True),
            app_name=dict(required=False),
            application_id=dict(required=False),
            changelog=dict(required=False),
            description=dict(required=False),
            revision=dict(required=True),
            user=dict(required=False),
            appname=dict(required=False, removed_in_version='4.0.0', removed_from_collection='community.general'),
            environment=dict(required=False, removed_in_version='4.0.0', removed_from_collection='community.general'),
            validate_certs=dict(default=True, type='bool', removed_in_version='4.0.0', removed_from_collection='community.general'),
        ),
        required_one_of=[['app_name', 'application_id']],
        mutually_exclusive=[['app_name', 'application_id']],
    )

    if module.params['app_name']:
        data = 'filter[name]=' + str(module.params['app_name'])
        newrelic_api = 'https://api.newrelic.com/v2/applications.json'
        headers = {'x-api-key': module.params['token'],
                   'Content-Type': 'application/x-www-form-urlencoded'}
        (resp, info) = fetch_url(module,
                                 newrelic_api,
                                 headers=headers,
                                 data=data,
                                 method='GET')
        if info['status'] != 200:
            module.fail_json(msg="unable to get application list from newrelic: %s" % info['msg'])
        else:
            body = json.loads(resp.read())
        if body is None:
            module.fail_json(msg='No Data for applications')
        else:
            app_id = body['applications'][0]['id']
            if app_id is None:
                module.fail_json(msg="App not found in NewRelic Registerd Applications List")
    else:
        app_id = module.params['application_id']

    # Send the data to NewRelic
    url = 'https://api.newrelic.com/v2/applications/' + str(app_id) + '/deployments.json'
    data = {
        'deployment': {
            'revision': str(module.params['revision']),
            'changelog': str(module.params['changelog']),
            'description': str(module.params['description']),
            'user': str(module.params['user']), }
    }

    headers = {'x-api-key': module.params['token'],
               'Content-Type': 'application/json'}
    (response, info) = fetch_url(module, url,
                                 data=module.jsonify(data),
                                 headers=headers, method='POST')
    if info['status'] == 201:
        module.exit_json(changed=True)
    else:
        module.fail_json(msg='unable to update newrelic: %s' % info['msg'])


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2013 Matt Coddington <coddington@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: newrelic_deployment
author: "Matt Coddington (@mcodd)"
short_description: Notify newrelic about app deployments
description:
  - Notify newrelic about app deployments (see https://docs.newrelic.com/docs/apm/new-relic-apm/maintenance/record-monitor-deployments/)
options:
  token:
    type: str
    description:
      - API token, to place in the Api-Key header.
    required: true
  app_name:
    type: str
    description:
      - (one of app_name or application_id are required) The value of app_name in the newrelic.yml file used by the application
    required: false
  application_id:
    type: str
    description:
      - (one of app_name or application_id are required) The application ID, found in the metadata of the application in APM
    required: false
  changelog:
    type: str
    description:
      - A list of changes for this deployment
    required: false
  description:
    type: str
    description:
      - Text annotation for the deployment - notes for you
    required: false
  revision:
    type: str
    description:
      - A revision number (e.g., git commit SHA)
    required: True
  user:
    type: str
    description:
      - The name of the user/process that triggered this deployment
    required: false
  appname:
    type: str
    description:
      - Name of the application.
      - This option has been deprecated and will be removed. Please do not use.
    required: false
  environment:
    type: str
    description:
      - The environment for this deployment.
      - This option has been deprecated and will be removed. Please do not use.
    required: false
  validate_certs:
    description:
      - If C(false), SSL certificates will not be validated. This should only be used
        on personally controlled sites using self-signed certificates.
      - This option has been deprecated and will be removed. Please do not use.
    required: false
    default: true
    type: bool
requirements: []
'''

EXAMPLES = '''
- name:  Notify newrelic about an app deployment
  community.general.newrelic_deployment:
    token: AAAAAA
    application_id: 12345678
    user: ansible deployment
    revision: '1.0'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six.moves.urllib.parse import quote
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
            appname=dict(required=False),
            environment=dict(required=False),
            validate_certs=dict(required=False, default=True, type='bool'),
        ),
        required_one_of=[['app_name', 'application_id']],
        supports_check_mode=True
    )

    # build list of params
    params = {}
    if module.params["app_name"] and module.params["application_id"]:
        module.fail_json(msg="only one of 'app_name' or 'application_id' can be set")

    app_id = None
    if module.params["app_name"]:
        app_id = get_application_id(module)
    elif module.params["application_id"]:
        app_id = module.params["application_id"]
    else:
        module.fail_json(msg="you must set one of 'app_name' or 'application_id'")

    if app_id is None:
        module.fail_json(msg="No application with name %s is found in NewRelic" % quote(module.params["app_name"], safe=''))

    for item in ["changelog", "description", "revision", "user"]:
        if module.params[item]:
            params[item] = module.params[item]

    # If we're in check mode, just exit pretending like we succeeded
    if module.check_mode:
        module.exit_json(changed=True)

    # Send the data to NewRelic
    url = "https://api.newrelic.com/v2/applications/%s/deployments.json" % quote(str(app_id), safe='')
    data = {
        'deployment': params
    }
    headers = {
        'Api-Key': module.params["token"],
        'Content-Type': 'application/json',
    }
    response, info = fetch_url(module, url, data=module.jsonify(data), headers=headers, method="POST")
    if info['status'] in (200, 201):
        module.exit_json(changed=True)
    else:
        module.fail_json(msg="Unable to update newrelic: %s" % info['msg'])


def get_application_id(module):
    url = "https://api.newrelic.com/v2/applications.json"
    data = "filter[name]=%s" % quote(module.params["app_name"], safe='')
    headers = {
        'Api-Key': quote(module.params["token"], safe=''),
    }
    response, info = fetch_url(module, url, data=data, headers=headers)
    if info['status'] not in (200, 201):
        module.fail_json(msg="unable to get application from newrelic: %s" % info['msg'])
        return None

    result = json.loads(response.read())
    if result is None or len(result["applications"]) == 0:
        module.fail_json(msg='No application found')
        return None
    return result["applications"][0]["id"]


if __name__ == '__main__':
    main()

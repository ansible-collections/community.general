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
  application_id:
    type: str
    description:
      - The application id, found in the metadata of the application in APM.
    required: true
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
    required: false
  user:
    type: str
    description:
      - The name of the user/process that triggered this deployment
    required: false
  validate_certs:
    description:
      - If C(false), SSL certificates will not be validated. This should only be used
        on personally controlled sites using self-signed certificates.
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
from ansible.module_utils.six.moves.urllib.parse import urlencode

# ===========================================
# Module execution.
#


def main():

    module = AnsibleModule(
        argument_spec=dict(
            token=dict(required=True, no_log=True),
            application_id=dict(required=True),
            changelog=dict(required=False),
            description=dict(required=False),
            revision=dict(required=False),
            user=dict(required=False),
            validate_certs=dict(default=True, type='bool'),
        ),
        supports_check_mode=True
    )

    # build list of params
    params = {}
    if not module.params["application_id"]:
        module.fail_json(msg="you must set the 'application_id'")

    for item in ["changelog", "description", "revision", "user"]:
        if module.params[item]:
            params[item] = module.params[item]

    # If we're in check mode, just exit pretending like we succeeded
    if module.check_mode:
        module.exit_json(changed=True)

    # Send the data to NewRelic
    url = "https://api.newrelic.com/v2/applications/%s/deployments.json" % module.params["application_id"]
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
        module.fail_json(msg="unable to update newrelic: %s" % info['msg'])


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2014 Benjamin Curtis <benjamin.curtis@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: honeybadger_deployment
author: "Benjamin Curtis (@stympy)"
short_description: Notify Honeybadger.io about app deployments
description:
  - Notify Honeybadger.io about app deployments (see U(http://docs.honeybadger.io/article/188-deployment-tracking)).
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  token:
    type: str
    description:
      - API token.
    required: true
  environment:
    type: str
    description:
      - The environment name, typically V(production), V(staging), and so on.
    required: true
  user:
    type: str
    description:
      - The username of the person doing the deployment.
  repo:
    type: str
    description:
      - URL of the project repository.
  revision:
    type: str
    description:
      - A hash, number, tag, or other identifier showing what revision was deployed.
  url:
    type: str
    description:
      - Optional URL to submit the notification to.
    default: "https://api.honeybadger.io/v1/deploys"
  validate_certs:
    description:
      - If V(false), SSL certificates for the target URL are not validated. This should only be used on personally controlled
        sites using self-signed certificates.
    type: bool
    default: true
"""

EXAMPLES = r"""
- name: Notify Honeybadger.io about an app deployment
  community.general.honeybadger_deployment:
    token: AAAAAA
    environment: staging
    user: ansible
    revision: b6826b8
    repo: 'git@github.com:user/repo.git'
"""

RETURN = """#"""

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.urls import fetch_url


# ===========================================
# Module execution.
#

def main():

    module = AnsibleModule(
        argument_spec=dict(
            token=dict(required=True, no_log=True),
            environment=dict(required=True),
            user=dict(required=False),
            repo=dict(),
            revision=dict(),
            url=dict(default='https://api.honeybadger.io/v1/deploys'),
            validate_certs=dict(default=True, type='bool'),
        ),
        supports_check_mode=True
    )

    params = {}

    if module.params["environment"]:
        params["deploy[environment]"] = module.params["environment"]

    if module.params["user"]:
        params["deploy[local_username]"] = module.params["user"]

    if module.params["repo"]:
        params["deploy[repository]"] = module.params["repo"]

    if module.params["revision"]:
        params["deploy[revision]"] = module.params["revision"]

    params["api_key"] = module.params["token"]

    url = module.params.get('url')

    # If we're in check mode, just exit pretending like we succeeded
    if module.check_mode:
        module.exit_json(changed=True)

    try:
        data = urlencode(params)
        response, info = fetch_url(module, url, data=data)
    except Exception as e:
        module.fail_json(msg='Unable to notify Honeybadger: %s' % to_native(e), exception=traceback.format_exc())
    else:
        if info['status'] == 201:
            module.exit_json(changed=True)
        else:
            module.fail_json(msg="HTTP result code: %d connecting to %s" % (info['status'], url))


if __name__ == '__main__':
    main()

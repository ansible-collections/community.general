#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: jenkins_build_info
short_description: Get information about Jenkins builds
version_added: 7.4.0
description:
  - Get information about Jenkins builds with Jenkins REST API.
requirements:
  - "python-jenkins >= 0.4.12"
author:
  - Juan Casanova (@juanmcasanova)
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
options:
  name:
    description:
      - Name of the Jenkins job to which the build belongs.
    required: true
    type: str
  build_number:
    description:
      - An integer which specifies a build of a job.
      - If not specified the last build information is returned.
    type: int
  password:
    description:
      - Password to authenticate with the Jenkins server.
    type: str
  token:
    description:
      - API token used to authenticate with the Jenkins server.
    type: str
  url:
    description:
      - URL of the Jenkins server.
    default: http://localhost:8080
    type: str
  user:
    description:
      - User to authenticate with the Jenkins server.
    type: str
"""

EXAMPLES = r"""
- name: Get information about a jenkins build using basic authentication
  community.general.jenkins_build_info:
    name: "test-check"
    build_number: 1
    user: admin
    password: asdfg
    url: http://localhost:8080

- name: Get information about a jenkins build anonymously
  community.general.jenkins_build_info:
    name: "stop-check"
    build_number: 3
    url: http://localhost:8080

- name: Get information about a jenkins build using token authentication
  community.general.jenkins_build_info:
    name: "delete-experiment"
    build_number: 30
    user: Jenkins
    token: abcdefghijklmnopqrstuvwxyz123456
    url: http://localhost:8080
"""

RETURN = r"""
name:
  description: Name of the jenkins job.
  returned: success
  type: str
  sample: "test-job"
state:
  description: State of the jenkins job.
  returned: success
  type: str
  sample: present
user:
  description: User used for authentication.
  returned: success
  type: str
  sample: admin
url:
  description: URL to connect to the Jenkins server.
  returned: success
  type: str
  sample: https://jenkins.mydomain.com
build_info:
  description: Build info of the jenkins job.
  returned: success
  type: dict
"""

import traceback

JENKINS_IMP_ERR = None
try:
    import jenkins
    python_jenkins_installed = True
except ImportError:
    JENKINS_IMP_ERR = traceback.format_exc()
    python_jenkins_installed = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


class JenkinsBuildInfo:

    def __init__(self, module):
        self.module = module

        self.name = module.params.get('name')
        self.password = module.params.get('password')
        self.token = module.params.get('token')
        self.user = module.params.get('user')
        self.jenkins_url = module.params.get('url')
        self.build_number = module.params.get('build_number')
        self.server = self.get_jenkins_connection()

        self.result = {
            'changed': False,
            'url': self.jenkins_url,
            'name': self.name,
            'user': self.user,
        }

    def get_jenkins_connection(self):
        try:
            if self.user and self.password:
                return jenkins.Jenkins(self.jenkins_url, self.user, self.password)
            elif self.user and self.token:
                return jenkins.Jenkins(self.jenkins_url, self.user, self.token)
            elif self.user and not (self.password or self.token):
                return jenkins.Jenkins(self.jenkins_url, self.user)
            else:
                return jenkins.Jenkins(self.jenkins_url)
        except Exception as e:
            self.module.fail_json(msg='Unable to connect to Jenkins server, %s' % to_native(e))

    def get_build_status(self):
        try:
            if self.build_number is None:
                job_info = self.server.get_job_info(self.name)
                self.build_number = job_info['lastBuild']['number']

            return self.server.get_build_info(self.name, self.build_number)
        except jenkins.JenkinsException as e:
            response = {}
            response["result"] = "ABSENT"
            return response
        except Exception as e:
            self.module.fail_json(msg='Unable to fetch build information, %s' % to_native(e),
                                  exception=traceback.format_exc())

    def get_result(self):
        result = self.result
        build_status = self.get_build_status()

        if build_status['result'] == "ABSENT":
            result['failed'] = True
        result['build_info'] = build_status

        return result


def test_dependencies(module):
    if not python_jenkins_installed:
        module.fail_json(
            msg=missing_required_lib("python-jenkins",
                                     url="https://python-jenkins.readthedocs.io/en/latest/install.html"),
            exception=JENKINS_IMP_ERR)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            build_number=dict(type='int'),
            name=dict(required=True),
            password=dict(no_log=True),
            token=dict(no_log=True),
            url=dict(default="http://localhost:8080"),
            user=dict(),
        ),
        mutually_exclusive=[['password', 'token']],
        supports_check_mode=True,
    )

    test_dependencies(module)
    jenkins_build_info = JenkinsBuildInfo(module)

    result = jenkins_build_info.get_result()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

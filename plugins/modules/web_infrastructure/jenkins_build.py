#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: jenkins_build
short_description: Manage jenkins builds
version_added: 2.2.0
description:
    - Manage Jenkins builds with Jenkins REST API.
requirements:
  - "python-jenkins >= 0.4.12"
author:
  - Brett Milford (@brettmilford)
  - Tong He (@unnecessary-username)
options:
  args:
    description:
      - A list of parameters to pass to the build.
    type: dict
  name:
    description:
      - Name of the Jenkins job to build.
    required: true
    type: str
  build_number:
    description:
      - An integer which specifies a build of a job. Is required to remove a build from the queue.
    type: int
  password:
    description:
      - Password to authenticate with the Jenkins server.
    type: str
  state:
    description:
      - Attribute that specifies if the build is to be created, deleted or stopped.
      - The C(stopped) state has been added in community.general 3.3.0.
    default: present
    choices: ['present', 'absent', 'stopped']
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
'''

EXAMPLES = '''
- name: Create a jenkins build using basic authentication
  community.general.jenkins_build:
    name: "test-check"
    args:
      cloud: "test"
      availability_zone: "test_az"
    state: present
    user: admin
    password: asdfg
    url: http://localhost:8080

- name: Stop a running jenkins build anonymously
  community.general.jenkins_build:
    name: "stop-check"
    build_number: 3
    state: stopped
    url: http://localhost:8080

- name: Delete a jenkins build using token authentication
  community.general.jenkins_build:
    name: "delete-experiment"
    build_number: 30
    state: absent
    user: Jenkins
    token: abcdefghijklmnopqrstuvwxyz123456
    url: http://localhost:8080
'''

RETURN = '''
---
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
  description: Url to connect to the Jenkins server.
  returned: success
  type: str
  sample: https://jenkins.mydomain.com
build_info:
  description: Build info of the jenkins job.
  returned: success
  type: dict
'''

import traceback
from time import sleep

JENKINS_IMP_ERR = None
try:
    import jenkins
    python_jenkins_installed = True
except ImportError:
    JENKINS_IMP_ERR = traceback.format_exc()
    python_jenkins_installed = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


class JenkinsBuild:

    def __init__(self, module):
        self.module = module

        self.name = module.params.get('name')
        self.password = module.params.get('password')
        self.args = module.params.get('args')
        self.state = module.params.get('state')
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
            'state': self.state,
        }

        self.EXCL_STATE = "excluded state"

    def get_jenkins_connection(self):
        try:
            if (self.user and self.password):
                return jenkins.Jenkins(self.jenkins_url, self.user, self.password)
            elif (self.user and self.token):
                return jenkins.Jenkins(self.jenkins_url, self.user, self.token)
            elif (self.user and not (self.password or self.token)):
                return jenkins.Jenkins(self.jenkins_url, self.user)
            else:
                return jenkins.Jenkins(self.jenkins_url)
        except Exception as e:
            self.module.fail_json(msg='Unable to connect to Jenkins server, %s' % to_native(e))

    def get_next_build(self):
        try:
            build_number = self.server.get_job_info(self.name)['nextBuildNumber']
        except Exception as e:
            self.module.fail_json(msg='Unable to get job info from Jenkins server, %s' % to_native(e),
                                  exception=traceback.format_exc())

        return build_number

    def get_build_status(self):
        try:
            response = self.server.get_build_info(self.name, self.build_number)
            return response

        except Exception as e:
            self.module.fail_json(msg='Unable to fetch build information, %s' % to_native(e),
                                  exception=traceback.format_exc())

    def present_build(self):
        self.build_number = self.get_next_build()

        try:
            if self.args is None:
                self.server.build_job(self.name)
            else:
                self.server.build_job(self.name, self.args)
        except Exception as e:
            self.module.fail_json(msg='Unable to create build for %s: %s' % (self.jenkins_url, to_native(e)),
                                  exception=traceback.format_exc())

    def stopped_build(self):
        build_info = None
        try:
            build_info = self.server.get_build_info(self.name, self.build_number)
            if build_info['building'] is True:
                self.server.stop_build(self.name, self.build_number)
        except Exception as e:
            self.module.fail_json(msg='Unable to stop build for %s: %s' % (self.jenkins_url, to_native(e)),
                                  exception=traceback.format_exc())
        else:
            if build_info['building'] is False:
                self.module.exit_json(**self.result)

    def absent_build(self):
        try:
            self.server.delete_build(self.name, self.build_number)
        except Exception as e:
            self.module.fail_json(msg='Unable to delete build for %s: %s' % (self.jenkins_url, to_native(e)),
                                  exception=traceback.format_exc())

    def get_result(self):
        result = self.result
        build_status = self.get_build_status()

        if build_status['result'] is None:
            sleep(10)
            self.get_result()
        else:
            if self.state == "stopped" and build_status['result'] == "ABORTED":
                result['changed'] = True
                result['build_info'] = build_status
            elif build_status['result'] == "SUCCESS":
                result['changed'] = True
                result['build_info'] = build_status
            else:
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
            args=dict(type='dict'),
            build_number=dict(type='int'),
            name=dict(required=True),
            password=dict(no_log=True),
            state=dict(choices=['present', 'absent', 'stopped'], default="present"),
            token=dict(no_log=True),
            url=dict(default="http://localhost:8080"),
            user=dict(),
        ),
        mutually_exclusive=[['password', 'token']],
        required_if=[['state', 'absent', ['build_number'], True], ['state', 'stopped', ['build_number'], True]],
    )

    test_dependencies(module)
    jenkins_build = JenkinsBuild(module)

    if module.params.get('state') == "present":
        jenkins_build.present_build()
    elif module.params.get('state') == "stopped":
        jenkins_build.stopped_build()
    else:
        jenkins_build.absent_build()

    sleep(10)
    result = jenkins_build.get_result()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

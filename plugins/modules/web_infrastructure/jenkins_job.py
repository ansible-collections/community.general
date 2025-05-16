#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: jenkins_job
short_description: Manage jenkins jobs
description:
    - Manage Jenkins jobs by using Jenkins REST API.
requirements:
  - "python-jenkins >= 0.4.12"
author: "Sergio Millan Rodriguez (@sermilrod)"
options:
  config:
    type: str
    description:
      - config in XML format.
      - Required if job does not yet exist.
      - Mutually exclusive with C(enabled).
      - Considered if C(state=present).
    required: false
  enabled:
    description:
      - Whether the job should be enabled or disabled.
      - Mutually exclusive with C(config).
      - Considered if C(state=present).
    type: bool
    required: false
  name:
    type: str
    description:
      - Name of the Jenkins job.
    required: true
  password:
    type: str
    description:
      - Password to authenticate with the Jenkins server.
    required: false
  state:
    type: str
    description:
      - Attribute that specifies if the job has to be created or deleted.
    required: false
    default: present
    choices: ['present', 'absent']
  token:
    type: str
    description:
      - API token used to authenticate alternatively to password.
    required: false
  url:
    type: str
    description:
      - URL where the Jenkins server is accessible.
    required: false
    default: http://localhost:8080
  user:
    type: str
    description:
       - User to authenticate with the Jenkins server.
    required: false
  validate_certs:
    type: bool
    default: yes
    description:
      - If set to C(no), the SSL certificates will not be validated.
        This should only set to C(no) used on personally controlled sites
        using self-signed certificates as it avoids verifying the source site.
      - The C(python-jenkins) library only handles this by using the environment variable C(PYTHONHTTPSVERIFY).
    version_added: 2.3.0
'''

EXAMPLES = '''
- name: Create a jenkins job using basic authentication
  community.general.jenkins_job:
    config: "{{ lookup('file', 'templates/test.xml') }}"
    name: test
    password: admin
    url: http://localhost:8080
    user: admin

- name: Create a jenkins job using the token
  community.general.jenkins_job:
    config: "{{ lookup('template', 'templates/test.xml.j2') }}"
    name: test
    token: asdfasfasfasdfasdfadfasfasdfasdfc
    url: http://localhost:8080
    user: admin

- name: Delete a jenkins job using basic authentication
  community.general.jenkins_job:
    name: test
    password: admin
    state: absent
    url: http://localhost:8080
    user: admin

- name: Delete a jenkins job using the token
  community.general.jenkins_job:
    name: test
    token: asdfasfasfasdfasdfadfasfasdfasdfc
    state: absent
    url: http://localhost:8080
    user: admin

- name: Disable a jenkins job using basic authentication
  community.general.jenkins_job:
    name: test
    password: admin
    enabled: False
    url: http://localhost:8080
    user: admin

- name: Disable a jenkins job using the token
  community.general.jenkins_job:
    name: test
    token: asdfasfasfasdfasdfadfasfasdfasdfc
    enabled: False
    url: http://localhost:8080
    user: admin
'''

RETURN = '''
---
name:
  description: Name of the jenkins job.
  returned: success
  type: str
  sample: test-job
state:
  description: State of the jenkins job.
  returned: success
  type: str
  sample: present
enabled:
  description: Whether the jenkins job is enabled or not.
  returned: success
  type: bool
  sample: true
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
'''

import os
import traceback
import xml.etree.ElementTree as ET

JENKINS_IMP_ERR = None
try:
    import jenkins
    python_jenkins_installed = True
except ImportError:
    JENKINS_IMP_ERR = traceback.format_exc()
    python_jenkins_installed = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


class JenkinsJob(object):

    def __init__(self, module):
        self.module = module

        self.config = module.params.get('config')
        self.name = module.params.get('name')
        self.password = module.params.get('password')
        self.state = module.params.get('state')
        self.enabled = module.params.get('enabled')
        self.token = module.params.get('token')
        self.user = module.params.get('user')
        self.jenkins_url = module.params.get('url')
        self.server = self.get_jenkins_connection()

        self.result = {
            'changed': False,
            'url': self.jenkins_url,
            'name': self.name,
            'user': self.user,
            'state': self.state,
            'diff': {
                'before': "",
                'after': ""
            }
        }

        self.EXCL_STATE = "excluded state"
        if not module.params['validate_certs']:
            os.environ['PYTHONHTTPSVERIFY'] = '0'

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
            self.module.fail_json(msg='Unable to connect to Jenkins server, %s' % to_native(e), exception=traceback.format_exc())

    def get_job_status(self):
        try:
            response = self.server.get_job_info(self.name)
            if "color" not in response:
                return self.EXCL_STATE
            else:
                return to_native(response['color'])

        except Exception as e:
            self.module.fail_json(msg='Unable to fetch job information, %s' % to_native(e), exception=traceback.format_exc())

    def job_exists(self):
        try:
            return bool(self.server.job_exists(self.name))
        except Exception as e:
            self.module.fail_json(msg='Unable to validate if job exists, %s for %s' % (to_native(e), self.jenkins_url),
                                  exception=traceback.format_exc())

    def get_config(self):
        return job_config_to_string(self.config)

    def get_current_config(self):
        return job_config_to_string(self.server.get_job_config(self.name).encode('utf-8'))

    def has_config_changed(self):
        # config is optional, if not provided we keep the current config as is
        if self.config is None:
            return False

        config_file = self.get_config()
        machine_file = self.get_current_config()

        self.result['diff']['after'] = config_file
        self.result['diff']['before'] = machine_file

        if machine_file != config_file:
            return True
        return False

    def present_job(self):
        if self.config is None and self.enabled is None:
            self.module.fail_json(msg='one of the following params is required on state=present: config,enabled')

        if not self.job_exists():
            self.create_job()
        else:
            self.update_job()

    def has_state_changed(self, status):
        # Keep in current state if enabled arg_spec is not given
        if self.enabled is None:
            return False

        return (self.enabled is False and status != "disabled") or (self.enabled is True and status == "disabled")

    def switch_state(self):
        if self.enabled is False:
            self.server.disable_job(self.name)
        else:
            self.server.enable_job(self.name)

    def update_job(self):
        try:
            status = self.get_job_status()

            # Handle job config
            if self.has_config_changed():
                self.result['changed'] = True
                if not self.module.check_mode:
                    self.server.reconfig_job(self.name, self.get_config())

            # Handle job disable/enable
            elif status != self.EXCL_STATE and self.has_state_changed(status):
                self.result['changed'] = True
                if not self.module.check_mode:
                    self.switch_state()

        except Exception as e:
            self.module.fail_json(msg='Unable to reconfigure job, %s for %s' % (to_native(e), self.jenkins_url),
                                  exception=traceback.format_exc())

    def create_job(self):
        if self.config is None:
            self.module.fail_json(msg='missing required param: config')

        self.result['changed'] = True
        try:
            config_file = self.get_config()
            self.result['diff']['after'] = config_file
            if not self.module.check_mode:
                self.server.create_job(self.name, config_file)
        except Exception as e:
            self.module.fail_json(msg='Unable to create job, %s for %s' % (to_native(e), self.jenkins_url),
                                  exception=traceback.format_exc())

    def absent_job(self):
        if self.job_exists():
            self.result['changed'] = True
            self.result['diff']['before'] = self.get_current_config()
            if not self.module.check_mode:
                try:
                    self.server.delete_job(self.name)
                except Exception as e:
                    self.module.fail_json(msg='Unable to delete job, %s for %s' % (to_native(e), self.jenkins_url),
                                          exception=traceback.format_exc())

    def get_result(self):
        result = self.result
        if self.job_exists():
            result['enabled'] = self.get_job_status() != "disabled"
        else:
            result['enabled'] = None
        return result


def test_dependencies(module):
    if not python_jenkins_installed:
        module.fail_json(
            msg=missing_required_lib("python-jenkins",
                                     url="https://python-jenkins.readthedocs.io/en/latest/install.html"),
            exception=JENKINS_IMP_ERR)


def job_config_to_string(xml_str):
    return ET.tostring(ET.fromstring(xml_str)).decode('ascii')


def main():
    module = AnsibleModule(
        argument_spec=dict(
            config=dict(type='str', required=False),
            name=dict(type='str', required=True),
            password=dict(type='str', required=False, no_log=True),
            state=dict(type='str', required=False, choices=['present', 'absent'], default="present"),
            enabled=dict(required=False, type='bool'),
            token=dict(type='str', required=False, no_log=True),
            url=dict(type='str', required=False, default="http://localhost:8080"),
            user=dict(type='str', required=False),
            validate_certs=dict(type='bool', default=True),
        ),
        mutually_exclusive=[
            ['password', 'token'],
            ['config', 'enabled'],
        ],
        supports_check_mode=True,
    )

    test_dependencies(module)
    jenkins_job = JenkinsJob(module)

    if module.params.get('state') == "present":
        jenkins_job.present_job()
    else:
        jenkins_job.absent_job()

    result = jenkins_job.get_result()
    module.exit_json(**result)


if __name__ == '__main__':
    main()

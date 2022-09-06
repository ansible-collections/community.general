#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) Ansible Project
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: jenkins_job_info
short_description: Get information about Jenkins jobs
description:
  - This module can be used to query information about which Jenkins jobs which already exists.
  - This module was called C(jenkins_job_info) before Ansible 2.9. The usage did not change.
requirements:
  - "python-jenkins >= 0.4.12"
options:
  name:
    type: str
    description:
      - Exact name of the Jenkins job to fetch information about.
  glob:
    type: str
    description:
      - A shell glob of Jenkins job names to fetch information about.
  color:
    type: str
    description:
      - Only fetch jobs with the given status color.
  password:
    type: str
    description:
      - Password to authenticate with the Jenkins server.
      - This is mutually exclusive with I(token).
  token:
    type: str
    description:
      - API token used to authenticate with the Jenkins server.
      - This is mutually exclusive with I(password).
  url:
    type: str
    description:
      - URL where the Jenkins server is accessible.
    default: http://localhost:8080
  user:
    type: str
    description:
       - User to authenticate with the Jenkins server.
  validate_certs:
    description:
       - If set to C(False), the SSL certificates will not be validated.
       - This should only set to C(False) used on personally controlled sites using self-signed certificates.
    default: true
    type: bool
author:
  - "Chris St. Pierre (@stpierre)"
'''

EXAMPLES = '''
# Get all Jenkins jobs anonymously
- community.general.jenkins_job_info:
    user: admin
  register: my_jenkins_job_info

# Get all Jenkins jobs using basic auth
- community.general.jenkins_job_info:
    user: admin
    password: hunter2
  register: my_jenkins_job_info

# Get all Jenkins jobs using the token
- community.general.jenkins_job_info:
    user: admin
    token: abcdefghijklmnop
  register: my_jenkins_job_info

# Get info about a single job using basic auth
- community.general.jenkins_job_info:
    name: some-job-name
    user: admin
    password: hunter2
  register: my_jenkins_job_info

# Get info about a single job in a folder using basic auth
- community.general.jenkins_job_info:
    name: some-folder-name/some-job-name
    user: admin
    password: hunter2
  register: my_jenkins_job_info

# Get info about jobs matching a shell glob using basic auth
- community.general.jenkins_job_info:
    glob: some-job-*
    user: admin
    password: hunter2
  register: my_jenkins_job_info

# Get info about all failing jobs using basic auth
- community.general.jenkins_job_info:
    color: red
    user: admin
    password: hunter2
  register: my_jenkins_job_info

# Get info about passing jobs matching a shell glob using basic auth
- community.general.jenkins_job_info:
    name: some-job-*
    color: blue
    user: admin
    password: hunter2
  register: my_jenkins_job_info

- name: Get the info from custom URL with token and validate_certs=False
  community.general.jenkins_job_info:
    user: admin
    token: 126df5c60d66c66e3b75b11104a16a8a
    url: https://jenkins.example.com
    validate_certs: false
  register: my_jenkins_job_info
'''

RETURN = '''
---
jobs:
  description: All jobs found matching the specified criteria
  returned: success
  type: list
  sample:
    [
        {
            "name": "test-job",
            "fullname": "test-folder/test-job",
            "url": "http://localhost:8080/job/test-job/",
            "color": "blue"
        },
    ]
'''

import ssl
import fnmatch
import traceback

JENKINS_IMP_ERR = None
try:
    import jenkins
    HAS_JENKINS = True
except ImportError:
    JENKINS_IMP_ERR = traceback.format_exc()
    HAS_JENKINS = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


def get_jenkins_connection(module):
    url = module.params["url"]
    username = module.params.get("user")
    password = module.params.get("password")
    token = module.params.get("token")

    validate_certs = module.params.get('validate_certs')
    if not validate_certs and hasattr(ssl, 'SSLContext'):
        ssl._create_default_https_context = ssl._create_unverified_context
    if validate_certs and not hasattr(ssl, 'SSLContext'):
        module.fail_json(msg="Module does not support changing verification mode with python < 2.7.9."
                             " Either update Python or use validate_certs=false.")

    if username and (password or token):
        return jenkins.Jenkins(url, username, password or token)
    elif username:
        return jenkins.Jenkins(url, username)
    else:
        return jenkins.Jenkins(url)


def test_dependencies(module):
    if not HAS_JENKINS:
        module.fail_json(
            msg=missing_required_lib("python-jenkins",
                                     url="https://python-jenkins.readthedocs.io/en/latest/install.html"),
            exception=JENKINS_IMP_ERR)


def get_jobs(module):
    jenkins_conn = get_jenkins_connection(module)
    jobs = []
    if module.params.get("name"):
        try:
            job_info = jenkins_conn.get_job_info(module.params.get("name"))
        except jenkins.NotFoundException:
            pass
        else:
            jobs.append({
                "name": job_info["name"],
                "fullname": job_info["fullName"],
                "url": job_info["url"],
                "color": job_info["color"]
            })

    else:
        all_jobs = jenkins_conn.get_all_jobs()
        if module.params.get("glob"):
            jobs.extend(
                j for j in all_jobs
                if fnmatch.fnmatch(j["fullname"], module.params.get("glob")))
        else:
            jobs = all_jobs
        # python-jenkins includes the internal Jenkins class used for each job
        # in its return value; we strip that out because the leading underscore
        # (and the fact that it's not documented in the python-jenkins docs)
        # indicates that it's not part of the dependable public interface.
        for job in jobs:
            if "_class" in job:
                del job["_class"]

    if module.params.get("color"):
        jobs = [j for j in jobs if j["color"] == module.params.get("color")]

    return jobs


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str'),
            glob=dict(type='str'),
            color=dict(type='str'),
            password=dict(type='str', no_log=True),
            token=dict(type='str', no_log=True),
            url=dict(type='str', default="http://localhost:8080"),
            user=dict(type='str'),
            validate_certs=dict(type='bool', default=True),
        ),
        mutually_exclusive=[
            ['password', 'token'],
            ['name', 'glob'],
        ],
        supports_check_mode=True,
    )

    test_dependencies(module)
    jobs = list()

    try:
        jobs = get_jobs(module)
    except jenkins.JenkinsException as err:
        module.fail_json(
            msg='Unable to connect to Jenkins server, %s' % to_native(err),
            exception=traceback.format_exc())

    module.exit_json(changed=False, jobs=jobs)


if __name__ == '__main__':
    main()

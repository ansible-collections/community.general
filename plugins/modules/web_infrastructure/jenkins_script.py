#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2016, James Hogarth <james.hogarth@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
author: James Hogarth (@hogarthj)
module: jenkins_script
short_description: Executes a groovy script in the jenkins instance
description:
    - The C(jenkins_script) module takes a script plus a dict of values
      to use within the script and returns the result of the script being run.

options:
  script:
    type: str
    description:
      - The groovy script to be executed.
        This gets passed as a string Template if args is defined.
    required: true
  url:
    type: str
    description:
      - The jenkins server to execute the script against. The default is a local
        jenkins instance that is not being proxied through a webserver.
    default: http://localhost:8080
  validate_certs:
    description:
      - If set to C(no), the SSL certificates will not be validated.
        This should only set to C(no) used on personally controlled sites
        using self-signed certificates as it avoids verifying the source site.
    type: bool
    default: 'yes'
  user:
    type: str
    description:
      - The username to connect to the jenkins server with.
  password:
    type: str
    description:
      - The password to connect to the jenkins server with.
  timeout:
    type: int
    description:
      - The request timeout in seconds
    default: 10
  args:
    type: dict
    description:
      - A dict of key-value pairs used in formatting the script using string.Template (see https://docs.python.org/2/library/string.html#template-strings).

notes:
    - Since the script can do anything this does not report on changes.
      Knowing the script is being run it's important to set changed_when
      for the ansible output to be clear on any alterations made.

'''

EXAMPLES = '''
- name: Obtaining a list of plugins
  community.general.jenkins_script:
    script: 'println(Jenkins.instance.pluginManager.plugins)'
    user: admin
    password: admin

- name: Setting master using a variable to hold a more complicate script
  ansible.builtin.set_fact:
    setmaster_mode: |
        import jenkins.model.*
        instance = Jenkins.getInstance()
        instance.setMode(${jenkins_mode})
        instance.save()

- name: Use the variable as the script
  community.general.jenkins_script:
    script: "{{ setmaster_mode }}"
    args:
      jenkins_mode: Node.Mode.EXCLUSIVE

- name: Interacting with an untrusted HTTPS connection
  community.general.jenkins_script:
    script: "println(Jenkins.instance.pluginManager.plugins)"
    user: admin
    password: admin
    url: https://localhost
    validate_certs: no
'''

RETURN = '''
output:
    description: Result of script
    returned: success
    type: str
    sample: 'Result: true'
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import http_cookiejar as cookiejar
from ansible.module_utils.six.moves.urllib.parse import urlencode
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.common.text.converters import to_native


def is_csrf_protection_enabled(module):
    resp, info = fetch_url(module,
                           module.params['url'] + '/api/json',
                           timeout=module.params['timeout'],
                           method='GET')
    if info["status"] != 200:
        module.fail_json(msg="HTTP error " + str(info["status"]) + " " + info["msg"], output='')

    content = to_native(resp.read())
    return json.loads(content).get('useCrumbs', False)


def get_crumb(module, cookies):
    resp, info = fetch_url(module,
                           module.params['url'] + '/crumbIssuer/api/json',
                           method='GET',
                           timeout=module.params['timeout'],
                           cookies=cookies)
    if info["status"] != 200:
        module.fail_json(msg="HTTP error " + str(info["status"]) + " " + info["msg"], output='')

    content = to_native(resp.read())
    return json.loads(content)


def main():

    module = AnsibleModule(
        argument_spec=dict(
            script=dict(required=True, type="str"),
            url=dict(required=False, type="str", default="http://localhost:8080"),
            validate_certs=dict(required=False, type="bool", default=True),
            user=dict(required=False, type="str", default=None),
            password=dict(required=False, no_log=True, type="str", default=None),
            timeout=dict(required=False, type="int", default=10),
            args=dict(required=False, type="dict", default=None)
        )
    )

    if module.params['user'] is not None:
        if module.params['password'] is None:
            module.fail_json(msg="password required when user provided", output='')
        module.params['url_username'] = module.params['user']
        module.params['url_password'] = module.params['password']
        module.params['force_basic_auth'] = True

    if module.params['args'] is not None:
        from string import Template
        try:
            script_contents = Template(module.params['script']).substitute(module.params['args'])
        except KeyError as err:
            module.fail_json(msg="Error with templating variable: %s" % err, output='')
    else:
        script_contents = module.params['script']

    headers = {}
    cookies = None
    if is_csrf_protection_enabled(module):
        cookies = cookiejar.LWPCookieJar()
        crumb = get_crumb(module, cookies)
        headers = {crumb['crumbRequestField']: crumb['crumb']}

    resp, info = fetch_url(module,
                           module.params['url'] + "/scriptText",
                           data=urlencode({'script': script_contents}),
                           headers=headers,
                           method="POST",
                           timeout=module.params['timeout'],
                           cookies=cookies)

    if info["status"] != 200:
        module.fail_json(msg="HTTP error " + str(info["status"]) + " " + info["msg"], output='')

    result = to_native(resp.read())

    if 'Exception:' in result and 'at java.lang.Thread' in result:
        module.fail_json(msg="script failed with stacktrace:\n " + result, output='')

    module.exit_json(
        output=result,
    )


if __name__ == '__main__':
    main()

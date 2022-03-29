#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''

module: stackdriver
short_description: Send code deploy and annotation events to stackdriver
description:
  - Send code deploy and annotation events to Stackdriver
author: "Ben Whaley (@bwhaley)"
options:
  key:
    type: str
    description:
      - API key.
    required: true
  event:
    type: str
    description:
      - The type of event to send, either annotation or deploy
    choices: ['annotation', 'deploy']
    required: true
  revision_id:
    type: str
    description:
      - The revision of the code that was deployed. Required for deploy events
  deployed_by:
    type: str
    description:
      - The person or robot responsible for deploying the code
    default: "Ansible"
  deployed_to:
    type: str
    description:
      - "The environment code was deployed to. (ie: development, staging, production)"
  repository:
    type: str
    description:
      - The repository (or project) deployed
  msg:
    type: str
    description:
      - The contents of the annotation message, in plain text.  Limited to 256 characters. Required for annotation.
  annotated_by:
    type: str
    description:
      - The person or robot who the annotation should be attributed to.
    default: "Ansible"
  level:
    type: str
    description:
      - one of INFO/WARN/ERROR, defaults to INFO if not supplied.  May affect display.
    choices: ['INFO', 'WARN', 'ERROR']
    default: 'INFO'
  instance_id:
    type: str
    description:
      - id of an EC2 instance that this event should be attached to, which will limit the contexts where this event is shown
  event_epoch:
    type: str
    description:
      - "Unix timestamp of where the event should appear in the timeline, defaults to now. Be careful with this."
'''

EXAMPLES = '''
- name: Send a code deploy event to stackdriver
  community.general.stackdriver:
    key: AAAAAA
    event: deploy
    deployed_to: production
    deployed_by: leeroyjenkins
    repository: MyWebApp
    revision_id: abcd123

- name: Send an annotation event to stackdriver
  community.general.stackdriver:
    key: AAAAAA
    event: annotation
    msg: Greetings from Ansible
    annotated_by: leeroyjenkins
    level: WARN
    instance_id: i-abcd1234
'''

# ===========================================
# Stackdriver module specific support methods.
#

import json
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.urls import fetch_url


def send_deploy_event(module, key, revision_id, deployed_by='Ansible', deployed_to=None, repository=None):
    """Send a deploy event to Stackdriver"""
    deploy_api = "https://event-gateway.stackdriver.com/v1/deployevent"

    params = {}
    params['revision_id'] = revision_id
    params['deployed_by'] = deployed_by
    if deployed_to:
        params['deployed_to'] = deployed_to
    if repository:
        params['repository'] = repository

    return do_send_request(module, deploy_api, params, key)


def send_annotation_event(module, key, msg, annotated_by='Ansible', level=None, instance_id=None, event_epoch=None):
    """Send an annotation event to Stackdriver"""
    annotation_api = "https://event-gateway.stackdriver.com/v1/annotationevent"

    params = {}
    params['message'] = msg
    if annotated_by:
        params['annotated_by'] = annotated_by
    if level:
        params['level'] = level
    if instance_id:
        params['instance_id'] = instance_id
    if event_epoch:
        params['event_epoch'] = event_epoch

    return do_send_request(module, annotation_api, params, key)


def do_send_request(module, url, params, key):
    data = json.dumps(params)
    headers = {
        'Content-Type': 'application/json',
        'x-stackdriver-apikey': key
    }
    response, info = fetch_url(module, url, headers=headers, data=data, method='POST')
    if info['status'] != 200:
        module.fail_json(msg="Unable to send msg: %s" % info['msg'])


# ===========================================
# Module execution.
#

def main():

    module = AnsibleModule(
        argument_spec=dict(  # @TODO add types
            key=dict(required=True, no_log=True),
            event=dict(required=True, choices=['deploy', 'annotation']),
            msg=dict(),
            revision_id=dict(),
            annotated_by=dict(default='Ansible'),
            level=dict(default='INFO', choices=['INFO', 'WARN', 'ERROR']),
            instance_id=dict(),
            event_epoch=dict(),  # @TODO int?
            deployed_by=dict(default='Ansible'),
            deployed_to=dict(),
            repository=dict(),
        ),
        supports_check_mode=True
    )

    key = module.params["key"]
    event = module.params["event"]

    # Annotation params
    msg = module.params["msg"]
    annotated_by = module.params["annotated_by"]
    level = module.params["level"]
    instance_id = module.params["instance_id"]
    event_epoch = module.params["event_epoch"]

    # Deploy params
    revision_id = module.params["revision_id"]
    deployed_by = module.params["deployed_by"]
    deployed_to = module.params["deployed_to"]
    repository = module.params["repository"]

    ##################################################################
    # deploy requires revision_id
    # annotation requires msg
    # We verify these manually
    ##################################################################

    if event == 'deploy':
        if not revision_id:
            module.fail_json(msg="revision_id required for deploy events")
        try:
            send_deploy_event(module, key, revision_id, deployed_by, deployed_to, repository)
        except Exception as e:
            module.fail_json(msg="unable to sent deploy event: %s" % to_native(e),
                             exception=traceback.format_exc())

    if event == 'annotation':
        if not msg:
            module.fail_json(msg="msg required for annotation events")
        try:
            send_annotation_event(module, key, msg, annotated_by, level, instance_id, event_epoch)
        except Exception as e:
            module.fail_json(msg="unable to sent annotation event: %s" % to_native(e),
                             exception=traceback.format_exc())

    changed = True
    module.exit_json(changed=changed, deployed_by=deployed_by)


if __name__ == '__main__':
    main()

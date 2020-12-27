#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2014, Steve Smith <ssmith@atlassian.com>
# Atlassian open-source approval reference OSR-76.
#
# (c) 2020, Per Abildgaard Toft <per@minfejl.dk> Search and update function
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: jira
short_description: create and modify issues in a JIRA instance
description:
  - Create and modify issues in a JIRA instance.

options:
  uri:
    type: str
    required: true
    description:
      - Base URI for the JIRA instance.

  operation:
    type: str
    required: true
    aliases: [ command ]
    choices: [ comment, create, edit, fetch, link, search, transition, update ]
    description:
      - The operation to perform.

  username:
    type: str
    required: true
    description:
      - The username to log-in with.

  password:
    type: str
    required: true
    description:
      - The password to log-in with.

  project:
    type: str
    required: false
    description:
      - The project for this operation. Required for issue creation.

  summary:
    type: str
    required: false
    description:
     - The issue summary, where appropriate.

  description:
    type: str
    required: false
    description:
     - The issue description, where appropriate.

  issuetype:
    type: str
    required: false
    description:
     - The issue type, for issue creation.

  issue:
    type: str
    required: false
    description:
     - An existing issue key to operate on.
    aliases: ['ticket']

  comment:
    type: str
    required: false
    description:
     - The comment text to add.

  status:
    type: str
    required: false
    description:
     - The desired status; only relevant for the transition operation.

  assignee:
    type: str
    required: false
    description:
     - Sets the assignee on create or transition operations. Note not all transitions will allow this.

  linktype:
    type: str
    required: false
    description:
     - Set type of link, when action 'link' selected.

  inwardissue:
    type: str
    required: false
    description:
     - Set issue from which link will be created.

  outwardissue:
    type: str
    required: false
    description:
     - Set issue to which link will be created.

  fields:
    type: dict
    required: false
    description:
     - This is a free-form data structure that can contain arbitrary data. This is passed directly to the JIRA REST API
       (possibly after merging with other required data, as when passed to create). See examples for more information,
       and the JIRA REST API for the structure required for various fields.

  jql:
    required: false
    description:
     - Query JIRA in JQL Syntax, e.g. 'CMDB Hostname'='test.example.com'.
    type: str
    version_added: '0.2.0'

  maxresults:
    required: false
    description:
     - Limit the result of I(operation=search). If no value is specified, the default jira limit will be used.
     - Used when I(operation=search) only, ignored otherwise.
    type: int
    version_added: '0.2.0'

  timeout:
    type: float
    required: false
    description:
      - Set timeout, in seconds, on requests to JIRA API.
    default: 10

  validate_certs:
    required: false
    description:
      - Require valid SSL certificates (set to `false` if you'd like to use self-signed certificates)
    default: true
    type: bool

notes:
  - "Currently this only works with basic-auth."

author:
- "Steve Smith (@tarka)"
- "Per Abildgaard Toft (@pertoft)"
"""

EXAMPLES = r"""
# Create a new issue and add a comment to it:
- name: Create an issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    project: ANS
    operation: create
    summary: Example Issue
    description: Created using Ansible
    issuetype: Task
  args:
    fields:
        customfield_13225: "test"
        customfield_12931: '{"value": "Test"}'
  register: issue

- name: Comment on issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: comment
    comment: A comment added by Ansible

# Assign an existing issue using edit
- name: Assign an issue using free-form fields
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key}}'
    operation: edit
    assignee: ssmith

# Create an issue with an existing assignee
- name: Create an assigned issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    project: ANS
    operation: create
    summary: Assigned issue
    description: Created and assigned using Ansible
    issuetype: Task
    assignee: ssmith

# Edit an issue
- name: Set the labels on an issue using free-form fields
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: edit
  args:
    fields:
        labels:
          - autocreated
          - ansible

# Updating a field using operations: add, set & remove
- name: Change the value of a Select dropdown
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: update
  args:
    fields:
      customfield_12931: [ {'set': {'value': 'Virtual'}} ]
      customfield_13820: [ {'set': {'value':'Manually'}} ]
  register: cmdb_issue
  delegate_to: localhost


# Retrieve metadata for an issue and use it to create an account
- name: Get an issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    project: ANS
    operation: fetch
    issue: ANS-63
  register: issue

# Search for an issue
# You can limit the search for specific fields by adding optional args. Note! It must be a dict, hence, lastViewed: null
- name: Search for an issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    project: ANS
    operation: search
    maxresults: 10
    jql: project=cmdb AND cf[13225]="test"
  args:
    fields:
      lastViewed: null
  register: issue

- name: Create a unix account for the reporter
  become: true
  user:
    name: '{{ issue.meta.fields.creator.name }}'
    comment: '{{ issue.meta.fields.creator.displayName }}'

# You can get list of valid linktypes at /rest/api/2/issueLinkType
# url of your jira installation.
- name: Create link from HSP-1 to MKY-1
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    operation: link
    linktype: Relates
    inwardissue: HSP-1
    outwardissue: MKY-1

# Transition an issue by target status
- name: Close the issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: transition
    status: Done
  args:
    fields:
      customfield_14321: [ {'set': {'value': 'Value of Select' }} ]
      comment:  [ { 'add': { 'body' : 'Test' } }]

"""

import base64
import json
import sys
import traceback

from ansible.module_utils.six.moves.urllib.request import pathname2url

from ansible.module_utils._text import to_text, to_bytes, to_native

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def request(url, user, passwd, timeout, data=None, method=None):
    if data:
        data = json.dumps(data)

    # NOTE: fetch_url uses a password manager, which follows the
    # standard request-then-challenge basic-auth semantics. However as
    # JIRA allows some unauthorised operations it doesn't necessarily
    # send the challenge, so the request occurs as the anonymous user,
    # resulting in unexpected results. To work around this we manually
    # inject the basic-auth header up-front to ensure that JIRA treats
    # the requests as authorized for this user.
    auth = to_text(base64.b64encode(to_bytes('{0}:{1}'.format(user, passwd), errors='surrogate_or_strict')))
    response, info = fetch_url(module, url, data=data, method=method, timeout=timeout,
                               headers={'Content-Type': 'application/json',
                                        'Authorization': "Basic %s" % auth})

    if info['status'] not in (200, 201, 204):
        error = None
        try:
            error = json.loads(info['body'])
        except Exception:
            module.fail_json(msg=to_native(info['body']), exception=traceback.format_exc())
        if error:
            msg = []
            for key in ('errorMessages', 'errors'):
                if error.get(key):
                    msg.append(to_native(error[key]))
            if msg:
                module.fail_json(msg=', '.join(msg))
            module.fail_json(msg=to_native(error))
        # Fallback print body, if it cant be decoded
        module.fail_json(msg=to_native(info['body']))

    body = response.read()

    if body:
        return json.loads(to_text(body, errors='surrogate_or_strict'))
    return {}


def post(url, user, passwd, timeout, data):
    return request(url, user, passwd, timeout, data=data, method='POST')


def put(url, user, passwd, timeout, data):
    return request(url, user, passwd, timeout, data=data, method='PUT')


def get(url, user, passwd, timeout):
    return request(url, user, passwd, timeout)


def create(restbase, user, passwd, params):
    createfields = {
        'project': {'key': params['project']},
        'summary': params['summary'],
        'issuetype': {'name': params['issuetype']}}

    if params['description']:
        createfields['description'] = params['description']

    # Merge in any additional or overridden fields
    if params['fields']:
        createfields.update(params['fields'])

    data = {'fields': createfields}

    url = restbase + '/issue/'

    return True, post(url, user, passwd, params['timeout'], data)


def comment(restbase, user, passwd, params):
    data = {
        'body': params['comment']
    }
    url = restbase + '/issue/' + params['issue'] + '/comment'

    return True, post(url, user, passwd, params['timeout'], data)


def edit(restbase, user, passwd, params):
    data = {
        'fields': params['fields']
    }
    url = restbase + '/issue/' + params['issue']

    return True, put(url, user, passwd, params['timeout'], data)


def update(restbase, user, passwd, params):
    data = {
        "update": params['fields'],
    }
    url = restbase + '/issue/' + params['issue']

    return True, put(url, user, passwd, params['timeout'], data)


def fetch(restbase, user, passwd, params):
    url = restbase + '/issue/' + params['issue']
    return False, get(url, user, passwd, params['timeout'])


def search(restbase, user, passwd, params):
    url = restbase + '/search?jql=' + pathname2url(params['jql'])
    if params['fields']:
        fields = params['fields'].keys()
        url = url + '&fields=' + '&fields='.join([pathname2url(f) for f in fields])
    if params['maxresults']:
        url = url + '&maxResults=' + str(params['maxresults'])
    return False, get(url, user, passwd, params['timeout'])


def transition(restbase, user, passwd, params):
    # Find the transition id
    turl = restbase + '/issue/' + params['issue'] + "/transitions"
    tmeta = get(turl, user, passwd, params['timeout'])

    target = params['status']
    tid = None
    for t in tmeta['transitions']:
        if t['name'] == target:
            tid = t['id']
            break

    if not tid:
        raise ValueError("Failed find valid transition for '%s'" % target)

    # Perform it
    url = restbase + '/issue/' + params['issue'] + "/transitions"
    data = {'transition': {"id": tid},
            'update': params['fields']}

    return True, post(url, user, passwd, params['timeout'], data)


def link(restbase, user, passwd, params):
    data = {
        'type': {'name': params['linktype']},
        'inwardIssue': {'key': params['inwardissue']},
        'outwardIssue': {'key': params['outwardissue']},
    }

    url = restbase + '/issueLink/'

    return True, post(url, user, passwd, params['timeout'], data)


def main():

    global module
    module = AnsibleModule(
        argument_spec=dict(
            uri=dict(type='str', required=True),
            operation=dict(type='str', choices=['create', 'comment', 'edit', 'update', 'fetch', 'transition', 'link', 'search'],
                           aliases=['command'], required=True),
            username=dict(type='str', required=True),
            password=dict(type='str', required=True, no_log=True),
            project=dict(type='str', ),
            summary=dict(type='str', ),
            description=dict(type='str', ),
            issuetype=dict(type='str', ),
            issue=dict(type='str', aliases=['ticket']),
            comment=dict(type='str', ),
            status=dict(type='str', ),
            assignee=dict(type='str', ),
            fields=dict(default={}, type='dict'),
            linktype=dict(type='str', ),
            inwardissue=dict(type='str', ),
            outwardissue=dict(type='str', ),
            jql=dict(type='str', ),
            maxresults=dict(type='int'),
            timeout=dict(type='float', default=10),
            validate_certs=dict(default=True, type='bool'),
        ),
        required_if=(
            ('operation', 'create', ['project', 'issuetype', 'summary']),
            ('operation', 'comment', ['issue', 'comment']),
            ('operation', 'fetch', ['issue']),
            ('operation', 'transition', ['issue', 'status']),
            ('operation', 'link', ['linktype', 'inwardissue', 'outwardissue']),
            ('operation', 'search', ['jql']),
        ),
        supports_check_mode=False
    )

    op = module.params['operation']

    # Handle rest of parameters
    uri = module.params['uri']
    user = module.params['username']
    passwd = module.params['password']
    if module.params['assignee']:
        module.params['fields']['assignee'] = {'name': module.params['assignee']}

    if not uri.endswith('/'):
        uri = uri + '/'
    restbase = uri + 'rest/api/2'

    # Dispatch
    try:

        # Lookup the corresponding method for this operation. This is
        # safe as the AnsibleModule should remove any unknown operations.
        thismod = sys.modules[__name__]
        method = getattr(thismod, op)

        changed, ret = method(restbase, user, passwd, module.params)

    except Exception as e:
        return module.fail_json(msg=to_native(e), exception=traceback.format_exc())

    module.exit_json(changed=changed, meta=ret)


if __name__ == '__main__':
    main()

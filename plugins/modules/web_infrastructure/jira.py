#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, Steve Smith <ssmith@atlassian.com>
# Atlassian open-source approval reference OSR-76.
#
# Copyright (c) 2020, Per Abildgaard Toft <per@minfejl.dk> Search and update function
# Copyright (c) 2021, Brandon McNama <brandonmcnama@outlook.com> Issue attachment functionality
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: jira
short_description: Create and modify issues in a JIRA instance
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
    choices: [ attach, comment, create, edit, fetch, link, search, transition, update ]
    description:
      - The operation to perform.

  username:
    type: str
    description:
      - The username to log-in with.
      - Must be used with I(password). Mutually exclusive with I(token).

  password:
    type: str
    description:
      - The password to log-in with.
      - Must be used with I(username).  Mutually exclusive with I(token).

  token:
    type: str
    description:
      - The personal access token to log-in with.
      - Mutually exclusive with I(username) and I(password).
    version_added: 4.2.0

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
     - Note that JIRA may not allow changing field values on specific transitions or states.

  description:
    type: str
    required: false
    description:
     - The issue description, where appropriate.
     - Note that JIRA may not allow changing field values on specific transitions or states.

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
     - Note that JIRA may not allow changing field values on specific transitions or states.

  comment_visibility:
    type: dict
    description:
     - Used to specify comment comment visibility.
     - See U(https://developer.atlassian.com/cloud/jira/platform/rest/v2/api-group-issue-comments/#api-rest-api-2-issue-issueidorkey-comment-post) for details.
    suboptions:
      type:
        description:
         - Use type to specify which of the JIRA visibility restriction types will be used.
        type: str
        required: true
        choices: [group, role]
      value:
        description:
         - Use value to specify value corresponding to the type of visibility restriction. For example name of the group or role.
        type: str
        required: true
    version_added: '3.2.0'

  status:
    type: str
    required: false
    description:
     - Only used when I(operation) is C(transition), and a bit of a misnomer, it actually refers to the transition name.

  assignee:
    type: str
    required: false
    description:
     - Sets the the assignee when I(operation) is C(create), C(transition) or C(edit).
     - Recent versions of JIRA no longer accept a user name as a user identifier. In that case, use I(account_id) instead.
     - Note that JIRA may not allow changing field values on specific transitions or states.

  account_id:
    type: str
    description:
     - Sets the account identifier for the assignee when I(operation) is C(create), C(transition) or C(edit).
     - Note that JIRA may not allow changing field values on specific transitions or states.
    version_added: 2.5.0

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
     - When passed to comment, the data structure is merged at the first level since community.general 4.6.0. Useful to add JIRA properties for example.
     - Note that JIRA may not allow changing field values on specific transitions or states.
    default: {}

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
      - Require valid SSL certificates (set to C(false) if you'd like to use self-signed certificates)
    default: true
    type: bool

  attachment:
    type: dict
    version_added: 2.5.0
    description:
      - Information about the attachment being uploaded.
    suboptions:
      filename:
        required: true
        type: path
        description:
          - The path to the file to upload (from the remote node) or, if I(content) is specified,
            the filename to use for the attachment.
      content:
        type: str
        description:
          - The Base64 encoded contents of the file to attach. If not specified, the contents of I(filename) will be
            used instead.
      mimetype:
        type: str
        description:
          - The MIME type to supply for the upload. If not specified, best-effort detection will be
            done.

notes:
  - "Currently this only works with basic-auth, or tokens."
  - "To use with JIRA Cloud, pass the login e-mail as the I(username) and the API token as I(password)."

author:
- "Steve Smith (@tarka)"
- "Per Abildgaard Toft (@pertoft)"
- "Brandon McNama (@DWSR)"
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
        customfield_12931: {"value": "Test"}
  register: issue

- name: Comment on issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: comment
    comment: A comment added by Ansible

- name: Comment on issue with restricted visibility
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: comment
    comment: A comment added by Ansible
    comment_visibility:
      type: role
      value: Developers

- name: Comment on issue with property to mark it internal
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: comment
    comment: A comment added by Ansible
    fields:
      properties:
        - key: 'sd.public.comment'
          value:
            internal: true

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

# Transition an issue
- name: Resolve the issue
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: '{{ issue.meta.key }}'
    operation: transition
    status: Resolve Issue
    account_id: 112233445566778899aabbcc
    fields:
      resolution:
        name: Done
      description: I am done! This is the last description I will ever give you.

# Attach a file to an issue
- name: Attach a file
  community.general.jira:
    uri: '{{ server }}'
    username: '{{ user }}'
    password: '{{ pass }}'
    issue: HSP-1
    operation: attach
    attachment:
      filename: topsecretreport.xlsx
"""

import base64
import binascii
import json
import mimetypes
import os
import random
import string
import traceback

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper, cause_changes
from ansible.module_utils.six.moves.urllib.request import pathname2url
from ansible.module_utils.common.text.converters import to_text, to_bytes, to_native
from ansible.module_utils.urls import fetch_url


class JIRA(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            attachment=dict(type='dict', options=dict(
                content=dict(type='str'),
                filename=dict(type='path', required=True),
                mimetype=dict(type='str')
            )),
            uri=dict(type='str', required=True),
            operation=dict(
                type='str',
                choices=['attach', 'create', 'comment', 'edit', 'update', 'fetch', 'transition', 'link', 'search'],
                aliases=['command'], required=True
            ),
            username=dict(type='str'),
            password=dict(type='str', no_log=True),
            token=dict(type='str', no_log=True),
            project=dict(type='str', ),
            summary=dict(type='str', ),
            description=dict(type='str', ),
            issuetype=dict(type='str', ),
            issue=dict(type='str', aliases=['ticket']),
            comment=dict(type='str', ),
            comment_visibility=dict(type='dict', options=dict(
                type=dict(type='str', choices=['group', 'role'], required=True),
                value=dict(type='str', required=True)
            )),
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
            account_id=dict(type='str'),
        ),
        mutually_exclusive=[
            ['username', 'token'],
            ['password', 'token'],
            ['assignee', 'account_id'],
        ],
        required_together=[
            ['username', 'password'],
        ],
        required_one_of=[
            ['username', 'token'],
        ],
        required_if=(
            ('operation', 'attach', ['issue', 'attachment']),
            ('operation', 'create', ['project', 'issuetype', 'summary']),
            ('operation', 'comment', ['issue', 'comment']),
            ('operation', 'fetch', ['issue']),
            ('operation', 'transition', ['issue', 'status']),
            ('operation', 'link', ['linktype', 'inwardissue', 'outwardissue']),
            ('operation', 'search', ['jql']),
        ),
        supports_check_mode=False
    )

    state_param = 'operation'

    def __init_module__(self):
        if self.vars.fields is None:
            self.vars.fields = {}
        if self.vars.assignee:
            self.vars.fields['assignee'] = {'name': self.vars.assignee}
        if self.vars.account_id:
            self.vars.fields['assignee'] = {'accountId': self.vars.account_id}
        self.vars.uri = self.vars.uri.strip('/')
        self.vars.set('restbase', self.vars.uri + '/rest/api/2')

    @cause_changes(on_success=True)
    def operation_create(self):
        createfields = {
            'project': {'key': self.vars.project},
            'summary': self.vars.summary,
            'issuetype': {'name': self.vars.issuetype}}

        if self.vars.description:
            createfields['description'] = self.vars.description

        # Merge in any additional or overridden fields
        if self.vars.fields:
            createfields.update(self.vars.fields)

        data = {'fields': createfields}
        url = self.vars.restbase + '/issue/'
        self.vars.meta = self.post(url, data)

    @cause_changes(on_success=True)
    def operation_comment(self):
        data = {
            'body': self.vars.comment
        }
        # if comment_visibility is specified restrict visibility
        if self.vars.comment_visibility is not None:
            data['visibility'] = self.vars.comment_visibility

        # Use 'fields' to merge in any additional data
        if self.vars.fields:
            data.update(self.vars.fields)

        url = self.vars.restbase + '/issue/' + self.vars.issue + '/comment'
        self.vars.meta = self.post(url, data)

    @cause_changes(on_success=True)
    def operation_edit(self):
        data = {
            'fields': self.vars.fields
        }
        url = self.vars.restbase + '/issue/' + self.vars.issue
        self.vars.meta = self.put(url, data)

    @cause_changes(on_success=True)
    def operation_update(self):
        data = {
            "update": self.vars.fields,
        }
        url = self.vars.restbase + '/issue/' + self.vars.issue
        self.vars.meta = self.put(url, data)

    def operation_fetch(self):
        url = self.vars.restbase + '/issue/' + self.vars.issue
        self.vars.meta = self.get(url)

    def operation_search(self):
        url = self.vars.restbase + '/search?jql=' + pathname2url(self.vars.jql)
        if self.vars.fields:
            fields = self.vars.fields.keys()
            url = url + '&fields=' + '&fields='.join([pathname2url(f) for f in fields])
        if self.vars.maxresults:
            url = url + '&maxResults=' + str(self.vars.maxresults)

        self.vars.meta = self.get(url)

    @cause_changes(on_success=True)
    def operation_transition(self):
        # Find the transition id
        turl = self.vars.restbase + '/issue/' + self.vars.issue + "/transitions"
        tmeta = self.get(turl)

        target = self.vars.status
        tid = None
        for t in tmeta['transitions']:
            if t['name'] == target:
                tid = t['id']
                break
        else:
            raise ValueError("Failed find valid transition for '%s'" % target)

        fields = dict(self.vars.fields)
        if self.vars.summary is not None:
            fields.update({'summary': self.vars.summary})
        if self.vars.description is not None:
            fields.update({'description': self.vars.description})

        # Perform it
        data = {'transition': {"id": tid},
                'fields': fields}
        if self.vars.comment is not None:
            data.update({"update": {
                "comment": [{
                    "add": {"body": self.vars.comment}
                }],
            }})
        url = self.vars.restbase + '/issue/' + self.vars.issue + "/transitions"
        self.vars.meta = self.post(url, data)

    @cause_changes(on_success=True)
    def operation_link(self):
        data = {
            'type': {'name': self.vars.linktype},
            'inwardIssue': {'key': self.vars.inwardissue},
            'outwardIssue': {'key': self.vars.outwardissue},
        }
        url = self.vars.restbase + '/issueLink/'
        self.vars.meta = self.post(url, data)

    @cause_changes(on_success=True)
    def operation_attach(self):
        v = self.vars
        filename = v.attachment.get('filename')
        content = v.attachment.get('content')

        if not any((filename, content)):
            raise ValueError('at least one of filename or content must be provided')
        mime = v.attachment.get('mimetype')

        if not os.path.isfile(filename):
            raise ValueError('The provided filename does not exist: %s' % filename)

        content_type, data = self._prepare_attachment(filename, content, mime)

        url = v.restbase + '/issue/' + v.issue + '/attachments'
        return True, self.post(
            url, data, content_type=content_type, additional_headers={"X-Atlassian-Token": "no-check"}
        )

    # Ideally we'd just use prepare_multipart from ansible.module_utils.urls, but
    # unfortunately it does not support specifying the encoding and also defaults to
    # base64. Jira doesn't support base64 encoded attachments (and is therefore not
    # spec compliant. Go figure). I originally wrote this function as an almost
    # exact copypasta of prepare_multipart, but ran into some encoding issues when
    # using the noop encoder. Hand rolling the entire message body seemed to work
    # out much better.
    #
    # https://community.atlassian.com/t5/Jira-questions/Jira-dosen-t-decode-base64-attachment-request-REST-API/qaq-p/916427
    #
    # content is expected to be a base64 encoded string since Ansible doesn't
    # support passing raw bytes objects.
    @staticmethod
    def _prepare_attachment(filename, content=None, mime_type=None):
        def escape_quotes(s):
            return s.replace('"', '\\"')

        boundary = "".join(random.choice(string.digits + string.ascii_letters) for dummy in range(30))
        name = to_native(os.path.basename(filename))

        if not mime_type:
            try:
                mime_type = mimetypes.guess_type(filename or '', strict=False)[0] or 'application/octet-stream'
            except Exception:
                mime_type = 'application/octet-stream'
        main_type, sep, sub_type = mime_type.partition('/')

        if not content and filename:
            with open(to_bytes(filename, errors='surrogate_or_strict'), 'rb') as f:
                content = f.read()
        else:
            try:
                content = base64.b64decode(content)
            except binascii.Error as e:
                raise Exception("Unable to base64 decode file content: %s" % e)

        lines = [
            "--{0}".format(boundary),
            'Content-Disposition: form-data; name="file"; filename={0}'.format(escape_quotes(name)),
            "Content-Type: {0}".format("{0}/{1}".format(main_type, sub_type)),
            '',
            to_text(content),
            "--{0}--".format(boundary),
            ""
        ]

        return (
            "multipart/form-data; boundary={0}".format(boundary),
            "\r\n".join(lines)
        )

    def request(
            self,
            url,
            data=None,
            method=None,
            content_type='application/json',
            additional_headers=None
    ):
        if data and content_type == 'application/json':
            data = json.dumps(data)

        headers = {}
        if isinstance(additional_headers, dict):
            headers = additional_headers.copy()

        # NOTE: fetch_url uses a password manager, which follows the
        # standard request-then-challenge basic-auth semantics. However as
        # JIRA allows some unauthorised operations it doesn't necessarily
        # send the challenge, so the request occurs as the anonymous user,
        # resulting in unexpected results. To work around this we manually
        # inject the auth header up-front to ensure that JIRA treats
        # the requests as authorized for this user.

        if self.vars.token is not None:
            headers.update({
                "Content-Type": content_type,
                "Authorization": "Bearer %s" % self.vars.token,
            })
        else:
            auth = to_text(base64.b64encode(to_bytes('{0}:{1}'.format(self.vars.username, self.vars.password),
                                                     errors='surrogate_or_strict')))
            headers.update({
                "Content-Type": content_type,
                "Authorization": "Basic %s" % auth,
            })

        response, info = fetch_url(
            self.module, url, data=data, method=method, timeout=self.vars.timeout, headers=headers
        )

        if info['status'] not in (200, 201, 204):
            error = None
            try:
                error = json.loads(info['body'])
            except Exception:
                msg = 'The request "{method} {url}" returned the unexpected status code {status} {msg}\n{body}'.format(
                    status=info['status'],
                    msg=info['msg'],
                    body=info.get('body'),
                    url=url,
                    method=method,
                )
                self.module.fail_json(msg=to_native(msg), exception=traceback.format_exc())
            if error:
                msg = []
                for key in ('errorMessages', 'errors'):
                    if error.get(key):
                        msg.append(to_native(error[key]))
                if msg:
                    self.module.fail_json(msg=', '.join(msg))
                self.module.fail_json(msg=to_native(error))
            # Fallback print body, if it cant be decoded
            self.module.fail_json(msg=to_native(info['body']))

        body = response.read()

        if body:
            return json.loads(to_text(body, errors='surrogate_or_strict'))
        return {}

    def post(self, url, data, content_type='application/json', additional_headers=None):
        return self.request(url, data=data, method='POST', content_type=content_type,
                            additional_headers=additional_headers)

    def put(self, url, data):
        return self.request(url, data=data, method='PUT')

    def get(self, url):
        return self.request(url)


def main():
    jira = JIRA()
    jira.run()


if __name__ == '__main__':
    main()

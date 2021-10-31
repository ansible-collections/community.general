#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Evgeniy Krysanov <evgeniy.krysanov@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: bitbucket_pipeline_variable
short_description: Manages Bitbucket pipeline variables
description:
  - Manages Bitbucket pipeline variables.
author:
  - Evgeniy Krysanov (@catcombo)
extends_documentation_fragment:
  - community.general.bitbucket
options:
  repository:
    description:
      - The repository name.
    type: str
    required: true
  workspace:
    description:
      - The repository owner.
      - Alias I(username) has been deprecated and will become an alias of I(user) in community.general 6.0.0.
    type: str
    required: true
    aliases: [ username ]
  name:
    description:
      - The pipeline variable name.
    type: str
    required: true
  value:
    description:
      - The pipeline variable value.
    type: str
  secured:
    description:
      - Whether to encrypt the variable value.
    type: bool
    default: no
  state:
    description:
      - Indicates desired state of the variable.
    type: str
    required: true
    choices: [ absent, present ]
notes:
  - Check mode is supported.
  - For secured values return parameter C(changed) is always C(True).
'''

EXAMPLES = r'''
- name: Create or update pipeline variables from the list
  community.general.bitbucket_pipeline_variable:
    repository: 'bitbucket-repo'
    workspace: bitbucket_workspace
    name: '{{ item.name }}'
    value: '{{ item.value }}'
    secured: '{{ item.secured }}'
    state: present
  with_items:
    - { name: AWS_ACCESS_KEY, value: ABCD1234, secured: False }
    - { name: AWS_SECRET, value: qwe789poi123vbn0, secured: True }

- name: Remove pipeline variable
  community.general.bitbucket_pipeline_variable:
    repository: bitbucket-repo
    workspace: bitbucket_workspace
    name: AWS_ACCESS_KEY
    state: absent
'''

RETURN = r''' # '''

from ansible.module_utils.basic import AnsibleModule, _load_params
from ansible_collections.community.general.plugins.module_utils.source_control.bitbucket import BitbucketHelper

error_messages = {
    'required_value': '`value` is required when the `state` is `present`',
}

BITBUCKET_API_ENDPOINTS = {
    'pipeline-variable-list': '%s/2.0/repositories/{workspace}/{repo_slug}/pipelines_config/variables/' % BitbucketHelper.BITBUCKET_API_URL,
    'pipeline-variable-detail': '%s/2.0/repositories/{workspace}/{repo_slug}/pipelines_config/variables/{variable_uuid}' % BitbucketHelper.BITBUCKET_API_URL,
}


def get_existing_pipeline_variable(module, bitbucket):
    """
    Search for a pipeline variable

    :param module: instance of the :class:`AnsibleModule`
    :param bitbucket: instance of the :class:`BitbucketHelper`
    :return: existing variable or None if not found
    :rtype: dict or None

    Return example::

        {
            'name': 'AWS_ACCESS_OBKEY_ID',
            'value': 'x7HU80-a2',
            'type': 'pipeline_variable',
            'secured': False,
            'uuid': '{9ddb0507-439a-495a-99f3-5464f15128127}'
        }

    The `value` key in dict is absent in case of secured variable.
    """
    variables_base_url = BITBUCKET_API_ENDPOINTS['pipeline-variable-list'].format(
        workspace=module.params['workspace'],
        repo_slug=module.params['repository'],
    )
    # Look through the all response pages in search of variable we need
    page = 1
    while True:
        next_url = "%s?page=%s" % (variables_base_url, page)
        info, content = bitbucket.request(
            api_url=next_url,
            method='GET',
        )

        if info['status'] == 404:
            module.fail_json(msg='Invalid `repository` or `workspace`.')

        if info['status'] != 200:
            module.fail_json(msg='Failed to retrieve the list of pipeline variables: {0}'.format(info))

        # We are at the end of list
        if 'pagelen' in content and content['pagelen'] == 0:
            return None

        page += 1
        var = next(filter(lambda v: v['key'] == module.params['name'], content['values']), None)

        if var is not None:
            var['name'] = var.pop('key')
            return var


def create_pipeline_variable(module, bitbucket):
    info, content = bitbucket.request(
        api_url=BITBUCKET_API_ENDPOINTS['pipeline-variable-list'].format(
            workspace=module.params['workspace'],
            repo_slug=module.params['repository'],
        ),
        method='POST',
        data={
            'key': module.params['name'],
            'value': module.params['value'],
            'secured': module.params['secured'],
        },
    )

    if info['status'] != 201:
        module.fail_json(msg='Failed to create pipeline variable `{name}`: {info}'.format(
            name=module.params['name'],
            info=info,
        ))


def update_pipeline_variable(module, bitbucket, variable_uuid):
    info, content = bitbucket.request(
        api_url=BITBUCKET_API_ENDPOINTS['pipeline-variable-detail'].format(
            workspace=module.params['workspace'],
            repo_slug=module.params['repository'],
            variable_uuid=variable_uuid,
        ),
        method='PUT',
        data={
            'value': module.params['value'],
            'secured': module.params['secured'],
        },
    )

    if info['status'] != 200:
        module.fail_json(msg='Failed to update pipeline variable `{name}`: {info}'.format(
            name=module.params['name'],
            info=info,
        ))


def delete_pipeline_variable(module, bitbucket, variable_uuid):
    info, content = bitbucket.request(
        api_url=BITBUCKET_API_ENDPOINTS['pipeline-variable-detail'].format(
            workspace=module.params['workspace'],
            repo_slug=module.params['repository'],
            variable_uuid=variable_uuid,
        ),
        method='DELETE',
    )

    if info['status'] != 204:
        module.fail_json(msg='Failed to delete pipeline variable `{name}`: {info}'.format(
            name=module.params['name'],
            info=info,
        ))


class BitBucketPipelineVariable(AnsibleModule):
    def __init__(self, *args, **kwargs):
        params = _load_params() or {}
        if params.get('secured'):
            kwargs['argument_spec']['value'].update({'no_log': True})
        super(BitBucketPipelineVariable, self).__init__(*args, **kwargs)


def main():
    argument_spec = BitbucketHelper.bitbucket_argument_spec()
    argument_spec.update(
        repository=dict(type='str', required=True),
        workspace=dict(
            type='str', aliases=['username'], required=True,
            deprecated_aliases=[dict(name='username', version='6.0.0', collection_name='community.general')],
        ),
        name=dict(type='str', required=True),
        value=dict(type='str'),
        secured=dict(type='bool', default=False),
        state=dict(type='str', choices=['present', 'absent'], required=True),
    )
    module = BitBucketPipelineVariable(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=BitbucketHelper.bitbucket_required_one_of(),
        required_together=BitbucketHelper.bitbucket_required_together(),
    )

    bitbucket = BitbucketHelper(module)

    value = module.params['value']
    state = module.params['state']
    secured = module.params['secured']

    # Check parameters
    if (value is None) and (state == 'present'):
        module.fail_json(msg=error_messages['required_value'])

    # Retrieve access token for authorized API requests
    bitbucket.fetch_access_token()

    # Retrieve existing pipeline variable (if any)
    existing_variable = get_existing_pipeline_variable(module, bitbucket)
    changed = False

    # Create new variable in case it doesn't exists
    if not existing_variable and (state == 'present'):
        if not module.check_mode:
            create_pipeline_variable(module, bitbucket)
        changed = True

    # Update variable if it is secured or the old value does not match the new one
    elif existing_variable and (state == 'present'):
        if (existing_variable['secured'] != secured) or (existing_variable.get('value') != value):
            if not module.check_mode:
                update_pipeline_variable(module, bitbucket, existing_variable['uuid'])
            changed = True

    # Delete variable
    elif existing_variable and (state == 'absent'):
        if not module.check_mode:
            delete_pipeline_variable(module, bitbucket, existing_variable['uuid'])
        changed = True

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

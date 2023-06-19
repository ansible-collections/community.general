#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, Evgeniy Krysanov <evgeniy.krysanov@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: bitbucket_pipeline_key_pair
short_description: Manages Bitbucket pipeline SSH key pair
description:
  - Manages Bitbucket pipeline SSH key pair.
author:
  - Evgeniy Krysanov (@catcombo)
extends_documentation_fragment:
  - community.general.bitbucket
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  repository:
    description:
      - The repository name.
    type: str
    required: true
  workspace:
    description:
      - The repository owner.
      - "B(Note:) O(ignore:username) used to be an alias of this option. Since community.general 6.0.0 it is an alias of O(user)."
    type: str
    required: true
  public_key:
    description:
      - The public key.
    type: str
  private_key:
    description:
      - The private key.
    type: str
  state:
    description:
      - Indicates desired state of the key pair.
    type: str
    required: true
    choices: [ absent, present ]
notes:
  - Check mode is supported.
'''

EXAMPLES = r'''
- name: Create or update SSH key pair
  community.general.bitbucket_pipeline_key_pair:
    repository: 'bitbucket-repo'
    workspace: bitbucket_workspace
    public_key: '{{lookup("file", "bitbucket.pub") }}'
    private_key: '{{lookup("file", "bitbucket") }}'
    state: present

- name: Remove SSH key pair
  community.general.bitbucket_pipeline_key_pair:
    repository: bitbucket-repo
    workspace: bitbucket_workspace
    state: absent
'''

RETURN = r''' # '''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.source_control.bitbucket import BitbucketHelper

error_messages = {
    'invalid_params': 'Account, repository or SSH key pair was not found',
    'required_keys': '`public_key` and `private_key` are required when the `state` is `present`',
}

BITBUCKET_API_ENDPOINTS = {
    'ssh-key-pair': '%s/2.0/repositories/{workspace}/{repo_slug}/pipelines_config/ssh/key_pair' % BitbucketHelper.BITBUCKET_API_URL,
}


def get_existing_ssh_key_pair(module, bitbucket):
    """
    Retrieves an existing ssh key pair from repository
    specified in module param `repository`

    :param module: instance of the :class:`AnsibleModule`
    :param bitbucket: instance of the :class:`BitbucketHelper`
    :return: existing key pair or None if not found
    :rtype: dict or None

    Return example::

        {
            "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ...2E8HAeT",
            "type": "pipeline_ssh_key_pair"
        }
    """
    api_url = BITBUCKET_API_ENDPOINTS['ssh-key-pair'].format(
        workspace=module.params['workspace'],
        repo_slug=module.params['repository'],
    )

    info, content = bitbucket.request(
        api_url=api_url,
        method='GET',
    )

    if info['status'] == 404:
        # Account, repository or SSH key pair was not found.
        return None

    return content


def update_ssh_key_pair(module, bitbucket):
    info, content = bitbucket.request(
        api_url=BITBUCKET_API_ENDPOINTS['ssh-key-pair'].format(
            workspace=module.params['workspace'],
            repo_slug=module.params['repository'],
        ),
        method='PUT',
        data={
            'private_key': module.params['private_key'],
            'public_key': module.params['public_key'],
        },
    )

    if info['status'] == 404:
        module.fail_json(msg=error_messages['invalid_params'])

    if info['status'] != 200:
        module.fail_json(msg='Failed to create or update pipeline ssh key pair : {0}'.format(info))


def delete_ssh_key_pair(module, bitbucket):
    info, content = bitbucket.request(
        api_url=BITBUCKET_API_ENDPOINTS['ssh-key-pair'].format(
            workspace=module.params['workspace'],
            repo_slug=module.params['repository'],
        ),
        method='DELETE',
    )

    if info['status'] == 404:
        module.fail_json(msg=error_messages['invalid_params'])

    if info['status'] != 204:
        module.fail_json(msg='Failed to delete pipeline ssh key pair: {0}'.format(info))


def main():
    argument_spec = BitbucketHelper.bitbucket_argument_spec()
    argument_spec.update(
        repository=dict(type='str', required=True),
        workspace=dict(type='str', required=True),
        public_key=dict(type='str'),
        private_key=dict(type='str', no_log=True),
        state=dict(type='str', choices=['present', 'absent'], required=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=BitbucketHelper.bitbucket_required_one_of(),
        required_together=BitbucketHelper.bitbucket_required_together(),
    )

    bitbucket = BitbucketHelper(module)

    state = module.params['state']
    public_key = module.params['public_key']
    private_key = module.params['private_key']

    # Check parameters
    if ((public_key is None) or (private_key is None)) and (state == 'present'):
        module.fail_json(msg=error_messages['required_keys'])

    # Retrieve access token for authorized API requests
    bitbucket.fetch_access_token()

    # Retrieve existing ssh key
    key_pair = get_existing_ssh_key_pair(module, bitbucket)
    changed = False

    # Create or update key pair
    if (not key_pair or (key_pair.get('public_key') != public_key)) and (state == 'present'):
        if not module.check_mode:
            update_ssh_key_pair(module, bitbucket)
        changed = True

    # Delete key pair
    elif key_pair and (state == 'absent'):
        if not module.check_mode:
            delete_ssh_key_pair(module, bitbucket)
        changed = True

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()

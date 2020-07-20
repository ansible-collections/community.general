#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: gcp_storage_bucket_permissions
version_added: 1.0.0
short_description: Add an IAM Member and IAM Role to a Storage Bucket
description: This module gives an IAM Member permissions to a Storage Bucket.

options:
    project_id:
        description:
            - GCP account project id.
        required: yes
        type: str
    bucket_name:
        description:
            - GCP Storage Bucket to apply permissions to.
        required: yes
        type: str
    member:
        description:
            - IAM Member. U(https://cloud.google.com/storage/docs/json_api/v1/buckets/setIamPolicy).
        required: yes
        type: str
    role:
        description:
            - IAM Role to apply to IAM Member. U(https://cloud.google.com/storage/docs/access-control/iam-roles).
        required: yes
        type: str
    service_account_file:
        description:
            - GCP credentails file.
        required: yes
        type: str

author:
    - Chanaka Samarajeewa (@csamarajeewa)
'''

EXAMPLES = '''

# Add permission

- name: Add bucket permission
  community.general.gcp_storage_bucket_permissions:
    project_id: "{{ item.project_id | default(lookup('env','GCE_PROJECT')) }}"
    bucket_name: "{{ item.bucket_name }}"
    member: "{{ item.project_transfer_service_account }}"
    role: "{{ item.project_transfer_service_account_role }}"
    service_account_file: "{{ gcp_gce_credentials_file_path_local | default(lookup('env','GCE_CREDENTIALS_FILE_PATH')) }}"
  loop: "{{ gcp_storage_bucket_iam_permissions }}"

'''

import traceback
import datetime
import json
from ansible.module_utils.basic import AnsibleModule

LIB_IMP_ERR = None
try:
    from google.oauth2 import service_account
    from google.cloud import storage
    HAS_LIB = True
except:
    HAS_LIB = False
    LIB_IMP_ERR = traceback.format_exc()


def run_module():
    module_args = dict(
        project_id=dict(type='str', required=True),
        bucket_name=dict(type='str', required=True),
        member=dict(type='str', required=True),
        role=dict(type='str', required=True),
        service_account_file=dict(type='str', required=True)
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    if not HAS_LIB:
        module.fail_json(msg=missing_required_lib("Please install google-cloud, google-auth library."),
                         exception=LIB_IMP_ERR)

    # Perform changes
    credentials = service_account.Credentials.from_service_account_file(module.params['service_account_file'])
    project_id = module.params['project_id']
    bucket_name = module.params['bucket_name']
    role = module.params['role']
    member = module.params['member']

    storage_client = storage.Client(project=project_id, credentials=credentials)

    bucket = storage_client.bucket(bucket_name)
    policy = bucket.get_iam_policy()

    for current_role in policy:
        policy[current_role].discard(member)

    policy[role].add(member)
    bucket.set_iam_policy(policy)

    result['changed'] = 'True'

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

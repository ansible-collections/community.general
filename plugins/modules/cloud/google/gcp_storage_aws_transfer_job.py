#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: gcp_storage_aws_transfer_job
version_added: 1.0.0
short_description: Creates GCP Transfer Jobs between AWS S3 and GCP Storage
description:
    - This module will create GCP Storage Transfer Jobs which transfers AWS S3 Bucket objects into the specified GCP Bucket.
     - If there is an existing Transfer Job with the same description it will delete it and create a new job.
     - If you include the parameter I(aws_s3_bucket_prefix), it will transfer that prefix only, otherwise it will transfer all objects in the bucket.
     - The Transfer Jobs will only pull changed or new objects when they execute.

options:
    project_id:
        description:
            - GCP account project id.
        required: yes
        type: str
    scheduled_start_date_utc:
        description:
            - Start date of transfer job in YYYY/MM/DD format.
            - For details on how transfer job schedules work see

              U(https://cloud.google.com/storage-transfer/docs/reference/rest/v1/transferJobs#schedule).
        required: yes
        type: str
    scheduled_end_date_utc:
        description:
            - End date of transfer job in YYYY/MM/DD format.
        required: yes
        type: str
    scheduled_start_time_utc:
        description:
            - Transfer job start time in HH:SS format.
        required: yes
        type: str
    gcp_storage_bucket:
        description:
            - The GCP storage bucket to transfer objects into.
        required: yes
        type: str
    service_account_file:
        description:
            - GCP credentails file.
        required: yes
        type: str
    aws_s3_bucket:
        description:
            - AWS S3 bucket which contains the source objects.
        required: yes
        type: str
    aws_s3_bucket_prefix:
        description:
            - Prefix within the S3 bucket which contains the source objects.
        required: false
        type: str
    description:
        description:
            - This is used as a unique name for the transfer job. If a job with the same description exists, it is replaced, or deleted depending on state.
        required: yes
        type: str
    state:
        description:
            - Whether to create/update or delete a transfer job. Options are present and absent.
        required: yes
        type: str
    aws_access_key:
        description:
            - The AWS IAM account access key used by the transfer job to retreive S3 objects.
        required: yes
        type: str
    aws_secret_key:
        description:
            - The AWS IAM account access key secret used by the transfer job to retreive S3 objects.
        required: yes
        type: str

author:
    - Chanaka Samarajeewa (@csamarajeewa)
'''

EXAMPLES = '''

# Create a new job / replace existing job

- name: Create Bucket Transfer Job
  community.general.gcp_storage_aws_transfer_job:
    project_id: "{{ item.project_id }}"
    scheduled_start_date_utc: "{{ item.scheduled_start_date_utc }}"
    scheduled_end_date_utc: "{{ item.scheduled_end_date_utc }}"
    scheduled_start_time_utc: "{{ item.scheduled_start_time_utc }}"
    gcp_storage_bucket: "{{ item.gcp_storage_bucket }}"
    service_account_file: "{{ lookup('env','GCE_CREDENTIALS_FILE_PATH') }}"
    aws_s3_bucket: "{{ item.aws_s3_bucket }}"
    aws_s3_bucket_prefix: "{{ item.aws_s3_bucket_prefix | default(omit) }}"
    aws_access_key: "{{ item.aws_access_key }}"
    aws_secret_key: "{{ item.aws_secret_key }}"
    description: "{{ item.description }}"
    state: present
  loop: "{{ gcp_create_transfer_jobs }}"

# Delete an existing job

- name: Delete Bucket Transfer Job
  community.general.gcp_storage_aws_transfer_job:
    project_id: "{{ item.project_id }}"
    scheduled_start_date_utc: "{{ item.scheduled_start_date_utc }}"
    scheduled_end_date_utc: "{{ item.scheduled_end_date_utc }}"
    scheduled_start_time_utc: "{{ item.scheduled_start_time_utc }}"
    gcp_storage_bucket: "{{ item.gcp_storage_bucket }}"
    service_account_file: "{{ lookup('env','GCE_CREDENTIALS_FILE_PATH') }}"
    aws_s3_bucket: "{{ item.aws_s3_bucket }}"
    aws_s3_bucket_prefix: "{{ item.aws_s3_bucket_prefix | default(omit) }}"
    aws_access_key: "{{ item.aws_access_key }}"
    aws_secret_key: "{{ item.aws_secret_key }}"
    description: "{{ item.description }}"
    state: absent
  loop: "{{ gcp_create_transfer_jobs }}"

'''

RETURN = '''
message:
    description: Message indicating whether the job was created or deleted.
    type: str
    returned: always
'''


import datetime
import json
import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib

try:
    import googleapiclient.discovery
    from google.oauth2 import service_account
    HAS_LIB = True
except ImportError as e:
    HAS_LIB = False
    LIB_IMP_ERR = traceback.format_exc()


def _validate_params(params):
    """
    Validate params.

    This function calls _validated_date to verify
    date time parameters.

    :param params: Ansible dictionary containing configuration.
    :type  params: ``dict``

    :return: True or raises ValueError
    :rtype: ``bool`` or `class:ValueError`
    """
    fields = [
        {'name': 'scheduled_start_date_utc', 'type': str, 'required': True},
        {'name': 'scheduled_end_date_utc', 'type': str, 'required': True},
        {'name': 'scheduled_start_time_utc', 'type': str, 'required': True},
    ]

    date_format = '%Y/%m/%d'
    time_format = '%H:%M'

    try:
        if 'scheduled_start_date_utc' in params and params['scheduled_start_date_utc'] is not None:
            _validated_date(params['scheduled_start_date_utc'], date_format)
        if 'scheduled_end_date_utc' in params and params['scheduled_end_date_utc'] is not None:
            _validated_date(params['scheduled_end_date_utc'], date_format)
        if 'scheduled_start_time_utc' in params and params['scheduled_start_time_utc'] is not None:
            _validated_date(params['scheduled_start_time_utc'], time_format)
    except Exception:
        raise

    return True


def _validated_date(param, format):
    try:
        value = datetime.datetime.strptime(param, format)
    except Exception as e:
        raise ValueError("Incorrect format. Date and Times must be formatted as YYYY/MM/DD and HH:SS")


def run_module():

    module_args = dict(
        project_id=dict(type='str', required=True),
        scheduled_start_date_utc=dict(type='str', required=True),
        scheduled_end_date_utc=dict(type='str', required=True),
        scheduled_start_time_utc=dict(type='str', required=True),
        gcp_storage_bucket=dict(type='str', required=True),
        service_account_file=dict(type='str', required=True),
        aws_s3_bucket=dict(type='str', required=True),
        aws_s3_bucket_prefix=dict(type='str', required=False),
        aws_access_key=dict(type='str', required=True),
        aws_secret_key=dict(type='str', required=True),
        description=dict(type='str', required=True),
        state=dict(type='str', required=True)
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
        module.fail_json(msg=missing_required_lib("Please install google-api-python-client, google-auth library."),
                         exception=LIB_IMP_ERR)

    try:
        _validate_params(module.params)
    except Exception as e:
        module.fail_json(msg=e.message, changed=False)

    start_date = datetime.datetime.strptime(module.params['scheduled_start_date_utc'], '%Y/%m/%d')
    end_date = datetime.datetime.strptime(module.params['scheduled_end_date_utc'], '%Y/%m/%d')
    start_time = datetime.datetime.strptime(module.params['scheduled_start_time_utc'], '%H:%M')

    delete_transfer_job = {
        'project_id': module.params['project_id'],
        'transfer_job': {
            'status': 'DELETED'
        }
    }

    transfer_job = {
        'description': module.params['description'],
        'status': 'ENABLED',
        'projectId': module.params['project_id'],
        'schedule': {
            'scheduleStartDate': {
                'day': start_date.day,
                'month': start_date.month,
                'year': start_date.year
            },
            'scheduleEndDate': {
                'day': start_date.day,
                'month': end_date.month,
                'year': end_date.year
            },
            'startTimeOfDay': {
                'hours': start_time.hour,
                'minutes': start_time.minute,
                'seconds': start_time.second
            }
        },
        'transferSpec': {
            'objectConditions': {
                'includePrefixes': module.params['aws_s3_bucket_prefix']
            },
            'transferOptions': {
                'overwriteObjectsAlreadyExistingInSink': 'False',
                'deleteObjectsUniqueInSink': 'False',
                'deleteObjectsFromSourceAfterTransfer': 'False'
            },
            'awsS3DataSource': {
                'bucketName': module.params['aws_s3_bucket'],
                'awsAccessKey': {
                    'accessKeyId': module.params['aws_access_key'],
                    'secretAccessKey': module.params['aws_secret_key']
                }
            },
            'gcsDataSink': {
                'bucketName': module.params['gcp_storage_bucket']
            }
        }
    }

    credentials = service_account.Credentials.from_service_account_file(module.params['service_account_file'])
    storagetransfer = googleapiclient.discovery.build('storagetransfer', 'v1', credentials=credentials)

    filterString = (
        '{{"project_id": "{project_id}"}}'
    ).format(project_id=module.params['project_id'])

    queryResult = storagetransfer.transferJobs().list(filter=filterString).execute()
    result['message'] = queryResult

    # Delete existing job if exists, then create new job
    if 'transferJobs' in queryResult:
        for transferJob in queryResult['transferJobs']:
            if transferJob['description'] == module.params['description']:
                storagetransfer.transferJobs().patch(body=delete_transfer_job, jobName=transferJob['name']).execute()
                result['message'] = 'deleted'

    if 'present' in module.params['state']:
        storagetransfer.transferJobs().create(body=transfer_job).execute()
        result['message'] = 'created'

    result['changed'] = 'True'

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

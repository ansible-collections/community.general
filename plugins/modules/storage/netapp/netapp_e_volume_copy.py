#!/usr/bin/python

# (c) 2016, NetApp, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: netapp_e_volume_copy
short_description: NetApp E-Series create volume copy pairs
description:
    - Create and delete snapshots images on volume groups for NetApp E-series storage arrays.
author: Kevin Hulquest (@hulquest)
extends_documentation_fragment:
- netapp.ontap.netapp.eseries

options:
    api_username:
        required: true
        description:
        - The username to authenticate with the SANtricity WebServices Proxy or embedded REST API.
    api_password:
        required: true
        description:
        - The password to authenticate with the SANtricity WebServices Proxy or embedded REST API.
    api_url:
        required: true
        description:
        - The url to the SANtricity WebServices Proxy or embedded REST API, for example C(https://prod-1.wahoo.acme.com/devmgr/v2).
    validate_certs:
        required: false
        default: true
        description:
        - Should https certificates be validated?
    source_volume_id:
        description:
            - The id of the volume copy source.
            - If used, must be paired with destination_volume_id
            - Mutually exclusive with volume_copy_pair_id, and search_volume_id
    destination_volume_id:
        description:
            - The id of the volume copy destination.
            - If used, must be paired with source_volume_id
            - Mutually exclusive with volume_copy_pair_id, and search_volume_id
    volume_copy_pair_id:
        description:
            - The id of a given volume copy pair
            - Mutually exclusive with destination_volume_id, source_volume_id, and search_volume_id
            - Can use to delete or check presence of volume pairs
            - Must specify this or (destination_volume_id and source_volume_id)
    state:
        description:
            - Whether the specified volume copy pair should exist or not.
        required: True
        choices: ['present', 'absent']
    create_copy_pair_if_does_not_exist:
        description:
            - Defines if a copy pair will be created if it does not exist.
            - If set to True destination_volume_id and source_volume_id are required.
        type: bool
        default: True
    start_stop_copy:
        description:
            - starts a re-copy or stops a copy in progress
            - "Note: If you stop the initial file copy before it it done the copy pair will be destroyed"
            - Requires volume_copy_pair_id
    search_volume_id:
        description:
            - Searches for all valid potential target and source volumes that could be used in a copy_pair
            - Mutually exclusive with volume_copy_pair_id, destination_volume_id and source_volume_id
'''
RESULTS = """
"""
EXAMPLES = """
---
msg:
    description: Success message
    returned: success
    type: str
    sample: Json facts for the volume copy that was created.
"""
RETURN = """
msg:
    description: Success message
    returned: success
    type: str
    sample: Created Volume Copy Pair with ID
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible_collections.netapp.ontap.plugins.module_utils.netapp import request

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def find_volume_copy_pair_id_from_source_volume_id_and_destination_volume_id(params):
    get_status = 'storage-systems/%s/volume-copy-jobs' % params['ssid']
    url = params['api_url'] + get_status

    (rc, resp) = request(url, method='GET', url_username=params['api_username'],
                         url_password=params['api_password'], headers=HEADERS,
                         validate_certs=params['validate_certs'])

    volume_copy_pair_id = None
    for potential_copy_pair in resp:
        if potential_copy_pair['sourceVolume'] == params['source_volume_id']:
            if potential_copy_pair['sourceVolume'] == params['source_volume_id']:
                volume_copy_pair_id = potential_copy_pair['id']

    return volume_copy_pair_id


def create_copy_pair(params):
    get_status = 'storage-systems/%s/volume-copy-jobs' % params['ssid']
    url = params['api_url'] + get_status

    rData = {
        "sourceId": params['source_volume_id'],
        "targetId": params['destination_volume_id']
    }

    (rc, resp) = request(url, data=json.dumps(rData), ignore_errors=True, method='POST',
                         url_username=params['api_username'], url_password=params['api_password'], headers=HEADERS,
                         validate_certs=params['validate_certs'])
    if rc != 200:
        return False, (rc, resp)
    else:
        return True, (rc, resp)


def delete_copy_pair_by_copy_pair_id(params):
    get_status = 'storage-systems/%s/volume-copy-jobs/%s?retainRepositories=false' % (
        params['ssid'], params['volume_copy_pair_id'])
    url = params['api_url'] + get_status

    (rc, resp) = request(url, ignore_errors=True, method='DELETE',
                         url_username=params['api_username'], url_password=params['api_password'], headers=HEADERS,
                         validate_certs=params['validate_certs'])
    if rc != 204:
        return False, (rc, resp)
    else:
        return True, (rc, resp)


def find_volume_copy_pair_id_by_volume_copy_pair_id(params):
    get_status = 'storage-systems/%s/volume-copy-jobs/%s?retainRepositories=false' % (
        params['ssid'], params['volume_copy_pair_id'])
    url = params['api_url'] + get_status

    (rc, resp) = request(url, ignore_errors=True, method='DELETE',
                         url_username=params['api_username'], url_password=params['api_password'], headers=HEADERS,
                         validate_certs=params['validate_certs'])
    if rc != 200:
        return False, (rc, resp)
    else:
        return True, (rc, resp)


def start_stop_copy(params):
    get_status = 'storage-systems/%s/volume-copy-jobs-control/%s?control=%s' % (
        params['ssid'], params['volume_copy_pair_id'], params['start_stop_copy'])
    url = params['api_url'] + get_status

    (response_code, response_data) = request(url, ignore_errors=True, method='POST',
                                             url_username=params['api_username'], url_password=params['api_password'],
                                             headers=HEADERS,
                                             validate_certs=params['validate_certs'])

    if response_code == 200:
        return True, response_data[0]['percentComplete']
    else:
        return False, response_data


def check_copy_status(params):
    get_status = 'storage-systems/%s/volume-copy-jobs-control/%s' % (
        params['ssid'], params['volume_copy_pair_id'])
    url = params['api_url'] + get_status

    (response_code, response_data) = request(url, ignore_errors=True, method='GET',
                                             url_username=params['api_username'], url_password=params['api_password'],
                                             headers=HEADERS,
                                             validate_certs=params['validate_certs'])

    if response_code == 200:
        if response_data['percentComplete'] != -1:

            return True, response_data['percentComplete']
        else:
            return False, response_data['percentComplete']
    else:
        return False, response_data


def find_valid_copy_pair_targets_and_sources(params):
    get_status = 'storage-systems/%s/volumes' % params['ssid']
    url = params['api_url'] + get_status

    (response_code, response_data) = request(url, ignore_errors=True, method='GET',
                                             url_username=params['api_username'], url_password=params['api_password'],
                                             headers=HEADERS,
                                             validate_certs=params['validate_certs'])

    if response_code == 200:
        source_capacity = None
        candidates = []
        for volume in response_data:
            if volume['id'] == params['search_volume_id']:
                source_capacity = volume['capacity']
            else:
                candidates.append(volume)

        potential_sources = []
        potential_targets = []

        for volume in candidates:
            if volume['capacity'] > source_capacity:
                if volume['volumeCopyTarget'] is False:
                    if volume['volumeCopySource'] is False:
                        potential_targets.append(volume['id'])
            else:
                if volume['volumeCopyTarget'] is False:
                    if volume['volumeCopySource'] is False:
                        potential_sources.append(volume['id'])

        return potential_targets, potential_sources

    else:
        raise Exception("Response [%s]" % response_code)


def main():
    module = AnsibleModule(argument_spec=dict(
        source_volume_id=dict(type='str'),
        destination_volume_id=dict(type='str'),
        copy_priority=dict(required=False, default=0, type='int'),
        ssid=dict(required=True, type='str'),
        api_url=dict(required=True),
        api_username=dict(required=False),
        api_password=dict(required=False, no_log=True),
        validate_certs=dict(required=False, default=True),
        targetWriteProtected=dict(required=False, default=True, type='bool'),
        onlineCopy=dict(required=False, default=False, type='bool'),
        volume_copy_pair_id=dict(type='str'),
        status=dict(required=True, choices=['present', 'absent'], type='str'),
        create_copy_pair_if_does_not_exist=dict(required=False, default=True, type='bool'),
        start_stop_copy=dict(required=False, choices=['start', 'stop'], type='str'),
        search_volume_id=dict(type='str'),
    ),
        mutually_exclusive=[['volume_copy_pair_id', 'destination_volume_id'],
                            ['volume_copy_pair_id', 'source_volume_id'],
                            ['volume_copy_pair_id', 'search_volume_id'],
                            ['search_volume_id', 'destination_volume_id'],
                            ['search_volume_id', 'source_volume_id'],
                            ],
        required_together=[['source_volume_id', 'destination_volume_id'],
                           ],
        required_if=[["create_copy_pair_if_does_not_exist", True, ['source_volume_id', 'destination_volume_id'], ],
                     ["start_stop_copy", 'stop', ['volume_copy_pair_id'], ],
                     ["start_stop_copy", 'start', ['volume_copy_pair_id'], ],
                     ]

    )
    params = module.params

    if not params['api_url'].endswith('/'):
        params['api_url'] += '/'

    # Check if we want to search
    if params['search_volume_id'] is not None:
        try:
            potential_targets, potential_sources = find_valid_copy_pair_targets_and_sources(params)
        except Exception as e:
            module.fail_json(msg="Failed to find valid copy pair candidates. Error [%s]" % to_native(e))

        module.exit_json(changed=False,
                         msg=' Valid source devices found: %s Valid target devices found: %s' % (len(potential_sources), len(potential_targets)),
                         search_volume_id=params['search_volume_id'],
                         valid_targets=potential_targets,
                         valid_sources=potential_sources)

    # Check if we want to start or stop a copy operation
    if params['start_stop_copy'] == 'start' or params['start_stop_copy'] == 'stop':

        # Get the current status info
        currenty_running, status_info = check_copy_status(params)

        # If we want to start
        if params['start_stop_copy'] == 'start':

            # If we have already started
            if currenty_running is True:
                module.exit_json(changed=False, msg='Volume Copy Pair copy has started.',
                                 volume_copy_pair_id=params['volume_copy_pair_id'], percent_done=status_info)
            # If we need to start
            else:

                start_status, info = start_stop_copy(params)

                if start_status is True:
                    module.exit_json(changed=True, msg='Volume Copy Pair copy has started.',
                                     volume_copy_pair_id=params['volume_copy_pair_id'], percent_done=info)
                else:
                    module.fail_json(msg="Could not start volume copy pair Error: %s" % info)

        # If we want to stop
        else:
            # If it has already stopped
            if currenty_running is False:
                module.exit_json(changed=False, msg='Volume Copy Pair copy is stopped.',
                                 volume_copy_pair_id=params['volume_copy_pair_id'])

            # If we need to stop it
            else:
                start_status, info = start_stop_copy(params)

                if start_status is True:
                    module.exit_json(changed=True, msg='Volume Copy Pair copy has been stopped.',
                                     volume_copy_pair_id=params['volume_copy_pair_id'])
                else:
                    module.fail_json(msg="Could not stop volume copy pair Error: %s" % info)

    # If we want the copy pair to exist we do this stuff
    if params['status'] == 'present':

        # We need to check if it exists first
        if params['volume_copy_pair_id'] is None:
            params['volume_copy_pair_id'] = find_volume_copy_pair_id_from_source_volume_id_and_destination_volume_id(
                params)

        # If no volume copy pair is found we need need to make it.
        if params['volume_copy_pair_id'] is None:

            # In order to create we can not do so with just a volume_copy_pair_id

            copy_began_status, (rc, resp) = create_copy_pair(params)

            if copy_began_status is True:
                module.exit_json(changed=True, msg='Created Volume Copy Pair with ID: %s' % resp['id'])
            else:
                module.fail_json(msg="Could not create volume copy pair Code: %s Error: %s" % (rc, resp))

        # If it does exist we do nothing
        else:
            # We verify that it exists
            exist_status, (exist_status_code, exist_status_data) = find_volume_copy_pair_id_by_volume_copy_pair_id(
                params)

            if exist_status:
                module.exit_json(changed=False,
                                 msg=' Volume Copy Pair with ID: %s exists' % params['volume_copy_pair_id'])
            else:
                if exist_status_code == 404:
                    module.fail_json(
                        msg=' Volume Copy Pair with ID: %s does not exist. Can not create without source_volume_id and destination_volume_id' %
                            params['volume_copy_pair_id'])
                else:
                    module.fail_json(msg="Could not find volume copy pair Code: %s Error: %s" % (
                        exist_status_code, exist_status_data))

        module.fail_json(msg="Done")

    # If we want it to not exist we do this
    else:

        if params['volume_copy_pair_id'] is None:
            params['volume_copy_pair_id'] = find_volume_copy_pair_id_from_source_volume_id_and_destination_volume_id(
                params)

        # We delete it by the volume_copy_pair_id
        delete_status, (delete_status_code, delete_status_data) = delete_copy_pair_by_copy_pair_id(params)

        if delete_status is True:
            module.exit_json(changed=True,
                             msg=' Volume Copy Pair with ID: %s was deleted' % params['volume_copy_pair_id'])
        else:
            if delete_status_code == 404:
                module.exit_json(changed=False,
                                 msg=' Volume Copy Pair with ID: %s does not exist' % params['volume_copy_pair_id'])
            else:
                module.fail_json(msg="Could not delete volume copy pair Code: %s Error: %s" % (
                    delete_status_code, delete_status_data))


if __name__ == '__main__':
    main()

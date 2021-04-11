#!/usr/bin/python
#
# Copyright 2021 VMware, Inc
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
---
module: disk_info
version_added: "2.5.0"
short_description: Retrieves disk info
description:
    - This module retrieves disk info like free space, used percentage, mount location, and so on.
requirements:
  - psutil (Python module)
options:
    name:
        description:
            - This is the disk name to query, if this parameter is not passed, it queries all the disk information.
        type: str
    filter:
        description:
            - This is the parameter used to filter only the specific information from the output like freespace, mountpoint, fstype, and so on.
        type: list
        elements: str
        choices: ['freespace', 'usedspace', 'totalsize', 'mountpoint', 'fstype', 'capacity_percent']
author:
    - Saranya Sridharan (@saranyasridharan)
    - Swetha M (@swetm)
    - Nagendra Kini (@NagendraKini)
    - Anup Kumar (@anuppoojari)
    - Mehmoodkha Pathan (@Mehmoodpathan)
'''

EXAMPLES = '''
- name: Get disk info
  community.general.disk_info:

- name: Get Disk info for Particular disk info
  community.general.disk_info:
    name: diskname

- name: Filter the output parameters for specific disk
  community.general.disk_info:
    name: diskname
    filter:
      - mountpoint
      - freespace
      - totalsize

- name: Filter the output parameters for all disk
  community.general.disk_info:
    filter:
      - fstype
      - usedspace
      - capacity_percentage
'''


RETURN = '''
disk_info:
    description: Retrieves disk info, if filter option is given retrieves only filtered values like freespace, totalsize and so on.
    returned: dictionary of disks informations
    type: dict
    contains:
        totalsize:
            description: Size in bytes of the particular disk.
            type: int
            sample: 499963174912
        freespace:
            description: Freespace in bytes of the particular disk.
            type: int
            sample: 351641169920
        usedspace:
            description: Usedspace in bytes of the particular disk.
            type: int
            sample: 11198701568
        capacity_percentage:
            description: Used capacity percentage of the particular disk.
            type: float
            sample: 3.1
        fstype:
            description: Filesystem of the particular disk.
            type: str
            sample: apfs
        mountpoint:
            description: Mountpoint of the particular disk.
            type: str
            sample: /
'''


from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import traceback
PSUTIL_IMP_ERR = None
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    PSUTIL_IMP_ERR = traceback.format_exc()
    HAS_PSUTIL = False


# To get the disk partitions information
def disk_info(devicename):
    output = {}
    partitions = psutil.disk_partitions()
    found = False
    for partition in partitions:
        if not partition.device.startswith("/dev/"):
            continue
        output[partition.device] = {}
        output[partition.device]['mountpoint'] = partition.mountpoint
        output[partition.device]['fstype'] = partition.fstype
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        output[partition.device]['totalsize'] = partition_usage.total
        output[partition.device]['usedspace'] = partition_usage.used
        output[partition.device]['freespace'] = partition_usage.free
        output[partition.device]['capacity_percentage'] = partition_usage.percent
        if partition.device == devicename:
            found = True
            break
    if devicename is None:
        return output
    if devicename in output:
        return {devicename: output[devicename]}
    return {}


# To filter the required values from the output
def filter_result(output, filter):
    filteroutput = {}
    for key in output:
        filteroutput[key] = {param: output[key][param] for param in filter}
    return filteroutput


def main():
    module_args = dict(
        name=dict(type='str', required=False),
        filter=dict(type='list', required=False, elements='str', choices=['freespace', 'usedspace', 'totalsize', 'mountpoint', 'fstype', 'capacity_percent'])
    )

    result = dict(
        changed=False,
    )

    filter = []
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # To handle 'psutil' not installed scenario
    if not HAS_PSUTIL:
        module.fail_json(msg=missing_required_lib('psutil'), exception=PSUTIL_IMP_ERR)
    devicename = None
    if module.params['name']:
        devicename = module.params['name'].lower()
    if module.params['filter']:
        filter = module.params['filter']
        filter = [value.lower() for value in filter]
    output = disk_info(devicename)

    if output == {}:
        module.fail_json(msg="Queried disk %s is not found" % (devicename))

    if filter:
        output = filter_result(output, filter)
    result['disk_info'] = output
    module.exit_json(**result)


if __name__ == '__main__':
    main()

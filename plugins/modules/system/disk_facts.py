#!/usr/bin/python
#
# Copyright 2021 VMware, Inc
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: disk_facts
version_added: "2.5.0"
short_description: Get disk facts in the linux OS
description:
    - This module is to get disk facts like free space, used percentage, mount location etc in linux Ansible controller/controlled machines.
requirements:
  - psutil(python module)
options:
    name:
        description:
            - This is the disk name to query
        required: false
        default: all
        type: str
    filter:
        description:
            - This is the parameter used to filter the output
        required: false
        type: list
        elements: str
author:
    - Saranya Sridharan(@saranyasridharan), Swetha M, Nagendra Kini, Anup Kumar, Mehmoodkha Pathan
'''

EXAMPLES = '''
- name: Get disk facts
  community.general.disk_facts:

- name: Get Disk facts for Particular disk info
  community.general.disk_facts:
    name: diskname

- name: Filter the output parameters for specific disk
  community.general.disk_facts:
    name: diskname
    filter:
      - mountpoint
      - freespace
      - totalsize

- name: Filter the output parameters for all disk
  community.general.disk_facts:
    filter:
      - fstype
      - usedspace
      - capacity_percentage
'''


RETURN = '''
ansible_facts:
    description: disk information only filtered parameter values if filter option is given.
    returned: dictionary of disks informations
    type: dict
    sample: {
        '/dev/disk1s1': {
             'capacity_percentage': '2%'
        }
    }
'''


from ansible.module_utils.basic import AnsibleModule
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


# To calculate the disk size
def calculate_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return "{0:.2f}{1}{2}".format(bytes, unit, suffix)
        bytes /= factor


# To get the disk partitions information
def disk_facts(devicename):
    output = {}
    partitions = psutil.disk_partitions()
    found = False
    for partition in partitions:
        if partition.device == devicename:
            found = True
        output[partition.device] = {}
        output[partition.device]['mountpoint'] = partition.mountpoint
        output[partition.device]['fstype'] = partition.fstype
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        output[partition.device]['totalsize'] = calculate_size(partition_usage.total)
        output[partition.device]['usedspace'] = calculate_size(partition_usage.used)
        output[partition.device]['freespace'] = calculate_size(partition_usage.free)
        output[partition.device]['capacity_percentage'] = str(partition_usage.percent) + "%"
    if devicename == "all":
        return output
    if devicename in output.keys():
        return {devicename: output[devicename]}
    if not found:
        return 0


# To filter the required values from the output
def filter_result(output, filtervalue):
    filteroutput = {}
    keys = output.keys()
    for key in keys:
        filteroutput[key] = {}
        for parameter, value in output[key].items():
            if parameter in filtervalue:
                filteroutput[key][parameter] = value
    return filteroutput


def main():
    module_args = dict(
        name=dict(type='str', required=False, default="all"),
        filter=dict(type='list', required=False, elements='str')
    )

    result = dict(
        changed=False,
    )

    filter = ""
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # To handle 'psutil' not installed scenario
    if not HAS_PSUTIL:
        module.fail_json(msg="Missing required 'psutil' python module. Try installing it with: pip install psutil or pip3 install psutil`")

    devicename = module.params['name'].lower()
    if module.params['filter']:
        filter = module.params['filter']
        filter = [value.lower() for value in filter]
    output = disk_facts(devicename)

    if output == 0:
        module.fail_json(msg="Queried disk %s is not found" % (devicename))

    if filter:
        output = filter_result(output, filter)
    result['ansible_facts'] = output
    module.exit_json(**result)


if __name__ == '__main__':
    main()

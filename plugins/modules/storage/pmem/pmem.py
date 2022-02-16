#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2022, Masayoshi Mizuma <msys.mizuma@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
author:
 - Masayoshi Mizuma (@mizumm)
module: pmem
short_description: Configure Intel Optane Persistent Memory modules
version_added: 4.5.0
description:
 - This module allows Configuring Intel Optane Persistent Memory modules
   (PMem) using ipmctl and ndctl command line tools.
requirements:
 - ipmctl and ndctl command line tools
 - xmltodict
options:
  appdirect:
    description:
     - Percentage of the total capacity to use in AppDirect Mode (C(0)-C(100)).
     - Create AppDirect capacity utilizing hardware interleaving across the
       requested PMem modules if applicable given the specified target.
     - Total of I(appdirect), I(memorymode) and I(reserved) must be C(100)
    type: int
  appdirect_interleaved:
    description:
     - Create AppDirect capacity that is interleaved any other PMem modules.
    type: bool
    required: false
    default: true
  memorymode:
    description:
     - Percentage of the total capacity to use in Memory Mode (C(0)-C(100)).
    type: int
  reserved:
    description:
     - Percentage of the capacity to reserve (C(0)-C(100)). I(reserved) will not be mapped
       into the system physical address space and will be presented as reserved
       capacity with Show Device and Show Memory Resources Commands.
     - I(reserved) will be set automatically if this is not configured.
    type: int
    required: false
  socket:
    description:
     - This enables to set the configuration for each socket by using the socket ID.
     - Total of I(appdirect), I(memorymode) and I(reserved) must be C(100) within one socket.
    type: list
    elements: dict
    suboptions:
      id:
        description: The socket ID of the PMem module.
        type: int
        required: true
      appdirect:
        description:
         - Percentage of the total capacity to use in AppDirect Mode (C(0)-C(100)) within the socket ID.
        type: int
        required: true
      appdirect_interleaved:
        description:
         - Create AppDirect capacity that is interleaved any other PMem modules within the socket ID.
        type: bool
        required: false
        default: true
      memorymode:
        description:
         - Percentage of the total capacity to use in Memory Mode (C(0)-C(100)) within the socket ID.
        type: int
        required: true
      reserved:
        description:
          - Percentage of the capacity to reserve (C(0)-C(100)) within the socket ID.
        type: int
'''

RETURN = r'''
reboot_required:
    description: Indicates that the system reboot is required to complete the PMem configuration.
    returned: success
    type: bool
    sample: True
result:
    description:
     - Shows the value of AppDirect, Memory Mode and Reserved size in bytes.
     - If I(socket) argument is provided, shows the values in each socket with C(socket) which contains the socket ID.
    returned: success
    type: list
    elements: dict
    contains:
        appdirect:
          description: AppDirect size in bytes.
          type: int
        memorymode:
          description: Memory Mode size in bytes.
          type: int
        reserved:
          description: Reserved size in bytes.
          type: int
        socket:
          description: The socket ID to be configured.
          type: int
    sample: [
                {
                    "appdirect": 111669149696,
                    "memorymode": 970662608896,
                    "reserved": 3626500096,
                    "socket": 0
                },
                {
                    "appdirect": 111669149696,
                    "memorymode": 970662608896,
                    "reserved": 3626500096,
                    "socket": 1
                }
            ]
'''

EXAMPLES = r'''
- name: Configure the Pmem as AppDirect 10, Memory Mode 70, and the Reserved 20 percent.
  community.general.pmem:
    appdirect: 10
    memorymode: 70

- name: Configure the Pmem as AppDirect 10, Memory Mode 80, and the Reserved 10 percent.
  community.general.pmem:
    appdirect: 10
    memorymode: 80
    reserved: 10

- name: Configure the Pmem as AppDirect with not interleaved 10, Memory Mode 70, and the Reserved 20 percent.
  community.general.pmem:
    appdirect: 10
    appdirect_interleaved: False
    memorymode: 70

- name: Configure the Pmem each socket.
  community.general.pmem:
    socket:
      - id: 0
        appdirect: 10
        appdirect_interleaved: False
        memorymode: 70
        reserved: 20
      - id: 1
        appdirect: 10
        memorymode: 80
        reserved: 10
'''

import json
import re
import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib

try:
    import xmltodict
except ImportError:
    HAS_XMLTODICT_LIBRARY = False
    XMLTODICT_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_XMLTODICT_LIBRARY = True


class PersistentMemory(object):
    def __init__(self):
        module = AnsibleModule(
            argument_spec=dict(
                appdirect=dict(type='int'),
                appdirect_interleaved=dict(type='bool', default=True),
                memorymode=dict(type='int'),
                reserved=dict(type='int'),
                socket=dict(
                    type='list', elements='dict',
                    options=dict(
                        id=dict(required=True, type='int'),
                        appdirect=dict(required=True, type='int'),
                        appdirect_interleaved=dict(type='bool', default=True),
                        memorymode=dict(required=True, type='int'),
                        reserved=dict(type='int'),
                    ),
                ),
            ),
            required_together=(
                ['appdirect', 'memorymode'],
            ),
            required_one_of=(
                ['appdirect', 'memorymode', 'socket'],
            ),
            mutually_exclusive=(
                ['appdirect', 'socket'],
                ['memorymode', 'socket'],
            ),
        )

        if not HAS_XMLTODICT_LIBRARY:
            module.fail_json(
                msg=missing_required_lib('xmltodict'),
                exception=XMLTODICT_LIBRARY_IMPORT_ERROR)

        self.ipmctl_exec = module.get_bin_path('ipmctl', True)
        self.ndctl_exec = module.get_bin_path('ndctl', True)

        self.appdirect = module.params['appdirect']
        self.interleaved = module.params['appdirect_interleaved']
        self.memmode = module.params['memorymode']
        self.reserved = module.params['reserved']
        self.socket = module.params['socket']

        self.module = module
        self.changed = False
        self.result = []

    def pmem_run_command(self, command, returnCheck=True):
        # in case command[] has number
        cmd = [str(part) for part in command]

        self.module.log(msg='pmem_run_command: execute: %s' % cmd)

        rc, out, err = self.module.run_command(cmd)

        self.module.log(msg='pmem_run_command: result: %s' % out)

        if returnCheck and rc != 0:
            self.module.fail_json(msg='Error while running: %s' %
                                  cmd, rc=rc, out=out, err=err)

        return out

    def pmem_run_ipmctl(self, command, returnCheck=True):

        command = [self.ipmctl_exec] + command

        return self.pmem_run_command(command, returnCheck)

    def pmem_run_ndctl(self, command, returnCheck=True):

        command = [self.ndctl_exec] + command

        return self.pmem_run_command(command, returnCheck)

    def pmem_is_dcpmm_installed(self):
        # To check this system has dcpmm
        command = ['show', '-system', '-capabilities']
        return self.pmem_run_ipmctl(command)

    def pmem_argument_check(self):
        def percent_check(self, appdirect, memmode, reserved=None):
            if appdirect is None or (appdirect < 0 or appdirect > 100):
                return 'appdirect percent should be from 0 to 100.'
            if memmode is None or (memmode < 0 or memmode > 100):
                return 'memorymode percent should be from 0 to 100.'

            if reserved is None:
                if appdirect + memmode > 100:
                    return 'Total percent should be less equal 100.'
            else:
                if reserved < 0 or reserved > 100:
                    return 'reserved percent should be from 0 to 100.'
                if appdirect + memmode + reserved != 100:
                    return 'Total percent should be 100.'

        def socket_id_check(self):
            command = ['show', '-o', 'nvmxml', '-socket']
            out = self.pmem_run_ipmctl(command)
            sockets_dict = xmltodict.parse(out, dict_constructor=dict)['SocketList']['Socket']
            socket_ids = []
            for sl in sockets_dict:
                socket_ids.append(int(sl['SocketID'], 16))

            for skt in self.socket:
                if skt['id'] not in socket_ids:
                    return 'Invalid socket number: %d' % skt['id']

            return None

        if self.socket is None:
            return percent_check(self, self.appdirect, self.memmode, self.reserved)
        else:
            ret = socket_id_check(self)
            if ret is not None:
                return ret

            for skt in self.socket:
                ret = percent_check(
                    self, skt['appdirect'], skt['memorymode'], skt['reserved'])
                if ret is not None:
                    return ret

            return None

    def pmem_remove_namespaces(self):
        command = ['list', '-N']
        out = self.pmem_run_ndctl(command)

        # There's nothing namespaces in this system. Nothing to do.
        if not out:
            return

        namespaces = json.loads(out)

        # Disable and destroy all namespaces
        for ns in namespaces:
            command = ['disable-namespace', ns['dev']]
            self.pmem_run_ndctl(command)

            command = ['destroy-namespace', ns['dev']]
            self.pmem_run_ndctl(command)

        return

    def pmem_delete_goal(self):
        # delete the goal request
        command = ['delete', '-goal']
        self.pmem_run_ipmctl(command)

    def pmem_init_env(self):
        self.pmem_remove_namespaces()
        self.pmem_delete_goal()

    def pmem_get_capacity(self, skt=None):
        command = ['show', '-d', 'Capacity', '-u', 'B', '-o', 'nvmxml', '-dimm']
        if skt:
            command += ['-socket', skt['id']]
        out = self.pmem_run_ipmctl(command)

        dimm_list = xmltodict.parse(out, dict_constructor=dict)['DimmList']['Dimm']
        capacity = 0
        for entry in dimm_list:
            for key, v in entry.items():
                if key == 'Capacity':
                    capacity += int(v.split()[0])

        return capacity

    def pmem_create_memory_allocation(self, skt=None):
        def build_ipmctl_creation_opts(self, skt=None):
            ipmctl_opts = []

            if skt:
                appdirect = skt['appdirect']
                memmode = skt['memorymode']
                reserved = skt['reserved']
                socket_id = skt['id']
                ipmctl_opts += ['-socket', socket_id]
            else:
                appdirect = self.appdirect
                memmode = self.memmode
                reserved = self.reserved

            if reserved is None:
                res = 100 - memmode - appdirect
                ipmctl_opts += ['memorymode=%d' % memmode, 'reserved=%d' % res]
            else:
                ipmctl_opts += ['memorymode=%d' % memmode, 'reserved=%d' % reserved]

            if self.interleaved:
                ipmctl_opts += ['PersistentMemoryType=AppDirect']
            else:
                ipmctl_opts += ['PersistentMemoryType=AppDirectNotInterleaved']

            return ipmctl_opts

        def is_allocation_good(self, ipmctl_out, command):
            warning = re.compile('WARNING')
            error = re.compile('.*Error.*')
            ignore_error = re.compile(
                'Do you want to continue? [y/n] Error: Invalid data input.')

            errmsg = ''
            rc = True
            for line in ipmctl_out.splitlines():
                if warning.match(line):
                    errmsg = '%s (command: %s)' % (line, command)
                    rc = False
                    break
                elif error.match(line):
                    if not ignore_error:
                        errmsg = '%s (command: %s)' % (line, command)
                        rc = False
                        break

            return rc, errmsg

        def get_allocation_result(self, goal, skt=None):
            ret = {'appdirect': 0, 'memorymode': 0}

            if skt:
                ret['socket'] = skt['id']

            out = xmltodict.parse(goal, dict_constructor=dict)['ConfigGoalList']['ConfigGoal']
            for entry in out:

                # Probably it's a bug of ipmctl to show the socket goal
                # which isn't specified by the -socket option.
                # Anyway, filter the noise out here:
                if skt and skt['id'] != int(entry['SocketID'], 16):
                    continue

                for key, v in entry.items():
                    if key == 'MemorySize':
                        ret['memorymode'] += int(v.split()[0])
                    elif key == 'AppDirect1Size' or key == 'AapDirect2Size':
                        ret['appdirect'] += int(v.split()[0])

            capacity = self.pmem_get_capacity(skt)
            ret['reserved'] = capacity - ret['appdirect'] - ret['memorymode']

            return ret

        reboot_required = False

        ipmctl_opts = build_ipmctl_creation_opts(self, skt)

        # First, do dry run ipmctl create command to check the error and warning.
        command = ['create', '-goal'] + ipmctl_opts
        out = self.pmem_run_ipmctl(command, returnCheck=False)
        rc, errmsg = is_allocation_good(self, out, command)
        if rc is False:
            return reboot_required, {}, errmsg

        # Run actual creation here
        command = ['create', '-u', 'B', '-o', 'nvmxml', '-force', '-goal'] + ipmctl_opts
        goal = self.pmem_run_ipmctl(command)
        ret = get_allocation_result(self, goal, skt)
        reboot_required = True

        return reboot_required, ret, ''


def main():

    pmem = PersistentMemory()

    pmem.pmem_is_dcpmm_installed()

    error = pmem.pmem_argument_check()
    if error:
        pmem.module.fail_json(msg=error)

    pmem.pmem_init_env()
    pmem.changed = True

    if pmem.socket is None:
        reboot_required, ret, errmsg = pmem.pmem_create_memory_allocation()
        if errmsg:
            pmem.module.fail_json(msg=errmsg)
        pmem.result.append(ret)
    else:
        for skt in pmem.socket:
            skt_reboot_required, skt_ret, skt_errmsg = pmem.pmem_create_memory_allocation(skt)

            if skt_errmsg:
                pmem.module.fail_json(msg=skt_errmsg)

            if skt_reboot_required:
                reboot_required = True

            pmem.result.append(skt_ret)

    pmem.module.exit_json(
        changed=pmem.changed,
        reboot_required=reboot_required,
        result=pmem.result
    )


if __name__ == '__main__':
    main()

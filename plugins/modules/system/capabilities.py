#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2014, Nate Coraor <nate@bx.psu.edu>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: capabilities
short_description: Manage Linux capabilities
description:
    - This module manipulates files privileges using the Linux capabilities(7) system.
options:
    path:
        description:
            - Specifies the path to the file to be managed.
        type: str
        required: yes
        aliases: [ key ]
    capability:
        description:
            - Desired capability to set (with operator and flags, if state is C(present)) or remove (if state is C(absent))
        type: str
        required: yes
        aliases: [ cap ]
    state:
        description:
            - Whether the entry should be present or absent in the file's capabilities.
        type: str
        choices: [ absent, present ]
        default: present
notes:
    - The capabilities system will automatically transform operators and flags into the effective set,
      so for example, C(cap_foo=ep) will probably become C(cap_foo+ep).
    - This module does not attempt to determine the final operator and flags to compare,
      so you will want to ensure that your capabilities argument matches the final capabilities.
author:
- Nate Coraor (@natefoo)
'''

EXAMPLES = r'''
- name: Set cap_sys_chroot+ep on /foo
  community.general.capabilities:
    path: /foo
    capability: cap_sys_chroot+ep
    state: present

- name: Remove cap_net_bind_service from /bar
  community.general.capabilities:
    path: /bar
    capability: cap_net_bind_service
    state: absent
'''

from ansible.module_utils.basic import AnsibleModule

OPS = ('=', '-', '+')


class CapabilitiesModule(object):
    platform = 'Linux'
    distribution = None

    def __init__(self, module):
        self.module = module
        self.path = module.params['path'].strip()
        self.capability = module.params['capability'].strip().lower()
        self.state = module.params['state']
        self.getcap_cmd = module.get_bin_path('getcap', required=True)
        self.setcap_cmd = module.get_bin_path('setcap', required=True)
        self.capability_tup = self._parse_cap(self.capability, op_required=self.state == 'present')

        self.run()

    def run(self):

        current = self.getcap(self.path)
        caps = [cap[0] for cap in current]

        if self.state == 'present' and self.capability_tup not in current:
            # need to add capability
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg='capabilities changed')
            else:
                # remove from current cap list if it's already set (but op/flags differ)
                current = list(filter(lambda x: x[0] != self.capability_tup[0], current))
                # add new cap with correct op/flags
                current.append(self.capability_tup)
                self.module.exit_json(changed=True, state=self.state, msg='capabilities changed', stdout=self.setcap(self.path, current))
        elif self.state == 'absent' and self.capability_tup[0] in caps:
            # need to remove capability
            if self.module.check_mode:
                self.module.exit_json(changed=True, msg='capabilities changed')
            else:
                # remove from current cap list and then set current list
                current = filter(lambda x: x[0] != self.capability_tup[0], current)
                self.module.exit_json(changed=True, state=self.state, msg='capabilities changed', stdout=self.setcap(self.path, current))
        self.module.exit_json(changed=False, state=self.state)

    def getcap(self, path):
        rval = []
        cmd = "%s -v %s" % (self.getcap_cmd, path)
        rc, stdout, stderr = self.module.run_command(cmd)
        # If file xattrs are set but no caps are set the output will be:
        #   '/foo ='
        # If file xattrs are unset the output will be:
        #   '/foo'
        # If the file does not exist, the stderr will be (with rc == 0...):
        #   '/foo (No such file or directory)'
        if rc != 0 or stderr != "":
            self.module.fail_json(msg="Unable to get capabilities of %s" % path, stdout=stdout.strip(), stderr=stderr)
        if stdout.strip() != path:
            if ' =' in stdout:
                # process output of an older version of libcap
                caps = stdout.split(' =')[1].strip().split()
            else:
                # otherwise, we have a newer version here
                # see original commit message of cap/v0.2.40-18-g177cd41 in libcap.git
                caps = stdout.split()[1].strip().split()
            for cap in caps:
                cap = cap.lower()
                # getcap condenses capabilities with the same op/flags into a
                # comma-separated list, so we have to parse that
                if ',' in cap:
                    cap_group = cap.split(',')
                    cap_group[-1], op, flags = self._parse_cap(cap_group[-1])
                    for subcap in cap_group:
                        rval.append((subcap, op, flags))
                else:
                    rval.append(self._parse_cap(cap))
        return rval

    def setcap(self, path, caps):
        caps = ' '.join([''.join(cap) for cap in caps])
        cmd = "%s '%s' %s" % (self.setcap_cmd, caps, path)
        rc, stdout, stderr = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(msg="Unable to set capabilities of %s" % path, stdout=stdout, stderr=stderr)
        else:
            return stdout

    def _parse_cap(self, cap, op_required=True):
        opind = -1
        try:
            i = 0
            while opind == -1:
                opind = cap.find(OPS[i])
                i += 1
        except Exception:
            if op_required:
                self.module.fail_json(msg="Couldn't find operator (one of: %s)" % str(OPS))
            else:
                return (cap, None, None)
        op = cap[opind]
        cap, flags = cap.split(op)
        return (cap, op, flags)


# ==============================================================
# main

def main():
    # defining module
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='str', required=True, aliases=['key']),
            capability=dict(type='str', required=True, aliases=['cap']),
            state=dict(type='str', default='present', choices=['absent', 'present']),
        ),
        supports_check_mode=True,
    )

    CapabilitiesModule(module)


if __name__ == '__main__':
    main()

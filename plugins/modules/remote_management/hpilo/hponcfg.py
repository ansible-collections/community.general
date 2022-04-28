#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2012, Dag Wieers <dag@wieers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: hponcfg
author: Dag Wieers (@dagwieers)
short_description: Configure HP iLO interface using hponcfg
description:
 - This modules configures the HP iLO interface using hponcfg.
options:
  path:
    description:
     - The XML file as accepted by hponcfg.
    required: true
    aliases: ['src']
    type: path
  minfw:
    description:
     - The minimum firmware level needed.
    required: false
    type: str
  executable:
    description:
     - Path to the hponcfg executable (`hponcfg` which uses $PATH).
    default: hponcfg
    type: str
  verbose:
    description:
     - Run hponcfg in verbose mode (-v).
    default: no
    type: bool
requirements:
 - hponcfg tool
notes:
 - You need a working hponcfg on the target system.
'''

EXAMPLES = r'''
- name: Example hponcfg configuration XML
  ansible.builtin.copy:
    content: |
      <ribcl VERSION="2.0">
        <login USER_LOGIN="user" PASSWORD="password">
          <rib_info MODE="WRITE">
            <mod_global_settings>
              <session_timeout value="0"/>
              <ssh_status value="Y"/>
              <ssh_port value="22"/>
              <serial_cli_status value="3"/>
              <serial_cli_speed value="5"/>
            </mod_global_settings>
          </rib_info>
        </login>
      </ribcl>
    dest: /tmp/enable-ssh.xml

- name: Configure HP iLO using enable-ssh.xml
  community.general.hponcfg:
    src: /tmp/enable-ssh.xml

- name: Configure HP iLO on VMware ESXi hypervisor
  community.general.hponcfg:
    src: /tmp/enable-ssh.xml
    executable: /opt/hp/tools/hponcfg
'''

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    CmdModuleHelper, ArgFormat
)


class HPOnCfg(CmdModuleHelper):
    module = dict(
        argument_spec=dict(
            src=dict(type='path', required=True, aliases=['path']),
            minfw=dict(type='str'),
            executable=dict(default='hponcfg', type='str'),
            verbose=dict(default=False, type='bool'),
        )
    )
    command_args_formats = dict(
        src=dict(fmt=["-f", "{0}"]),
        verbose=dict(fmt="-v", style=ArgFormat.BOOLEAN),
        minfw=dict(fmt=["-m", "{0}"]),
    )
    check_rc = True

    def __init_module__(self):
        self.command = self.vars.executable
        # Consider every action a change (not idempotent yet!)
        self.changed = True

    def __run__(self):
        self.run_command(params=['src', 'verbose', 'minfw'])


def main():
    HPOnCfg.execute()


if __name__ == '__main__':
    main()

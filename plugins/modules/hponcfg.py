#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, Dag Wieers <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: hponcfg
author: Dag Wieers (@dagwieers)
short_description: Configure HP iLO interface using hponcfg
description:
  - This modules configures the HP iLO interface using hponcfg.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
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
     - Path to the hponcfg executable (C(hponcfg) which uses $PATH).
    default: hponcfg
    type: str
  verbose:
    description:
     - Run hponcfg in verbose mode (-v).
    default: false
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

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper


class HPOnCfg(ModuleHelper):
    module = dict(
        argument_spec=dict(
            src=dict(type='path', required=True, aliases=['path']),
            minfw=dict(type='str'),
            executable=dict(default='hponcfg', type='str'),
            verbose=dict(default=False, type='bool'),
        )
    )
    command_args_formats = dict(
        src=cmd_runner_fmt.as_opt_val("-f"),
        verbose=cmd_runner_fmt.as_bool("-v"),
        minfw=cmd_runner_fmt.as_opt_val("-m"),
    )
    use_old_vardict = False

    def __run__(self):
        runner = CmdRunner(
            self.module,
            self.vars.executable,
            self.command_args_formats,
            check_rc=True,
        )
        runner(['src', 'verbose', 'minfw']).run()

        # Consider every action a change (not idempotent yet!)
        self.changed = True


def main():
    HPOnCfg.execute()


if __name__ == '__main__':
    main()

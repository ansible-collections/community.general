#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Michael DeHaan <michael@ansible.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: say
short_description: Makes a computer to speak
description:
  - Makes a computer speak! Amuse your friends, annoy your coworkers!
notes:
  - In 2.5, this module has been renamed from C(osx_say) to M(community.general.say).
  - If you like this module, you may also be interested in the osx_say callback plugin.
  - A list of available voices, with language, can be found by running C(say -v ?) on a OSX host and C(espeak --voices) on a Linux host.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  msg:
    type: str
    description:
      - What to say.
    required: true
  voice:
    type: str
    description:
      - What voice to use.
    required: false
requirements: [say or espeak or espeak-ng]
author:
  - "Ansible Core Team"
  - "Michael DeHaan (@mpdehaan)"
"""

EXAMPLES = r"""
- name: Makes a computer to speak
  community.general.say:
    msg: '{{ inventory_hostname }} is all done'
    voice: Zarvox
  delegate_to: localhost
"""
import platform

from ansible.module_utils.basic import AnsibleModule


def say(module, executable, msg, voice):
    cmd = [executable, msg]
    if voice:
        cmd.extend(('-v', voice))
    module.run_command(cmd, check_rc=True)


def main():

    module = AnsibleModule(
        argument_spec=dict(
            msg=dict(required=True),
            voice=dict(required=False),
        ),
        supports_check_mode=True
    )

    msg = module.params['msg']
    voice = module.params['voice']
    possibles = ('say', 'espeak', 'espeak-ng')

    if platform.system() != 'Darwin':
        # 'say' binary available, it might be GNUstep tool which doesn't support 'voice' parameter
        voice = None

    for possible in possibles:
        executable = module.get_bin_path(possible)
        if executable:
            break
    else:
        module.fail_json(msg='Unable to find either %s' % ', '.join(possibles))

    if module.check_mode:
        module.exit_json(msg=msg, changed=False)

    say(module, executable, msg, voice)

    module.exit_json(msg=msg, changed=True)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
module: shutdown
short_description: Shut down a machine
notes:
  - C(PATH) is ignored on the remote node when searching for the C(shutdown) command. Use I(search_paths)
    to specify locations to search if the default paths do not work.
description:
    - Shut downs a machine.
version_added: "1.1.0"
options:
  delay:
    description:
      - Seconds to wait before shutdown. Passed as a parameter to the shutdown command.
      - On Linux, macOS and OpenBSD, this is converted to minutes and rounded down. If less than 60, it will be set to 0.
      - On Solaris and FreeBSD, this will be seconds.
    type: int
    default: 0
  msg:
    description:
      - Message to display to users before shutdown.
    type: str
    default: Shut down initiated by Ansible
  search_paths:
    description:
      - Paths to search on the remote machine for the C(shutdown) command.
      - I(Only) these paths will be searched for the C(shutdown) command. C(PATH) is ignored in the remote node when searching for the C(shutdown) command.
    type: list
    elements: path
    default: ['/sbin', '/usr/sbin', '/usr/local/sbin']

seealso:
- module: ansible.builtin.reboot
author:
    - Matt Davis (@nitzmahone)
    - Sam Doran (@samdoran)
    - Amin Vakil (@aminvakil)
'''

EXAMPLES = r'''
- name: Unconditionally shut down the machine with all defaults
  community.general.shutdown:

- name: Delay shutting down the remote node
  community.general.shutdown:
    delay: 60

- name: Shut down a machine with shutdown command in unusual place
  community.general.shutdown:
    search_paths:
     - '/lib/molly-guard'
'''

RETURN = r'''
shutdown:
  description: C(true) if the machine has been shut down.
  returned: always
  type: bool
  sample: true
'''

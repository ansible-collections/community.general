# -*- coding: utf-8 -*-
# Copyright (c) 2015, Filipe Niero Felisbino <filipenf@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
#
# contributed by Kelly Brazil <kellyjonbrazil@gmail.com>

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
  name: jc
  short_description: Convert output of many shell commands and file-types to JSON
  version_added: 1.1.0
  author: Kelly Brazil (@kellyjonbrazil)
  description:
    - Convert output of many shell commands and file-types to JSON.
    - Uses the L(jc library,https://github.com/kellyjonbrazil/jc).
  positional: parser
  options:
    _input:
      description: The data to convert.
      type: string
      required: true
    parser:
      description:
        - The correct parser for the input data.
        - For example C(ifconfig).
        - See U(https://github.com/kellyjonbrazil/jc#parsers) for the latest list of parsers.
      type: string
      required: true
    quiet:
      description: Set to C(false) to not suppress warnings.
      type: boolean
      default: true
    raw:
      description: Set to C(true) to return pre-processed JSON.
      type: boolean
      default: false
  requirements:
    - jc (https://github.com/kellyjonbrazil/jc)
'''

EXAMPLES = '''
# This step is optional in case you have the package already installed on your machine
- name: Make sure the jc Python library is installed on the Ansible controller
  delegate_to: localhost
  pip:
    name: jc
    state: present

- name: Run command
  ansible.builtin.command: uname -a
  register: result

- name: Convert command's result to JSON
  ansible.builtin.debug:
    msg: "{{ result.stdout | community.general.jc('uname') }}"
  # Possible output:
  #
  # "msg": {
  #   "hardware_platform": "x86_64",
  #   "kernel_name": "Linux",
  #   "kernel_release": "4.15.0-112-generic",
  #   "kernel_version": "#113-Ubuntu SMP Thu Jul 9 23:41:39 UTC 2020",
  #   "machine": "x86_64",
  #   "node_name": "kbrazil-ubuntu",
  #   "operating_system": "GNU/Linux",
  #   "processor": "x86_64"
  # }
'''

RETURN = '''
  _value:
    description: The processed output.
    type: any
'''

from ansible.errors import AnsibleError, AnsibleFilterError
import importlib

try:
    import jc
    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def jc(data, parser, quiet=True, raw=False):
    """Convert returned command output to JSON using the JC library

    Arguments:

        parser      required    (string) the correct parser for the input data (e.g. 'ifconfig')
                                see https://github.com/kellyjonbrazil/jc#parsers for latest list of parsers.
        quiet       optional    (bool) True to suppress warning messages (default is True)
        raw         optional    (bool) True to return pre-processed JSON (default is False)

    Returns:

        dictionary or list of dictionaries

    Example:
        # This step is optional in case you have the package already installed on your machine
        - name: add the jc prereqs to the running machine
          delegate_to: localhost
          pip:
            name: jc
            state: present
        - name: run date command
          hosts: ubuntu
          tasks:
          - shell: date
            register: result
          - set_fact:
              myvar: "{{ result.stdout | community.general.jc('date') }}"
          - debug:
              msg: "{{ myvar }}"

        produces:

        ok: [192.168.1.239] => {
            "msg": {
                "day": 9,
                "hour": 22,
                "minute": 6,
                "month": "Aug",
                "month_num": 8,
                "second": 22,
                "timezone": "UTC",
                "weekday": "Sun",
                "weekday_num": 1,
                "year": 2020
            }
        }
    """

    if not HAS_LIB:
        raise AnsibleError('You need to install "jc" prior to running jc filter')

    try:
        jc_parser = importlib.import_module('jc.parsers.' + parser)
        return jc_parser.parse(data, quiet=quiet, raw=raw)

    except Exception as e:
        raise AnsibleFilterError('Error in jc filter plugin:  %s' % e)


class FilterModule(object):
    ''' Query filter '''

    def filters(self):
        return {
            'jc': jc
        }

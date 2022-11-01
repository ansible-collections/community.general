# -*- coding: utf-8 -*-
# Copyright (c) 2017, Juan Manuel Parrilla <jparrill@redhat.com>
# Copyright (c) 2012-17 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author:
      - Juan Manuel Parrilla (@jparrill)
    name: hiera
    short_description: get info from hiera data
    requirements:
      - hiera (command line utility)
    description:
        - Retrieves data from an Puppetmaster node using Hiera as ENC.
    options:
      _terms:
            description:
                - The list of keys to lookup on the Puppetmaster.
            type: list
            elements: string
            required: true
      executable:
            description:
                - Binary file to execute Hiera.
            default: '/usr/bin/hiera'
            env:
                - name: ANSIBLE_HIERA_BIN
      config_file:
            description:
                - File that describes the hierarchy of Hiera.
            default: '/etc/hiera.yaml'
            env:
                - name: ANSIBLE_HIERA_CFG
# FIXME: incomplete options .. _terms? environment/fqdn?
'''

EXAMPLES = """
# All this examples depends on hiera.yml that describes the hierarchy

- name: "a value from Hiera 'DB'"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.hiera', 'foo') }}"

- name: "a value from a Hiera 'DB' on other environment"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.hiera', 'foo environment=production') }}"

- name: "a value from a Hiera 'DB' for a concrete node"
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.hiera', 'foo fqdn=puppet01.localdomain') }}"
"""

RETURN = """
    _raw:
        description:
            - a value associated with input key
        type: list
        elements: str
"""

import os

from ansible.plugins.lookup import LookupBase
from ansible.utils.cmd_functions import run_cmd
from ansible.module_utils.common.text.converters import to_text


class Hiera(object):
    def __init__(self, hiera_cfg, hiera_bin):
        self.hiera_cfg = hiera_cfg
        self.hiera_bin = hiera_bin

    def get(self, hiera_key):
        pargs = [self.hiera_bin]
        pargs.extend(['-c', self.hiera_cfg])

        pargs.extend(hiera_key)

        rc, output, err = run_cmd("{0} -c {1} {2}".format(
            self.hiera_bin, self.hiera_cfg, hiera_key[0]))

        return to_text(output.strip())


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        hiera = Hiera(self.get_option('config_file'), self.get_option('executable'))
        ret = [hiera.get(terms)]
        return ret

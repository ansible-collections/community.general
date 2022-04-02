# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: bitwarden
    author:
      - Markus Fischbacher (@rockaut)
    requirements:
      - C(bw) Bitwarden command line utility. See U(https://bitwarden.com/help/cli/) or U(https://github.com/bitwarden/cli/).
    short_description: fetch data from bitwarden cli
    description:
      - C(bitwarden) wraps the C(bw) command line utility to fetch your passwords from Bitwarden.
    options:
      _terms:
        description: Search term or object's globally unique id.
        required: True
      object:
        description: Retrieves the requested field or object.
        default: 'item'
      command:
        description: field to return from each matching item (case-insensitive).
        default: 'get'
    notes:
      - This lookup currently need an logged in an unlocked bitwarden cli session
      - This lookup stores potentially sensitive data from bitwarden as Ansible facts.
        Facts are subject to caching if enabled, which means this data could be stored in clear text
        on disk or in a database.
      - Tested with C(bw) version 1.22.0
'''

EXAMPLES = """
# These examples only work when already signed in and unlocked bitwarden cli
# You can pass your session key along with environment vars

- name: Retrieve whole item for CASTLE
  ansible.builtin.debug:
    var: lookup('community.general.bitwarden', 'CASTLE')

- name: Retrieve only password for FORTONE
  ansible.builtin.debug:
    var: lookup('community.general.bitwarden', 'FORTONE', object='password')

- name: Retrieve only username for FORTONE
  ansible.builtin.debug:
    var: lookup('community.general.bitwarden', 'FORTONE', object='username')
"""

RETURN = """
  _raw:
    description: field data requested
    type: list
    elements: str
"""

import errno
import json
import os

from subprocess import Popen, PIPE

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleLookupError
from ansible.module_utils.common.text.converters import to_text

def debug():
  import debugpy

  # 5678 is the default attach port in the VS Code debug configurations. Unless a host and port are specified, host defaults to 127.0.0.1
  debugpy.listen(5678)
  print("Waiting for debugger attach")
  debugpy.wait_for_client()

  debugpy.breakpoint()
  print('break on this line')


class Bitwarden(object):

    def __init__(self, path='bw'):
        self.cli_path = path

    def get_status(self):
        args = [
            'status'
        ]

        rc, out, err = self._run(args)
        return json.loads(out.strip())

    def get(self, object='item', id=None):
        args = [
          'get',
          object,
          id
        ]

        rc, out, err = self._run(args)

        return to_text(out.strip())

    def _run(self, args, expected_rc=0, command_input=None, ignore_errors=False):
        command = [self.cli_path] + args
        p = Popen(command, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate(input=command_input)
        rc = p.wait()
        if not ignore_errors and rc != expected_rc:
            raise AnsibleLookupError(to_text(err))
        return rc, out, err


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        bw = Bitwarden()

        object = kwargs.get('object', 'item')
        command = kwargs.get('command', 'get')

        values = []
        if command == 'get':
          for term in terms:
              result = bw.get(object, term)
              values.append(result)

        return values

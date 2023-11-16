# Copyright (c) 2023, Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.module_utils.six import raise_from

try:
    from fqdn import FQDN
except ImportError as imp_exc:
    ANOTHER_LIBRARY_IMPORT_ERROR = imp_exc
else:
    ANOTHER_LIBRARY_IMPORT_ERROR = None


DOCUMENTATION = '''
  name: fqdn_valid
  short_description: Validates fully-qualified domain names against RFC 1123
  version_added: 8.1.0
  author: Vladimir Botka (@vbotka)
  requirements:
  - fqdn>=1.5.1 (PyPI)
  description:
    - This test validates Fully Qualified Domain Names (FQDNs)
      conforming to the Internet Engineering Task Force specification
      RFC 1123 and RFC 952.
    - The design intent is to validate that a string would be
      traditionally acceptable as a public Internet hostname to
      RFC-conforming software, which is a strict subset of the logic
      in modern web browsers like Mozilla Firefox and Chromium that
      determines whether make a DNS lookup.
    - Certificate Authorities like Let's Encrypt run a narrower set of
      string validation logic to determine validity for issuance. This
      test is not intended to achieve functional parity with CA
      issuance.
    - Single label names are allowed by default (O(min_labels=1)).
  options:
    _input:
      description: Name of the host.
      type: str
      required: true
    min_labels:
      description: Required minimum of labels, separated by period.
      default: 1
      type: int
      required: false
    allow_underscores:
      description: Allow underscore characters.
      default: false
      type: bool
      required: false
'''

EXAMPLES = '''
- name: Make sure that hostname is valid
  ansible.builtin.assert:
    that: hostname is community.general.fqdn_valid

- name: Make sure that hostname is at least 3 labels long (a.b.c)
  ansible.builtin.assert:
    that: hostname is community.general.fqdn_valid(min_labels=3)

- name: Make sure that hostname is at least 2 labels long (a.b). Allow '_'
  ansible.builtin.assert:
    that: hostname is community.general.fqdn_valid(min_labels=2, allow_underscores=True)
'''

RETURN = '''
  _value:
    description: Whether the name is valid.
    type: bool
'''


def fqdn_valid(name, min_labels=1, allow_underscores=False):
    """
    Example:
      - 'srv.example.com' is community.general.fqdn_valid
      - 'foo_bar.example.com' is community.general.fqdn_valid(allow_underscores=True)
    """

    if ANOTHER_LIBRARY_IMPORT_ERROR:
        raise_from(
            AnsibleError('Python package fqdn must be installed to use this test.'),
            ANOTHER_LIBRARY_IMPORT_ERROR
        )

    fobj = FQDN(name, min_labels=min_labels, allow_underscores=allow_underscores)
    return (fobj.is_valid)


class TestModule(object):
    ''' Ansible test hostname validity.
        https://pypi.org/project/fqdn/
    '''

    def tests(self):
        return {
            'fqdn_valid': fqdn_valid,
        }

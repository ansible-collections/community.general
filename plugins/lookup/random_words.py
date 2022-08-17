# -*- coding: utf-8 -*-
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

"""The community.general.random_words Ansible lookup plugin."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
    name: random_words
    author:
      - Thomas Sjögren (@konstruktoid)
    short_description: Return a number of random words
    version_added: "4.0.0"
    requirements:
      - xkcdpass U(https://github.com/redacted/XKCD-password-generator)
    description:
      - Returns a number of random words. The output can for example be used for
        passwords.
      - See U(https://xkcd.com/936/) for background.
    options:
      numwords:
        description:
          - The number of words.
        default: 6
        type: int
      min_length:
        description:
          - Minimum length of words to make password.
        default: 5
        type: int
      max_length:
        description:
          - Maximum length of words to make password.
        default: 9
        type: int
      delimiter:
        description:
          - The delimiter character between words.
        default: " "
        type: str
      case:
        description:
          - The method for setting the case of each word in the passphrase.
        choices: ["alternating", "upper", "lower", "random", "capitalize"]
        default: "lower"
        type: str
"""

EXAMPLES = r"""
- name: Generate password with default settings
  ansible.builtin.debug:
    var: lookup('community.general.random_words')
  # Example result: 'traitor gigabyte cesarean unless aspect clear'

- name: Generate password with six, five character, words
  ansible.builtin.debug:
    var: lookup('community.general.random_words', min_length=5, max_length=5)
  # Example result: 'brink banjo getup staff trump comfy'

- name: Generate password with three capitalized words and the '-' delimiter
  ansible.builtin.debug:
    var: lookup('community.general.random_words', numwords=3, delimiter='-', case='capitalize')
  # Example result: 'Overlabor-Faucet-Coastline'

- name: Generate password with three words without any delimiter
  ansible.builtin.debug:
    var: lookup('community.general.random_words', numwords=3, delimiter='')
  # Example result: 'deskworkmonopolystriking'
  # https://www.ncsc.gov.uk/blog-post/the-logic-behind-three-random-words
"""

RETURN = r"""
  _raw:
    description: A single-element list containing random words.
    type: list
    elements: str
"""

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase

try:
    from xkcdpass import xkcd_password as xp

    HAS_XKCDPASS = True
except ImportError:
    HAS_XKCDPASS = False


class LookupModule(LookupBase):
    """The random_words Ansible lookup class."""

    def run(self, terms, variables=None, **kwargs):

        if not HAS_XKCDPASS:
            raise AnsibleLookupError(
                "Python xkcdpass library is required. "
                'Please install using "pip install xkcdpass"'
            )

        self.set_options(var_options=variables, direct=kwargs)
        method = self.get_option("case")
        delimiter = self.get_option("delimiter")
        max_length = self.get_option("max_length")
        min_length = self.get_option("min_length")
        numwords = self.get_option("numwords")

        words = xp.locate_wordfile()
        wordlist = xp.generate_wordlist(
            max_length=max_length, min_length=min_length, wordfile=words
        )

        values = xp.generate_xkcdpassword(
            wordlist, case=method, delimiter=delimiter, numwords=numwords
        )

        return [values]

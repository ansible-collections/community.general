# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Abhijeet Kasurde <akasurde@redhat.com>
# Copyright: (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
    name: random_string
    author:
      - Abhijeet Kasurde (@Akasurde)
    short_description: Generates random string
    version_added: '3.2.0'
    description:
      - Generates random string based upon the given constraints.
    options:
      length:
        description: The length of the string.
        default: 8
        type: int
      upper:
        description:
        - Include uppercase letters in the string.
        default: true
        type: bool
      lower:
        description:
        - Include lowercase letters in the string.
        default: true
        type: bool
      numbers:
        description:
        - Include numbers in the string.
        default: true
        type: bool
      special:
        description:
        - Include special characters in the string.
        - Special characters are taken from Python standard library C(string).
          See L(the documentation of string.punctuation,https://docs.python.org/3/library/string.html#string.punctuation)
          for which characters will be used.
        - The choice of special characters can be changed to setting I(override_special).
        default: true
        type: bool
      min_numeric:
        description:
        - Minimum number of numeric characters in the string.
        - If set, overrides I(numbers=false).
        default: 0
        type: int
      min_upper:
        description:
        - Minimum number of uppercase alphabets in the string.
        - If set, overrides I(upper=false).
        default: 0
        type: int
      min_lower:
        description:
        - Minimum number of lowercase alphabets in the string.
        - If set, overrides I(lower=false).
        default: 0
        type: int
      min_special:
        description:
        - Minimum number of special character in the string.
        default: 0
        type: int
      override_special:
        description:
        - Overide a list of special characters to use in the string.
        - If set I(min_special) should be set to a non-default value.
        type: str
      override_all:
        description:
        - Override all values of I(numbers), I(upper), I(lower), and I(special) with
          the given list of characters.
        type: str
      base64:
        description:
        - Returns base64 encoded string.
        type: bool
        default: false
"""

EXAMPLES = r"""
- name: Generate random string
  ansible.builtin.debug:
    var: lookup('community.general.random_string')
  # Example result: ['DeadBeeF']

- name: Generate random string with length 12
  ansible.builtin.debug:
    var: lookup('community.general.random_string', length=12)
  # Example result: ['Uan0hUiX5kVG']

- name: Generate base64 encoded random string
  ansible.builtin.debug:
    var: lookup('community.general.random_string', base64=True)
  # Example result: ['NHZ6eWN5Qk0=']

- name: Generate a random string with 1 lower, 1 upper, 1 number and 1 special char (atleast)
  ansible.builtin.debug:
    var: lookup('community.general.random_string', min_lower=1, min_upper=1, min_special=1, min_numeric=1)
  # Example result: ['&Qw2|E[-']

- name: Generate a random string with all lower case characters
  debug:
    var: query('community.general.random_string', upper=false, numbers=false, special=false)
  # Example result: ['exolxzyz']

- name: Generate random hexadecimal string
  debug:
    var: query('community.general.random_string', upper=false, lower=false, override_special=hex_chars, numbers=false)
  vars:
    hex_chars: '0123456789ABCDEF'
  # Example result: ['D2A40737']

- name: Generate random hexadecimal string with override_all
  debug:
    var: query('community.general.random_string', override_all=hex_chars)
  vars:
    hex_chars: '0123456789ABCDEF'
  # Example result: ['D2A40737']
"""

RETURN = r"""
  _raw:
    description: A one-element list containing a random string
    type: list
    elements: str
"""

import base64
import random
import string

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_bytes, to_text


class LookupModule(LookupBase):
    @staticmethod
    def get_random(random_generator, chars, length):
        if not chars:
            raise AnsibleLookupError(
                "Available characters cannot be None, please change constraints"
            )
        return "".join(random_generator.choice(chars) for dummy in range(length))

    @staticmethod
    def b64encode(string_value, encoding="utf-8"):
        return to_text(
            base64.b64encode(
                to_bytes(string_value, encoding=encoding, errors="surrogate_or_strict")
            )
        )

    def run(self, terms, variables=None, **kwargs):
        number_chars = string.digits
        lower_chars = string.ascii_lowercase
        upper_chars = string.ascii_uppercase
        special_chars = string.punctuation
        random_generator = random.SystemRandom()

        self.set_options(var_options=variables, direct=kwargs)

        length = self.get_option("length")
        base64_flag = self.get_option("base64")
        override_all = self.get_option("override_all")
        values = ""
        available_chars_set = ""

        if override_all:
            # Override all the values
            available_chars_set = override_all
        else:
            upper = self.get_option("upper")
            lower = self.get_option("lower")
            numbers = self.get_option("numbers")
            special = self.get_option("special")
            override_special = self.get_option("override_special")

            if override_special:
                special_chars = override_special

            if upper:
                available_chars_set += upper_chars
            if lower:
                available_chars_set += lower_chars
            if numbers:
                available_chars_set += number_chars
            if special:
                available_chars_set += special_chars

            mapping = {
                "min_numeric": number_chars,
                "min_lower": lower_chars,
                "min_upper": upper_chars,
                "min_special": special_chars,
            }

            for m in mapping:
                if self.get_option(m):
                    values += self.get_random(random_generator, mapping[m], self.get_option(m))

        remaining_pass_len = length - len(values)
        values += self.get_random(random_generator, available_chars_set, remaining_pass_len)

        # Get pseudo randomization
        shuffled_values = list(values)
        # Randomize the order
        random.shuffle(shuffled_values)

        if base64_flag:
            return [self.b64encode("".join(shuffled_values))]

        return ["".join(shuffled_values)]

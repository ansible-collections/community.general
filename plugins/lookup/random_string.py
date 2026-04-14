# Copyright (c) 2021, Abhijeet Kasurde <akasurde@redhat.com>
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: random_string
author:
  - Abhijeet Kasurde (@Akasurde)
short_description: Generates random string
version_added: '3.2.0'
description:
  - Generates random string based upon the given constraints.
  - Uses L(secrets.SystemRandom,https://docs.python.org/3/library/secrets.html#secrets.SystemRandom), so should be strong enough
    for cryptographic purposes.
options:
  length:
    description: The length of the string.
    default: 8
    type: int
  upper:
    description:
      - Possibly include uppercase letters in the string.
      - To ensure atleast one uppercase letter, set O(min_upper) to V(1).
    default: true
    type: bool
  lower:
    description:
      - Possibly include lowercase letters in the string.
      - To ensure atleast one lowercase letter, set O(min_lower) to V(1).
    default: true
    type: bool
  numbers:
    description:
      - Possibly include numbers in the string.
      - To ensure atleast one numeric character, set O(min_numeric) to V(1).
    default: true
    type: bool
  special:
    description:
      - Possibly include special characters in the string.
      - Special characters are taken from Python standard library C(string). See L(the documentation of
        string.punctuation,https://docs.python.org/3/library/string.html#string.punctuation)
        for which characters are used.
      - The choice of special characters can be changed to setting O(override_special).
      - To ensure atleast one special character, set O(min_special) to V(1).
    default: true
    type: bool
  min_numeric:
    description:
      - Minimum number of numeric characters in the string.
      - If set, overrides O(numbers=false).
    default: 0
    type: int
  min_upper:
    description:
      - Minimum number of uppercase alphabets in the string.
      - If set, overrides O(upper=false).
    default: 0
    type: int
  min_lower:
    description:
      - Minimum number of lowercase alphabets in the string.
      - If set, overrides O(lower=false).
    default: 0
    type: int
  min_special:
    description:
      - Minimum number of special character in the string.
    default: 0
    type: int
  override_special:
    description:
      - Override a list of special characters to use in the string.
      - If set O(min_special) should be set to a non-default value.
    type: str
  override_all:
    description:
      - Override all values of O(numbers), O(upper), O(lower), and O(special) with the given list of characters.
    type: str
  ignore_similar_chars:
    description:
      - Ignore similar characters, such as V(l) and V(1), or V(O) and V(0).
      - These characters can be configured in O(similar_chars).
    default: false
    type: bool
    version_added: 7.5.0
  similar_chars:
    description:
      - Override a list of characters not to be use in the string.
    default: "il1LoO0"
    type: str
    version_added: 7.5.0
  base64:
    description:
      - Returns base64 encoded string.
    type: bool
    default: false
  seed:
    description:
      - Seed for random string generator.
      - B(Note) that this drastically reduces the security of this plugin. First, when O(seed) is provided, a non-cryptographic random number generator is used.
        Second, if the seed does not contain enough entropy, the generated string is weak.
        B(Do not use the generated string as a password or a secure token when using this option!)
    type: str
    version_added: 11.3.0
  avoid_special_first:
    description:
      - Avoid special characters at the first position of the string.
    type: bool
    default: false
    version_added: 12.6.0
  avoid_special_last:
    description:
      - Avoid special characters at the last position of the string.
    type: bool
    default: false
    version_added: 12.6.0
"""

EXAMPLES = r"""
- name: Generate random string
  ansible.builtin.debug:
    var: lookup('community.general.random_string')
  # Example result: 'DeadBeeF'

- name: Generate random string with seed
  ansible.builtin.debug:
    var: lookup('community.general.random_string', seed=12345)
  # Example result: '6[~(2q5O'
  # NOTE: Do **not** use this string as a password or a secure token,
  #       unless you know exactly what you are doing!
  #       Specifying seed uses a non-secure random number generator.

- name: Generate random string with length 12
  ansible.builtin.debug:
    var: lookup('community.general.random_string', length=12)
  # Example result: 'Uan0hUiX5kVG'

- name: Generate base64 encoded random string
  ansible.builtin.debug:
    var: lookup('community.general.random_string', base64=True)
  # Example result: 'NHZ6eWN5Qk0='

- name: Generate a random string with 1 lower, 1 upper, 1 number and 1 special char (at least)
  ansible.builtin.debug:
    var: lookup('community.general.random_string', min_lower=1, min_upper=1, min_special=1, min_numeric=1)
  # Example result: '&Qw2|E[-'

- name: Generate a random string with all lower case characters
  ansible.builtin.debug:
    var: query('community.general.random_string', upper=false, numbers=false, special=false)
  # Example result: ['exolxzyz']

- name: Generate random hexadecimal string
  ansible.builtin.debug:
    var: query('community.general.random_string', upper=false, lower=false, override_special=hex_chars, numbers=false)
  vars:
    hex_chars: '0123456789ABCDEF'
  # Example result: ['D2A40737']

- name: Generate random hexadecimal string with override_all
  ansible.builtin.debug:
    var: query('community.general.random_string', override_all=hex_chars)
  vars:
    hex_chars: '0123456789ABCDEF'
  # Example result: ['D2A40737']

- name: Generate random string with avoid_special_first
  debug:
    var: query('community.general.random_string', avoid_special_first=true)
  # Example result: ['Uan0hUiX5kVG']

- name: Generate random string with avoid_special_last
  debug:
    var: query('community.general.random_string', avoid_special_last=true)
  # Example result: ['Uan0hUiX5kVG']
"""

RETURN = r"""
_raw:
  description: A one-element list containing a random string.
  type: list
  elements: str
"""

import base64
import random
import secrets
import string

from ansible.errors import AnsibleLookupError
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):
    @staticmethod
    def get_random(random_generator, chars, length):
        if not chars:
            raise AnsibleLookupError("Available characters cannot be None, please change constraints")
        return "".join(random_generator.choice(chars) for dummy in range(length))

    @staticmethod
    def b64encode(string_value, encoding="utf-8"):
        return to_text(base64.b64encode(to_bytes(string_value, encoding=encoding, errors="surrogate_or_strict")))

    def run(self, terms, variables=None, **kwargs):
        number_chars = string.digits
        lower_chars = string.ascii_lowercase
        upper_chars = string.ascii_uppercase
        special_chars = string.punctuation

        self.set_options(var_options=variables, direct=kwargs)

        length = self.get_option("length")
        base64_flag = self.get_option("base64")
        override_all = self.get_option("override_all")
        override_special = self.get_option("override_special")
        ignore_similar_chars = self.get_option("ignore_similar_chars")
        similar_chars = self.get_option("similar_chars")
        avoid_special_first = self.get_option("avoid_special_first")
        avoid_special_last = self.get_option("avoid_special_last")
        seed = self.get_option("seed")

        if seed is None:
            random_generator = secrets.SystemRandom()
        else:
            random_generator = random.Random(seed)

        result = []
        available_chars_set = ""

        if ignore_similar_chars:
            number_chars = "".join([sc for sc in number_chars if sc not in similar_chars])
            lower_chars = "".join([sc for sc in lower_chars if sc not in similar_chars])
            upper_chars = "".join([sc for sc in upper_chars if sc not in similar_chars])
            special_chars = "".join([sc for sc in special_chars if sc not in similar_chars])

        if override_all:
            # Override all the values
            available_chars_set = override_all
        else:
            upper = self.get_option("upper")
            lower = self.get_option("lower")
            numbers = self.get_option("numbers")
            special = self.get_option("special")

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

        if len(available_chars_set) == 0:
            raise AnsibleLookupError("Available characters cannot be empty, please change constraints")

        min_numeric = self.get_option("min_numeric")
        min_lower = self.get_option("min_lower")
        min_upper = self.get_option("min_upper")
        min_special = self.get_option("min_special")
        if length < min_numeric + min_lower + min_upper + min_special:
            raise AnsibleLookupError("Minimum requirements exceed total length, please increase the length")

        # Ensure minimum requirements
        result += [random_generator.choice(number_chars) for dummy in range(min_numeric)]
        result += [random_generator.choice(lower_chars) for dummy in range(min_lower)]
        result += [random_generator.choice(upper_chars) for dummy in range(min_upper)]
        if override_special:
            result += [random_generator.choice(override_special) for dummy in range(min_special)]
        else:
            result += [random_generator.choice(special_chars) for dummy in range(min_special)]

        # Fill remaining length
        remaining_length = length - len(result)
        result += [random_generator.choice(available_chars_set) for dummy in range(remaining_length)]

        # Shuffle to avoid predictable pattern
        random_generator.shuffle(result)

        # Handle first/last character constraints
        if avoid_special_first and result[0] in special_chars:
            for i in range(1, len(result)):
                if result[i] not in special_chars:
                    result[0], result[i] = result[i], result[0]
                    break
            else:
                raise AnsibleLookupError("No character satisfies the constraints for avoid_special_first")

        if avoid_special_last and result[-1] in special_chars:
            for i in range(len(result) - 2, -1, -1):
                if result[i] not in special_chars:
                    result[-1], result[i] = result[i], result[-1]
                    break
            else:
                raise AnsibleLookupError("No character satisfies the constraints for avoid_special_last")

        if base64_flag:
            return [self.b64encode("".join(result))]

        return ["".join(result)]

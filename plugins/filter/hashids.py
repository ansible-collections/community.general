# -*- coding: utf-8 -*-

# Copyright (c) 2021, Andrew Pantuso (@ajpantuso) <ajpantuso@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.errors import (
    AnsibleError,
    AnsibleFilterError,
    AnsibleFilterTypeError,
)

from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.common.collections import is_sequence

try:
    from hashids import Hashids
    HAS_HASHIDS = True
except ImportError:
    HAS_HASHIDS = False


def initialize_hashids(**kwargs):
    if not HAS_HASHIDS:
        raise AnsibleError("The hashids library must be installed in order to use this plugin")

    params = dict((k, v) for k, v in kwargs.items() if v)

    try:
        return Hashids(**params)
    except TypeError as e:
        raise AnsibleFilterError(
            "The provided parameters %s are invalid: %s" % (
                ', '.join(["%s=%s" % (k, v) for k, v in params.items()]),
                to_native(e)
            )
        )


def hashids_encode(nums, salt=None, alphabet=None, min_length=None):
    """Generates a YouTube-like hash from a sequence of ints

       :nums: Sequence of one or more ints to hash
       :salt: String to use as salt when hashing
       :alphabet: String of 16 or more unique characters to produce a hash
       :min_length: Minimum length of hash produced
    """

    hashids = initialize_hashids(
        salt=salt,
        alphabet=alphabet,
        min_length=min_length
    )

    # Handles the case where a single int is not encapsulated in a list or tuple.
    # User convenience seems preferable to strict typing in this case
    # Also avoids obfuscated error messages related to single invalid inputs
    if not is_sequence(nums):
        nums = [nums]

    try:
        hashid = hashids.encode(*nums)
    except TypeError as e:
        raise AnsibleFilterTypeError(
            "Data to encode must by a tuple or list of ints: %s" % to_native(e)
        )

    return hashid


def hashids_decode(hashid, salt=None, alphabet=None, min_length=None):
    """Decodes a YouTube-like hash to a sequence of ints

       :hashid: Hash string to decode
       :salt: String to use as salt when hashing
       :alphabet: String of 16 or more unique characters to produce a hash
       :min_length: Minimum length of hash produced
    """

    hashids = initialize_hashids(
        salt=salt,
        alphabet=alphabet,
        min_length=min_length
    )
    nums = hashids.decode(hashid)
    return list(nums)


class FilterModule(object):

    def filters(self):
        return {
            'hashids_encode': hashids_encode,
            'hashids_decode': hashids_decode,
        }

# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andrew Pantuso (@ajpantuso) <ajpantuso@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.errors import (
    AnsibleError,
    AnsibleFilterError,
    AnsibleFilterTypeError,
)

from ansible.module_utils.common.text.converters import to_native

try:
    from hashids import Hashids
    HAS_HASHIDS = True
except ImportError:
    HAS_HASHIDS = False


def initialize_hashids(salt, alphabet, min_length):
    if not HAS_HASHIDS:
        raise AnsibleError("The hashids library must be installed in order to use this plugin")

    unchecked_params = {
        'salt': salt,
        'alphabet': alphabet,
        'min_length': min_length,
    }

    params = {}

    for k in unchecked_params:
        if unchecked_params[k]:
            params[k] = unchecked_params[k]

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
    """Generates a youtube-like hash from a sequence of Ints

       :nums: Sequence of one or more Ints to hash
       :salt: String to use as salt when hashing
       :alphabet: String of 16 or more unique characters to produce a hash
       :min_length: Minimum length of hash produced
    """

    hashids = initialize_hashids(salt, alphabet, min_length)

    # Handles the case where a single Int is not encapsulated in a list or tuple.
    # User convenience seems prefferable to strict typing in this case
    if isinstance(nums, int):
        nums = [nums]

    try:
        hashid = hashids.encode(*nums)
    except TypeError as e:
        raise AnsibleFilterTypeError(
            "Data to encode must by a tuple or list of Ints: %s" % to_native(e)
        )

    return hashid


def hashids_decode(hashid, salt=None, alphabet=None, min_length=None):
    """Generates a youtube-like hash from a sequence of Ints

       :hashid: Hash string to decode
       :salt: String to use as salt when hashing
       :alphabet: String of 16 or more unique characters to produce a hash
       :min_length: Minimum length of hash produced
    """

    hashids = initialize_hashids(salt, alphabet, min_length)
    nums = hashids.decode(hashid)
    return nums


class FilterModule(object):

    def filters(self):
        return {
            'hashids_encode': hashids_encode,
            'hashids_decode': hashids_decode,
        }

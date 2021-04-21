# -*- coding: utf-8 -*-
# Copyright (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common._collections_compat import Mapping, Sequence


def groupby_as_dict(sequence, attribute):
    '''
    Given a sequence of dictionaries and an attribute name, returns a dictionary mapping
    the value of this attribute to the dictionary.

    If multiple dictionaries in the sequence have the same value for this attribute,
    the filter will fail.
    '''
    if not isinstance(sequence, Sequence):
        raise AnsibleFilterError('Input is not a sequence')

    result = dict()
    for list_index, element in enumerate(sequence):
        if not isinstance(element, Mapping):
            raise AnsibleFilterError('Sequence element #{0} is not a mapping'.format(list_index))
        if attribute not in element:
            raise AnsibleFilterError('Attribute not contained in element #{0} of sequence'.format(list_index))
        result_index = element[attribute]
        if result_index in result:
            raise AnsibleFilterError('Multiple sequence entries have attribute value {0!r}'.format(result_index))
        result[result_index] = element
    return result


class FilterModule(object):
    ''' Ansible list filters '''

    def filters(self):
        return {
            'groupby_as_dict': groupby_as_dict,
        }

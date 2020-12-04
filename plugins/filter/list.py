# -*- coding: utf-8 -*-
# Copyright (c) 2020, Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError, AnsibleFilterError
from ansible.module_utils.six import string_types
from ansible.module_utils.common._collections_compat import Mapping, Sequence
from collections import defaultdict
from operator import itemgetter


def lists_mergeby(l1, l2, index):
    ''' merge lists by attribute index. Example:
        - debug: msg="{{ l1|community.general.lists_mergeby(l2, 'index')|list }}" '''

    if not isinstance(l1, Sequence):
        raise AnsibleFilterError('First argument for community.general.lists_mergeby must be list. %s is %s' %
                                 (l1, type(l1)))

    if not isinstance(l2, Sequence):
        raise AnsibleFilterError('Second argument for community.general.lists_mergeby must be list. %s is %s' %
                                 (l2, type(l2)))

    if not isinstance(index, string_types):
        raise AnsibleFilterError('Third argument for community.general.lists_mergeby must be string. %s is %s' %
                                 (index, type(index)))

    d = defaultdict(dict)
    for l in (l1, l2):
        for elem in l:
            if not isinstance(elem, Mapping):
                raise AnsibleFilterError('Elements of list arguments for lists_mergeby must be dictionaries. Found {0!r}.'.format(elem))
            if index in elem.keys():
                d[elem[index]].update(elem)
    return sorted(d.values(), key=itemgetter(index))


class FilterModule(object):
    ''' Ansible list filters '''

    def filters(self):
        return {
            'lists_mergeby': lists_mergeby,
        }

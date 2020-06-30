# -*- coding: utf-8 -*-
# Copyright (c) 2020, Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError, AnsibleFilterError
from collections import defaultdict
from operator import itemgetter


def lists_mergeby(l1, l2, index):
    '''Merge lists by attribute index. Example:
    - debug: msg="{{ l1|lists_mergeby(l2, 'index')|list }}"
    '''
    d = defaultdict(dict)
    for l in (l1, l2):
        for elem in l:
            d[elem[index]].update(elem)
    return sorted(d.values(), key=itemgetter(index))


class FilterModule(object):
    ''' Ansible list filters '''

    def filters(self):
        return {
            'lists_mergeby': lists_mergeby
        }

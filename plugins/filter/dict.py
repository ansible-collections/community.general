# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


def list_to_dict(values, keys):
    '''Convert a list of values and a list of keys to a dictionary by combining these lists.

    Example: ``[1, 2, 3] | community.general.list_to_dict(['k1', 'k2'])`` results in ``{'k1': 1, 'k2': 2}``.

    This is equivalent to ``[1, 2, 3] | zip(['k1', 'k2']) | community.general.dict``.
    '''
    return dict(zip(keys, values))


def dict_filter(sequence):
    '''Convert a list of tuples to a dictionary.

    Example: ``[[1, 2], ['a', 'b']] | community.general.dict`` results in ``{1: 2, 'a': 'b'}``
    '''
    return dict(sequence)


class FilterModule(object):
    '''Ansible jinja2 filters'''

    def filters(self):
        return {
            'list_to_dict': list_to_dict,
            'dict': dict_filter,
        }

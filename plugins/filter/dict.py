# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


def dict_filter(sequence):
    '''Convert a list of tuples to a dictionary.

    Example: ``[[1, 2], ['a', 'b']] | community.general.dict`` results in ``{1: 2, 'a': 'b'}``
    '''
    return dict(sequence)


class FilterModule(object):
    '''Ansible jinja2 filters'''

    def filters(self):
        return {
            'dict': dict_filter,
        }

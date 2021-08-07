# -*- coding: utf-8 -*-
# Copyright (C) 2021 Eric Lavarde <elavarde@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from distutils.version import LooseVersion


def version_sort(value, reverse=False):
    '''Sort a list according to loose versions so that e.g. 2.9 is smaller than 2.10'''
    return sorted(value, key=LooseVersion, reverse=reverse)


class FilterModule(object):
    ''' Version sort filter '''

    def filters(self):
        return {
            'version_sort': version_sort
        }

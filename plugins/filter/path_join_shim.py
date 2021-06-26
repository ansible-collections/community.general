# -*- coding: utf-8 -*-

# Copyright: (c) 2020-2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


import os.path


def path_join(list):
    '''Join list of paths.

    This is a minimal shim for ansible.builtin.path_join included in ansible-base 2.10.
    This should only be called by Ansible 2.9 or earlier. See meta/runtime.yml for details.
    '''
    return os.path.join(*list)


class FilterModule(object):
    '''Ansible jinja2 filters'''

    def filters(self):
        return {
            'path_join': path_join,
        }

# -*- coding: utf-8 -*-
# (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# Copyright: (c) 2020, Ansible Project
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
    options:
      path:
        type: path
        required: true
        aliases: [ dest ]
        description: Path of the destination file that you want process.
      allow_creation:
        type: bool
        default: false
        description: If the destination file do not exists allow to create it.
      backup:
        type: bool
        default: false
        description: Make a backup of the destination file before update it.
    '''

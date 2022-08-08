#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: collection_module
short_description: Test collection module
description:
  - This is a test module in a local collection.
author: "Felix Fontein (@felixfontein)"
options: {}
'''

EXAMPLES = ''' # '''

RETURN = ''' # '''

from ansible.module_utils.basic import AnsibleModule


def main():
    AnsibleModule(argument_spec={}).exit_json()


if __name__ == '__main__':
    main()

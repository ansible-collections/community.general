#!/usr/bin/python

# Copyright (c) 2021, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = '''
---
module: local_module
short_description: Test local module
description:
  - This is a test module locally next to a playbook.
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

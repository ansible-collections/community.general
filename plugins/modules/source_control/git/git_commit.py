#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Federico Olivieri (lvrfrc87@gmail.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: git_commit
author:
    - "Federico Olivieri (@Federico87)"
version_added: "2.10"
short_description: Perform git add and git commit operations.
description:
    - Manage C(git add) and C(git commit) on a local git.
options:
    path:
        description:
            - Folder path where C(.git/) is located.
        required: true
        type: path
    comment:
        description:
            - Git commit comment. Same as C(git commit -m).
        type: str
        required: true
    add:
        description:
            - List of files to be staged. Same as C(git add .).
              File globs not accepted, such as C(./*) or C(*).
        type: list
        default: ["."]
        elements: str
requirements:
    - git>=2.10.0 (the command line tool)
'''

EXAMPLES = '''
- name: Add and commit two files.
  community.general.git_commit:
    path: /Users/federicoolivieri/git/git_test_module
    comment: My amazing backup
    add: ['test.txt', 'txt.test']

- name: Add all files using default and commit.
  community.general.git_commit:
    path: /Users/federicoolivieri/git/git_test_module
    comment: My amazing backup
'''

RETURN = '''
output:
    description: list of git cli command stdout
    type: list
    returned: always
    sample: [
        "[master 99830f4] Remove [ test.txt, tax.txt ]\n 4 files changed, 26 insertions(+)..."
    ]
'''

import os
from ansible.module_utils.basic import AnsibleModule


def git_commit(module):

    add = module.params.get('add')
    path = module.params.get('path')
    comment = module.params.get('comment')

    if add:
        add_cmds = ['git', '-C', path, 'add', '{0}'.format(' '.join(add))]

    if comment:
        commit_cmds = ['git', '-C', path, 'commit', '-m', '"{0}"'.format(comment), '--porcelain']
    
    return [add_cmds + commit_cmds ]


def main():

    argument_spec = dict(
        path=dict(required=True, type="path"),
        comment=dict(required=True),
        add=dict(type="list", elements='str', default=["."]),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    result_output = list()
    result = dict(changed=False)

    for cmd in git_commit(module):
        _rc, output, error = module.run_command(cmd, check_rc=False)

        if output:
            if 'no changes added to commit' in output:
                module.fail_json(msg=output)
            elif 'nothing to commit, working tree clean' in output:
                module.fail_json(msg=output)
            else:
                result_output.append(output)
                result.update(changed=True)

        if error:
            if 'error:' in error:
                module.fail_json(msg=error)
            elif 'fatal:' in error:
                module.fail_json(msg=error)
            else:
                result_output.append(error)
                result.update(changed=True)

    if result_output:
        result.update(output=result_output)

    module.exit_json(**result)


if __name__ == "__main__":
    main()

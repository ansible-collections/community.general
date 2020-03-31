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
            - List of files under C(path) to be staged. Same as C(git add .).
              File globs not accepted, such as C(./*) or C(*).
        type: list
        elements: str
        required: true
        default: ["."]
    empty_commit:
        descripion:
            - Drive module behaviour in case nothing to commit.
              If C(allow) empty commit is allowed, same as C(--allow-empty).
              Do not commit if C(skip). Fail job if C(fail). In order to C(allow)
              to work, C(add) argument must not provided in module.
        type: str
        default: 'fail'
requirements:
    - git>=2.10.0 (the command line tool)
'''

EXAMPLES = '''
- name: Add and commit two files.
  community.general.git_commit:
    path: /Users/federicoolivieri/git/git_test_module
    comment: My amazing backup
    add: ['test.txt', 'txt.test']
    empty_commit: fail

- name: Empty commit. 
  community.general.git_commit:
    path: /Users/federicoolivieri/git/git_test_module
    comment: My amazing empty commit
    empty_commit: allow
    add: ['.']

- name: Skip if nothing to commit. 
  community.general.git_commit:
    path: /Users/federicoolivieri/git/git_test_module
    comment: Skip my amazing empty commit
    empty_commit: skyp
    add: ['.']
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


def git_add(module):

    add = module.params.get('add')

    if add:
        add_cmds = [
            'git',
            'add',
        ]
        for item in add:
            add_cmds.insert(len(add_cmds), item)

        return add_cmds


def git_commit(module):

    empty_commit = module.params.get('empty_commit')
    comment = module.params.get('comment')

    if comment and empty_commit == 'allow':
        commit_cmds = [
            'git', 
            'commit',
            '--allow-empty',
            '-m', 
            '"{0}"'.format(comment), 
            '--porcelain'
        ]
    
    if comment and empty_commit != 'allow':
        commit_cmds = [
            'git', 
            'commit',
            '-m', 
            '"{0}"'.format(comment), 
            '--porcelain'
        ]
    
    if commit_cmds:
        return commit_cmds


def main():

    argument_spec = dict(
        path=dict(required=True, type="path"),
        comment=dict(required=True),
        add=dict(type='list', elements='str', default=["."]),
        empty_commit=dict(choices=[ "allow", "fail", "skip" ], default='fail')
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    path = module.params.get('path')
    empty_commit = module.params.get('empty_commit')

    result = dict(changed=False)

    rc, output, error = module.run_command(
        git_add(module),
        cwd=path, 
        check_rc=False,
    )
    
    # "git add do_not_exist" -> rc: 128
    # "git add i_exist"      -> rc: 0
    # "git add ."            -> rc: 0
    if rc != 0 and empty_commit != 'skip':
        module.fail_json(
            msg=error,
        )
    elif rc != 0 and empty_commit == 'skip':
        rc = 0
        result.update(changed=False, output=output, rc=rc)
    else:
        porcelain_list = ('M', 'A', 'D', 'R', 'C', 'U')
        # A  test.txt            -> rc: 1
        # "" (nothing to commit) -> rc: 1
        rc, output, error = module.run_command(
            git_commit(module),
            cwd=path, 
            check_rc=False,
        )

        if rc == 1:

            if empty_commit == 'allow' and not output:
                rc = 0
                result.update(changed=True, output=output, rc=rc)
                
            if empty_commit == 'fail' and output:
                for porc in output.splitlines():
                    if porc.startswith(porcelain_list):
                        rc = 0
                        result.update(changed=True, output=output, rc=rc)
            elif empty_commit == 'fail' and not output:
                module.fail_json(msg='Empty commit not allowed with empty_commit=fail',rc=rc)


    module.exit_json(**result)


if __name__ == "__main__":
    main()

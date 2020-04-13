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
    empty_commit:
        description:
            - Drive module behaviour in case nothing to commit.
              If C(allow) empty commit is allowed, same as C(--allow-empty).
              Do not commit if C(skip). Fail job if C(fail).
        choices: ['allow', 'fail', 'skip']
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
    empty_commit: skip
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
from ansible.utils.display import Display

display = Display()


def git_add(module):

    add = module.params.get('add')
    path = module.params.get('path')

    if not add:
        add = ["."]
    # "git add do_not_exist" -> rc: 128
    # "git add i_exist"      -> rc: 0
    # "git add ."            -> rc: 0
    add_cmds = [
        'git',
        'add',
        '--',
        '--',
    ]

    add_cmds.extend(add)

    rc, _output, error = module.run_command(add_cmds, cwd=path)

    if rc != 0:
        module.fail_json(msg=error)

    if rc == 0:
        # no output returned when rc = 0
        return


def git_commit(module):

    def git_commit_run(cmd, path):

        rc, output, error = module.run_command(cmd, cwd=path)

        if rc != 0:
            module.fail_json(msg=error)
        if rc == 0:
            return output

    result = dict(changed=False)
    empty_commit = module.params.get('empty_commit')
    comment = module.params.get('comment')
    path = module.params.get('path')
    cmd_porcelain = ['git', 'commit', '--porcelain']

    # rc is always 1 for "git commit --porcelain"
    _rc, output, error = module.run_command(cmd_porcelain, cwd=path)

    if error:
        module.fail_json(msg=error)

    # do not allow empty commit with empty_commit=fail
    if empty_commit == 'fail' and not output:
        module.fail_json(msg='No empty commit allowed with empty_commit=fail')

    # add and commit if output and empty_commit=fail
    if empty_commit == 'fail' and output:

        git_add(module)

        commit_cmds = [
            'git',
            'commit',
            '-m',
            comment,
        ]

        output = git_commit_run(commit_cmds, path)

        if output:
            result.update(
                git_commit=output,
                changed=True
            )

            return result

    # if empty_commit=allow skip git_add()
    if empty_commit == 'allow' and not output:
        commit_cmds = [
            'git',
            'commit',
            '--allow-empty',
            '-m',
            '"{0}"'.format(comment),
        ]

        output = git_commit_run(commit_cmds, path)

        if output:
            result.update(
                git_commit=output,
                changed=True
            )

            return result

    # if empty_commit=allow and pending stages, issue a warning and carry-on
    if empty_commit == 'allow' and output:
        display.warning(msg='You are going to run an empty commit but you have pending changes: {0}'.format(output))

        commit_cmds = [
            'git',
            'commit',
            '--allow-empty',
            '-m',
            '"{0}"'.format(comment),
        ]

        output = git_commit_run(commit_cmds, path)

        if output:
            result.update(
                git_commit=output,
                changed=True
            )

            return result

    # return if empty_commit=skip and nothing to commit
    if empty_commit == 'skip' and not output:

        result.update(changed=False)

        return result

    # if empty_commit=skip and pending stages, issue a warning and return
    if empty_commit == 'skip' and output:
        display.warning('You are going to skip commit but you have pending changes: {0}'.format(output))

        result.update(changed=False)

        return result


def main():

    argument_spec = dict(
        path=dict(required=True, type="path"),
        comment=dict(required=True),
        add=dict(type='list', elements='str'),
        empty_commit=dict(choices=["allow", "fail", "skip"], default='fail')
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    result = dict()
    result.update(git_commit(module))
    if result:
        module.exit_json(**result)


if __name__ == "__main__":
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Federico Olivieri (lvrfrc87@gmail.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: git_push
author:
    - "Federico Olivieri (@Federico87)"
version_added: "2.10"
short_description: Perform git push operations.
description:
    - Manage C(git push) on local or remote git repository.
options:
    path:
        description:
            - Folder path where C(.git/) is located.
        required: true
        type: path
    user:
        description:
            - Git username for https operations.
        type: str
    token:
        description:
            - Git API token for https operations.
        type: str
    branch:
        description:
            - Git branch where perform git push.
        required: True
        type: str
    push_option:
        description:
            - Git push options. Same as C(git --push-option=option).
        type: str
    mode:
        description:
            - Git operations are performend eithr over ssh, https or local.
              Same as C(git@git...) or C(https://user:token@git...).
        choices: ['ssh', 'https', 'local']
        default: ssh
        type: str
    url:
        description:
            - Git repo URL.
        required: True
        type: str
requirements:
    - git>=2.10.0 (the command line tool)
'''

EXAMPLES = '''

- name: Push changes via HTTPs.
  community.general.git_push:
    path: /Users/federicoolivieri/git/git_test_module
    user: Federico87
    token: m1Ap!T0k3n!!!
    branch: master
    mode: https
    url: https://gitlab.com/networkAutomation/git_test_module

- name: Push changes via SSH.
  community.general.git_push:
    path: /Users/federicoolivieri/git/git_test_module
    branch: master
    mode: ssh
    url: https://gitlab.com/networkAutomation/git_test_module

- name: Push changes on local repo.
  community.general.git_push:
    path: /Users/federicoolivieri/git/git_test_module
    comment: My amazing backup
    branch: master
    url: /Users/federicoolivieri/git/local_repo
'''

RETURN = '''
output:
    description: list of git cli commands stdout
    type: list
    returned: always
    sample: [
        "To https://gitlab.com/networkAutomation/git_test_module.git\n   372db19..99830f4  master -> master\n"
    ]
'''

import os
from ansible.module_utils.basic import AnsibleModule


def git_push(module):

    commands = list()

    path = module.params.get('path')
    url = module.params.get('url')
    user = module.params.get('user')
    token = module.params.get('token')
    branch = module.params.get('branch')
    push_option = module.params.get('push_option')
    mode = module.params.get('mode')

    def https(path, user, token, url, branch, push_option):
        if url.startswith('https://'):
            remote_add = [
                'git',
                '-C',
                path,
                'remote',
                'set-url',
                'origin',
                'https://{user}:{token}@{url}'.format(
                    url=url[8:],
                    user=user,
                    token=token,
                ),
            ]

            cmd = [
                'git',
                '-C',
                path,
                'push',
                'origin',
                branch,
                '--porcelain',
            ]

            if push_option:
                return [remote_add, cmd.insert(5, '--push-option={0} '.format(push_option))]

            if not push_option:
                return [remote_add, cmd]

    if mode == 'local':
        if 'https' in url or 'ssh' in url:
            module.fail_json(msg='SSH or HTTPS mode selected but repo is LOCAL')

        cmd = [
            'git', 
            '-C',
            path, 
            'push',
            'origin',
            branch,
        ]

        if push_option:
            module.fail_json(msg='"--push-option" not supported with mode "local"')

        if not push_option:
            return [remote_add, cmd]

    if mode == 'https':
        for cmd in https(path, user, token, url, branch, push_option):
            commands.append(cmd)

    if mode == 'ssh':
        if 'https' in url:
            module.fail_json(msg='SSH mode selected but HTTPS URL provided')

        remote_add = [
            'git',
            '-C',
            path,
            'remote',
            'set-url',
            'origin',
            url
        ]

        cmd = 'git -C {path} push origin {branch}'.format(
            path=path,
            branch=branch
        )
        commands.append(remote_add)

        if push_option:
            return [remote_add, cmd.insert(5, '--push-option={0} '.format(push_option))]

        if not push_option:
            return [remote_add, cmd]

    return commands


def main():

    argument_spec = dict(
        path=dict(required=True, type="path"),
        user=dict(),
        token=dict(),
        branch=dict(required=True),
        push_option=dict(),
        mode=dict(choices=["ssh", "https", "local"], default='ssh'),
        url=dict(required=True),
    )

    required_if = [
        ("mode", "https", ["user", "token"]),
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=required_if,
    )

    result = dict(changed=False)

    result_output = list()

    for cmd in git_push(module):
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
            elif 'Everything up-to-date' in error:
                result_output.append(error)
                result.update(changed=True)
            else:
                result_output.append(error)
                result.update(changed=True)

    if result_output:
        result.update(output=result_output)

    module.exit_json(**result)


if __name__ == "__main__":
    main()

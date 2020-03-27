#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Federico Olivieri (lvrfrc87@gmail.com)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: community.general.git_acp
author:
    - "Federico Olivieri (@Federico87)"
version_added: "2.10"
short_description: Perform git commit and git push operations.
description:
    - Manage git commits and git push on local or remote git repository.
options:
    path:
        description:
            - Folder path where .git/ is located.
        required: true
        type: str
    user:
        description:
            - Git username for https operations.
        type: str
    token:
        description:
            - Git API token for https operations.
        type: str
    comment:
        description:
            - Git commit comment. Same as "git commit -m".
        type: str
        required: true
    add:
        description:
            - list of files to be staged. Same as "git add ."
              Asterisx values not accepted. i.e. "./*" or "*".
        type: list
        default: ["."]
        elements: str
    branch:
        description:
            - Git branch where perform git push.
        required: True
        type: str
    push_option:
        description:
            - Git push options. Same as "git --push-option=option".
        type: str
    mode:
        description:
            - Git operations are performend eithr over ssh, https or local.
              Same as "git@git..." or "https://user:token@git..." or "git init --bare"
        choices: ['ssh', 'https', 'local']
        default: ssh
        type: str
    url:
        description:
            - Git repo URL.
        type: str
requirements:
    - git>=2.10.0 (the command line tool)
'''

EXAMPLES = '''

- name: Commit and push via HTTPs.
  community.general.git_acp:
    path: /Users/federicoolivieri/git/git_test_module
    user: Federico87
    token: m1Ap!T0k3n!!!
    comment: My amazing backup
    add: ['test.txt', 'txt.test']
    branch: master
    mode: https
    url: https://gitlab.com/networkAutomation/git_test_module

- name: Commit and push via SSH.
  community.general.git_acp:
    path: /Users/federicoolivieri/git/git_test_module
    comment: My amazing backup
    add: ['test.txt', 'txt.test']
    branch: master
    mode: ssh
    url: https://gitlab.com/networkAutomation/git_test_module

- name: Commit and push using the defaults.
  community.general.git_acp:
    path: /Users/federicoolivieri/git/git_test_module
    comment: My amazing backup
    branch: master
    url: https://gitlab.com/networkAutomation/git_test_module
'''

RETURN = '''
output:
    description: list of git cli commands stdout
    type: list
    returned: always
    sample: [
        "[master 99830f4] Remove [ test.txt, tax.txt ]\n 4 files changed, 26 insertions(+)...",
        "To https://gitlab.com/networkAutomation/git_test_module.git\n   372db19..99830f4  master -> master\n"
    ]
'''

import os

from ansible.module_utils.basic import AnsibleModule


def git_commit(module):

    commands = list()

    add = module.params.get('add')
    path = module.params.get('path')
    comment = module.params.get('comment')

    if add:
        commands.append('git -C {0} add {1}'.format(
            path,
            ' '.join(add)
        ))

    if comment:
        commands.append('git -C {0} commit -m "{1}"'.format(
            path,
            comment
        ))

    return commands


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
            remote_add = 'git -C {path} remote set-url origin https://{user}:{token}@{url}'.format(
                path=path,
                url=url[8:],
                user=user,
                token=token,
            )
            cmd = 'git -C {path} push origin {branch}'.format(
                path=path,
                branch=branch,
            )

        if push_option:
            index = cmd.find('origin')
            return [remote_add, cmd[:index] + '--push-option={option} '.format(option=push_option) + cmd[index:]]

        if not push_option:
            return [remote_add, cmd]

    if mode == 'local':
        if 'https' in url or 'ssh' in url:
            module.fail_json(msg='SSH or HTTPS mode selected but repo is LOCAL')

        remote_add = 'git -C {path} remote set-url origin {url}'.format(
            path=path,
            url=url
        )
        cmd = "git -C {path} push origin {branch}".format(
            path=path,
            branch=branch
        )

        if push_option:
            index = cmd.find('origin')
            return [remote_add, cmd[:index] + '--push-option={option} '.format(option=push_option) + cmd[index:]]

        if not push_option:
            return [remote_add, cmd]

    if mode == 'https':
        for cmd in https(path, user, token, url, branch, push_option):
            commands.append(cmd)

    if mode == 'ssh':
        if 'https' in url:
            module.fail_json(msg='SSH mode selected but HTTPS URL provided')

        remote_add = 'git -C {path} remote set-url origin {url}'.format(
            path=path,
            url=url,
        )
        cmd = 'git -C {path} push origin {branch}'.format(
            path=path,
            branch=branch
        )
        commands.append(remote_add)

        if push_option:
            index = cmd.find('origin')
            commands.append(cmd[:index] + '--push-option={option} '.format(option=push_option) + cmd[index:])

        if not push_option:
            commands.append(cmd)

    return commands


def main():

    argument_spec = dict(
        path=dict(required=True, type="path"),
        user=dict(),
        token=dict(),
        comment=dict(required=True),
        add=dict(type="list", elements='str', default=["."]),
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

    git_commands = git_commit(module) + git_push(module)

    result_output = list()

    for cmd in git_commands:
        _rc, output, error = module.run_command(cmd, check_rc=False)

        if output:
            if 'no changes added to commit' in output:
                module.fail_json(msg=output)
            elif 'nothing to commit, working tree clean' in output:
                module.fail_json(msg=output)
            else:
                result_output.append(output)

        if error:
            if 'error:' in error:
                module.fail_json(msg=error)
            elif 'fatal:' in error:
                module.fail_json(msg=error)
            else:
                result_output.append(error)

    if result_output:
        result.update(output=result_output)
        result.update(changed=True)

    module.exit_json(**result)


if __name__ == "__main__":
    main()

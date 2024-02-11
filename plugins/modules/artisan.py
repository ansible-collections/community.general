#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Ralf Langebrake <ralf@langebrake.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: artisan

short_description: Laravel command line interface

version_added: 8.4.0

description:
    - >
      Artisan is the command line interface included with Laravel, the
      PHP web application framework for artisans. The module was heavily
      inspired by M(community.general.composer), which is typically used together with artisan.

extends_documentation_fragment:
    - community.general.attributes

attributes:
    check_mode:
        support: full
    diff_mode:
        support: none

options:
    working_dir:
        description:
            - Directory of your project that contains the Artisan executable.
        required: true
        type: path
    command:
        description:
            - Artisan command like V(migrate), V(clear-compiled), or V(app:custom-command).
        required: true
        type: str
    options:
        description:
            - Command options like seed or force without leading hyphens.
        required: false
        elements: str
        default: []
        type: list
    args:
        description:
            - Command arguments, mainly in custom commands.
        required: false
        elements: str
        default: []
        type: list
    php_path:
        description:
            - Path to the PHP executable on the remote host if PHP is not included in E(PATH).
        required: false
        type: path

requirements:
    - Laravel
    - PHP

notes:
    - Always appended in each execution are C(--no-ansi), C(--no-interaction), and C(--force) if available.
    - Ansible Artisan is intended primarily, but not exclusively, for production deployments.

author:
    - Ralf Langebrake (@codebarista)
'''

EXAMPLES = r'''
# php artisan down --secret="t0pS3cRet" --refresh=60 --retry=60 --no-ansi --no-interaction
- name: Put the application into maintenance / demo mode
  community.general.artisan:
    working_dir: "{{ project_src }}"
    command: down
    options:
      - secret="ToPs3cReT"
      - refresh=60
      - retry=60

# php artisan storage:link --no-ansi --no-interaction --force
- name: Connect the public/storage link to storage/app/public
  community.general.artisan:
    working_dir: "{{ project_src }}"
    command: storage:link

# php artisan app:custom-command --no-ansi --no-interaction maybe/a/path
- name: Run custom command with arguments
  community.general.artisan:
    working_dir: "{{ project_src }}"
    php_path: /usr/local/bin/php
    command: app:custom-command
    arguments: maybe/a/path
  changed_when: "'modified' in app_custom_command.stdout"
  register: app_custom_command

# php artisan migrate --database=sqlite --isolated=true --seed --force
- name: Run migrations and seed database
  community.general.artisan:
    working_dir: "{{ project_src }}"
    command: "{{ item }}"
    options:
      - database=sqlite
      - isolated=true
  loop:
    - migrate
    - seed

# php artisan up --no-ansi --no-interaction
- name: Clear caches and bring the application out of maintenance mode
  community.general.artisan:
    working_dir: "{{ project_src }}"
    command: "{{ item }}"
  loop:
    - cache:clear
    - event:clear
    - route:clear
    - view:clear
    - up
'''

import os
import re

from ansible.module_utils.basic import AnsibleModule


def parse(out):
    # remove any unicode strings
    pattern = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

    # split and trim lines
    lines = list(filter(None, out.splitlines()))
    message = stderr = lines[0]

    # second line has the exception message
    if len(lines) > 1:
        stderr = lines[1]

    # message, stderr, stderr_lines
    return [
        re.sub(pattern, '', message).strip(),
        re.sub(pattern, '', stderr).strip(),
        list(map(str.strip, lines))
    ]


def has_changed(message):
    # message fragments that Laravel gives us
    artisan_messages = [
        'No publishable',  # resources for tag
        'Nothing to',  # migrate,...
        'already',  # up, down, exists,...
        'Not modified',
        'No changes'
    ]

    for info in artisan_messages:
        if info in message:
            return False

    return True


def get_help(module, command):
    # get all available options and arguments from an artisan command using artisan help to json
    rc, out, err = artisan_command(module, 'help %s' % command, options='--format=json --no-ansi')

    # no command, no help, no json
    if rc != 0:
        module.fail_json(msg='%s is not part of the command definitions.' % command)

    return module.from_json(out)


def get_options(module, command_help):
    # set available command options
    available_options = command_help['definition']['options']

    # merge default options
    command_options = module.params['options'] + [
        'no-interaction',
        'no-ansi',
        'force',
    ]

    options = []

    # check availability and format options
    for option in command_options:
        option = list(map(str.strip, option.lstrip('-').split('=')))
        if option[0] in available_options:
            options.append('--%s' % '='.join(option))

    # return the unique options turnkey ready as a string
    return ' '.join(list(set(options))).strip()


def get_arguments(module, command_help):
    # set available command arguments
    available_arguments = command_help['definition']['arguments']

    # mostly we have no arguments
    arguments = ''

    # if arguments expected for command, join from params
    if len(available_arguments) > 0:
        arguments = ' '.join(module.params['args'])

    # return arguments turnkey ready as a string
    return arguments.strip()


def get_artisan(module):
    artisan = '%s/artisan' % os.path.abspath(module.params['working_dir'])

    # check artisan executable path
    if not os.path.isfile(artisan):
        module.fail_json(msg='The artisan executable is not present.', artisan=artisan)

    return artisan


def get_php(module):
    # in most cases, PHP is available by default
    if module.params['php_path'] is None:
        php = module.get_bin_path('php', True, ['/usr/local/bin'])
    else:
        php = os.path.abspath(module.params['php_path'])

    # check php executable path
    if not os.path.isfile(php):
        module.fail_json(msg='The php executable is not present.', php=php)

    return php


def artisan_command(module, command, options, arguments=''):
    # this is the artisan executable in the project root
    artisan = get_artisan(module)

    # PHP is essential for successful execution
    php = get_php(module)

    # combine the entire command
    command = '%s %s %s %s %s' % (php, artisan, command, options, arguments)

    return module.run_command(command.strip())


def run_module():
    # available arguments a user can pass to the module
    module_args = dict(
        working_dir=dict(type='path', required=True),
        command=dict(type='str', required=True),
        php_path=dict(type='path'),
        options=dict(type='list', elements='str', default=[]),
        args=dict(type='list', elements='str', default=[]),
    )

    # instantiate the AnsibleModule object
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # define the artisan command
    cmd = module.params['command'].strip()

    # get command info from help
    hlp = get_help(module, cmd)

    # merge default and param options
    opts = get_options(module, hlp)

    # merge param arguments
    args = get_arguments(module, hlp)

    # seed the result dict in the object
    result = dict(
        stdout='%s %s %s' % (cmd, opts, args),
        artisan=get_artisan(module),
        msg='Running check mode',
        changed=False,
    )

    # in check mode just return the current state
    if module.check_mode:
        module.exit_json(**result)

    # do what it needs to do
    rc, out, err = artisan_command(module, cmd, opts, args)

    # try to extract the most meaningful output possible
    message, stderr, lines = parse(out)

    # set first stdout line as message
    result['msg'] = message.replace('INFO', '').strip()
    result['stdout'] = message

    # if necessary, add an error message to output
    if rc != 0:
        module.fail_json(stderr=stderr, stderr_lines=lines[1:3], **result)

    # set changed status
    result['changed'] = has_changed(message)

    # in the event of a success simply pass the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

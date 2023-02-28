#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, Dimitrios Tydeas Mengidis <tydeas.dr@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: composer
author:
    - "Dimitrios Tydeas Mengidis (@dmtrs)"
    - "René Moser (@resmo)"
short_description: Dependency Manager for PHP
description:
    - >
      Composer is a tool for dependency management in PHP. It allows you to
      declare the dependent libraries your project needs and it will install
      them in your project for you.
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    command:
        type: str
        description:
            - Composer command like "install", "update" and so on.
        default: install
    arguments:
        type: str
        description:
            - Composer arguments like required package, version and so on.
        default: ''
    executable:
        type: path
        description:
            - Path to PHP Executable on the remote host, if PHP is not in PATH.
        aliases: [ php_path ]
    working_dir:
        type: path
        description:
            - Directory of your project (see --working-dir). This is required when
              the command is not run globally.
            - Will be ignored if I(global_command=true).
    global_command:
        description:
            - Runs the specified command globally.
        type: bool
        default: false
    prefer_source:
        description:
            - Forces installation from package sources when possible (see --prefer-source).
        default: false
        type: bool
    prefer_dist:
        description:
            - Forces installation from package dist even for dev versions (see --prefer-dist).
        default: false
        type: bool
    no_dev:
        description:
            - Disables installation of require-dev packages (see --no-dev).
        default: true
        type: bool
    no_scripts:
        description:
            - Skips the execution of all scripts defined in composer.json (see --no-scripts).
        default: false
        type: bool
    no_plugins:
        description:
            - Disables all plugins (see --no-plugins).
        default: false
        type: bool
    optimize_autoloader:
        description:
            - Optimize autoloader during autoloader dump (see --optimize-autoloader).
            - Convert PSR-0/4 autoloading to classmap to get a faster autoloader.
            - Recommended especially for production, but can take a bit of time to run.
        default: true
        type: bool
    classmap_authoritative:
        description:
            - Autoload classes from classmap only.
            - Implicitly enable optimize_autoloader.
            - Recommended especially for production, but can take a bit of time to run.
        default: false
        type: bool
    apcu_autoloader:
        description:
            - Uses APCu to cache found/not-found classes
        default: false
        type: bool
    ignore_platform_reqs:
        description:
            - Ignore php, hhvm, lib-* and ext-* requirements and force the installation even if the local machine does not fulfill these.
        default: false
        type: bool
    composer_executable:
        type: path
        description:
            - Path to composer executable on the remote host, if composer is not in C(PATH) or a custom composer is needed.
        version_added: 3.2.0
requirements:
    - php
    - composer installed in bin path (recommended /usr/local/bin) or specified in I(composer_executable)
notes:
    - Default options that are always appended in each execution are --no-ansi, --no-interaction and --no-progress if available.
    - We received reports about issues on macOS if composer was installed by Homebrew. Please use the official install method to avoid issues.
'''

EXAMPLES = '''
- name: Download and installs all libs and dependencies outlined in the /path/to/project/composer.lock
  community.general.composer:
    command: install
    working_dir: /path/to/project

- name: Install a new package
  community.general.composer:
    command: require
    arguments: my/package
    working_dir: /path/to/project

- name: Clone and install a project with all dependencies
  community.general.composer:
    command: create-project
    arguments: package/package /path/to/project ~1.0
    working_dir: /path/to/project
    prefer_dist: true

- name: Install a package globally
  community.general.composer:
    command: require
    global_command: true
    arguments: my/package
'''

import re
from ansible.module_utils.basic import AnsibleModule


def parse_out(string):
    return re.sub(r"\s+", " ", string).strip()


def has_changed(string):
    for no_change in ["Nothing to install or update", "Nothing to install, update or remove"]:
        if no_change in string:
            return False

    return True


def get_available_options(module, command='install'):
    # get all available options from a composer command using composer help to json
    rc, out, err = composer_command(module, "help %s" % command, arguments="--no-interaction --format=json")
    if rc != 0:
        output = parse_out(err)
        module.fail_json(msg=output)

    command_help_json = module.from_json(out)
    return command_help_json['definition']['options']


def composer_command(module, command, arguments="", options=None, global_command=False):
    if options is None:
        options = []

    if module.params['executable'] is None:
        php_path = module.get_bin_path("php", True, ["/usr/local/bin"])
    else:
        php_path = module.params['executable']

    if module.params['composer_executable'] is None:
        composer_path = module.get_bin_path("composer", True, ["/usr/local/bin"])
    else:
        composer_path = module.params['composer_executable']

    cmd = "%s %s %s %s %s %s" % (php_path, composer_path, "global" if global_command else "", command, " ".join(options), arguments)
    return module.run_command(cmd)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(default="install", type="str"),
            arguments=dict(default="", type="str"),
            executable=dict(type="path", aliases=["php_path"]),
            working_dir=dict(type="path"),
            global_command=dict(default=False, type="bool"),
            prefer_source=dict(default=False, type="bool"),
            prefer_dist=dict(default=False, type="bool"),
            no_dev=dict(default=True, type="bool"),
            no_scripts=dict(default=False, type="bool"),
            no_plugins=dict(default=False, type="bool"),
            apcu_autoloader=dict(default=False, type="bool"),
            optimize_autoloader=dict(default=True, type="bool"),
            classmap_authoritative=dict(default=False, type="bool"),
            ignore_platform_reqs=dict(default=False, type="bool"),
            composer_executable=dict(type="path"),
        ),
        required_if=[('global_command', False, ['working_dir'])],
        supports_check_mode=True
    )

    # Get composer command with fallback to default
    command = module.params['command']
    if re.search(r"\s", command):
        module.fail_json(msg="Use the 'arguments' param for passing arguments with the 'command'")

    arguments = module.params['arguments']
    global_command = module.params['global_command']
    available_options = get_available_options(module=module, command=command)

    options = []

    # Default options
    default_options = [
        'no-ansi',
        'no-interaction',
        'no-progress',
    ]

    for option in default_options:
        if option in available_options:
            option = "--%s" % option
            options.append(option)

    if not global_command:
        options.extend(['--working-dir', "'%s'" % module.params['working_dir']])

    option_params = {
        'prefer_source': 'prefer-source',
        'prefer_dist': 'prefer-dist',
        'no_dev': 'no-dev',
        'no_scripts': 'no-scripts',
        'no_plugins': 'no-plugins',
        'apcu_autoloader': 'acpu-autoloader',
        'optimize_autoloader': 'optimize-autoloader',
        'classmap_authoritative': 'classmap-authoritative',
        'ignore_platform_reqs': 'ignore-platform-reqs',
    }

    for param, option in option_params.items():
        if module.params.get(param) and option in available_options:
            option = "--%s" % option
            options.append(option)

    if module.check_mode:
        if 'dry-run' in available_options:
            options.append('--dry-run')
        else:
            module.exit_json(skipped=True, msg="command '%s' does not support check mode, skipping" % command)

    rc, out, err = composer_command(module, command, arguments, options, global_command)

    if rc != 0:
        output = parse_out(err)
        module.fail_json(msg=output, stdout=err)
    else:
        # Composer version > 1.0.0-alpha9 now use stderr for standard notification messages
        output = parse_out(out + err)
        module.exit_json(changed=has_changed(output), msg=output, stdout=out + err)


if __name__ == '__main__':
    main()

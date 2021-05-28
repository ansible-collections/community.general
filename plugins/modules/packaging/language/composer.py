#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2014, Dimitrios Tydeas Mengidis <tydeas.dr@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
            - Will be ignored if C(global_command=true).
            - Alias C(working-dir) has been deprecated and will be removed in community.general 5.0.0.
        aliases: [ working-dir ]
    global_command:
        description:
            - Runs the specified command globally.
            - Alias C(global-command) has been deprecated and will be removed in community.general 5.0.0.
        type: bool
        default: false
        aliases: [ global-command ]
    prefer_source:
        description:
            - Forces installation from package sources when possible (see --prefer-source).
            - Alias C(prefer-source) has been deprecated and will be removed in community.general 5.0.0.
        default: false
        type: bool
        aliases: [ prefer-source ]
    prefer_dist:
        description:
            - Forces installation from package dist even for dev versions (see --prefer-dist).
            - Alias C(prefer-dist) has been deprecated and will be removed in community.general 5.0.0.
        default: false
        type: bool
        aliases: [ prefer-dist ]
    no_dev:
        description:
            - Disables installation of require-dev packages (see --no-dev).
            - Alias C(no-dev) has been deprecated and will be removed in community.general 5.0.0.
        default: true
        type: bool
        aliases: [ no-dev ]
    no_scripts:
        description:
            - Skips the execution of all scripts defined in composer.json (see --no-scripts).
            - Alias C(no-scripts) has been deprecated and will be removed in community.general 5.0.0.
        default: false
        type: bool
        aliases: [ no-scripts ]
    no_plugins:
        description:
            - Disables all plugins ( see --no-plugins ).
            - Alias C(no-plugins) has been deprecated and will be removed in community.general 5.0.0.
        default: false
        type: bool
        aliases: [ no-plugins ]
    optimize_autoloader:
        description:
            - Optimize autoloader during autoloader dump (see --optimize-autoloader).
            - Convert PSR-0/4 autoloading to classmap to get a faster autoloader.
            - Recommended especially for production, but can take a bit of time to run.
            - Alias C(optimize-autoloader) has been deprecated and will be removed in community.general 5.0.0.
        default: true
        type: bool
        aliases: [ optimize-autoloader ]
    classmap_authoritative:
        description:
            - Autoload classes from classmap only.
            - Implicitely enable optimize_autoloader.
            - Recommended especially for production, but can take a bit of time to run.
            - Alias C(classmap-authoritative) has been deprecated and will be removed in community.general 5.0.0.
        default: false
        type: bool
        aliases: [ classmap-authoritative ]
    apcu_autoloader:
        description:
            - Uses APCu to cache found/not-found classes
            - Alias C(apcu-autoloader) has been deprecated and will be removed in community.general 5.0.0.
        default: false
        type: bool
        aliases: [ apcu-autoloader ]
    ignore_platform_reqs:
        description:
            - Ignore php, hhvm, lib-* and ext-* requirements and force the installation even if the local machine does not fulfill these.
            - Alias C(ignore-platform-reqs) has been deprecated and will be removed in community.general 5.0.0.
        default: false
        type: bool
        aliases: [ ignore-platform-reqs ]
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
    prefer_dist: yes

- name: Install a package globally
  community.general.composer:
    command: require
    global_command: yes
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
            working_dir=dict(
                type="path", aliases=["working-dir"],
                deprecated_aliases=[dict(name='working-dir', version='5.0.0', collection_name='community.general')]),
            global_command=dict(
                default=False, type="bool", aliases=["global-command"],
                deprecated_aliases=[dict(name='global-command', version='5.0.0', collection_name='community.general')]),
            prefer_source=dict(
                default=False, type="bool", aliases=["prefer-source"],
                deprecated_aliases=[dict(name='prefer-source', version='5.0.0', collection_name='community.general')]),
            prefer_dist=dict(
                default=False, type="bool", aliases=["prefer-dist"],
                deprecated_aliases=[dict(name='prefer-dist', version='5.0.0', collection_name='community.general')]),
            no_dev=dict(
                default=True, type="bool", aliases=["no-dev"],
                deprecated_aliases=[dict(name='no-dev', version='5.0.0', collection_name='community.general')]),
            no_scripts=dict(
                default=False, type="bool", aliases=["no-scripts"],
                deprecated_aliases=[dict(name='no-scripts', version='5.0.0', collection_name='community.general')]),
            no_plugins=dict(
                default=False, type="bool", aliases=["no-plugins"],
                deprecated_aliases=[dict(name='no-plugins', version='5.0.0', collection_name='community.general')]),
            apcu_autoloader=dict(
                default=False, type="bool", aliases=["apcu-autoloader"],
                deprecated_aliases=[dict(name='apcu-autoloader', version='5.0.0', collection_name='community.general')]),
            optimize_autoloader=dict(
                default=True, type="bool", aliases=["optimize-autoloader"],
                deprecated_aliases=[dict(name='optimize-autoloader', version='5.0.0', collection_name='community.general')]),
            classmap_authoritative=dict(
                default=False, type="bool", aliases=["classmap-authoritative"],
                deprecated_aliases=[dict(name='classmap-authoritative', version='5.0.0', collection_name='community.general')]),
            ignore_platform_reqs=dict(
                default=False, type="bool", aliases=["ignore-platform-reqs"],
                deprecated_aliases=[dict(name='ignore-platform-reqs', version='5.0.0', collection_name='community.general')]),
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

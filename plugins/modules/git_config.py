#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Marius Gedminas <marius@pov.lt>
# Copyright (c) 2016, Matthew Gamble <git@matthewgamble.net>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: git_config
author:
  - Matthew Gamble (@djmattyg007)
  - Marius Gedminas (@mgedmin)
requirements: ['git']
short_description: Read and write git configuration
description:
  - The M(community.general.git_config) module changes git configuration by invoking C(git config).
    This is needed if you do not want to use M(ansible.builtin.template) for the entire git
    config file (for example because you need to change just C(user.email) in
    /etc/.git/config).  Solutions involving M(ansible.builtin.command) are cumbersome or
    do not work correctly in check mode.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  list_all:
    description:
      - List all settings (optionally limited to a given O(scope)).
    type: bool
    default: false
  name:
    description:
      - The name of the setting. If no value is supplied, the value will
        be read from the config if it has been set.
    type: str
  repo:
    description:
      - Path to a git repository for reading and writing values from a
        specific repo.
    type: path
  file:
    description:
      - Path to an adhoc git configuration file to be managed using the V(file) scope.
    type: path
    version_added: 2.0.0
  scope:
    description:
      - Specify which scope to read/set values from.
      - This is required when setting config values.
      - If this is set to V(local), you must also specify the O(repo) parameter.
      - If this is set to V(file), you must also specify the O(file) parameter.
      - It defaults to system only when not using O(list_all=true).
    choices: [ "file", "local", "global", "system" ]
    type: str
  state:
    description:
      - "Indicates the setting should be set/unset.
        This parameter has higher precedence than O(value) parameter:
        when O(state=absent) and O(value) is defined, O(value) is discarded."
    choices: [ 'present', 'absent' ]
    default: 'present'
    type: str
  value:
    description:
      - When specifying the name of a single setting, supply a value to
        set that setting to the given value.
    type: str
  add_mode:
    description:
      - Specify if a value should replace the existing value(s) or if the new
        value should be added alongside other values with the same name.
      - This option is only relevant when adding/replacing values. If O(state=absent) or
        values are just read out, this option is not considered.
    choices: [ "add", "replace-all" ]
    type: str
    default: "replace-all"
    version_added: 8.1.0
'''

EXAMPLES = '''
- name: Add a setting to ~/.gitconfig
  community.general.git_config:
    name: alias.ci
    scope: global
    value: commit

- name: Add a setting to ~/.gitconfig
  community.general.git_config:
    name: alias.st
    scope: global
    value: status

- name: Remove a setting from ~/.gitconfig
  community.general.git_config:
    name: alias.ci
    scope: global
    state: absent

- name: Add a setting to ~/.gitconfig
  community.general.git_config:
    name: core.editor
    scope: global
    value: vim

- name: Add a setting system-wide
  community.general.git_config:
    name: alias.remotev
    scope: system
    value: remote -v

- name: Add a setting to a system scope (default)
  community.general.git_config:
    name: alias.diffc
    value: diff --cached

- name: Add a setting to a system scope (default)
  community.general.git_config:
    name: color.ui
    value: auto

- name: Add several options for the same name
  community.general.git_config:
    name: push.pushoption
    value: "{{ item }}"
    add_mode: add
  loop:
    - merge_request.create
    - merge_request.draft

- name: Make etckeeper not complaining when it is invoked by cron
  community.general.git_config:
    name: user.email
    repo: /etc
    scope: local
    value: 'root@{{ ansible_fqdn }}'

- name: Read individual values from git config
  community.general.git_config:
    name: alias.ci
    scope: global

- name: Scope system is also assumed when reading values, unless list_all=true
  community.general.git_config:
    name: alias.diffc

- name: Read all values from git config
  community.general.git_config:
    list_all: true
    scope: global

- name: When list_all is yes and no scope is specified, you get configuration from all scopes
  community.general.git_config:
    list_all: true

- name: Specify a repository to include local settings
  community.general.git_config:
    list_all: true
    repo: /path/to/repo.git
'''

RETURN = '''
---
config_value:
  description: When O(list_all=false) and value is not set, a string containing the value of the setting in name
  returned: success
  type: str
  sample: "vim"

config_values:
  description: When O(list_all=true), a dict containing key/value pairs of multiple configuration settings
  returned: success
  type: dict
  sample:
    core.editor: "vim"
    color.ui: "auto"
    alias.diffc: "diff --cached"
    alias.remotev: "remote -v"
'''

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(
        argument_spec=dict(
            list_all=dict(required=False, type='bool', default=False),
            name=dict(type='str'),
            repo=dict(type='path'),
            file=dict(type='path'),
            add_mode=dict(required=False, type='str', default='replace-all', choices=['add', 'replace-all']),
            scope=dict(required=False, type='str', choices=['file', 'local', 'global', 'system']),
            state=dict(required=False, type='str', default='present', choices=['present', 'absent']),
            value=dict(required=False),
        ),
        mutually_exclusive=[['list_all', 'name'], ['list_all', 'value'], ['list_all', 'state']],
        required_if=[
            ('scope', 'local', ['repo']),
            ('scope', 'file', ['file'])
        ],
        required_one_of=[['list_all', 'name']],
        supports_check_mode=True,
    )
    git_path = module.get_bin_path('git', True)

    params = module.params
    # We check error message for a pattern, so we need to make sure the messages appear in the form we're expecting.
    # Set the locale to C to ensure consistent messages.
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    name = params['name'] or ''
    unset = params['state'] == 'absent'
    new_value = params['value'] or ''
    add_mode = params['add_mode']

    scope = determine_scope(params)
    cwd = determine_cwd(scope, params)

    base_args = [git_path, "config", "--includes"]

    if scope == 'file':
        base_args.append('-f')
        base_args.append(params['file'])
    elif scope:
        base_args.append("--" + scope)

    list_args = list(base_args)

    if params['list_all']:
        list_args.append('-l')

    if name:
        list_args.append("--get-all")
        list_args.append(name)

    (rc, out, err) = module.run_command(list_args, cwd=cwd, expand_user_and_vars=False)

    if params['list_all'] and scope and rc == 128 and 'unable to read config file' in err:
        # This just means nothing has been set at the given scope
        module.exit_json(changed=False, msg='', config_values={})
    elif rc >= 2:
        # If the return code is 1, it just means the option hasn't been set yet, which is fine.
        module.fail_json(rc=rc, msg=err, cmd=' '.join(list_args))

    old_values = out.rstrip().splitlines()

    if params['list_all']:
        config_values = {}
        for value in old_values:
            k, v = value.split('=', 1)
            config_values[k] = v
        module.exit_json(changed=False, msg='', config_values=config_values)
    elif not new_value and not unset:
        module.exit_json(changed=False, msg='', config_value=old_values[0] if old_values else '')
    elif unset and not out:
        module.exit_json(changed=False, msg='no setting to unset')
    elif new_value in old_values and (len(old_values) == 1 or add_mode == "add"):
        module.exit_json(changed=False, msg="")

    # Until this point, the git config was just read and in case no change is needed, the module has already exited.

    set_args = list(base_args)
    if unset:
        set_args.append("--unset-all")
        set_args.append(name)
    else:
        set_args.append("--" + add_mode)
        set_args.append(name)
        set_args.append(new_value)

    if not module.check_mode:
        (rc, out, err) = module.run_command(set_args, cwd=cwd, ignore_invalid_cwd=False, expand_user_and_vars=False)
        if err:
            module.fail_json(rc=rc, msg=err, cmd=set_args)

    if unset:
        after_values = []
    elif add_mode == "add":
        after_values = old_values + [new_value]
    else:
        after_values = [new_value]

    module.exit_json(
        msg='setting changed',
        diff=dict(
            before_header=' '.join(set_args),
            before=build_diff_value(old_values),
            after_header=' '.join(set_args),
            after=build_diff_value(after_values),
        ),
        changed=True
    )


def determine_scope(params):
    if params['scope']:
        return params['scope']
    elif params['list_all']:
        return ""
    else:
        return 'system'


def build_diff_value(value):
    if not value:
        return "\n"
    elif len(value) == 1:
        return value[0] + "\n"
    else:
        return value


def determine_cwd(scope, params):
    if scope == 'local':
        return params['repo']
    elif params['list_all'] and params['repo']:
        # Include local settings from a specific repo when listing all available settings
        return params['repo']
    else:
        # Run from root directory to avoid accidentally picking up any local config settings
        return "/"


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Marius Gedminas <marius@pov.lt>
# (c) 2016, Matthew Gamble <git@matthewgamble.net>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
  - The C(git_config) module changes git configuration by invoking 'git config'.
    This is needed if you don't want to use M(ansible.builtin.template) for the entire git
    config file (e.g. because you need to change just C(user.email) in
    /etc/.git/config).  Solutions involving M(ansible.builtin.command) are cumbersome or
    don't work correctly in check mode.
options:
  list_all:
    description:
      - List all settings (optionally limited to a given I(scope)).
    type: bool
    default: 'no'
  name:
    description:
      - The name of the setting. If no value is supplied, the value will
        be read from the config if it has been set.
  repo:
    description:
      - Path to a git repository for reading and writing values from a
        specific repo.
  file:
    description:
      - Path to an adhoc git configuration file to be managed using the C(file) scope.
    type: path
    version_added: 2.0.0
  scope:
    description:
      - Specify which scope to read/set values from.
      - This is required when setting config values.
      - If this is set to C(local), you must also specify the C(repo) parameter.
      - If this is set to C(file), you must also specify the C(file) parameter.
      - It defaults to system only when not using I(list_all)=C(yes).
    choices: [ "file", "local", "global", "system" ]
  state:
    description:
      - "Indicates the setting should be set/unset.
        This parameter has higher precedence than I(value) parameter:
        when I(state)=absent and I(value) is defined, I(value) is discarded."
    choices: [ 'present', 'absent' ]
    default: 'present'
  value:
    description:
      - When specifying the name of a single setting, supply a value to
        set that setting to the given value.
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

- name: Scope system is also assumed when reading values, unless list_all=yes
  community.general.git_config:
    name: alias.diffc

- name: Read all values from git config
  community.general.git_config:
    list_all: yes
    scope: global

- name: When list_all is yes and no scope is specified, you get configuration from all scopes
  community.general.git_config:
    list_all: yes

- name: Specify a repository to include local settings
  community.general.git_config:
    list_all: yes
    repo: /path/to/repo.git
'''

RETURN = '''
---
config_value:
  description: When list_all=no and value is not set, a string containing the value of the setting in name
  returned: success
  type: str
  sample: "vim"

config_values:
  description: When list_all=yes, a dict containing key/value pairs of multiple configuration settings
  returned: success
  type: dict
  sample:
    core.editor: "vim"
    color.ui: "auto"
    alias.diffc: "diff --cached"
    alias.remotev: "remote -v"
'''
import os

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import shlex_quote


def main():
    module = AnsibleModule(
        argument_spec=dict(
            list_all=dict(required=False, type='bool', default=False),
            name=dict(type='str'),
            repo=dict(type='path'),
            file=dict(type='path'),
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

    if params['name']:
        name = params['name']
    else:
        name = None

    if params['scope']:
        scope = params['scope']
    elif params['list_all']:
        scope = None
    else:
        scope = 'system'

    if params['state'] == 'absent':
        unset = 'unset'
        params['value'] = None
    else:
        unset = None

    if params['value']:
        new_value = params['value']
    else:
        new_value = None

    args = [git_path, "config", "--includes"]
    if params['list_all']:
        args.append('-l')
    if scope:
        args.append("--" + scope)
    if name:
        args.append(name)

    if scope == 'file':
        args.append('-f')
        args.append(params['file'])

    if scope == 'local':
        dir = params['repo']
    elif params['list_all'] and params['repo']:
        # Include local settings from a specific repo when listing all available settings
        dir = params['repo']
    else:
        # Run from root directory to avoid accidentally picking up any local config settings
        dir = "/"

    (rc, out, err) = module.run_command(' '.join(args), cwd=dir)
    if params['list_all'] and scope and rc == 128 and 'unable to read config file' in err:
        # This just means nothing has been set at the given scope
        module.exit_json(changed=False, msg='', config_values={})
    elif rc >= 2:
        # If the return code is 1, it just means the option hasn't been set yet, which is fine.
        module.fail_json(rc=rc, msg=err, cmd=' '.join(args))

    if params['list_all']:
        values = out.rstrip().splitlines()
        config_values = {}
        for value in values:
            k, v = value.split('=', 1)
            config_values[k] = v
        module.exit_json(changed=False, msg='', config_values=config_values)
    elif not new_value and not unset:
        module.exit_json(changed=False, msg='', config_value=out.rstrip())
    elif unset and not out:
        module.exit_json(changed=False, msg='no setting to unset')
    else:
        old_value = out.rstrip()
        if old_value == new_value:
            module.exit_json(changed=False, msg="")

    if not module.check_mode:
        if unset:
            args.insert(len(args) - 1, "--" + unset)
            cmd = args
        else:
            new_value_quoted = shlex_quote(new_value)
            cmd = args + [new_value_quoted]
        try:  # try using extra parameter from ansible-base 2.10.4 onwards
            (rc, out, err) = module.run_command(cmd, cwd=dir, ignore_invalid_cwd=False)
        except TypeError:
            # @TODO remove try/except when community.general drop support for 2.10.x
            if not os.path.isdir(dir):
                module.fail_json(msg="Cannot find directory '{0}'".format(dir))
            (rc, out, err) = module.run_command(cmd, cwd=dir)
        if err:
            module.fail_json(rc=rc, msg=err, cmd=cmd)

    module.exit_json(
        msg='setting changed',
        diff=dict(
            before_header=' '.join(args),
            before=old_value + "\n",
            after_header=' '.join(args),
            after=(new_value or '') + "\n"
        ),
        changed=True
    )


if __name__ == '__main__':
    main()

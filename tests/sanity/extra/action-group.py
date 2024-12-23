#!/usr/bin/env python
# Copyright (c) 2024, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
"""Make sure all modules that should show up in the action group."""

from __future__ import annotations

import os
import re
import yaml


ACTION_GROUPS = {
    # The format is as follows:
    # * 'pattern': a regular expression matching all module names potentially belonging to the action group;
    # * 'exclusions': a list of modules that are not part of the action group; all other modules matching 'pattern' must be part of it;
    # * 'doc_fragment': the docs fragment that documents membership of the action group.
    'consul': {
        'pattern': re.compile('^consul_.*$'),
        'exclusions': [
            'consul_acl_bootstrap',
            'consul_kv',
        ],
        'doc_fragment': 'community.general.consul.actiongroup_consul',
    },
    'keycloak': {
        'pattern': re.compile('^keycloak_.*$'),
        'exclusions': [
            'keycloak_realm_info',
        ],
        'doc_fragment': 'community.general.keycloak.actiongroup_keycloak',
    },
    'proxmox': {
        'pattern': re.compile('^proxmox(_.*)?$'),
        'exclusions': [],
        'doc_fragment': 'community.general.proxmox.actiongroup_proxmox',
    },
}


def main():
    """Main entry point."""

    # Load redirects
    meta_runtime = 'meta/runtime.yml'
    self_path = 'tests/sanity/extra/action-group.py'
    try:
        with open(meta_runtime, 'rb') as f:
            data = yaml.safe_load(f)
        action_groups = data['action_groups']
    except Exception as exc:
        print(f'{meta_runtime}: cannot load action groups: {exc}')
        return

    for action_group in action_groups:
        if action_group not in ACTION_GROUPS:
            print(f'{meta_runtime}: found unknown action group {action_group!r}; likely {self_path} needs updating')
    for action_group, action_group_data in list(ACTION_GROUPS.items()):
        if action_group not in action_groups:
            print(f'{meta_runtime}: cannot find action group {action_group!r}; likely {self_path} needs updating')

    modules_directory = 'plugins/modules/'
    modules_suffix = '.py'

    for file in os.listdir(modules_directory):
        if not file.endswith(modules_suffix):
            continue
        module_name = file[:-len(modules_suffix)]

        for action_group, action_group_data in ACTION_GROUPS.items():
            action_group_content = action_groups.get(action_group) or []
            path = os.path.join(modules_directory, file)

            if not action_group_data['pattern'].match(module_name):
                if module_name in action_group_content:
                    print(f'{path}: module is in action group {action_group!r} despite not matching its pattern as defined in {self_path}')
                continue

            should_be_in_action_group = module_name not in action_group_data['exclusions']

            if should_be_in_action_group:
                if module_name not in action_group_content:
                    print(f'{meta_runtime}: module {module_name!r} is not part of {action_group!r} action group')
                else:
                    action_group_content.remove(module_name)

            documentation = []
            in_docs = False
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('DOCUMENTATION ='):
                        in_docs = True
                    elif line.startswith(("'''", '"""')) and in_docs:
                        in_docs = False
                    elif in_docs:
                        documentation.append(line)
            if in_docs:
                print(f'{path}: cannot find DOCUMENTATION end')
            if not documentation:
                print(f'{path}: cannot find DOCUMENTATION')
                continue

            try:
                docs = yaml.safe_load('\n'.join(documentation))
                if not isinstance(docs, dict):
                    raise Exception('is not a top-level dictionary')
            except Exception as exc:
                print(f'{path}: cannot load DOCUMENTATION as YAML: {exc}')
                continue

            docs_fragments = docs.get('extends_documentation_fragment') or []
            is_in_action_group = action_group_data['doc_fragment'] in docs_fragments

            if should_be_in_action_group != is_in_action_group:
                if should_be_in_action_group:
                    print(
                        f'{path}: module does not document itself as part of action group {action_group!r}, but it should;'
                        f' you need to add {action_group_data["doc_fragment"]} to "extends_documentation_fragment" in DOCUMENTATION'
                    )
                else:
                    print(f'{path}: module documents itself as part of action group {action_group!r}, but it should not be')

    for action_group, action_group_data in ACTION_GROUPS.items():
        action_group_content = action_groups.get(action_group) or []
        for module_name in action_group_content:
            print(
                f'{meta_runtime}: module {module_name} mentioned in {action_group!r} action group'
                f' does not exist or does not match pattern defined in {self_path}'
            )


if __name__ == '__main__':
    main()

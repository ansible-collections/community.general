#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2023, Andrew Hyatt <andy@hyatt.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: copr
short_description: Enable or disable dnf repositories using config-manager
version_added: 8.1.0
description: This module enables or disables repositories using the C(dnf config-manager) sub-command.
author: Andrew Hyatt (@ahyattdev) <andy@hyatt.xyz>
requirements:
  - dnf
  - dnf-plugins-core
notes:
  - Supports C(check_mode).
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Repository id, for example C(crb).
    default: []
    required: false
    type: list
    elements: str
state:
    description:
      - Whether the repositories should be V(enabled) or V(disabled).
    default: enabled
    required: false
    type: str
    choices: [enabled, disabled]
'''

EXAMPLES = r'''
- name: Ensure the crb repository is enabled
  community.general.dnf_config_manager:
    name: crb
    state: enabled

- name: Ensure the appstream and zfs repositories are disabled
  community.general.dnf_config_manager:
    name:
      - appstream
      - zfs
    state: present
'''

RETURN = r'''
repo_states_pre:
  description: Repo IDs before action taken.
  returned: success
  type: dict
  contains:
    repo_id:
      description: Repository ID
      type: str
  sample: |-
    {
      "appstream": "enabled",
      "appstream-debuginfo": "disabled",
      "appstream-source": "disabled",
      "baseos": "enabled",
      "baseos-debuginfo": "disabled",
      "baseos-source": "disabled",
      "crb": "enabled",
      "crb-debug": "disabled",
      "crb-source": "disabled"
    }
repo_states_post:
  description: Repo IDs after action taken.
  returned: success
  type: dict
  contains:
    repo_id:
      description: Repository ID
      type: str
  sample: |-
    {
      "appstream": "enabled",
      "appstream-debuginfo": "disabled",
      "appstream-source": "disabled",
      "baseos": "enabled",
      "baseos-debuginfo": "disabled",
      "baseos-source": "disabled",
      "crb": "enabled",
      "crb-debug": "disabled",
      "crb-source": "disabled"
    }
changed_repos:
    description: Repositories changed.
    returned: success
    type: list
    elements: str
    sample: [ 'crb' ]
'''

from ansible.module_utils.basic import AnsibleModule
import os
import re

DNF_BIN = "/usr/bin/dnf"
REPO_ID_RE = re.compile('^Repo-id\s*:\s*(\S+)$')
REPO_STATUS_RE = re.compile('^Repo-status\s*:\s*(disabled|enabled)$')

def get_repo_states(module):
    rc, out, err = module.run_command([DNF_BIN, 'repolist', '--all', '--verbose'], check_rc=True)

    repos = dict()
    last_repo = ''
    for i, line in enumerate(out.split('\n')):
        m = REPO_ID_RE.match(line)
        if m:
            if len(last_repo) > 0:
                module.fail_json(msg='dnf repolist parse failure: parsed another repo id before next status')
            last_repo = m.group(1)
            continue
        m = REPO_STATUS_RE.match(line)
        if m:
            if len(last_repo) == 0:
                module.fail_json(msg='dnf repolist parse failure: parsed status before repo id')
            repos[last_repo] = m.group(1)
            last_repo = ''
    return repos, out

def set_repo_states(module, repo_ids, state):
    rc, out, err = module.run_command([DNF_BIN, 'config-manager', '--set-{0}'.format(state)] + repo_ids, check_rc=True)
    return out

def main():
    module_args = dict(
        name=dict(type='list', required=False, default=[]),
        state=dict(type='str', required=False, choices=['enabled', 'disabled'], default='enabled')
    )

    result = dict(
        changed=False,
        msg=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if not os.path.exists(DNF_BIN):
        module.fail_json(msg="%s was not found" % DNF_BIN)

    repo_states, result['msg'] = get_repo_states(module)
    result['repo_states_pre'] = repo_states

    desired_repo_state = module.params['state']
    names = module.params['name']
    
    to_change = []
    for repo_id in names:
        if not repo_id in repo_states:
            module.fail_json(msg='unknown repo {0}'.format(repo_id))
        if repo_states[repo_id] != desired_repo_state:
            to_change.append(repo_id)
    result['changed'] = len(to_change) > 0

    if module.check_mode:
        module.exit_json(**result)
    
    if len(to_change) > 0:
        result['msg'] = set_repo_states(module, to_change, desired_repo_state)

    repo_states_post, result['msg'] = get_repo_states(module)
    for repo_id in to_change:
      if repo_states_post[repo_id] != desired_repo_state:
        module.fail_json(msg='repo {0} is not {1} after dnf config-manager command'.format(repo_id, desired_repo_state))
    result['repo_states_post'] = repo_states_post
    result['changed_repos'] = to_change

    module.exit_json(**result)

if __name__ == "__main__":
    main()

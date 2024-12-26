#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Daniel Jaouen <dcj24@cornell.edu>
# Copyright (c) 2016, Indrajit Raychaudhuri <irc+code@indrajit.com>
#
# Based on homebrew (Andrew Dunham <andrew@du.nham.ca>)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: homebrew_tap
author:
  - "Indrajit Raychaudhuri (@indrajitr)"
  - "Daniel Jaouen (@danieljaouen)"
short_description: Tap a Homebrew repository
description:
  - Tap external Homebrew repositories.
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
      - The GitHub user/organization repository to tap.
    required: true
    aliases: ['tap']
    type: list
    elements: str
  url:
    description:
      - The optional git URL of the repository to tap. The URL is not assumed to be on GitHub, and the protocol does not have
        to be HTTP. Any location and protocol that git can handle is fine.
      - O(name) option may not be a list of multiple taps (but a single tap instead) when this option is provided.
    required: false
    type: str
  state:
    description:
      - State of the repository.
    choices: ['present', 'absent']
    required: false
    default: 'present'
    type: str
  path:
    description:
      - A V(:) separated list of paths to search for C(brew) executable.
    default: '/usr/local/bin:/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin'
    type: path
    version_added: '2.1.0'
requirements: [homebrew]
"""

EXAMPLES = r"""
- name: Tap a Homebrew repository, state present
  community.general.homebrew_tap:
    name: homebrew/dupes

- name: Tap a Homebrew repository, state absent
  community.general.homebrew_tap:
    name: homebrew/dupes
    state: absent

- name: Tap a Homebrew repository, state present
  community.general.homebrew_tap:
    name: homebrew/dupes,homebrew/science
    state: present

- name: Tap a Homebrew repository using url, state present
  community.general.homebrew_tap:
    name: telemachus/brew
    url: 'https://bitbucket.org/telemachus/brew'
"""

import re

from ansible.module_utils.basic import AnsibleModule


def a_valid_tap(tap):
    '''Returns True if the tap is valid.'''
    regex = re.compile(r'^([\w-]+)/(homebrew-)?([\w-]+)$')
    return regex.match(tap)


def already_tapped(module, brew_path, tap):
    '''Returns True if already tapped.'''

    rc, out, err = module.run_command([
        brew_path,
        'tap',
    ])

    taps = [tap_.strip().lower() for tap_ in out.split('\n') if tap_]
    tap_name = re.sub('homebrew-', '', tap.lower())

    return tap_name in taps


def add_tap(module, brew_path, tap, url=None):
    '''Adds a single tap.'''
    failed, changed, msg = False, False, ''

    if not a_valid_tap(tap):
        failed = True
        msg = 'not a valid tap: %s' % tap

    elif not already_tapped(module, brew_path, tap):
        if module.check_mode:
            module.exit_json(changed=True)

        rc, out, err = module.run_command([
            brew_path,
            'tap',
            tap,
            url,
        ])
        if rc == 0:
            changed = True
            msg = 'successfully tapped: %s' % tap
        else:
            failed = True
            msg = 'failed to tap: %s due to %s' % (tap, err)

    else:
        msg = 'already tapped: %s' % tap

    return (failed, changed, msg)


def add_taps(module, brew_path, taps):
    '''Adds one or more taps.'''
    failed, changed, unchanged, added, msg = False, False, 0, 0, ''

    for tap in taps:
        (failed, changed, msg) = add_tap(module, brew_path, tap)
        if failed:
            break
        if changed:
            added += 1
        else:
            unchanged += 1

    if failed:
        msg = 'added: %d, unchanged: %d, error: ' + msg
        msg = msg % (added, unchanged)
    elif added:
        changed = True
        msg = 'added: %d, unchanged: %d' % (added, unchanged)
    else:
        msg = 'added: %d, unchanged: %d' % (added, unchanged)

    return (failed, changed, msg)


def remove_tap(module, brew_path, tap):
    '''Removes a single tap.'''
    failed, changed, msg = False, False, ''

    if not a_valid_tap(tap):
        failed = True
        msg = 'not a valid tap: %s' % tap

    elif already_tapped(module, brew_path, tap):
        if module.check_mode:
            module.exit_json(changed=True)

        rc, out, err = module.run_command([
            brew_path,
            'untap',
            tap,
        ])
        if not already_tapped(module, brew_path, tap):
            changed = True
            msg = 'successfully untapped: %s' % tap
        else:
            failed = True
            msg = 'failed to untap: %s due to %s' % (tap, err)

    else:
        msg = 'already untapped: %s' % tap

    return (failed, changed, msg)


def remove_taps(module, brew_path, taps):
    '''Removes one or more taps.'''
    failed, changed, unchanged, removed, msg = False, False, 0, 0, ''

    for tap in taps:
        (failed, changed, msg) = remove_tap(module, brew_path, tap)
        if failed:
            break
        if changed:
            removed += 1
        else:
            unchanged += 1

    if failed:
        msg = 'removed: %d, unchanged: %d, error: ' + msg
        msg = msg % (removed, unchanged)
    elif removed:
        changed = True
        msg = 'removed: %d, unchanged: %d' % (removed, unchanged)
    else:
        msg = 'removed: %d, unchanged: %d' % (removed, unchanged)

    return (failed, changed, msg)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(aliases=['tap'], type='list', required=True, elements='str'),
            url=dict(default=None, required=False),
            state=dict(default='present', choices=['present', 'absent']),
            path=dict(
                default="/usr/local/bin:/opt/homebrew/bin:/home/linuxbrew/.linuxbrew/bin",
                required=False,
                type='path',
            ),
        ),
        supports_check_mode=True,
    )

    path = module.params['path']
    if path:
        path = path.split(':')

    brew_path = module.get_bin_path(
        'brew',
        required=True,
        opt_dirs=path,
    )

    taps = module.params['name']
    url = module.params['url']

    if module.params['state'] == 'present':
        if url is None:
            # No tap URL provided explicitly, continue with bulk addition
            # of all the taps.
            failed, changed, msg = add_taps(module, brew_path, taps)
        else:
            # When an tap URL is provided explicitly, we allow adding
            # *single* tap only. Validate and proceed to add single tap.
            if len(taps) > 1:
                msg = "List of multiple taps may not be provided with 'url' option."
                module.fail_json(msg=msg)
            else:
                failed, changed, msg = add_tap(module, brew_path, taps[0], url)

        if failed:
            module.fail_json(msg=msg)
        else:
            module.exit_json(changed=changed, msg=msg)

    elif module.params['state'] == 'absent':
        failed, changed, msg = remove_taps(module, brew_path, taps)

        if failed:
            module.fail_json(msg=msg)
        else:
            module.exit_json(changed=changed, msg=msg)


if __name__ == '__main__':
    main()

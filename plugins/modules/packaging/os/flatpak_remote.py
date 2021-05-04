#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017 John Kwiatkoski (@JayKayy) <jkwiat40@gmail.com>
# Copyright: (c) 2018 Alexander Bethke (@oolongbrothers) <oolongbrothers@gmx.net>
# Copyright: (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


# ATTENTION CONTRIBUTORS!
#
# TL;DR: Run this module's integration tests manually before opening a pull request
#
# Long explanation:
# The integration tests for this module are currently NOT run on the Ansible project's continuous
# delivery pipeline. So please: When you make changes to this module, make sure that you run the
# included integration tests manually for both Python 2 and Python 3:
#
#   Python 2:
#       ansible-test integration -v --docker fedora28 --docker-privileged --allow-unsupported --python 2.7 flatpak_remote
#   Python 3:
#       ansible-test integration -v --docker fedora28 --docker-privileged --allow-unsupported --python 3.6 flatpak_remote
#
# Because of external dependencies, the current integration tests are somewhat too slow and brittle
# to be included right now. I have plans to rewrite the integration tests based on a local flatpak
# repository so that they can be included into the normal CI pipeline.
# //oolongbrothers


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatpak_remote
short_description: Manage flatpak repository remotes
description:
- Allows users to add or remove flatpak remotes.
- The flatpak remotes concept is comparable to what is called repositories in other packaging
  formats.
- Currently, remote addition is only supported via I(flatpakrepo) file URLs.
- Existing remotes will not be updated.
- See the M(community.general.flatpak) module for managing flatpaks.
author:
- John Kwiatkoski (@JayKayy)
- Alexander Bethke (@oolongbrothers)
requirements:
- flatpak
options:
  executable:
    description:
    - The path to the C(flatpak) executable to use.
    - By default, this module looks for the C(flatpak) executable on the path.
    type: str
    default: flatpak
  flatpakrepo_url:
    description:
    - The URL to the I(flatpakrepo) file representing the repository remote to add.
    - When used with I(state=present), the flatpak remote specified under the I(flatpakrepo_url)
      is added using the specified installation C(method).
    - When used with I(state=absent), this is not required.
    - Required when I(state=present).
    type: str
  method:
    description:
    - The installation method to use.
    - Defines if the I(flatpak) is supposed to be installed globally for the whole C(system)
      or only for the current C(user).
    type: str
    choices: [ system, user ]
    default: system
  name:
    description:
    - The desired name for the flatpak remote to be registered under on the managed host.
    - When used with I(state=present), the remote will be added to the managed host under
      the specified I(name).
    - When used with I(state=absent) the remote with that name will be removed.
    type: str
    required: true
  state:
    description:
    - Indicates the desired package state.
    type: str
    choices: [ absent, present ]
    default: present
'''

EXAMPLES = r'''
- name: Add the Gnome flatpak remote to the system installation
  community.general.flatpak_remote:
    name: gnome
    state: present
    flatpakrepo_url: https://sdk.gnome.org/gnome-apps.flatpakrepo

- name: Add the flathub flatpak repository remote to the user installation
  community.general.flatpak_remote:
    name: flathub
    state: present
    flatpakrepo_url: https://dl.flathub.org/repo/flathub.flatpakrepo
    method: user

- name: Remove the Gnome flatpak remote from the user installation
  community.general.flatpak_remote:
    name: gnome
    state: absent
    method: user

- name: Remove the flathub remote from the system installation
  community.general.flatpak_remote:
    name: flathub
    state: absent
'''

RETURN = r'''
command:
  description: The exact flatpak command that was executed
  returned: When a flatpak command has been executed
  type: str
  sample: "/usr/bin/flatpak remote-add --system flatpak-test https://dl.flathub.org/repo/flathub.flatpakrepo"
msg:
  description: Module error message
  returned: failure
  type: str
  sample: "Executable '/usr/local/bin/flatpak' was not found on the system."
rc:
  description: Return code from flatpak binary
  returned: When a flatpak command has been executed
  type: int
  sample: 0
stderr:
  description: Error output from flatpak binary
  returned: When a flatpak command has been executed
  type: str
  sample: "error: GPG verification enabled, but no summary found (check that the configured URL in remote config is correct)\n"
stdout:
  description: Output from flatpak binary
  returned: When a flatpak command has been executed
  type: str
  sample: "flathub\tFlathub\thttps://dl.flathub.org/repo/\t1\t\n"
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native


def add_remote(module, binary, name, flatpakrepo_url, method):
    """Add a new remote."""
    global result
    command = [binary, "remote-add", "--{0}".format(method), name, flatpakrepo_url]
    _flatpak_command(module, module.check_mode, command)
    result['changed'] = True


def remove_remote(module, binary, name, method):
    """Remove an existing remote."""
    global result
    command = [binary, "remote-delete", "--{0}".format(method), "--force", name]
    _flatpak_command(module, module.check_mode, command)
    result['changed'] = True


def remote_exists(module, binary, name, method):
    """Check if the remote exists."""
    command = [binary, "remote-list", "-d", "--{0}".format(method)]
    # The query operation for the remote needs to be run even in check mode
    output = _flatpak_command(module, False, command)
    for line in output.splitlines():
        listed_remote = line.split()
        if len(listed_remote) == 0:
            continue
        if listed_remote[0] == to_native(name):
            return True
    return False


def _flatpak_command(module, noop, command):
    global result
    result['command'] = ' '.join(command)
    if noop:
        result['rc'] = 0
        return ""

    result['rc'], result['stdout'], result['stderr'] = module.run_command(
        command, check_rc=True
    )
    return result['stdout']


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            flatpakrepo_url=dict(type='str'),
            method=dict(type='str', default='system',
                        choices=['user', 'system']),
            state=dict(type='str', default="present",
                       choices=['absent', 'present']),
            executable=dict(type='str', default="flatpak")
        ),
        # This module supports check mode
        supports_check_mode=True,
    )

    name = module.params['name']
    flatpakrepo_url = module.params['flatpakrepo_url']
    method = module.params['method']
    state = module.params['state']
    executable = module.params['executable']
    binary = module.get_bin_path(executable, None)

    if flatpakrepo_url is None:
        flatpakrepo_url = ''

    global result
    result = dict(
        changed=False
    )

    # If the binary was not found, fail the operation
    if not binary:
        module.fail_json(msg="Executable '%s' was not found on the system." % executable, **result)

    remote_already_exists = remote_exists(module, binary, to_bytes(name), method)

    if state == 'present' and not remote_already_exists:
        add_remote(module, binary, name, flatpakrepo_url, method)
    elif state == 'absent' and remote_already_exists:
        remove_remote(module, binary, name, method)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

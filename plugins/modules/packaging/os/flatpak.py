#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017 John Kwiatkoski (@JayKayy) <jkwiat40@gmail.com>
# Copyright: (c) 2018 Alexander Bethke (@oolongbrothers) <oolongbrothers@gmx.net>
# Copyright: (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: flatpak
short_description: Manage flatpaks
description:
- Allows users to add or remove flatpaks.
- See the M(community.general.flatpak_remote) module for managing flatpak remotes.
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
    type: path
    default: flatpak
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
    - The name of the flatpak to manage. To operate on several packages this
      can accept a list of packages.
    - When used with I(state=present), I(name) can be specified as a URL to a
      C(flatpakref) file or the unique reverse DNS name that identifies a flatpak.
    - Both C(https://) and C(http://) URLs are supported.
    - When supplying a reverse DNS name, you can use the I(remote) option to specify on what remote
      to look for the flatpak. An example for a reverse DNS name is C(org.gnome.gedit).
    - When used with I(state=absent), it is recommended to specify the name in the reverse DNS
      format.
    - When supplying a URL with I(state=absent), the module will try to match the
      installed flatpak based on the name of the flatpakref to remove it. However, there is no
      guarantee that the names of the flatpakref file and the reverse DNS name of the installed
      flatpak do match.
    type: list
    elements: str
    required: true
  no_dependencies:
    description:
    - If installing runtime dependencies should be omitted or not
    - This parameter is primarily implemented for integration testing this module.
      There might however be some use cases where you would want to have this, like when you are
      packaging your own flatpaks.
    type: bool
    default: false
    version_added: 3.2.0
  remote:
    description:
    - The flatpak remote (repository) to install the flatpak from.
    - By default, C(flathub) is assumed, but you do need to add the flathub flatpak_remote before
      you can use this.
    - See the M(community.general.flatpak_remote) module for managing flatpak remotes.
    type: str
    default: flathub
  state:
    description:
    - Indicates the desired package state.
    choices: [ absent, present ]
    type: str
    default: present
'''

EXAMPLES = r'''
- name: Install the spotify flatpak
  community.general.flatpak:
    name:  https://s3.amazonaws.com/alexlarsson/spotify-repo/spotify.flatpakref
    state: present

- name: Install the gedit flatpak package without dependencies (not recommended)
  community.general.flatpak:
    name: https://git.gnome.org/browse/gnome-apps-nightly/plain/gedit.flatpakref
    state: present
    no_dependencies: true

- name: Install the gedit package from flathub for current user
  community.general.flatpak:
    name: org.gnome.gedit
    state: present
    method: user

- name: Install the Gnome Calendar flatpak from the gnome remote system-wide
  community.general.flatpak:
    name: org.gnome.Calendar
    state: present
    remote: gnome

- name: Install multiple packages
  community.general.flatpak:
    name:
      - org.gimp.GIMP
      - org.inkscape.Inkscape
      - org.mozilla.firefox

- name: Remove the gedit flatpak
  community.general.flatpak:
    name: org.gnome.gedit
    state: absent

- name: Remove multiple packages
  community.general.flatpak:
    name:
      - org.gimp.GIMP
      - org.inkscape.Inkscape
      - org.mozilla.firefox
    state: absent
'''

RETURN = r'''
command:
  description: The exact flatpak command that was executed
  returned: When a flatpak command has been executed
  type: str
  sample: "/usr/bin/flatpak install --user --nontinteractive flathub org.gnome.Calculator"
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
  sample: "error: Error searching remote flathub: Can't find ref org.gnome.KDE"
stdout:
  description: Output from flatpak binary
  returned: When a flatpak command has been executed
  type: str
  sample: "org.gnome.Calendar/x86_64/stable\tcurrent\norg.gnome.gitg/x86_64/stable\tcurrent\n"
'''

from distutils.version import StrictVersion

from ansible.module_utils.six.moves.urllib.parse import urlparse
from ansible.module_utils.basic import AnsibleModule

OUTDATED_FLATPAK_VERSION_ERROR_MESSAGE = "Unknown option --columns=application"


def install_flat(module, binary, remote, names, method, no_dependencies):
    """Add new flatpaks."""
    global result
    uri_names = []
    id_names = []
    for name in names:
        if name.startswith('http://') or name.startswith('https://'):
            uri_names.append(name)
        else:
            id_names.append(name)
    base_command = [binary, "install", "--{0}".format(method)]
    flatpak_version = _flatpak_version(module, binary)
    if StrictVersion(flatpak_version) < StrictVersion('1.1.3'):
        base_command += ["-y"]
    else:
        base_command += ["--noninteractive"]
    if no_dependencies:
        base_command += ["--no-deps"]
    if uri_names:
        command = base_command + uri_names
        _flatpak_command(module, module.check_mode, command)
    if id_names:
        command = base_command + [remote] + id_names
        _flatpak_command(module, module.check_mode, command)
    result['changed'] = True


def uninstall_flat(module, binary, names, method):
    """Remove existing flatpaks."""
    global result
    installed_flat_names = [
        _match_installed_flat_name(module, binary, name, method)
        for name in names
    ]
    command = [binary, "uninstall"]
    flatpak_version = _flatpak_version(module, binary)
    if StrictVersion(flatpak_version) < StrictVersion('1.1.3'):
        command += ["-y"]
    else:
        command += ["--noninteractive"]
    command += ["--{0}".format(method)] + installed_flat_names
    _flatpak_command(module, module.check_mode, command)
    result['changed'] = True


def flatpak_exists(module, binary, names, method):
    """Check if the flatpaks are installed."""
    command = [binary, "list", "--{0}".format(method), "--app"]
    output = _flatpak_command(module, False, command)
    installed = []
    not_installed = []
    for name in names:
        parsed_name = _parse_flatpak_name(name).lower()
        if parsed_name in output.lower():
            installed.append(name)
        else:
            not_installed.append(name)
    return installed, not_installed


def _match_installed_flat_name(module, binary, name, method):
    # This is a difficult function, since if the user supplies a flatpakref url,
    # we have to rely on a naming convention:
    # The flatpakref file name needs to match the flatpak name
    global result
    parsed_name = _parse_flatpak_name(name)
    # Try running flatpak list with columns feature
    command = [binary, "list", "--{0}".format(method), "--app", "--columns=application"]
    _flatpak_command(module, False, command, ignore_failure=True)
    if result['rc'] != 0 and OUTDATED_FLATPAK_VERSION_ERROR_MESSAGE in result['stderr']:
        # Probably flatpak before 1.2
        matched_flatpak_name = \
            _match_flat_using_flatpak_column_feature(module, binary, parsed_name, method)
    else:
        # Probably flatpak >= 1.2
        matched_flatpak_name = \
            _match_flat_using_outdated_flatpak_format(module, binary, parsed_name, method)

    if matched_flatpak_name:
        return matched_flatpak_name
    else:
        result['msg'] = "Flatpak removal failed: Could not match any installed flatpaks to " +\
            "the name `{0}`. ".format(_parse_flatpak_name(name)) +\
            "If you used a URL, try using the reverse DNS name of the flatpak"
        module.fail_json(**result)


def _match_flat_using_outdated_flatpak_format(module, binary, parsed_name, method):
    global result
    command = [binary, "list", "--{0}".format(method), "--app", "--columns=application"]
    output = _flatpak_command(module, False, command)
    for row in output.split('\n'):
        if parsed_name.lower() == row.lower():
            return row


def _match_flat_using_flatpak_column_feature(module, binary, parsed_name, method):
    global result
    command = [binary, "list", "--{0}".format(method), "--app"]
    output = _flatpak_command(module, False, command)
    for row in output.split('\n'):
        if parsed_name.lower() in row.lower():
            return row.split()[0]


def _parse_flatpak_name(name):
    if name.startswith('http://') or name.startswith('https://'):
        file_name = urlparse(name).path.split('/')[-1]
        file_name_without_extension = file_name.split('.')[0:-1]
        common_name = ".".join(file_name_without_extension)
    else:
        common_name = name
    return common_name


def _flatpak_version(module, binary):
    global result
    command = [binary, "--version"]
    output = _flatpak_command(module, False, command)
    version_number = output.split()[1]
    return version_number


def _flatpak_command(module, noop, command, ignore_failure=False):
    global result
    result['command'] = ' '.join(command)
    if noop:
        result['rc'] = 0
        return ""

    result['rc'], result['stdout'], result['stderr'] = module.run_command(
        command, check_rc=not ignore_failure
    )
    return result['stdout']


def main():
    # This module supports check mode
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='list', elements='str', required=True),
            remote=dict(type='str', default='flathub'),
            method=dict(type='str', default='system',
                        choices=['user', 'system']),
            state=dict(type='str', default='present',
                       choices=['absent', 'present']),
            no_dependencies=dict(type='bool', default=False),
            executable=dict(type='path', default='flatpak')
        ),
        supports_check_mode=True,
    )

    name = module.params['name']
    state = module.params['state']
    remote = module.params['remote']
    no_dependencies = module.params['no_dependencies']
    method = module.params['method']
    executable = module.params['executable']
    binary = module.get_bin_path(executable, None)

    global result
    result = dict(
        changed=False
    )

    # If the binary was not found, fail the operation
    if not binary:
        module.fail_json(msg="Executable '%s' was not found on the system." % executable, **result)

    installed, not_installed = flatpak_exists(module, binary, name, method)
    if state == 'present' and not_installed:
        install_flat(module, binary, remote, not_installed, method, no_dependencies)
    elif state == 'absent' and installed:
        uninstall_flat(module, binary, installed, method)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

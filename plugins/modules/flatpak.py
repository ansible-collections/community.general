#!/usr/bin/python

# Copyright (c) 2017 John Kwiatkoski (@JayKayy) <jkwiat40@gmail.com>
# Copyright (c) 2018 Alexander Bethke (@oolongbrothers) <oolongbrothers@gmx.net>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
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
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: partial
    details:
      - If O(state=latest), the module always returns RV(ignore:changed=true).
  diff_mode:
    support: none
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
      - Defines if the C(flatpak) is supposed to be installed globally for the whole V(system) or only for the current V(user).
    type: str
    choices: [system, user]
    default: system
  name:
    description:
      - The name of the flatpak to manage. To operate on several packages this can accept a list of packages.
      - Should be specified as the unique reverse DNS name that identifies a flatpak (for example V(org.gnome.gedit)).
      - When supplying a reverse DNS name, you can use the O(remote) option to specify on what remote to look for the flatpak.
      - When used with O(state=present), O(name) can also be specified as a C(https://) or C(http://) URL to a C(flatpakref) file.
        However, it is recommended you use O(from_url) instead to get reliable idempotency.
        Passing URLs in O(name) will be deprecated in the future.
      - When used with O(state=absent) or O(state=latest), always specify the name in the reverse DNS format.
      - When supplying a URL with O(state=absent) or O(state=latest), the module tries to match the installed flatpak based
        on the name of the flatpakref to remove or update it. However, there is no guarantee that the names of the flatpakref
        file and the reverse DNS name of the installed flatpak do match.
    type: list
    elements: str
    required: true
  from_url:
    description:
      - A C(http://) or C(https://) URL pointing to a C(.flatpakref) file to install from.
      - When this option is set, O(name) must contain exactly one entry specifying the reverse DNS application ID of the
        flatpak (for example V(com.onepassword.OnePassword)). This is used to check whether the flatpak is already installed.
      - O(name) and O(from_url) cannot both contain URLs.
      - This option is recommended instead of passing a URL in O(name); passing URLs in O(name) will be deprecated in the future.
    type: str
    version_added: "12.6.0"
  no_dependencies:
    description:
      - If installing runtime dependencies should be omitted or not.
      - This parameter is primarily implemented for integration testing this module. There might however be some use cases
        where you would want to have this, like when you are packaging your own flatpaks.
    type: bool
    default: false
    version_added: 3.2.0
  remote:
    description:
      - The flatpak remote (repository) to install the flatpak from.
      - By default, V(flathub) is assumed, but you do need to add the flathub flatpak_remote before you can use this.
      - See the M(community.general.flatpak_remote) module for managing flatpak remotes.
    type: str
    default: flathub
  state:
    description:
      - Indicates the desired package state.
      - The value V(latest) is supported since community.general 8.6.0.
    choices: [absent, present, latest]
    type: str
    default: present
"""

EXAMPLES = r"""
- name: Install the spotify flatpak
  community.general.flatpak:
    name: com.spotify.Client
    from_url: https://s3.amazonaws.com/alexlarsson/spotify-repo/spotify.flatpakref
    state: present

- name: Install the gedit flatpak package without dependencies (not recommended)
  community.general.flatpak:
    name: org.gnome.gedit
    from_url: https://git.gnome.org/browse/gnome-apps-nightly/plain/gedit.flatpakref
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

- name: Install GIMP using custom flatpak binary path
  community.general.flatpak:
    name: org.gimp.GIMP
    state: present
    executable: /usr/local/bin/flatpak-dev

- name: Install multiple packages
  community.general.flatpak:
    name:
      - org.gimp.GIMP
      - org.inkscape.Inkscape
      - org.mozilla.firefox

- name: Update the spotify flatpak
  community.general.flatpak:
    name: com.spotify.Client
    from_url: https://s3.amazonaws.com/alexlarsson/spotify-repo/spotify.flatpakref
    state: latest

- name: Update the gedit flatpak package without dependencies (not recommended)
  community.general.flatpak:
    name: org.gnome.gedit
    from_url: https://git.gnome.org/browse/gnome-apps-nightly/plain/gedit.flatpakref
    state: latest
    no_dependencies: true

- name: Update the gedit package from flathub for current user
  community.general.flatpak:
    name: org.gnome.gedit
    state: latest
    method: user

- name: Update the Gnome Calendar flatpak from the gnome remote system-wide
  community.general.flatpak:
    name: org.gnome.Calendar
    state: latest
    remote: gnome

- name: Update multiple packages
  community.general.flatpak:
    name:
      - org.gimp.GIMP
      - org.inkscape.Inkscape
      - org.mozilla.firefox
    state: latest

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
"""

RETURN = r"""
command:
  description: The exact flatpak command that was executed.
  returned: When a flatpak command has been executed
  type: str
  sample: "/usr/bin/flatpak install --user --nontinteractive flathub org.gnome.Calculator"
"""

from re import match
from urllib.parse import urlparse

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._version import LooseVersion

OUTDATED_FLATPAK_VERSION_ERROR_MESSAGE = "Unknown option --columns=application"


def install_flat(module, binary, remote, names, method, no_dependencies, from_url=None):
    """Add new flatpaks."""
    global result  # pylint: disable=global-variable-not-assigned
    uri_names = []
    id_names = []
    for name in names:
        if name.startswith("http://") or name.startswith("https://"):
            uri_names.append(name)
        else:
            id_names.append(name)
    base_command = [binary, "install", f"--{method}"]
    flatpak_version = _flatpak_version(module, binary)
    if LooseVersion(flatpak_version) < LooseVersion("1.1.3"):
        base_command += ["-y"]
    else:
        base_command += ["--noninteractive"]
    if no_dependencies:
        base_command += ["--no-deps"]
    if from_url:
        command = base_command + ["--from", from_url]
        _flatpak_command(module, module.check_mode, command)
    else:
        if uri_names:
            command = base_command + uri_names
            _flatpak_command(module, module.check_mode, command)
        if id_names:
            command = base_command + [remote] + id_names
            _flatpak_command(module, module.check_mode, command)
    result["changed"] = True


def update_flat(module, binary, names, method, no_dependencies):
    """Update existing flatpaks."""
    global result  # pylint: disable=global-variable-not-assigned
    installed_flat_names = [_match_installed_flat_name(module, binary, name, method) for name in names]
    command = [binary, "update", f"--{method}"]
    flatpak_version = _flatpak_version(module, binary)
    if LooseVersion(flatpak_version) < LooseVersion("1.1.3"):
        command += ["-y"]
    else:
        command += ["--noninteractive"]
    if no_dependencies:
        command += ["--no-deps"]
    command += installed_flat_names
    stdout = _flatpak_command(module, module.check_mode, command)
    result["changed"] = (
        True if module.check_mode else (stdout.find("Nothing to do.") == -1 and stdout.find("Nothing to update.") == -1)
    )


def uninstall_flat(module, binary, names, method):
    """Remove existing flatpaks."""
    global result  # pylint: disable=global-variable-not-assigned
    installed_flat_names = [_match_installed_flat_name(module, binary, name, method) for name in names]
    command = [binary, "uninstall"]
    flatpak_version = _flatpak_version(module, binary)
    if LooseVersion(flatpak_version) < LooseVersion("1.1.3"):
        command += ["-y"]
    else:
        command += ["--noninteractive"]
    command += [f"--{method}"] + installed_flat_names
    _flatpak_command(module, module.check_mode, command)
    result["changed"] = True


def flatpak_exists(module, binary, names, method):
    """Check if the flatpaks are installed."""
    command = [binary, "list", f"--{method}"]
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
    global result  # pylint: disable=global-variable-not-assigned
    parsed_name = _parse_flatpak_name(name)
    # Try running flatpak list with columns feature
    command = [binary, "list", f"--{method}", "--columns=application"]
    _flatpak_command(module, False, command, ignore_failure=True)
    if result["rc"] != 0 and OUTDATED_FLATPAK_VERSION_ERROR_MESSAGE in result["stderr"]:
        # Probably flatpak before 1.2
        matched_flatpak_name = _match_flat_using_flatpak_column_feature(module, binary, parsed_name, method)
    else:
        # Probably flatpak >= 1.2
        matched_flatpak_name = _match_flat_using_outdated_flatpak_format(module, binary, parsed_name, method)

    if matched_flatpak_name:
        return matched_flatpak_name
    else:
        result["msg"] = (
            "Flatpak removal failed: Could not match any installed flatpaks to "
            f"the name `{_parse_flatpak_name(name)}`. "
            "If you used a URL, try using the reverse DNS name of the flatpak"
        )
        module.fail_json(**result)


def _match_flat_using_outdated_flatpak_format(module, binary, parsed_name, method):
    global result  # pylint: disable=global-variable-not-assigned
    command = [binary, "list", f"--{method}", "--columns=application"]
    output = _flatpak_command(module, False, command)
    for row in output.split("\n"):
        if parsed_name.lower() == row.lower():
            return row


def _match_flat_using_flatpak_column_feature(module, binary, parsed_name, method):
    global result  # pylint: disable=global-variable-not-assigned
    command = [binary, "list", f"--{method}"]
    output = _flatpak_command(module, False, command)
    for row in output.split("\n"):
        if parsed_name.lower() in row.lower():
            return row.split()[0]


def _is_flatpak_id(part):
    # For guidelines on application IDs, refer to the following resources:
    # Flatpak:
    # https://docs.flatpak.org/en/latest/conventions.html#application-ids
    # Flathub:
    # https://docs.flathub.org/docs/for-app-authors/requirements#application-id
    return match(r"^[a-z]{2,}(\.\w+)+\.[\w-]+$", part)


def _parse_flatpak_name(name):
    if name.startswith("http://") or name.startswith("https://"):
        file_name = urlparse(name).path.split("/")[-1]
        file_name_without_extension = file_name.split(".")[0:-1]
        common_name = ".".join(file_name_without_extension)
    else:
        parts = name.split("/")
        for part in parts:
            if _is_flatpak_id(part):
                common_name = part
                break
        else:
            common_name = name
    return common_name


def _flatpak_version(module, binary):
    global result  # pylint: disable=global-variable-not-assigned
    command = [binary, "--version"]
    output = _flatpak_command(module, False, command)
    version_number = output.split()[1]
    return version_number


def _flatpak_command(module, noop, command, ignore_failure=False):
    global result  # pylint: disable=global-variable-not-assigned
    result["command"] = " ".join(command)
    if noop:
        result["rc"] = 0
        return ""

    result["rc"], result["stdout"], result["stderr"] = module.run_command(command, check_rc=not ignore_failure)
    return result["stdout"]


def main():
    # This module supports check mode
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="list", elements="str", required=True),
            from_url=dict(type="str"),
            remote=dict(type="str", default="flathub"),
            method=dict(type="str", default="system", choices=["user", "system"]),
            state=dict(type="str", default="present", choices=["absent", "present", "latest"]),
            no_dependencies=dict(type="bool", default=False),
            executable=dict(type="path", default="flatpak"),
        ),
        supports_check_mode=True,
    )

    name = module.params["name"]
    from_url = module.params["from_url"]
    state = module.params["state"]
    remote = module.params["remote"]
    no_dependencies = module.params["no_dependencies"]
    method = module.params["method"]
    executable = module.params["executable"]
    binary = module.get_bin_path(executable, None)

    global result
    result = dict(changed=False)

    # If the binary was not found, fail the operation
    if not binary:
        module.fail_json(msg=f"Executable '{executable}' was not found on the system.", **result)

    url_names = [n for n in name if n.startswith("http://") or n.startswith("https://")]
    if from_url is not None:
        if not (from_url.startswith("http://") or from_url.startswith("https://")):
            module.fail_json(msg="The 'from_url' parameter must be an http:// or https:// URL.", **result)
        if url_names:
            module.fail_json(msg="The 'name' and 'from_url' parameters cannot both contain URLs.", **result)
        if len(name) != 1:
            module.fail_json(msg="When 'from_url' is used, 'name' must contain exactly one entry.", **result)
    module.run_command_environ_update = dict(LANGUAGE="C", LC_ALL="C")

    installed, not_installed = flatpak_exists(module, binary, name, method)
    if state == "absent" and installed:
        uninstall_flat(module, binary, installed, method)
    else:
        if state == "latest" and installed:
            update_flat(module, binary, installed, method, no_dependencies)
        if state in ("present", "latest") and not_installed:
            install_flat(module, binary, remote, not_installed, method, no_dependencies, from_url)

    module.exit_json(**result)


if __name__ == "__main__":
    main()

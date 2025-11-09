#!/usr/bin/python

# Copyright (c) 2013, Johan Wiren <johan.wiren.se@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: gem
short_description: Manage Ruby gems
description:
  - Manage installation and uninstallation of Ruby gems.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    type: str
    description:
      - The name of the gem to be managed.
    required: true
  state:
    type: str
    description:
      - The desired state of the gem. V(latest) ensures that the latest version is installed.
    choices: [present, absent, latest]
    default: present
  gem_source:
    type: path
    description:
      - The path to a local gem used as installation source.
  include_dependencies:
    description:
      - Whether to include dependencies or not.
    type: bool
    default: true
  repository:
    type: str
    description:
      - The repository from which the gem is installed.
    aliases: [source]
  user_install:
    description:
      - Install gem in user's local gems cache or for all users.
    type: bool
    default: true
  executable:
    type: path
    description:
      - Override the path to the gem executable.
  install_dir:
    type: path
    description:
      - Install the gems into a specific directory. These gems are independent from the global installed ones. Specifying
        this requires user_install to be false.
  bindir:
    type: path
    description:
      - Install executables into a specific directory.
    version_added: 3.3.0
  norc:
    type: bool
    default: true
    description:
      - Avoid loading any C(.gemrc) file. Ignored for RubyGems prior to 2.5.2.
      - The default changed from V(false) to V(true) in community.general 6.0.0.
    version_added: 3.3.0
  env_shebang:
    description:
      - Rewrite the shebang line on installed scripts to use /usr/bin/env.
    default: false
    type: bool
  version:
    type: str
    description:
      - Version of the gem to be installed/removed.
  pre_release:
    description:
      - Allow installation of pre-release versions of the gem.
    default: false
    type: bool
  include_doc:
    description:
      - Install with or without docs.
    default: false
    type: bool
  build_flags:
    type: str
    description:
      - Allow adding build flags for gem compilation.
  force:
    description:
      - Force gem to (un-)install, bypassing dependency checks.
    default: false
    type: bool
author:
  - "Ansible Core Team"
  - "Johan Wiren (@johanwiren)"
"""

EXAMPLES = r"""
- name: Install version 1.0 of vagrant
  community.general.gem:
    name: vagrant
    version: 1.0
    state: present

- name: Install latest available version of rake
  community.general.gem:
    name: rake
    state: latest

- name: Install rake version 1.0 from a local gem on disk
  community.general.gem:
    name: rake
    gem_source: /path/to/gems/rake-1.0.gem
    state: present
"""

import re

from ansible.module_utils.basic import AnsibleModule


def get_rubygems_path(module):
    if module.params["executable"]:
        result = module.params["executable"].split(" ")
    else:
        result = [module.get_bin_path("gem", True)]
    return result


def get_rubygems_version(module):
    if hasattr(get_rubygems_version, "ver"):
        return get_rubygems_version.ver

    cmd = get_rubygems_path(module) + ["--version"]
    (rc, out, err) = module.run_command(cmd, check_rc=True)

    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", out)
    if not match:
        return None

    ver = tuple(int(x) for x in match.groups())
    get_rubygems_version.ver = ver

    return ver


def get_rubygems_environ(module):
    if module.params["install_dir"]:
        return {"GEM_HOME": module.params["install_dir"]}
    return None


def get_installed_versions(module, remote=False):
    cmd = get_rubygems_path(module)
    cmd.append("query")
    cmd.extend(common_opts(module))
    if remote:
        cmd.append("--remote")
        if module.params["repository"]:
            cmd.extend(["--source", module.params["repository"]])
    cmd.append("-n")
    cmd.append(f"^{module.params['name']}$")

    environ = get_rubygems_environ(module)
    (rc, out, err) = module.run_command(cmd, environ_update=environ, check_rc=True)
    installed_versions = []
    for line in out.splitlines():
        match = re.match(r"\S+\s+\((?:default: )?(.+)\)", line)
        if match:
            versions = match.group(1)
            for version in versions.split(", "):
                installed_versions.append(version.split()[0])
    return installed_versions


def exists(module):
    if module.params["state"] == "latest":
        remoteversions = get_installed_versions(module, remote=True)
        if remoteversions:
            module.params["version"] = remoteversions[0]
    installed_versions = get_installed_versions(module)
    if module.params["version"]:
        if module.params["version"] in installed_versions:
            return True
    else:
        if installed_versions:
            return True
    return False


def common_opts(module):
    opts = []
    ver = get_rubygems_version(module)
    if module.params["norc"] and ver and ver >= (2, 5, 2):
        opts.append("--norc")
    return opts


def uninstall(module):
    if module.check_mode:
        return
    cmd = get_rubygems_path(module)
    environ = get_rubygems_environ(module)
    cmd.append("uninstall")
    cmd.extend(common_opts(module))
    if module.params["install_dir"]:
        cmd.extend(["--install-dir", module.params["install_dir"]])

    if module.params["bindir"]:
        cmd.extend(["--bindir", module.params["bindir"]])

    if module.params["version"]:
        cmd.extend(["--version", module.params["version"]])
    else:
        cmd.append("--all")
    cmd.append("--executable")
    if module.params["force"]:
        cmd.append("--force")
    cmd.append(module.params["name"])
    return module.run_command(cmd, environ_update=environ, check_rc=True)


def install(module):
    if module.check_mode:
        return

    ver = get_rubygems_version(module)

    cmd = get_rubygems_path(module)
    cmd.append("install")
    cmd.extend(common_opts(module))
    if module.params["version"]:
        cmd.extend(["--version", module.params["version"]])
    if module.params["repository"]:
        cmd.extend(["--source", module.params["repository"]])
    if not module.params["include_dependencies"]:
        cmd.append("--ignore-dependencies")
    else:
        if ver and ver < (2, 0, 0):
            cmd.append("--include-dependencies")
    if module.params["user_install"]:
        cmd.append("--user-install")
    else:
        cmd.append("--no-user-install")
    if module.params["install_dir"]:
        cmd.extend(["--install-dir", module.params["install_dir"]])
    if module.params["bindir"]:
        cmd.extend(["--bindir", module.params["bindir"]])
    if module.params["pre_release"]:
        cmd.append("--pre")
    if not module.params["include_doc"]:
        if ver and ver < (2, 0, 0):
            cmd.append("--no-rdoc")
            cmd.append("--no-ri")
        else:
            cmd.append("--no-document")
    if module.params["env_shebang"]:
        cmd.append("--env-shebang")
    cmd.append(module.params["gem_source"])
    if module.params["build_flags"]:
        cmd.extend(["--", module.params["build_flags"]])
    if module.params["force"]:
        cmd.append("--force")
    module.run_command(cmd, check_rc=True)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            executable=dict(type="path"),
            gem_source=dict(type="path"),
            include_dependencies=dict(default=True, type="bool"),
            name=dict(required=True, type="str"),
            repository=dict(aliases=["source"], type="str"),
            state=dict(default="present", choices=["present", "absent", "latest"], type="str"),
            user_install=dict(default=True, type="bool"),
            install_dir=dict(type="path"),
            bindir=dict(type="path"),
            norc=dict(type="bool", default=True),
            pre_release=dict(default=False, type="bool"),
            include_doc=dict(default=False, type="bool"),
            env_shebang=dict(default=False, type="bool"),
            version=dict(type="str"),
            build_flags=dict(type="str"),
            force=dict(default=False, type="bool"),
        ),
        supports_check_mode=True,
        mutually_exclusive=[["gem_source", "repository"], ["gem_source", "version"]],
    )

    if module.params["version"] and module.params["state"] == "latest":
        module.fail_json(msg="Cannot specify version when state=latest")
    if module.params["gem_source"] and module.params["state"] == "latest":
        module.fail_json(msg="Cannot maintain state=latest when installing from local source")
    if module.params["user_install"] and module.params["install_dir"]:
        module.fail_json(msg="install_dir requires user_install=false")

    if not module.params["gem_source"]:
        module.params["gem_source"] = module.params["name"]

    changed = False

    if module.params["state"] in ["present", "latest"]:
        if not exists(module):
            install(module)
            changed = True
    elif module.params["state"] == "absent":
        if exists(module):
            command_output = uninstall(module)
            if command_output is not None and exists(module):
                rc, out, err = command_output
                module.fail_json(
                    msg=(
                        f"Failed to uninstall gem '{module.params['name']}': it is still present after 'gem uninstall'. "
                        "This usually happens with default or system gems provided by the OS, "
                        "which cannot be removed with the gem command."
                    ),
                    rc=rc,
                    stdout=out,
                    stderr=err,
                )
            else:
                changed = True
    result = {}
    result["name"] = module.params["name"]
    result["state"] = module.params["state"]
    if module.params["version"]:
        result["version"] = module.params["version"]
    result["changed"] = changed

    module.exit_json(**result)


if __name__ == "__main__":
    main()

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
  - community.general._attributes
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
  override_platform_install_dir:
    description:
      - Resolve the user gem installation directory via C(gem environment) and pass it explicitly
        as C(--install-dir) to both C(gem install) and C(gem uninstall), instead of using C(--user-install).
      - This is needed on distributions (such as Fedora) where a platform-specific C(operating_system.rb)
        injects C(--install-dir) as a default for all gem commands, which conflicts with C(--user-install)
        and causes C(gem uninstall) to search the wrong directory.
      - Cannot be combined with O(user_install=false) or O(install_dir).
    default: false
    type: bool
    version_added: 13.0.0
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

import os
import re

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils import _cmd_runner_fmt as fmt
from ansible_collections.community.general.plugins.module_utils._cmd_runner import CmdRunner

RE_VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)")
RE_INSTALLED = re.compile(r"\S+\s+\((?:default: )?(.+)\)")


def get_rubygems_path(module: AnsibleModule) -> list[str]:
    if module.params["executable"]:
        return module.params["executable"].split()
    return [module.get_bin_path("gem", True)]


def get_user_install_dir(module: AnsibleModule) -> str | None:
    cmd = get_rubygems_path(module)
    rc, out, err = module.run_command(cmd + ["environment"], check_rc=True)
    for line in out.splitlines():
        match = re.search(r"USER INSTALLATION DIRECTORY:\s*(.+)", line)
        if match:
            return match.group(1).strip()
    return None


def get_rubygems_version(module: AnsibleModule) -> tuple[int, ...] | None:
    cmd = get_rubygems_path(module) + ["--version"]
    rc, out, err = module.run_command(cmd, check_rc=True)
    match = RE_VERSION.match(out)
    if not match:
        return None
    return tuple(int(x) for x in match.groups())


def make_runner(module: AnsibleModule, ver: tuple[int, ...] | None) -> CmdRunner:
    command = get_rubygems_path(module)

    environ_update = {}
    if module.params["install_dir"]:
        environ_update["GEM_HOME"] = module.params["install_dir"]

    if ver and ver < (2, 0, 0):
        include_dependencies_fmt = fmt.as_bool("--include-dependencies", "--ignore-dependencies")
        include_doc_fmt = fmt.as_bool_not(["--no-rdoc", "--no-ri"])
    else:
        include_dependencies_fmt = fmt.as_bool_not("--ignore-dependencies")
        include_doc_fmt = fmt.as_bool_not("--no-document")

    norc_fmt = fmt.as_bool("--norc") if (ver and ver >= (2, 5, 2)) else fmt.as_bool([])

    return CmdRunner(
        module,
        command=command,
        environ_update=environ_update,
        check_rc=True,
        arg_formats=dict(
            _list_subcmd=fmt.as_fixed("list"),
            _install_subcmd=fmt.as_fixed("install"),
            _uninstall_subcmd=fmt.as_fixed("uninstall"),
            norc=norc_fmt,
            _remote_flag=fmt.as_fixed("--remote"),
            repository=fmt.as_opt_val("--source"),
            _name_pattern=fmt.as_func(lambda v: [f"^{v}$"]),
            version=fmt.as_opt_val("--version"),
            include_dependencies=include_dependencies_fmt,
            user_install=fmt.as_bool("--user-install", "--no-user-install"),
            install_dir=fmt.as_opt_val("--install-dir"),
            bindir=fmt.as_opt_val("--bindir"),
            pre_release=fmt.as_bool("--pre"),
            include_doc=include_doc_fmt,
            env_shebang=fmt.as_bool("--env-shebang"),
            gem_source=fmt.as_list(),
            build_flags=fmt.as_opt_val("--"),
            force=fmt.as_bool("--force"),
            _uninstall_version=fmt.as_func(lambda v: ["--version", v] if v else ["--all"], ignore_none=False),
            _executable_flag=fmt.as_fixed("--executable"),
            name=fmt.as_list(),
        ),
    )


def get_installed_versions(runner: CmdRunner, remote: bool = False) -> list[str]:
    name = runner.module.params["name"]
    if remote:
        args_order = ["_list_subcmd", "norc", "_remote_flag", "repository", "_name_pattern"]
    else:
        args_order = ["_list_subcmd", "norc", "_name_pattern"]
    with runner(args_order) as ctx:
        rc, out, err = ctx.run(_name_pattern=name)
    installed_versions = []
    for line in out.splitlines():
        match = RE_INSTALLED.match(line)
        if match:
            versions = match.group(1)
            for version in versions.split(", "):
                installed_versions.append(version.split()[0])
    return installed_versions


def exists(runner: CmdRunner) -> bool:
    module = runner.module
    if module.params["state"] == "latest":
        remoteversions = get_installed_versions(runner, remote=True)
        if remoteversions:
            module.params["version"] = remoteversions[0]
    installed_versions = get_installed_versions(runner)
    if module.params["version"]:
        return module.params["version"] in installed_versions
    return bool(installed_versions)


def install(runner: CmdRunner, user_dir: str | None = None) -> None:
    args_order = [
        "_install_subcmd",
        "norc",
        "version",
        "repository",
        "include_dependencies",
        "user_install",
        "install_dir",
        "bindir",
        "pre_release",
        "include_doc",
        "env_shebang",
        "gem_source",
        "build_flags",
        "force",
    ]
    with runner(args_order, check_mode_skip=True) as ctx:
        if user_dir:
            bindir = runner.module.params["bindir"] or os.path.join(user_dir, "bin")
            ctx.run(user_install=False, install_dir=user_dir, bindir=bindir)
        else:
            ctx.run()


def uninstall(runner: CmdRunner, user_dir: str | None = None) -> tuple[int, str, str] | None:
    args_order = [
        "_uninstall_subcmd",
        "norc",
        "install_dir",
        "bindir",
        "_uninstall_version",
        "_executable_flag",
        "force",
        "name",
    ]
    with runner(args_order, check_mode_skip=True) as ctx:
        kwargs = {"_uninstall_version": runner.module.params["version"]}
        if user_dir:
            kwargs["install_dir"] = user_dir
        return ctx.run(**kwargs)


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
            override_platform_install_dir=dict(default=False, type="bool"),
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
    if module.params["override_platform_install_dir"]:
        if not module.params["user_install"]:
            module.fail_json(msg="override_platform_install_dir requires user_install=true")
        if module.params["install_dir"]:
            module.fail_json(msg="override_platform_install_dir cannot be combined with install_dir")

    if not module.params["gem_source"]:
        module.params["gem_source"] = module.params["name"]

    ver = get_rubygems_version(module)

    user_dir = None
    if module.params["override_platform_install_dir"]:
        user_dir = get_user_install_dir(module)

    runner = make_runner(module, ver)

    changed = False

    if module.params["state"] in ["present", "latest"]:
        if not exists(runner):
            install(runner, user_dir)
            changed = True
    elif module.params["state"] == "absent":
        if exists(runner):
            command_output = uninstall(runner, user_dir)
            if command_output is not None and exists(runner):
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

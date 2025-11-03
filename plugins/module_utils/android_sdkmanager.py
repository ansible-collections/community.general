# Copyright (c) 2024, Stanislav Shamilov <shamilovstas@protonmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


import re

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt

__state_map = {"present": "--install", "absent": "--uninstall"}

# sdkmanager --help 2>&1 | grep -A 2 -- --channel
__channel_map = {"stable": 0, "beta": 1, "dev": 2, "canary": 3}


def __map_channel(channel_name):
    if channel_name not in __channel_map:
        raise ValueError(f"Unknown channel name '{channel_name}'")
    return __channel_map[channel_name]


def sdkmanager_runner(module, **kwargs):
    return CmdRunner(
        module,
        command="sdkmanager",
        arg_formats=dict(
            state=cmd_runner_fmt.as_map(__state_map),
            name=cmd_runner_fmt.as_list(),
            installed=cmd_runner_fmt.as_fixed("--list_installed"),
            list=cmd_runner_fmt.as_fixed("--list"),
            newer=cmd_runner_fmt.as_fixed("--newer"),
            sdk_root=cmd_runner_fmt.as_opt_eq_val("--sdk_root"),
            channel=cmd_runner_fmt.as_func(lambda x: [f"--channel={__map_channel(x)}"]),
        ),
        force_lang="C.UTF-8",  # Without this, sdkmanager binary crashes
        **kwargs,
    )


class Package:
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __ne__(self, other):
        if not isinstance(other, Package):
            return True
        return self.name != other.name

    def __eq__(self, other):
        if not isinstance(other, Package):
            return False

        return self.name == other.name


class SdkManagerException(Exception):
    pass


class AndroidSdkManager:
    _RE_INSTALLED_PACKAGES_HEADER = re.compile(r"^Installed packages:$")
    _RE_UPDATABLE_PACKAGES_HEADER = re.compile(r"^Available Updates:$")

    # Example: '  platform-tools     | 27.0.0  | Android SDK Platform-Tools 27 | platform-tools  '
    _RE_INSTALLED_PACKAGE = re.compile(r"^\s*(?P<name>\S+)\s*\|\s*[0-9][^|]*\b\s*\|\s*.+\s*\|\s*(\S+)\s*$")

    # Example: '   platform-tools | 27.0.0    | 35.0.2'
    _RE_UPDATABLE_PACKAGE = re.compile(r"^\s*(?P<name>\S+)\s*\|\s*[0-9][^|]*\b\s*\|\s*[0-9].*\b\s*$")

    _RE_UNKNOWN_PACKAGE = re.compile(r"^Warning: Failed to find package \'(?P<package>\S+)\'\s*$")
    _RE_ACCEPT_LICENSE = re.compile(
        r"^The following packages can not be installed since their licenses or those of "
        r"the packages they depend on were not accepted"
    )

    def __init__(self, module):
        self.runner = sdkmanager_runner(module)

    def get_installed_packages(self):
        with self.runner("installed sdk_root channel") as ctx:
            rc, stdout, stderr = ctx.run()
            return self._parse_packages(stdout, self._RE_INSTALLED_PACKAGES_HEADER, self._RE_INSTALLED_PACKAGE)

    def get_updatable_packages(self):
        with self.runner("list newer sdk_root channel") as ctx:
            rc, stdout, stderr = ctx.run()
            return self._parse_packages(stdout, self._RE_UPDATABLE_PACKAGES_HEADER, self._RE_UPDATABLE_PACKAGE)

    def apply_packages_changes(self, packages, accept_licenses=False):
        """Install or delete packages, depending on the `module.vars.state` parameter"""
        if len(packages) == 0:
            return 0, "", ""

        if accept_licenses:
            license_prompt_answer = "y"
        else:
            license_prompt_answer = "N"
        for package in packages:
            with self.runner("state name sdk_root channel", data=license_prompt_answer) as ctx:
                rc, stdout, stderr = ctx.run(name=package.name)

                for line in stdout.splitlines():
                    if self._RE_ACCEPT_LICENSE.match(line):
                        raise SdkManagerException("Licenses for some packages were not accepted")

                if rc != 0:
                    self._try_parse_stderr(stderr)
                    return rc, stdout, stderr
        return 0, "", ""

    def _try_parse_stderr(self, stderr):
        data = stderr.splitlines()
        for line in data:
            unknown_package_regex = self._RE_UNKNOWN_PACKAGE.match(line)
            if unknown_package_regex:
                package = unknown_package_regex.group("package")
                raise SdkManagerException(f"Unknown package {package}")

    @staticmethod
    def _parse_packages(stdout, header_regexp, row_regexp):
        data = stdout.splitlines()

        section_found = False
        packages = set()

        for line in data:
            if not section_found:
                section_found = header_regexp.match(line)
                continue
            else:
                p = row_regexp.match(line)
                if p:
                    packages.add(Package(p.group("name")))
        return packages

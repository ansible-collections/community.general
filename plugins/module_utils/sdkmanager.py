# -*- coding: utf-8 -*-

# Copyright (c) 2024, Stanislav Shamilov <shamilovstas@protonmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.community.general.plugins.module_utils import cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner

__state_map = {
    "present": "--install",
    "absent": "--uninstall"
}

# sdkmanager --help 2>&1 | grep -A 2 -- --channel
__channel_map = {
    "stable": 0,
    "beta": 1,
    "dev": 2,
    "canary": 3
}


def __map_channel(channel_name):
    if channel_name not in __channel_map:
        raise ValueError("Unknown channel name '%s'" % channel_name)
    return __channel_map[channel_name]


def sdkmanager_runner(module, **kwargs):
    return CmdRunner(
        module,
        command='sdkmanager',
        arg_formats=dict(
            state=cmd_runner_fmt.as_map(__state_map),
            name=cmd_runner_fmt.as_list(),
            installed=cmd_runner_fmt.as_fixed("--list_installed"),
            list=cmd_runner_fmt.as_fixed('--list'),
            newer=cmd_runner_fmt.as_fixed("--newer"),
            sdk_root=cmd_runner_fmt.as_opt_eq_val("--sdk_root", ignore_none=True),
            channel=cmd_runner_fmt.as_func(lambda x: ["{0}={1}".format("--channel", __map_channel(x))])
        ),
        force_lang="C.UTF-8",  # Without this, sdkmanager binary crashes
        **kwargs
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


class AndroidSdkManager(object):
    _RE_INSTALLED_PACKAGES_HEADER = re.compile(r'^Installed packages:$')
    _RE_UPDATABLE_PACKAGES_HEADER = re.compile(r'^Available Updates:$')

    # Example: '  platform-tools     | 27.0.0  | Android SDK Platform-Tools 27 | platform-tools  '
    _RE_INSTALLED_PACKAGE = (
        re.compile(r'^\s*(?P<name>\S+)\s*\|\s*\S+\s*\|\s*.+\s*\|\s*(\S+)\s*$')
    )

    # Example: '   platform-tools | 27.0.0    | 35.0.2'
    _RE_UPDATABLE_PACKAGE = re.compile(r'^\s*(?P<name>\S+)\s*\|\s*\S+\s*\|\s*\S+\s*$')

    _RE_UNKNOWN_PACKAGE = re.compile(r'^Warning: Failed to find package \'(?P<package>\S+)\'\s*$')
    _RE_ACCEPT_LICENSE = re.compile(r'^The following packages can not be installed since their licenses or those of '
                                    r'the packages they depend on were not accepted')

    def __init__(self, runner):
        self.runner = runner

    def get_installed_packages(self):
        with self.runner('installed sdk_root channel') as ctx:
            rc, stdout, stderr = ctx.run()
            return self._parse_packages(stdout, self._RE_INSTALLED_PACKAGES_HEADER, self._RE_INSTALLED_PACKAGE)

    def get_updatable_packages(self):
        with self.runner('list newer sdk_root channel') as ctx:
            rc, stdout, stderr = ctx.run()
            return self._parse_packages(stdout, self._RE_UPDATABLE_PACKAGES_HEADER, self._RE_UPDATABLE_PACKAGE)

    def apply_packages_changes(self, packages):
        """ Install or delete packages, depending on the `module.vars.state` parameter """
        if len(packages) == 0:
            return 0, '', ''
        command_arg = [x.name for x in packages]

        data = 'N'  # Answer 'No' in case sdkmanager wants us to accept license
        with self.runner('state name sdk_root channel', data=data) as ctx:
            rc, stdout, stderr = ctx.run(name=command_arg, data=data)

            data = stdout.split('\n')

            for line in data:
                if self._RE_ACCEPT_LICENSE.match(line):
                    raise SdkManagerException("Licenses for some packages were not accepted")

            if rc != 0:
                self._try_parse_stderr(stderr)
            return rc, stdout, stderr

    def _try_parse_stderr(self, stderr):
        data = stderr.split('\n')
        for line in data:
            unknown_package_regex = self._RE_UNKNOWN_PACKAGE.match(line)
            if unknown_package_regex:
                package = unknown_package_regex.group('package')
                raise SdkManagerException("Unknown package %s" % package)

    @staticmethod
    def _parse_packages(stdout, header_regexp, row_regexp):
        data = stdout.split('\n')

        updatable_section_found = False
        i = 0
        lines_count = len(data)
        packages = set()

        while i < lines_count:
            if not updatable_section_found:
                updatable_section_found = header_regexp.match(data[i])
                if updatable_section_found:
                    # Table has the following structure. Once header is found, 2 lines need to be skipped
                    #
                    # Available Updates:                                <--- we are here
                    #   ID             | Installed | Available
                    #   -------        | -------   | -------
                    #   platform-tools | 27.0.0    | 35.0.2             <--- skip to here
                    i += 3  # skip table header
                else:
                    i += 1  # just iterate next until we find the section's header
                continue
            else:
                p = row_regexp.match(data[i])
                if p:
                    packages.add(Package(p.group('name')))
                i += 1
        return packages

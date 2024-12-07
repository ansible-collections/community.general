from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.community.general.plugins.module_utils import cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner

_state_map = {
    "present": "--install",
    "absent": "--uninstall"
}

# sdkmanager --help 2>&1 | grep -A 2 -- --channel
_channel_map = {
    "stable": 0,
    "beta": 1,
    "dev": 2,
    "canary": 3
}


def map_channel(channel_name):
    if channel_name not in _channel_map:
        raise ValueError("Unknown channel name '%s'" % channel_name)
    return _channel_map[channel_name]


def sdkmanager_runner(module, **kwargs):
    return CmdRunner(
        module,
        command='sdkmanager',
        arg_formats=dict(
            state=cmd_runner_fmt.as_map(_state_map),
            name=cmd_runner_fmt.as_list(),
            update=cmd_runner_fmt.as_fixed("--update"),
            installed=cmd_runner_fmt.as_fixed("--list_installed"),
            list=cmd_runner_fmt.as_fixed('--list'),
            newer=cmd_runner_fmt.as_fixed("--newer"),
            sdk_root=cmd_runner_fmt.as_opt_eq_val("--sdk_root", ignore_none=True),
            channel=cmd_runner_fmt.as_func(lambda x: ["{0}={1}".format("--channel", map_channel(x))])
        ),
        force_lang="C.UTF-8",
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


class AndroidSdkManager(object):
    _RE_INSTALLED_PACKAGES_HEADER = re.compile(r'^Installed packages:$')
    _RE_UPDATABLE_PACKAGES_HEADER = re.compile(r'^Available Updates:$')

    # Example: '  platform-tools     | 27.0.0  | Android SDK Platform-Tools 27 | platform-tools  '
    _RE_INSTALLED_PACKAGE = (
        re.compile(r'^\s*(?P<name>\S+)\s*\|\s*\S+\s*\|\s*.+\s*\|\s*(\S+)\s*$')
    )

    # Example: '   platform-tools | 27.0.0    | 35.0.2'
    _RE_UPDATABLE_PACKAGE = re.compile(r'^\s*(?P<name>\S+)\s*\|\s*\S+\s*\|\s*\S+\s*$')

    def __init__(self, runner):
        self.runner = runner

    def get_installed_packages(self):
        with self.runner('installed sdk_root channel') as ctx:
            rc, stdout, stderr = ctx.run()

            data = stdout.split('\n')

            installed_section_found = False
            i = 0
            lines_count = len(data)
            packages = set()

            while i < lines_count:

                if not installed_section_found:
                    installed_section_found = self._RE_INSTALLED_PACKAGES_HEADER.match(data[i])
                    if installed_section_found:
                        i += 3
                    else:
                        i += 1
                    continue
                else:
                    p = self._RE_INSTALLED_PACKAGE.search(data[i])
                    if p:
                        package = Package(p.group('name'))
                        packages.add(package)
                i += 1
        return packages

    def get_updatable_packages(self):
        with self.runner('list newer sdk_root channel') as ctx:
            rc, stdout, stderr = ctx.run()
            data = stdout.split('\n')

            updatable_section_found = False
            i = 0
            lines_count = len(data)
            packages = set()

            while i < lines_count:
                if not updatable_section_found:
                    updatable_section_found = self._RE_UPDATABLE_PACKAGES_HEADER.match(data[i])
                    if updatable_section_found:
                        # Table has the following structure. Once it is found, 2 lines need to be skipped
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
                    p = self._RE_UPDATABLE_PACKAGE.match(data[i])
                    if p:
                        packages.add(Package(p.group('name')))
                    i += 1
        return packages

    def install_packages(self, packages):
        return self.apply_packages_changes(packages, 'present')

    def uninstall_packages(self, packages):
        return self.apply_packages_changes(packages, 'absent')

    def apply_packages_changes(self, packages, state):
        if len(packages) == 0:
            return 0, '', ''
        command_arg = [x.name for x in packages]
        with self.runner('state name sdk_root channel') as ctx:
            return ctx.run(name=command_arg, state=state)

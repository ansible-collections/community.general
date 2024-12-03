import re

from ansible_collections.community.general.plugins.module_utils import cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner

_state_map = {
    "present": "--install",
    "absent": "--uninstall"
}


def sdkmanager_runner(module, **kwargs):
    return CmdRunner(
        module,
        command='sdkmanager',
        arg_formats=dict(
            state=cmd_runner_fmt.as_map(_state_map),
            name=cmd_runner_fmt.as_list(),
            update=cmd_runner_fmt.as_fixed("--update"),
            installed=cmd_runner_fmt.as_fixed("--list_installed")
        ),
        **kwargs
    )


class Package:
    def __init__(self, name, version, description=''):
        self.name = name
        self.version = version
        self.description = description

    def __str__(self):
        return "%s;%s (%s)" % (self.name, self.version, self.description)

    def __hash__(self):
        return hash((self.name, self.version))

    def __ne__(self, other):
        if not isinstance(other, Package):
            return True
        return self.name != other.name or self.version != other

    def __eq__(self, other):
        if not isinstance(other, Package):
            return False

        return self.name == other.name and self.version == other.version

    def get_formatted(self):
        if self.version is None:
            return self.name
        else:
            return "%s;%s" % (self.name, self.version)


class AndroidSdkManager(object):
    _RE_INSTALLED_PACKAGES_HEADER = re.compile(r'^\s+Path\s+|\s+Version\s+|\s+Description\s+|\s+Location\s+$')
    _RE_INSTALLED_PACKAGES = (
        re.compile(r'^\s+(?P<name>\S+)\s+\|\s+(?P<version>\S+)\s+\|\s(?P<description>.+)\s\|\s+(\S+)$')
    )

    @staticmethod
    def package_split(package):
        parts = package.split(';', maxsplit=1)
        if len(parts) > 1:
            return parts
        return parts[0], None

    def __init__(self, runner):
        self.runner = runner

    def get_installed_packages(self):
        with self.runner('installed') as ctx:
            rc, stdout, stderr = ctx.run()

            packages = set()
            data = stdout.split('\n')

            lines_count = len(data)

            i = 0

            while i < lines_count:
                line = data[i]
                if self._RE_INSTALLED_PACKAGES_HEADER.match(line):
                    i += 1
                else:
                    p = self._RE_INSTALLED_PACKAGES.search(line)
                    if p:
                        name = AndroidSdkManager.package_split(p.group('name'))[0]
                        package = Package(name, p.group('version'), p.group('description'))
                        packages.add(package)
                i += 1
            return packages

    def install_packages(self, packages):
        self.apply_packages_changes(packages, 'present')

    def uninstall_packages(self, packages):
        self.apply_packages_changes(packages, 'absent')

    def apply_packages_changes(self, packages, state):
        if len(packages) == 0:
            return
        command_arg = [x.get_formatted() for x in packages]
        # ValueError: ['build-tools;34.0.0', 'build-tools;35.0.0']
        # raise ValueError(command_arg)
        with self.runner('state name') as ctx:
            ctx.run(name=command_arg, state=state)


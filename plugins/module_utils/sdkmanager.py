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
    _RE_INSTALLED_PACKAGES_HEADER = re.compile(r'^\s+Path\s+|\s+Version\s+|\s+Description\s+|\s+Location\s+$')
    _RE_INSTALLED_PACKAGES = (
        re.compile(r'^\s+(?P<name>\S+)\s+\|\s+(?P<version>\S+)\s+\|\s(?P<description>.+)\s\|\s+(\S+)$')
    )

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
                        package = Package(p.group('name'))
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
        command_arg = [x.name for x in packages]
        # ValueError: ['build-tools;34.0.0', 'build-tools;35.0.0']
        # raise ValueError(command_arg)
        with self.runner('state name') as ctx:
            ctx.run(name=command_arg, state=state)


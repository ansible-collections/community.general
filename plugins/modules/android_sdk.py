import re

from ansible_collections.community.general.plugins.module_utils.mh.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.sdkmanager import sdkmanager_runner


class AndroidSdk(StateModuleHelper):
    _RE_INSTALLED_PACKAGES_HEADER = re.compile(r'^\s+Path\s+|\s+Version\s+|\s+Description\s+|\s+Location\s+$')
    _RE_INSTALLED_PACKAGES = re.compile(r'^\s+(\S+)\s+\|\s+(\S+)\s+\|\s(.+)\s\|\s+(\S+)$')
    module = dict(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent', 'latest']),
            package=dict(type='list', elements='str', aliases=['pkg', 'name']),
            update=dict(type='bool', default=False)
        )
    )
    use_old_vardict = False
    output_params = ('installed')

    def _get_formatted_packages(self):
        arg_pkgs = self.vars.package
        packages = []
        for arg_pkg in arg_pkgs:
            pkg, version = package_split(arg_pkg)
            fmt_pkg = format_cmdline_package(pkg, version)
            packages.append(fmt_pkg)
        return packages

    def _get_installed_packages(self):
        with self.sdkmanager('installed') as ctx:
            rc, stdout, stderr = ctx.run()

            packages = []
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
                        name = p.group(1)
                        version = p.group(2)
                        description = p.group(3)
                        packages.append((name, version, description))
                i += 1
            return packages

    def __state_fallback__(self):
        packages = self._get_formatted_packages()

        installed = self._get_installed_packages()
        self.vars.installed = installed
        with self.sdkmanager('state name') as ctx:
            ctx.run(name=packages)

    def update_packages(self):
        with self.sdkmanager('update') as ctx:
            ctx.run()

    def __init_module__(self):
        self.sdkmanager = sdkmanager_runner(self.module)

    def __run__(self):
        super().__run__()

        if self.vars.update:
            self.update_packages()


def format_cmdline_package(package, version):
    if version is None:
        return package
    else:
        return "%s;%s" % (package, version)


def package_split(package):
    parts = package.split('=', maxsplit=1)
    if len(parts) > 1:
        return parts
    return parts[0], None


def main():
    AndroidSdk.execute()


if __name__ == '__main__':
    main()

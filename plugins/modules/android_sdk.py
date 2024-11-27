import re

from ansible_collections.community.general.plugins.module_utils.mh.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.sdkmanager import sdkmanager_runner


class AndroidSdk(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent', 'latest']),
            package=dict(type='list', elements='str', aliases=['pkg', 'name']),
            update=dict(type='bool', default=False)
        )
    )
    use_old_vardict = False

    def _get_formatted_packages(self):
        arg_pkgs = self.vars.package
        packages = []
        for arg_pkg in arg_pkgs:
            pkg, version = package_split(arg_pkg)
            fmt_pkg = format_cmdline_package(pkg, version)
            packages.append(fmt_pkg)
        return packages

    def __state_fallback__(self):
        packages = self._get_formatted_packages()
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

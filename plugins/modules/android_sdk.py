from ansible_collections.community.general.plugins.module_utils.mh.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.sdkmanager import sdkmanager_runner, Package, \
    AndroidSdkManager


class AndroidSdk(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent', 'latest']),
            package=dict(type='list', elements='str', aliases=['pkg', 'name']),
            update=dict(type='bool', default=False)
        )
    )
    use_old_vardict = False
    output_params = ('installed', 'removed')

    @staticmethod
    def arg_package_split(package):
        parts = package.split('=', maxsplit=1)
        if len(parts) > 1:
            return parts
        return parts[0], None

    def __init_module__(self):
        self.sdkmanager = AndroidSdkManager(sdkmanager_runner(self.module))

    def _parse_packages(self):
        arg_pkgs = self.vars.package
        packages = set()
        for arg_pkg in arg_pkgs:
            pkg, version = AndroidSdk.arg_package_split(arg_pkg)
            package = Package(pkg, version)
            packages.add(package)

        if len(packages) < len(arg_pkgs):
            self.do_raise("Packages may not repeat")
        return packages

    def state_present(self):
        packages = self._parse_packages()
        installed = self.sdkmanager.get_installed_packages()
        pending_installation = packages.difference(installed)
        self.sdkmanager.install_packages(pending_installation)
        self.vars.installed = AndroidSdk._packages_to_str(pending_installation)

    def state_absent(self):
        packages = self._parse_packages()
        installed = self.sdkmanager.get_installed_packages()
        to_be_deleted = packages.intersection(installed)
        self.sdkmanager.uninstall_packages(to_be_deleted)
        self.vars.removed = AndroidSdk._packages_to_str(to_be_deleted)

    def update_packages(self):
        pass
        # with self.sdkmanager('update') as ctx:
        #     ctx.run()

    @staticmethod
    def _packages_to_str(packages):
        return [{'name': x.name, 'version': x.version} for x in packages]

    def __run__(self):
        super().__run__()

        if self.vars.update:
            self.update_packages()


def main():
    AndroidSdk.execute()


if __name__ == '__main__':
    main()

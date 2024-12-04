from ansible_collections.community.general.plugins.module_utils.mh.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.sdkmanager import sdkmanager_runner, Package, \
    AndroidSdkManager


class AndroidSdk(StateModuleHelper):
    module = dict(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent', 'latest']),
            package=dict(type='list', elements='str', aliases=['pkg', 'name']),
            update=dict(type='bool', default=False)
        ),
        supports_check_mode=True
    )
    use_old_vardict = False
    output_params = ('installed', 'removed')
    change_params = ('installed', 'removed')
    diff_params = ('installed', 'removed')

    def __init_module__(self):
        self.sdkmanager = AndroidSdkManager(sdkmanager_runner(self.module))
        self.vars.set('installed', [], change=True)
        self.vars.set('removed', [], change=True)

    def _parse_packages(self):
        arg_pkgs = self.vars.package
        packages = set()
        for arg_pkg in arg_pkgs:
            package = Package(arg_pkg)
            packages.add(package)

        if len(packages) < len(arg_pkgs):
            self.do_raise("Packages may not repeat")
        return packages

    def state_present(self):
        packages = self._parse_packages()
        installed = self.sdkmanager.get_installed_packages()
        pending_installation = packages.difference(installed)

        self.vars.installed = AndroidSdk._map_packages_to_names(pending_installation)
        if not self.check_mode:
            self.sdkmanager.install_packages(pending_installation)

    def state_absent(self):
        packages = self._parse_packages()
        installed = self.sdkmanager.get_installed_packages()
        to_be_deleted = packages.intersection(installed)
        self.vars.removed = AndroidSdk._map_packages_to_names(to_be_deleted)
        if not self.check_mode:
            self.sdkmanager.uninstall_packages(to_be_deleted)

    def state_latest(self):
        packages = self._parse_packages()
        installed = self.sdkmanager.get_installed_packages()
        updatable = self.sdkmanager.get_updatable_packages()
        not_installed = packages.difference(installed)
        to_be_installed = not_installed.intersection(updatable)
        self.vars.installed = AndroidSdk._map_packages_to_names(to_be_installed)

        if not self.check_mode:
            self.sdkmanager.install_packages(packages)

    def update_packages(self):
        pass
        # with self.sdkmanager('update') as ctx:
        #     ctx.run()

    @staticmethod
    def _map_packages_to_names(packages):
        return [x.name for x in packages]

    def __run__(self):
        super().__run__()

        if self.vars.update:
            self.update_packages()


def main():
    AndroidSdk.execute()


if __name__ == '__main__':
    main()

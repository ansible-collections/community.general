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
    output_params = ('installed')

    def __init_module__(self):
        self.sdkmanager = AndroidSdkManager(sdkmanager_runner(self.module))

    def _parse_packages(self):
        arg_pkgs = self.vars.package
        packages = []
        for arg_pkg in arg_pkgs:
            pkg, version = package_split(arg_pkg)
            package = Package(pkg, version)
            packages.append(package)
        return packages

    def __state_fallback__(self):
        packages = self._parse_packages()
        installed = self.sdkmanager.get_installed_packages()
        pending_installation = []
        for package in packages:
            for existing in installed:
                if existing.name == package.name:
                    if existing.version == package.version:
                        pass#do nothing, package exists
                    # else:
                        # package exists, but needs to be updated/downgraded
                else:
                    pending_installation.append(package)

        self.vars.installed = installed

    def update_packages(self):
        pass
        # with self.sdkmanager('update') as ctx:
        #     ctx.run()

    def __run__(self):
        super().__run__()

        if self.vars.update:
            self.update_packages()


def package_split(package):
    parts = package.split('=', maxsplit=1)
    if len(parts) > 1:
        return parts
    return parts[0], None


def main():
    AndroidSdk.execute()


if __name__ == '__main__':
    main()

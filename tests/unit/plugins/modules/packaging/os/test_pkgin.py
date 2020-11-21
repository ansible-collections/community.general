# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import mock
from ansible_collections.community.general.tests.unit.compat import unittest

from ansible_collections.community.general.plugins.modules.packaging.os import pkgin


class TestPkginQueryPackage(unittest.TestCase):

    def setUp(self):
        pkgin.PKGIN_PATH = ""

    @mock.patch('ansible_collections.community.general.plugins.modules.packaging.os.pkgin.AnsibleModule')
    def test_package_without_version_is_present(self, mock_module):
        # given
        package = 'py37-conan'
        parseable_flag_not_supported = 1
        mock_module.run_command.side_effect = [
            (parseable_flag_not_supported, "pkgin 0.11.7 for Darwin-18.6.0 x86_64 (using SQLite 3.27.2)", None),
            (0, "%s-1.21.0 = C/C++ package manager" % package, None),
        ]

        # when
        command_result = pkgin.query_package(mock_module, package)

        # then
        self.assertEquals(command_result, pkgin.PackageState.PRESENT)

    @mock.patch('ansible_collections.community.general.plugins.modules.packaging.os.pkgin.AnsibleModule')
    def test_package_with_version_is_present(self, mock_module):
        # given
        package = 'py37-conan-1.21.0'
        parseable_flag_not_supported = 1
        mock_module.run_command.side_effect = [
            (parseable_flag_not_supported, "pkgin 0.11.7 for Darwin-18.6.0 x86_64 (using SQLite 3.27.2)", None),
            (0, "%s = C/C++ package manager" % package, None),
        ]

        # when
        command_result = pkgin.query_package(mock_module, package)

        # then
        self.assertEquals(command_result, pkgin.PackageState.PRESENT)

    @mock.patch('ansible_collections.community.general.plugins.modules.packaging.os.pkgin.AnsibleModule')
    def test_package_found_but_not_installed(self, mock_module):
        # given
        package = 'cmake'
        parseable_flag_not_supported = 1
        mock_module.run_command.side_effect = [
            (parseable_flag_not_supported, "pkgin 0.11.7 for Darwin-18.6.0 x86_64 (using SQLite 3.27.2)", None),
            (0, "cmake316-3.16.0nb1 = Cross platform make\ncmake314-3.14.6nb1 = Cross platform make\ncmake-3.14.0  Cross platform make", None),
        ]

        # when
        command_result = pkgin.query_package(mock_module, package)

        # then
        self.assertEquals(command_result, pkgin.PackageState.NOT_INSTALLED)

    @mock.patch('ansible_collections.community.general.plugins.modules.packaging.os.pkgin.AnsibleModule')
    def test_package_found_outdated(self, mock_module):
        # given
        package = 'cmake316'
        parseable_flag_not_supported = 1
        mock_module.run_command.side_effect = [
            (parseable_flag_not_supported, "pkgin 0.11.7 for Darwin-18.6.0 x86_64 (using SQLite 3.27.2)", None),
            (0, "cmake316-3.16.0nb1 < Cross platform make", None),
        ]

        # when
        command_result = pkgin.query_package(mock_module, package)

        # then
        self.assertEquals(command_result, pkgin.PackageState.OUTDATED)

    @mock.patch('ansible_collections.community.general.plugins.modules.packaging.os.pkgin.AnsibleModule')
    def test_package_with_version_found_outdated(self, mock_module):
        # given
        package = 'cmake316-3.16.0nb1'
        parseable_flag_not_supported = 1
        mock_module.run_command.side_effect = [
            (parseable_flag_not_supported, "pkgin 0.11.7 for Darwin-18.6.0 x86_64 (using SQLite 3.27.2)", None),
            (0, "cmake316-3.16.0nb1 < Cross platform make", None),
        ]

        # when
        command_result = pkgin.query_package(mock_module, package)

        # then
        self.assertEquals(command_result, pkgin.PackageState.OUTDATED)

    @mock.patch('ansible_collections.community.general.plugins.modules.packaging.os.pkgin.AnsibleModule')
    def test_package_not_found(self, mock_module):
        # given
        package = 'cmake320-3.20.0nb1'
        parseable_flag_not_supported = 1
        mock_module.run_command.side_effect = [
            (parseable_flag_not_supported, "pkgin 0.11.7 for Darwin-18.6.0 x86_64 (using SQLite 3.27.2)", None),
            (1, None, "No results found for %s" % package),
        ]

        # when
        command_result = pkgin.query_package(mock_module, package)

        # then
        self.assertEquals(command_result, pkgin.PackageState.NOT_FOUND)

    @mock.patch('ansible_collections.community.general.plugins.modules.packaging.os.pkgin.AnsibleModule')
    def test_with_parseable_flag_supported_package_is_present(self, mock_module):
        # given
        package = 'py37-conan'
        parseable_flag_supported = 0
        mock_module.run_command.side_effect = [
            (parseable_flag_supported, "pkgin 0.11.7 for Darwin-18.6.0 x86_64 (using SQLite 3.27.2)", None),
            (0, "%s-1.21.0;=;C/C++ package manager" % package, None),
        ]

        # when
        command_result = pkgin.query_package(mock_module, package)

        # then
        self.assertEquals(command_result, pkgin.PackageState.PRESENT)

    @mock.patch('ansible_collections.community.general.plugins.modules.packaging.os.pkgin.AnsibleModule')
    def test_with_parseable_flag_not_supported_package_is_present(self, mock_module):
        # given
        package = 'py37-conan'
        parseable_flag_not_supported = 1
        mock_module.run_command.side_effect = [
            (parseable_flag_not_supported, "pkgin 0.11.7 for Darwin-18.6.0 x86_64 (using SQLite 3.27.2)", None),
            (0, "%s-1.21.0 = C/C++ package manager" % package, None),
        ]

        # when
        command_result = pkgin.query_package(mock_module, package)

        # then
        self.assertEquals(command_result, pkgin.PackageState.PRESENT)

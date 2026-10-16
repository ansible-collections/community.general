# Copyright (c) 2025 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from ansible_collections.community.general.plugins.modules import sssd_info


class TestSssdInfo(unittest.TestCase):
    """Unit tests for the sssd_info module."""

    @classmethod
    def setUpClass(cls):
        """Create the dbus module mock."""
        # Mock the entire dbus module
        cls.mock_dbus = Mock()
        cls.mock_dbus.SystemBus = Mock()
        cls.mock_dbus.Interface = Mock()

        # Create mock exceptions
        class MockDBusException(Exception):
            def __init__(self, *args, **kwargs):
                super().__init__(*args)
                self._dbus_error_name = kwargs.get("dbus_error_name", "org.freedesktop.DBus.Error.UnknownObject")

            def get_dbus_name(self):
                return self._dbus_error_name

        cls.mock_dbus.exceptions = Mock()
        cls.mock_dbus.exceptions.DBusException = MockDBusException

    def setUp(self):
        """Set up test fixtures."""
        dbus_patcher = patch.object(sssd_info, "dbus", self.mock_dbus, create=True)
        dbus_patcher.start()
        self.addCleanup(dbus_patcher.stop)
        deps_patcher = patch.object(sssd_info.deps, "validate")
        deps_patcher.start()
        self.addCleanup(deps_patcher.stop)

        # Reset all mocks
        self.mock_dbus.reset_mock()
        self.mock_dbus.SystemBus.reset_mock()
        self.mock_dbus.Interface.reset_mock()

        # Create fresh mocks for each test
        self.mock_bus = Mock()
        self.mock_sssd_obj = Mock()
        self.mock_infopipe_iface = Mock()
        self.mock_domain_obj = Mock()
        self.mock_domain_iface = Mock()

        # Configure the mock chain
        self.mock_dbus.SystemBus.return_value = self.mock_bus
        self.mock_bus.get_object.return_value = self.mock_sssd_obj

        # Fix the Interface mock to accept dbus_interface parameter
        def interface_side_effect(obj, dbus_interface=None):
            if dbus_interface == "org.freedesktop.sssd.infopipe":
                return self.mock_infopipe_iface
            elif dbus_interface == "org.freedesktop.sssd.infopipe.Domains.Domain":
                return self.mock_domain_iface
            return Mock()

        self.mock_dbus.Interface.side_effect = interface_side_effect

    def test_domain_list_success(self):
        """Test successful retrieval of domain list."""
        # Mock the ListDomains response
        self.mock_infopipe_iface.ListDomains.return_value = [
            "/org/freedesktop/sssd/infopipe/Domains/ipa_2eexample_2ecom",
            "/org/freedesktop/sssd/infopipe/Domains/ad_2eexample_2ecom",
        ]

        # Mock AnsibleModule
        with patch.object(sssd_info, "AnsibleModule") as mock_module_class:
            mock_module = Mock()
            mock_module.params = {"action": "domain_list", "domain": None, "server_type": None}
            mock_module.fail_json = Mock(side_effect=Exception("fail_json called"))
            mock_module.exit_json = Mock()
            mock_module_class.return_value = mock_module

            # Run the module
            sssd_info.main()

            # Verify exit_json was called with correct results
            mock_module.exit_json.assert_called_once()
            result = (
                mock_module.exit_json.call_args[0][0]
                if mock_module.exit_json.call_args[0]
                else mock_module.exit_json.call_args[1]
            )

            self.assertIn("domain_list", result)
            self.assertEqual(result["domain_list"], ["ipa.example.com", "ad.example.com"])

    def test_domain_status_online(self):
        """Test checking online domain status."""
        # Mock domain status as online
        self.mock_domain_iface.IsOnline.return_value = True

        # Setup mock chain for domain object
        self.mock_bus.get_object.return_value = self.mock_domain_obj

        # Mock AnsibleModule
        with patch.object(sssd_info, "AnsibleModule") as mock_module_class:
            mock_module = Mock()
            mock_module.params = {"action": "domain_status", "domain": "example.com", "server_type": None}
            mock_module.fail_json = Mock(side_effect=Exception("fail_json called"))
            mock_module.exit_json = Mock()
            mock_module_class.return_value = mock_module

            # Run the module
            sssd_info.main()

            # Verify exit_json was called with correct results
            mock_module.exit_json.assert_called_once()
            result = (
                mock_module.exit_json.call_args[0][0]
                if mock_module.exit_json.call_args[0]
                else mock_module.exit_json.call_args[1]
            )

            self.assertIn("online", result)
            self.assertEqual(result["online"], "online")

    def test_domain_status_offline(self):
        """Test checking offline domain status."""
        # Mock domain status as offline
        self.mock_domain_iface.IsOnline.return_value = False

        # Setup mock chain for domain object
        self.mock_bus.get_object.return_value = self.mock_domain_obj

        # Mock AnsibleModule
        with patch.object(sssd_info, "AnsibleModule") as mock_module_class:
            mock_module = Mock()
            mock_module.params = {"action": "domain_status", "domain": "example.com", "server_type": None}
            mock_module.fail_json = Mock(side_effect=Exception("fail_json called"))
            mock_module.exit_json = Mock()
            mock_module_class.return_value = mock_module

            # Run the module
            sssd_info.main()

            # Verify exit_json was called with correct results
            mock_module.exit_json.assert_called_once()
            result = (
                mock_module.exit_json.call_args[0][0]
                if mock_module.exit_json.call_args[0]
                else mock_module.exit_json.call_args[1]
            )

            self.assertIn("online", result)
            self.assertEqual(result["online"], "offline")

    def test_domain_not_found(self):
        """Test error when domain is not found."""
        # Mock DBusException for domain not found
        # Mock AnsibleModule
        with patch.object(sssd_info, "AnsibleModule") as mock_module_class:
            mock_module = Mock()
            mock_module.params = {"action": "domain_status", "domain": "nonexistent.com", "server_type": None}
            mock_module.fail_json = Mock()
            mock_module.exit_json = Mock()
            mock_module_class.return_value = mock_module

            # Mock the exception in domain_object
            with patch.object(sssd_info.SSSDHandler, "domain_object") as mock_get_domain:
                mock_get_domain.side_effect = Exception("Domain not found: nonexistent.com. Error: Domain not found")

                # Run the module
                sssd_info.main()

                # Verify fail_json was called with error message
                mock_module.fail_json.assert_called_once()
                error_msg = mock_module.fail_json.call_args[1].get("msg", "")
                self.assertIn("Domain not found: nonexistent.com", error_msg)

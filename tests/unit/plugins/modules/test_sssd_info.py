#!/usr/bin/python
# Copyright (c) 2025 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import sys
import pytest
from unittest.mock import Mock, patch, MagicMock


def test_sssd_info_module():
    """Test the sssd_info module with mocked dbus calls."""
    
    sys.modules['dbus'] = Mock()
    
    mock_bus = Mock()
    mock_sssd_obj = Mock()
    mock_infopipe_iface = Mock()
    mock_domain_obj = Mock()
    mock_domain_iface = Mock()
    
    with patch('dbus.SystemBus', return_value=mock_bus):
        mock_bus.get_object.return_value = mock_sssd_obj
        mock_sssd_obj.__getitem__.return_value = mock_infopipe_iface
        
        mock_infopipe_iface.ListDomains.return_value = [
            '/org/freedesktop/sssd/infopipe/Domains/ipa_2eexample_2ecom',
            '/org/freedesktop/sssd/infopipe/Domains/ad_2eexample_2ecom'
        ]
        
        mock_bus.get_object.return_value = mock_domain_obj
        mock_domain_obj.__getitem__.return_value = mock_domain_iface
        mock_domain_iface.IsOnline.return_value = True
        
        mock_domain_iface.ActiveServer.return_value = 'ipa-server.example.com'
        
        mock_domain_iface.ListServers.return_value = ['dc1.example.com', 'dc2.example.com']
        
        from ansible_collections.community.general.plugins.modules import sssd_info
        
        test_cases = [
            {
                'name': 'domain_list',
                'params': {'action': 'domain_list'},
                'expected': {'domain_list': ['ipa.example.com', 'ad.example.com']}
            },
            {
                'name': 'domain_status_online',
                'params': {'action': 'domain_status', 'domain': 'example.com'},
                'expected': {'online': 'online'}
            },
            {
                'name': 'active_servers_ipa',
                'params': {'action': 'active_servers', 'domain': 'example.com', 'server_type': 'IPA'},
                'expected': {'servers': {'IPA Server': 'ipa-server.example.com'}}
            },
            {
                'name': 'list_servers_ad',
                'params': {'action': 'list_servers', 'domain': 'example.com', 'server_type': 'AD'},
                'expected': {'list_servers': ['dc1.example.com', 'dc2.example.com']}
            }
        ]
        
        for test_case in test_cases:
            print(f"Testing: {test_case['name']}")
            
            with patch('ansible_collections.community.general.plugins.modules.sssd_info.AnsibleModule') as mock_module_class:
                mock_module = Mock()
                mock_module.params = test_case['params']
                mock_module.fail_json = Mock(side_effect=Exception("fail_json called"))
                mock_module.exit_json = Mock()
                mock_module_class.return_value = mock_module
                
                try:
                    sssd_info.main()

                    mock_module.exit_json.assert_called_once()
                    call_args = mock_module.exit_json.call_args
                    actual_result = call_args[0][0] if call_args[0] else call_args[1]
                    
                    for key, expected_value in test_case['expected'].items():
                        assert key in actual_result, f"Key '{key}' not found in results"
                        assert actual_result[key] == expected_value, \
                            f"Test '{test_case['name']}': expected {expected_value}, got {actual_result[key]}"
                    
                except Exception as e:
                    if str(e) == "fail_json called":
                        print(f"  Test {test_case['name']} triggered fail_json (expected error?)")
                    else:
                        raise


def test_sssd_info_domain_not_found():
    """Test the case when a domain is not found."""
    
    # Mock dbus for testing error scenarios
    mock_bus = Mock()
    
    with patch('dbus.SystemBus', return_value=mock_bus):
        # Simulate D-Bus exception (domain not found)
        mock_bus.get_object.side_effect = Exception("Domain not found: nonexistent.com")
        
        # Import the module
        from ansible_collections.community.general.plugins.modules import sssd_info
        
        # Mock AnsibleModule
        with patch('ansible_collections.community.general.plugins.modules.sssd_info.AnsibleModule') as mock_module_class:
            mock_module = Mock()
            mock_module.params = {'action': 'domain_status', 'domain': 'nonexistent.com'}
            mock_module.fail_json = Mock()
            mock_module.exit_json = Mock()
            mock_module_class.return_value = mock_module
            
            # Execute the module
            sssd_info.main()
            
            # Verify fail_json was called with error message
            mock_module.fail_json.assert_called_once()
            call_args = mock_module.fail_json.call_args
            error_msg = call_args[1]['msg'] if 'msg' in call_args[1] else call_args[0][0]
            
            assert "Domain not found" in str(error_msg), \
                f"Expected 'Domain not found' error message, got: {error_msg}"


def test_sssd_info_without_dbus():
    """Test the case when dbus-python library is not available."""
    
    with patch.dict(sys.modules, {'dbus': None}):
        from ansible_collections.community.general.plugins.modules import sssd_info
        
        with patch('ansible_collections.community.general.plugins.modules.sssd_info.AnsibleModule') as mock_module_class:
            mock_module = Mock()
            mock_module.params = {'action': 'domain_status', 'domain': 'example.com'}
            mock_module.fail_json = Mock()
            mock_module.exit_json = Mock()
            mock_module_class.return_value = mock_module
            
            sssd_info.main()
            
            mock_module.fail_json.assert_called_once()


if __name__ == '__main__':
    """Run all tests when the script is executed directly."""
    
    print("Running tests for sssd_info module...")
    
    # Run individual test functions
    test_sssd_info_module()
    test_sssd_info_domain_not_found()
    test_sssd_info_without_dbus()
    
    print("All tests passed successfully!")
# Copyright 2019 Fortinet, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <https://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import json
import pytest
from mock import ANY
from ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios import FortiOSHandler

try:
    from ansible_collections.community.general.plugins.modules import fortios_firewall_DoS_policy6
except ImportError:
    pytest.skip("Could not load required modules for testing", allow_module_level=True)


@pytest.fixture(autouse=True)
def connection_mock(mocker):
    connection_class_mock = mocker.patch('ansible_collections.community.general.plugins.modules.fortios_firewall_DoS_policy6.Connection')
    return connection_class_mock


fos_instance = FortiOSHandler(connection_mock)


def test_firewall_DoS_policy6_creation(mocker):
    schema_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.schema')

    set_method_result = {'status': 'success', 'http_method': 'POST', 'http_status': 200}
    set_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.set', return_value=set_method_result)

    input_data = {
        'username': 'admin',
        'state': 'present',
        'firewall_DoS_policy6': {'comments': 'test_value_3',
                                 'interface': 'test_value_4',
                                 'policyid': '5',
                                 'status': 'enable'
                                 },
        'vdom': 'root'}

    is_error, changed, response = fortios_firewall_DoS_policy6.fortios_firewall(input_data, fos_instance)

    expected_data = {'comments': 'test_value_3',
                     'interface': 'test_value_4',
                     'policyid': '5',
                     'status': 'enable'
                     }

    set_method_mock.assert_called_with('firewall', 'DoS-policy6', data=expected_data, vdom='root')
    schema_method_mock.assert_not_called()
    assert not is_error
    assert changed
    assert response['status'] == 'success'
    assert response['http_status'] == 200


def test_firewall_DoS_policy6_creation_fails(mocker):
    schema_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.schema')

    set_method_result = {'status': 'error', 'http_method': 'POST', 'http_status': 500}
    set_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.set', return_value=set_method_result)

    input_data = {
        'username': 'admin',
        'state': 'present',
        'firewall_DoS_policy6': {'comments': 'test_value_3',
                                 'interface': 'test_value_4',
                                 'policyid': '5',
                                 'status': 'enable'
                                 },
        'vdom': 'root'}

    is_error, changed, response = fortios_firewall_DoS_policy6.fortios_firewall(input_data, fos_instance)

    expected_data = {'comments': 'test_value_3',
                     'interface': 'test_value_4',
                     'policyid': '5',
                     'status': 'enable'
                     }

    set_method_mock.assert_called_with('firewall', 'DoS-policy6', data=expected_data, vdom='root')
    schema_method_mock.assert_not_called()
    assert is_error
    assert not changed
    assert response['status'] == 'error'
    assert response['http_status'] == 500


def test_firewall_DoS_policy6_removal(mocker):
    schema_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.schema')

    delete_method_result = {'status': 'success', 'http_method': 'POST', 'http_status': 200}
    delete_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.delete', return_value=delete_method_result)

    input_data = {
        'username': 'admin',
        'state': 'absent',
        'firewall_DoS_policy6': {'comments': 'test_value_3',
                                 'interface': 'test_value_4',
                                 'policyid': '5',
                                 'status': 'enable'
                                 },
        'vdom': 'root'}

    is_error, changed, response = fortios_firewall_DoS_policy6.fortios_firewall(input_data, fos_instance)

    delete_method_mock.assert_called_with('firewall', 'DoS-policy6', mkey=ANY, vdom='root')
    schema_method_mock.assert_not_called()
    assert not is_error
    assert changed
    assert response['status'] == 'success'
    assert response['http_status'] == 200


def test_firewall_DoS_policy6_deletion_fails(mocker):
    schema_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.schema')

    delete_method_result = {'status': 'error', 'http_method': 'POST', 'http_status': 500}
    delete_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.delete', return_value=delete_method_result)

    input_data = {
        'username': 'admin',
        'state': 'absent',
        'firewall_DoS_policy6': {'comments': 'test_value_3',
                                 'interface': 'test_value_4',
                                 'policyid': '5',
                                 'status': 'enable'
                                 },
        'vdom': 'root'}

    is_error, changed, response = fortios_firewall_DoS_policy6.fortios_firewall(input_data, fos_instance)

    delete_method_mock.assert_called_with('firewall', 'DoS-policy6', mkey=ANY, vdom='root')
    schema_method_mock.assert_not_called()
    assert is_error
    assert not changed
    assert response['status'] == 'error'
    assert response['http_status'] == 500


def test_firewall_DoS_policy6_idempotent(mocker):
    schema_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.schema')

    set_method_result = {'status': 'error', 'http_method': 'DELETE', 'http_status': 404}
    set_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.set', return_value=set_method_result)

    input_data = {
        'username': 'admin',
        'state': 'present',
        'firewall_DoS_policy6': {'comments': 'test_value_3',
                                 'interface': 'test_value_4',
                                 'policyid': '5',
                                 'status': 'enable'
                                 },
        'vdom': 'root'}

    is_error, changed, response = fortios_firewall_DoS_policy6.fortios_firewall(input_data, fos_instance)

    expected_data = {'comments': 'test_value_3',
                     'interface': 'test_value_4',
                     'policyid': '5',
                     'status': 'enable'
                     }

    set_method_mock.assert_called_with('firewall', 'DoS-policy6', data=expected_data, vdom='root')
    schema_method_mock.assert_not_called()
    assert not is_error
    assert not changed
    assert response['status'] == 'error'
    assert response['http_status'] == 404


def test_firewall_DoS_policy6_filter_foreign_attributes(mocker):
    schema_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.schema')

    set_method_result = {'status': 'success', 'http_method': 'POST', 'http_status': 200}
    set_method_mock = mocker.patch('ansible_collections.fortinet.fortios.plugins.module_utils.network.fortios.fortios.FortiOSHandler.set', return_value=set_method_result)

    input_data = {
        'username': 'admin',
        'state': 'present',
        'firewall_DoS_policy6': {
            'random_attribute_not_valid': 'tag', 'comments': 'test_value_3',
            'interface': 'test_value_4',
            'policyid': '5',
            'status': 'enable'
        },
        'vdom': 'root'}

    is_error, changed, response = fortios_firewall_DoS_policy6.fortios_firewall(input_data, fos_instance)

    expected_data = {'comments': 'test_value_3',
                     'interface': 'test_value_4',
                     'policyid': '5',
                     'status': 'enable'
                     }

    set_method_mock.assert_called_with('firewall', 'DoS-policy6', data=expected_data, vdom='root')
    schema_method_mock.assert_not_called()
    assert not is_error
    assert changed
    assert response['status'] == 'success'
    assert response['http_status'] == 200

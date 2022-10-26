# Copyright (c) 2016-2017 Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import unittest
from .oneview_module_loader import SanManagerInfoModule
from .oneview_conftest import mock_ov_client, mock_ansible_module
from .hpe_test_utils import FactsParamsTestCase


class SanManagerInfoSpec(unittest.TestCase, FactsParamsTestCase):
    ERROR_MSG = 'Fake message error'

    PARAMS_GET_ALL = dict(
        config='config.json',
        provider_display_name=None
    )

    PARAMS_GET_BY_PROVIDER_DISPLAY_NAME = dict(
        config='config.json',
        provider_display_name="Brocade Network Advisor"
    )

    PRESENT_SAN_MANAGERS = [{
        "providerDisplayName": "Brocade Network Advisor",
        "uri": "/rest/fc-sans/device-managers//d60efc8a-15b8-470c-8470-738d16d6b319"
    }]

    def setUp(self):
        self.configure_mocks(self, SanManagerInfoModule)
        self.san_managers = self.mock_ov_client.san_managers

        FactsParamsTestCase.configure_client_mock(self, self.san_managers)

    def test_should_get_all(self):
        self.san_managers.get_all.return_value = self.PRESENT_SAN_MANAGERS
        self.mock_ansible_module.params = self.PARAMS_GET_ALL

        SanManagerInfoModule().run()

        self.mock_ansible_module.exit_json.assert_called_once_with(
            changed=False,
            san_managers=self.PRESENT_SAN_MANAGERS
        )

    def test_should_get_by_display_name(self):
        self.san_managers.get_by_provider_display_name.return_value = self.PRESENT_SAN_MANAGERS[0]
        self.mock_ansible_module.params = self.PARAMS_GET_BY_PROVIDER_DISPLAY_NAME

        SanManagerInfoModule().run()

        self.mock_ansible_module.exit_json.assert_called_once_with(
            changed=False,
            san_managers=self.PRESENT_SAN_MANAGERS
        )

    def test_should_return_empty_list_when_get_by_display_name_is_null(self):
        self.san_managers.get_by_provider_display_name.return_value = None
        self.mock_ansible_module.params = self.PARAMS_GET_BY_PROVIDER_DISPLAY_NAME

        SanManagerInfoModule().run()

        self.mock_ansible_module.exit_json.assert_called_once_with(
            changed=False,
            san_managers=[]
        )


if __name__ == '__main__':
    unittest.main()

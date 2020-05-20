#
# Copyright (c) 2017 Cisco and/or its affiliates.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)

from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.plugins.modules.network.nso import nso_show
from . import nso_module
from ..nso_module import MockResponse

from ansible_collections.community.general.tests.unit.modules.utils import set_module_args


class TestNsoShow(nso_module.TestNsoModule):
    module = nso_show

    @patch('ansible_collections.community.general.plugins.module_utils.network.nso.nso.open_url')
    def test_nso_show_missing(self, open_url_mock):
        path = '/ncs:devices/device{ce0}/missing'
        calls = [
            MockResponse('login', {}, 200, '{}', {'set-cookie': 'id'}),
            MockResponse('get_system_setting', {'operation': 'version'}, 200, '{"result": "4.5"}'),
            MockResponse('new_trans', {'mode': 'read'}, 200, '{"result": {"th": 1}}'),
            MockResponse('show_config',
                         {'path': path, 'result_as': 'json'}, 200,
                         '{"error": {"data": {"param": "path"}, "type": "rpc.method.invalid_params"}}'),
            MockResponse('logout', {}, 200, '{"result": {}}'),
        ]
        open_url_mock.side_effect = lambda *args, **kwargs: nso_module.mock_call(calls, *args, **kwargs)

        set_module_args({
            'username': 'user', 'password': 'password',
            'url': 'http://localhost:8080/jsonrpc',
            'path': path
        })
        self.execute_module(failed=True, msg='NSO show_config invalid params. path = /ncs:devices/device{ce0}/missing')

        self.assertEqual(0, len(calls))

    @patch('ansible_collections.community.general.plugins.module_utils.network.nso.nso.open_url')
    def test_nso_show_config(self, open_url_mock):
        path = '/ncs:devices/device{ce0}'
        calls = [
            MockResponse('login', {}, 200, '{}', {'set-cookie': 'id'}),
            MockResponse('get_system_setting', {'operation': 'version'}, 200, '{"result": "4.5"}'),
            MockResponse('new_trans', {'mode': 'read'}, 200, '{"result": {"th": 1}}'),
            MockResponse('show_config', {'path': path, 'result_as': 'json'}, 200, '{"result": {"data": {}}}'),
            MockResponse('logout', {}, 200, '{"result": {}}'),
        ]
        open_url_mock.side_effect = lambda *args, **kwargs: nso_module.mock_call(calls, *args, **kwargs)

        set_module_args({
            'username': 'user', 'password': 'password',
            'url': 'http://localhost:8080/jsonrpc',
            'path': path,
            'operational': False
        })
        self.execute_module(changed=False, output={"data": {}})
        self.assertEqual(0, len(calls))

    @patch('ansible_collections.community.general.plugins.module_utils.network.nso.nso.open_url')
    def test_nso_show_config_and_oper(self, open_url_mock):
        path = '/ncs:devices/device{ce0}/sync-from'
        calls = [
            MockResponse('login', {}, 200, '{}', {'set-cookie': 'id'}),
            MockResponse('get_system_setting', {'operation': 'version'}, 200, '{"result": "4.5"}'),
            MockResponse('new_trans', {'mode': 'read'}, 200, '{"result": {"th": 1}}'),
            MockResponse('show_config', {'path': path, 'result_as': 'json'}, 200, '{"result": {"data": {}}}'),
            MockResponse('logout', {}, 200, '{"result": {}}'),
        ]
        open_url_mock.side_effect = lambda *args, **kwargs: nso_module.mock_call(calls, *args, **kwargs)

        set_module_args({
            'username': 'user', 'password': 'password',
            'url': 'http://localhost:8080/jsonrpc',
            'path': path,
            'operational': True,
            'validate_certs': False
        })
        self.execute_module(changed=False, output={"data": {}})

        self.assertEqual(0, len(calls))

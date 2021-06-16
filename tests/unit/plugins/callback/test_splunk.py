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
__metaclass__ = type

from ansible.executor.task_result import TaskResult
from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch, call, MagicMock, Mock
from ansible_collections.community.general.plugins.callback.splunk import SplunkHTTPCollectorSource
from datetime import datetime

import json


class TestSplunkClient(unittest.TestCase):
    @patch('ansible_collections.community.general.plugins.callback.splunk.socket')
    def setUp(self, mock_socket):
        mock_socket.gethostname.return_value = 'my-host'
        mock_socket.gethostbyname.return_value = '1.2.3.4'
        self.splunk = SplunkHTTPCollectorSource()
        self.mock_task = Mock('MockTask')
        self.mock_task._role = 'myrole'
        self.mock_task._uuid = 'myuuid'
        self.task_fields = {'args': {}}
        self.mock_host = Mock('MockHost')
        self.mock_host.name = 'myhost'

    @patch('ansible_collections.community.general.plugins.callback.splunk.datetime')
    @patch('ansible_collections.community.general.plugins.callback.splunk.open_url')
    def test_timestamp_with_milliseconds(self, open_url_mock, mock_datetime):
        mock_datetime.utcnow.return_value = datetime(2020, 12, 1)
        result = TaskResult(host=self.mock_host, task=self.mock_task, return_data={}, task_fields=self.task_fields)

        self.splunk.send_event(
            url='endpoint', authtoken='token', validate_certs=False, include_milliseconds=True,
            batch="abcefghi-1234-5678-9012-abcdefghijkl", state='OK', result=result, runtime=100
        )

        args, kwargs = open_url_mock.call_args
        sent_data = json.loads(args[1])

        self.assertEqual(sent_data['event']['timestamp'], '2020-12-01 00:00:00.000000 +0000')
        self.assertEqual(sent_data['event']['host'], 'my-host')
        self.assertEqual(sent_data['event']['ip_address'], '1.2.3.4')

    @patch('ansible_collections.community.general.plugins.callback.splunk.datetime')
    @patch('ansible_collections.community.general.plugins.callback.splunk.open_url')
    def test_timestamp_without_milliseconds(self, open_url_mock, mock_datetime):
        mock_datetime.utcnow.return_value = datetime(2020, 12, 1)
        result = TaskResult(host=self.mock_host, task=self.mock_task, return_data={}, task_fields=self.task_fields)

        self.splunk.send_event(
            url='endpoint', authtoken='token', validate_certs=False, include_milliseconds=False,
            batch="abcefghi-1234-5678-9012-abcdefghijkl", state='OK', result=result, runtime=100
        )

        args, kwargs = open_url_mock.call_args
        sent_data = json.loads(args[1])

        self.assertEqual(sent_data['event']['timestamp'], '2020-12-01 00:00:00 +0000')
        self.assertEqual(sent_data['event']['host'], 'my-host')
        self.assertEqual(sent_data['event']['ip_address'], '1.2.3.4')

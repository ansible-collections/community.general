# (C) 2021, Victor Martinez <VictorMartinezRubio@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.executor.task_result import TaskResult
from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch, Mock
from ansible_collections.community.general.plugins.callback.opentelemetry import OpenTelemetrySource
from datetime import datetime

import json

from collections import OrderedDict


class TestOpentelemetry(unittest.TestCase):
    @patch('ansible_collections.community.general.plugins.callback.opentelemetry.play')
    @patch('ansible_collections.community.general.plugins.callback.opentelemetry.task')
    @patch('ansible_collections.community.general.plugins.callback.opentelemetry.socket')
    def setUp(self, mock_socket, mock_task, mock_play):
        mock_socket.gethostname.return_value = 'my-host'
        mock_socket.gethostbyname.return_value = '1.2.3.4'
        mock_task.get_name.return_value = 'mytask'
        mock_task.get_path.return_value = 'mypath'
        mock_task.action = 'myaction'
        mock_task.no_log = False
        mock_task._role = 'myrole'
        mock_task._uuid = 'myuuid'
        mock_task.args = {}
        mock_play.get_name.return_value = 'myplay'
        self.opentelemetry = OpenTelemetrySource(display=None)
        self.task_fields = {'args': {}}
        self.mock_host = Mock('MockHost')
        self.mock_host.name = 'myhost'

    def test_start_task(self):
        result = TaskResult(host=self.mock_host, task=self.mock_task, return_data={}, task_fields=self.task_fields)
        tasks_data = OrderedDict()

        self.opentelemetry.start_task(
            tasks_data,
            False,
            'myplay',
            self.mock_task
        )

        tasks_data['myuuid'].uuid = 'myuuid'

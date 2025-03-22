# -*- coding: utf-8 -*-
# Copyright (c) 2021, Victor Martinez <VictorMartinezRubio@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.playbook.task import Task
from ansible.executor.task_result import TaskResult
from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch, MagicMock, Mock
from ansible_collections.community.general.plugins.callback.opentelemetry import OpenTelemetrySource, TaskData
from collections import OrderedDict
import sys

OPENTELEMETRY_MINIMUM_PYTHON_VERSION = (3, 7)


class TestOpentelemetry(unittest.TestCase):
    @patch('ansible_collections.community.general.plugins.callback.opentelemetry.socket')
    def setUp(self, mock_socket):
        # TODO: this python version validation won't be needed as long as the _time_ns call is mocked.
        if sys.version_info < OPENTELEMETRY_MINIMUM_PYTHON_VERSION:
            self.skipTest("Python %s+ is needed for OpenTelemetry" %
                          ",".join(map(str, OPENTELEMETRY_MINIMUM_PYTHON_VERSION)))

        mock_socket.gethostname.return_value = 'my-host'
        mock_socket.gethostbyname.return_value = '1.2.3.4'
        self.opentelemetry = OpenTelemetrySource(display=None)
        self.task_fields = {'args': {}}
        self.mock_host = Mock('MockHost')
        self.mock_host.name = 'myhost'
        self.mock_host._uuid = 'myhost_uuid'
        self.mock_task = Task()
        self.mock_task.action = 'myaction'
        self.mock_task.no_log = False
        self.mock_task._role = 'myrole'
        self.mock_task._uuid = 'myuuid'
        self.mock_task.args = {}
        self.mock_task.get_name = MagicMock(return_value='mytask')
        self.mock_task.get_path = MagicMock(return_value='/mypath')
        self.my_task = TaskData('myuuid', 'mytask', '/mypath', 'myplay', 'myaction', '')
        self.my_task_result = TaskResult(host=self.mock_host, task=self.mock_task, return_data={}, task_fields=self.task_fields)

    def test_start_task(self):
        tasks_data = OrderedDict()

        self.opentelemetry.start_task(
            tasks_data,
            False,
            'myplay',
            self.mock_task
        )

        task_data = tasks_data['myuuid']
        self.assertEqual(task_data.uuid, 'myuuid')
        self.assertEqual(task_data.name, 'mytask')
        self.assertEqual(task_data.path, '/mypath')
        self.assertEqual(task_data.play, 'myplay')
        self.assertEqual(task_data.action, 'myaction')
        self.assertEqual(task_data.args, {})

    def test_finish_task_with_a_host_match(self):
        tasks_data = OrderedDict()
        tasks_data['myuuid'] = self.my_task

        self.opentelemetry.finish_task(
            tasks_data,
            'ok',
            self.my_task_result,
            ""
        )

        task_data = tasks_data['myuuid']
        host_data = task_data.host_data['myhost_uuid']
        self.assertEqual(host_data.uuid, 'myhost_uuid')
        self.assertEqual(host_data.name, 'myhost')
        self.assertEqual(host_data.status, 'ok')

    def test_finish_task_without_a_host_match(self):
        result = TaskResult(host=None, task=self.mock_task, return_data={}, task_fields=self.task_fields)
        tasks_data = OrderedDict()
        tasks_data['myuuid'] = self.my_task

        self.opentelemetry.finish_task(
            tasks_data,
            'ok',
            result,
            ""
        )

        task_data = tasks_data['myuuid']
        host_data = task_data.host_data['include']
        self.assertEqual(host_data.uuid, 'include')
        self.assertEqual(host_data.name, 'include')
        self.assertEqual(host_data.status, 'ok')
        self.assertEqual(self.opentelemetry.ansible_version, None)

    def test_finish_task_include_with_ansible_version(self):
        task_fields = {'args': {'_ansible_version': '1.2.3'}}
        result = TaskResult(host=None, task=self.mock_task, return_data={}, task_fields=task_fields)
        tasks_data = OrderedDict()
        tasks_data['myuuid'] = self.my_task

        self.opentelemetry.finish_task(
            tasks_data,
            'ok',
            result,
            ""
        )

        self.assertEqual(self.opentelemetry.ansible_version, '1.2.3')

    def test_get_error_message(self):
        test_cases = (
            ('my-exception', 'my-msg', None, 'my-exception'),
            (None, 'my-msg', None, 'my-msg'),
            (None, None, None, 'failed'),
        )

        for tc in test_cases:
            result = self.opentelemetry.get_error_message(generate_test_data(tc[0], tc[1], tc[2]))
            self.assertEqual(result, tc[3])

    def test_get_error_message_from_results(self):
        test_cases = (
            ('my-exception', 'my-msg', None, False, None),
            (None, 'my-msg', None, False, None),
            (None, None, None, False, None),
            ('my-exception', 'my-msg', None, True, 'shell(none) - my-exception'),
            (None, 'my-msg', None, True, 'shell(none) - my-msg'),
            (None, None, None, True, 'shell(none) - failed'),
        )

        for tc in test_cases:
            result = self.opentelemetry.get_error_message_from_results([generate_test_data(tc[0], tc[1], tc[2], tc[3])], 'shell')
            self.assertEqual(result, tc[4])

    def test_enrich_error_message(self):
        test_cases = (
            ('my-exception', 'my-msg', 'my-stderr', 'message: "my-msg"\nexception: "my-exception"\nstderr: "my-stderr"'),
            ('my-exception', None, 'my-stderr', 'message: "failed"\nexception: "my-exception"\nstderr: "my-stderr"'),
            (None, 'my-msg', 'my-stderr', 'message: "my-msg"\nexception: "None"\nstderr: "my-stderr"'),
            ('my-exception', 'my-msg', None, 'message: "my-msg"\nexception: "my-exception"\nstderr: "None"'),
            ('my-exception', 'my-msg', '\nline1\nline2', 'message: "my-msg"\nexception: "my-exception"\nstderr: "\nline1\nline2"')
        )

        for tc in test_cases:
            result = self.opentelemetry.enrich_error_message(generate_test_data(tc[0], tc[1], tc[2]))
            self.assertEqual(result, tc[3])

    def test_enrich_error_message_from_results(self):
        test_cases = (
            ('my-exception', 'my-msg', 'my-stderr', False, ''),
            ('my-exception', None, 'my-stderr', False, ''),
            (None, 'my-msg', 'my-stderr', False, ''),
            ('my-exception', 'my-msg', None, False, ''),
            ('my-exception', 'my-msg', '\nline1\nline2', False, ''),
            ('my-exception', 'my-msg', 'my-stderr', True, 'shell(none) - message: "my-msg"\nexception: "my-exception"\nstderr: "my-stderr"\n'),
            ('my-exception', None, 'my-stderr', True, 'shell(none) - message: "failed"\nexception: "my-exception"\nstderr: "my-stderr"\n'),
            (None, 'my-msg', 'my-stderr', True, 'shell(none) - message: "my-msg"\nexception: "None"\nstderr: "my-stderr"\n'),
            ('my-exception', 'my-msg', None, True, 'shell(none) - message: "my-msg"\nexception: "my-exception"\nstderr: "None"\n'),
            ('my-exception', 'my-msg', '\nline1\nline2', True, 'shell(none) - message: "my-msg"\nexception: "my-exception"\nstderr: "\nline1\nline2"\n')
        )

        for tc in test_cases:
            result = self.opentelemetry.enrich_error_message_from_results([generate_test_data(tc[0], tc[1], tc[2], tc[3])], 'shell')
            self.assertEqual(result, tc[4])

    def test_url_from_args(self):
        test_cases = (
            ({}, ""),
            ({'url': 'my-url'}, 'my-url'),
            ({'url': 'my-url', 'api_url': 'my-api_url'}, 'my-url'),
            ({'api_url': 'my-api_url'}, 'my-api_url'),
            ({'api_url': 'my-api_url', 'chart_repo_url': 'my-chart_repo_url'}, 'my-api_url')
        )

        for tc in test_cases:
            result = self.opentelemetry.url_from_args(tc[0])
            self.assertEqual(result, tc[1])

    def test_parse_and_redact_url_if_possible(self):
        test_cases = (
            ({}, None),
            ({'url': 'wrong'}, None),
            ({'url': 'https://my-url'}, 'https://my-url'),
            ({'url': 'https://user:pass@my-url'}, 'https://my-url'),
            ({'url': 'https://my-url:{{ my_port }}'}, 'https://my-url:{{ my_port }}'),
            ({'url': 'https://{{ my_hostname }}:{{ my_port }}'}, None),
            ({'url': '{{my_schema}}{{ my_hostname }}:{{ my_port }}'}, None)
        )

        for tc in test_cases:
            result = self.opentelemetry.parse_and_redact_url_if_possible(tc[0])
            if tc[1]:
                self.assertEqual(result.geturl(), tc[1])
            else:
                self.assertEqual(result, tc[1])


def generate_test_data(exception=None, msg=None, stderr=None, failed=False):
    res_data = OrderedDict()
    if exception:
        res_data['exception'] = exception
    if msg:
        res_data['msg'] = msg
    if stderr:
        res_data['stderr'] = stderr
    res_data['failed'] = failed
    return res_data

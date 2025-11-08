# Copyright (c) 2021, Victor Martinez <VictorMartinezRubio@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from collections import OrderedDict
from unittest.mock import patch, MagicMock, Mock

from ansible.playbook.task import Task
from ansible.executor.task_result import TaskResult
from ansible_collections.community.general.plugins.callback.elastic import ElasticSource, TaskData


class TestOpentelemetry(unittest.TestCase):
    @patch("ansible_collections.community.general.plugins.callback.elastic.socket")
    def setUp(self, mock_socket):
        mock_socket.gethostname.return_value = "my-host"
        mock_socket.gethostbyname.return_value = "1.2.3.4"
        self.elastic = ElasticSource(display=None)
        self.task_fields = {"args": {}}
        self.mock_host = Mock("MockHost")
        self.mock_host.name = "myhost"
        self.mock_host._uuid = "myhost_uuid"
        self.mock_task = Task()
        self.mock_task.action = "myaction"
        self.mock_task.no_log = False
        self.mock_task._role = "myrole"
        self.mock_task._uuid = "myuuid"
        self.mock_task.args = {}
        self.mock_task.get_name = MagicMock(return_value="mytask")
        self.mock_task.get_path = MagicMock(return_value="/mypath")
        self.my_task = TaskData("myuuid", "mytask", "/mypath", "myplay", "myaction", "")
        self.my_task_result = TaskResult(
            host=self.mock_host, task=self.mock_task, return_data={}, task_fields=self.task_fields
        )

    def test_start_task(self):
        tasks_data = OrderedDict()

        self.elastic.start_task(tasks_data, False, "myplay", self.mock_task)

        task_data = tasks_data["myuuid"]
        self.assertEqual(task_data.uuid, "myuuid")
        self.assertEqual(task_data.name, "mytask")
        self.assertEqual(task_data.path, "/mypath")
        self.assertEqual(task_data.play, "myplay")
        self.assertEqual(task_data.action, "myaction")
        self.assertEqual(task_data.args, "")

    def test_finish_task_with_a_host_match(self):
        tasks_data = OrderedDict()
        tasks_data["myuuid"] = self.my_task

        self.elastic.finish_task(tasks_data, "ok", self.my_task_result)

        task_data = tasks_data["myuuid"]
        host_data = task_data.host_data["myhost_uuid"]
        self.assertEqual(host_data.uuid, "myhost_uuid")
        self.assertEqual(host_data.name, "myhost")
        self.assertEqual(host_data.status, "ok")

    def test_finish_task_without_a_host_match(self):
        result = TaskResult(host=None, task=self.mock_task, return_data={}, task_fields=self.task_fields)
        tasks_data = OrderedDict()
        tasks_data["myuuid"] = self.my_task

        self.elastic.finish_task(tasks_data, "ok", result)

        task_data = tasks_data["myuuid"]
        host_data = task_data.host_data["include"]
        self.assertEqual(host_data.uuid, "include")
        self.assertEqual(host_data.name, "include")
        self.assertEqual(host_data.status, "ok")

    def test_get_error_message(self):
        test_cases = (
            ("my-exception", "my-msg", None, "my-exception"),
            (None, "my-msg", None, "my-msg"),
            (None, None, None, "failed"),
        )

        for tc in test_cases:
            result = self.elastic.get_error_message(generate_test_data(tc[0], tc[1], tc[2]))
            self.assertEqual(result, tc[3])

    def test_enrich_error_message(self):
        test_cases = (
            (
                "my-exception",
                "my-msg",
                "my-stderr",
                'message: "my-msg"\nexception: "my-exception"\nstderr: "my-stderr"',
            ),
            ("my-exception", None, "my-stderr", 'message: "failed"\nexception: "my-exception"\nstderr: "my-stderr"'),
            (None, "my-msg", "my-stderr", 'message: "my-msg"\nexception: "None"\nstderr: "my-stderr"'),
            ("my-exception", "my-msg", None, 'message: "my-msg"\nexception: "my-exception"\nstderr: "None"'),
            (
                "my-exception",
                "my-msg",
                "\nline1\nline2",
                'message: "my-msg"\nexception: "my-exception"\nstderr: "\nline1\nline2"',
            ),
        )

        for tc in test_cases:
            result = self.elastic.enrich_error_message(generate_test_data(tc[0], tc[1], tc[2]))
            self.assertEqual(result, tc[3])


def generate_test_data(exception=None, msg=None, stderr=None):
    res_data = OrderedDict()
    if exception:
        res_data["exception"] = exception
    if msg:
        res_data["msg"] = msg
    if stderr:
        res_data["stderr"] = stderr
    return res_data

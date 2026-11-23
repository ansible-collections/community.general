# Copyright (c) 2021, Victor Martinez <VictorMartinezRubio@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from collections import OrderedDict
from unittest.mock import MagicMock, Mock, patch

import pytest
from ansible.executor.task_result import TaskResult
from ansible.playbook.task import Task
from ansible.release import __version__ as ansible_release

from ansible_collections.community.general.plugins.callback.opentelemetry import (
    CallbackModule,
    HostData,
    OpenTelemetrySource,
    TaskData,
)

if tuple(int(x) for x in ansible_release.split(".")[:2]) >= (2, 21):
    # https://github.com/ansible/ansible/issues/86761
    pytest.skip("Temporarily skipping callback tests for ansible-core >= 2.21", allow_module_level=True)


class TestOpentelemetry(unittest.TestCase):
    @patch("ansible_collections.community.general.plugins.callback.opentelemetry.socket")
    def setUp(self, mock_socket):
        mock_socket.gethostname.return_value = "my-host"
        mock_socket.gethostbyname.return_value = "1.2.3.4"
        self.opentelemetry = OpenTelemetrySource(display=None)
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
        self.mock_span = Mock("MockSpan")
        self.mock_span.set_status = MagicMock()
        self.mock_span.set_attributes = MagicMock()
        self.mock_span.end = MagicMock()

    def test_run_task_with_host(self):
        tasks_data = OrderedDict()

        self.opentelemetry.start_task(tasks_data, False, "myplay", self.mock_task, self.mock_host)

        task_data = tasks_data["myuuid"]
        self.assertEqual(task_data.uuid, "myuuid")
        self.assertEqual(task_data.name, "mytask")
        self.assertEqual(task_data.path, "/mypath")
        self.assertEqual(task_data.play, "myplay")
        self.assertEqual(task_data.action, "myaction")
        self.assertEqual(task_data.args, {})

        host_data = task_data.host_data["myhost_uuid"]
        self.assertEqual(host_data.uuid, "myhost_uuid")
        self.assertEqual(host_data.name, "myhost")
        self.assertIsNotNone(host_data.start)

        self.opentelemetry.finish_task(tasks_data, "ok", self.my_task_result, "")
        self.assertEqual(host_data.status, "ok")

    def test_finish_task_with_a_host_match(self):
        tasks_data = OrderedDict()
        tasks_data["myuuid"] = self.my_task

        self.opentelemetry.finish_task(tasks_data, "ok", self.my_task_result, "")

        task_data = tasks_data["myuuid"]
        host_data = task_data.host_data["myhost_uuid"]
        self.assertEqual(host_data.uuid, "myhost_uuid")
        self.assertEqual(host_data.name, "myhost")
        self.assertEqual(host_data.status, "ok")

    def test_finish_task_without_a_host_match(self):
        result = TaskResult(host=None, task=self.mock_task, return_data={}, task_fields=self.task_fields)
        tasks_data = OrderedDict()
        tasks_data["myuuid"] = self.my_task

        self.opentelemetry.finish_task(tasks_data, "ok", result, "")

        task_data = tasks_data["myuuid"]
        host_data = task_data.host_data["include"]
        self.assertEqual(host_data.uuid, "include")
        self.assertEqual(host_data.name, "include")
        self.assertEqual(host_data.status, "ok")

    @patch("ansible_collections.community.general.plugins.callback.opentelemetry.OTEL_LIBRARY_IMPORT_ERROR", None)
    def test_skipped_task_without_runner_start(self):
        callback = CallbackModule()
        callback.play_name = "myplay"
        # keep the collected data so it can be inspected, it is otherwise released once its span is streamed
        callback.opentelemetry.stream_task_span = MagicMock()

        callback.v2_runner_on_skipped(self.my_task_result)

        task_data = callback.tasks_data["myuuid"]
        self.assertEqual(task_data.name, "mytask")
        self.assertEqual(task_data.play, "myplay")
        host_data = task_data.host_data["myhost_uuid"]
        self.assertEqual(host_data.name, "myhost")
        self.assertEqual(host_data.status, "skipped")
        callback.opentelemetry.stream_task_span.assert_called_once()

    @patch("ansible_collections.community.general.plugins.callback.opentelemetry.Status", create=True)
    @patch("ansible_collections.community.general.plugins.callback.opentelemetry.StatusCode", create=True)
    def test_update_span_data(self, mock_status_code, mock_status):
        unfinished_host = HostData("myhost_uuid", "myhost", "unreachable")
        self.opentelemetry.update_span_data(self.mock_task, unfinished_host, self.mock_span, True, True)
        self.mock_span.end.assert_called()

    def test_get_error_message(self):
        test_cases = (
            ("my-exception", "my-msg", None, "my-exception"),
            (None, "my-msg", None, "my-msg"),
            (None, None, None, "failed"),
        )

        for tc in test_cases:
            result = self.opentelemetry.get_error_message(generate_test_data(tc[0], tc[1], tc[2]))
            self.assertEqual(result, tc[3])

    def test_get_error_message_from_results(self):
        test_cases = (
            ("my-exception", "my-msg", None, False, None),
            (None, "my-msg", None, False, None),
            (None, None, None, False, None),
            ("my-exception", "my-msg", None, True, "shell(none) - my-exception"),
            (None, "my-msg", None, True, "shell(none) - my-msg"),
            (None, None, None, True, "shell(none) - failed"),
        )

        for tc in test_cases:
            result = self.opentelemetry.get_error_message_from_results(
                [generate_test_data(tc[0], tc[1], tc[2], tc[3])], "shell"
            )
            self.assertEqual(result, tc[4])

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
            result = self.opentelemetry.enrich_error_message(generate_test_data(tc[0], tc[1], tc[2]))
            self.assertEqual(result, tc[3])

    def test_enrich_error_message_from_results(self):
        test_cases = (
            ("my-exception", "my-msg", "my-stderr", False, ""),
            ("my-exception", None, "my-stderr", False, ""),
            (None, "my-msg", "my-stderr", False, ""),
            ("my-exception", "my-msg", None, False, ""),
            ("my-exception", "my-msg", "\nline1\nline2", False, ""),
            (
                "my-exception",
                "my-msg",
                "my-stderr",
                True,
                'shell(none) - message: "my-msg"\nexception: "my-exception"\nstderr: "my-stderr"\n',
            ),
            (
                "my-exception",
                None,
                "my-stderr",
                True,
                'shell(none) - message: "failed"\nexception: "my-exception"\nstderr: "my-stderr"\n',
            ),
            (
                None,
                "my-msg",
                "my-stderr",
                True,
                'shell(none) - message: "my-msg"\nexception: "None"\nstderr: "my-stderr"\n',
            ),
            (
                "my-exception",
                "my-msg",
                None,
                True,
                'shell(none) - message: "my-msg"\nexception: "my-exception"\nstderr: "None"\n',
            ),
            (
                "my-exception",
                "my-msg",
                "\nline1\nline2",
                True,
                'shell(none) - message: "my-msg"\nexception: "my-exception"\nstderr: "\nline1\nline2"\n',
            ),
        )

        for tc in test_cases:
            result = self.opentelemetry.enrich_error_message_from_results(
                [generate_test_data(tc[0], tc[1], tc[2], tc[3])], "shell"
            )
            self.assertEqual(result, tc[4])

    def test_url_from_args(self):
        test_cases = (
            ({}, ""),
            ({"url": "my-url"}, "my-url"),
            ({"url": "my-url", "api_url": "my-api_url"}, "my-url"),
            ({"api_url": "my-api_url"}, "my-api_url"),
            ({"api_url": "my-api_url", "chart_repo_url": "my-chart_repo_url"}, "my-api_url"),
        )

        for tc in test_cases:
            result = self.opentelemetry.url_from_args(tc[0])
            self.assertEqual(result, tc[1])

    def test_parse_and_redact_url_if_possible(self):
        test_cases = (
            ({}, None),
            ({"url": "wrong"}, None),
            ({"url": "https://my-url"}, "https://my-url"),
            ({"url": "https://user:pass@my-url"}, "https://my-url"),
            ({"url": "https://my-url:{{ my_port }}"}, "https://my-url:{{ my_port }}"),
            ({"url": "https://{{ my_hostname }}:{{ my_port }}"}, None),
            ({"url": "{{my_schema}}{{ my_hostname }}:{{ my_port }}"}, None),
        )

        for tc in test_cases:
            result = self.opentelemetry.parse_and_redact_url_if_possible(tc[0])
            if tc[1]:
                self.assertEqual(result.geturl(), tc[1])
            else:
                self.assertEqual(result, tc[1])


def test_span_event_carries_the_result_of_its_own_host(mocker):
    mocker.patch("ansible_collections.community.general.plugins.callback.opentelemetry.Status", create=True)
    mocker.patch("ansible_collections.community.general.plugins.callback.opentelemetry.StatusCode", create=True)
    opentelemetry = OpenTelemetrySource(display=None)
    task = Task()
    task.action = "myaction"
    task.no_log = False
    task._uuid = "myuuid"
    task.args = {}
    task.get_name = MagicMock(return_value="mytask")
    task.get_path = MagicMock(return_value="/mypath")
    tasks_data = OrderedDict()

    hosts = []
    for name in ("a", "b", "c"):
        host = Mock("MockHost")
        host.name = name
        host._uuid = f"{name}_uuid"
        hosts.append(host)
        opentelemetry.start_task(tasks_data, False, "myplay", task, host)
    for host in hosts:
        result = TaskResult(host=host, task=task, return_data={"msg": host.name}, task_fields={"args": {}})
        opentelemetry.finish_task(tasks_data, "ok", result, f'{{"msg": "{host.name}"}}')

    for host_data in tasks_data["myuuid"].host_data.values():
        span = MagicMock()
        opentelemetry.update_span_data(tasks_data["myuuid"], host_data, span, False, True)
        span.add_event.assert_called_once_with(f'{{"msg": "{host_data.name}"}}', attributes={})


def test_spans_are_exported_before_the_playbook_finishes(mocker):
    pytest.importorskip("opentelemetry.sdk.trace.export.in_memory_span_exporter")
    from opentelemetry.trace.status import Status, StatusCode

    mocker.patch(
        "ansible_collections.community.general.plugins.callback.opentelemetry.socket.gethostname",
        return_value="my-host",
    )
    mocker.patch(
        "ansible_collections.community.general.plugins.callback.opentelemetry.socket.gethostbyname",
        return_value="1.2.3.4",
    )
    opentelemetry = OpenTelemetrySource(display=None)
    opentelemetry.setup_tracing("ansible", "grpc", "spans.json")
    opentelemetry.start_playbook_span("myplaybook.yml", None)

    task = Task()
    task.action = "myaction"
    task.no_log = False
    task._uuid = "myuuid"
    task.args = {}
    task.get_name = MagicMock(return_value="mytask")
    task.get_path = MagicMock(return_value="/mypath")
    host = Mock("MockHost")
    host.name = "myhost"
    host._uuid = "myhost_uuid"
    tasks_data = OrderedDict()

    opentelemetry.start_task(tasks_data, False, "myplay", task, host)
    result = TaskResult(host=host, task=task, return_data={"msg": "done"}, task_fields={"args": {}})
    host_data = opentelemetry.finish_task(tasks_data, "ok", result, '{"msg": "done"}')
    opentelemetry.stream_task_span(tasks_data["myuuid"], host_data, False, True)

    finished_spans = opentelemetry.otel_exporter.get_finished_spans()
    assert [span.name for span in finished_spans] == ["mytask"]
    assert finished_spans[0].parent.span_id == opentelemetry.parent_span.get_span_context().span_id

    # the include span is emitted once the playbook span is ended
    include_result = TaskResult(host=None, task=task, return_data={}, task_fields={"args": {}})
    opentelemetry.finish_task(tasks_data, "included", include_result, "")
    assert len(opentelemetry.otel_exporter.get_finished_spans()) == 1

    opentelemetry.end_playbook_span(tasks_data, Status(status_code=StatusCode.OK), False, True)
    finished_spans = opentelemetry.otel_exporter.get_finished_spans()
    assert [span.name for span in finished_spans] == ["mytask", "mytask", "myplaybook.yml"]
    assert finished_spans[-1].status.status_code == StatusCode.OK


def test_task_result_is_streamed_as_soon_as_it_is_known(mocker):
    mocker.patch("ansible_collections.community.general.plugins.callback.opentelemetry.OTEL_LIBRARY_IMPORT_ERROR", None)
    callback = CallbackModule()
    callback.disable_logs = True
    callback.opentelemetry = MagicMock()

    task = Task()
    task.action = "myaction"
    task.no_log = False
    task._uuid = "myuuid"
    task.args = {}
    host = Mock("MockHost")
    host.name = "myhost"
    host._uuid = "myhost_uuid"
    callback.tasks_data["myuuid"] = TaskData("myuuid", "mytask", "/mypath", "myplay", "myaction", "")
    result = TaskResult(host=host, task=task, return_data={}, task_fields={"args": {}})

    callback.v2_runner_on_ok(result)

    callback.opentelemetry.finish_task.assert_called_once_with(callback.tasks_data, "ok", result, "")
    callback.opentelemetry.stream_task_span.assert_called_once_with(
        callback.tasks_data["myuuid"], callback.opentelemetry.finish_task.return_value, True, False
    )


def test_task_result_is_released_once_its_span_is_streamed(mocker):
    mocker.patch("ansible_collections.community.general.plugins.callback.opentelemetry.SpanKind", create=True)
    mocker.patch("ansible_collections.community.general.plugins.callback.opentelemetry.Status", create=True)
    mocker.patch("ansible_collections.community.general.plugins.callback.opentelemetry.StatusCode", create=True)
    mocker.patch(
        "ansible_collections.community.general.plugins.callback.opentelemetry.socket.gethostname",
        return_value="my-host",
    )
    mocker.patch(
        "ansible_collections.community.general.plugins.callback.opentelemetry.socket.gethostbyname",
        return_value="1.2.3.4",
    )
    opentelemetry = OpenTelemetrySource(display=None)
    opentelemetry.tracer = MagicMock()
    opentelemetry.parent_context = MagicMock()
    task_data = TaskData("myuuid", "mytask", "/mypath", "myplay", "myaction", {})
    finished_host_data = HostData("myhost_uuid", "myhost", "ok")
    task_data.add_host(finished_host_data)
    task_data.add_host(HostData("otherhost_uuid", "otherhost", "started"))

    opentelemetry.stream_task_span(task_data, finished_host_data, False, True)

    assert list(task_data.host_data) == ["otherhost_uuid"]
    opentelemetry.tracer.start_span.assert_called_once()


def test_unfinished_task_is_not_reported_as_success(mocker):
    mock_status = mocker.patch(
        "ansible_collections.community.general.plugins.callback.opentelemetry.Status", create=True
    )
    mock_status_code = mocker.patch(
        "ansible_collections.community.general.plugins.callback.opentelemetry.StatusCode", create=True
    )
    mocker.patch(
        "ansible_collections.community.general.plugins.callback.opentelemetry.socket.gethostname",
        return_value="my-host",
    )
    mocker.patch(
        "ansible_collections.community.general.plugins.callback.opentelemetry.socket.gethostbyname",
        return_value="1.2.3.4",
    )
    opentelemetry = OpenTelemetrySource(display=None)
    task_data = TaskData("myuuid", "mytask", "/mypath", "myplay", "myaction", {})
    host_data = HostData("myhost_uuid", "myhost", "started")
    span = MagicMock()

    opentelemetry.update_span_data(task_data, host_data, span, False, True)

    mock_status.assert_called_with(status_code=mock_status_code.UNSET, description="not finished")
    span.set_status.assert_called_once_with(mock_status.return_value)
    assert span.set_attributes.call_args[0][0]["ansible.task.message"] == "not finished"
    span.end.assert_called_once_with(end_time=None)


def generate_test_data(exception=None, msg=None, stderr=None, failed=False):
    res_data = OrderedDict()
    if exception:
        res_data["exception"] = exception
    if msg:
        res_data["msg"] = msg
    if stderr:
        res_data["stderr"] = stderr
    res_data["failed"] = failed
    return res_data

# Copyright (c) 2021, Victor Martinez <VictorMartinezRubio@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Victor Martinez (@v1v)  <VictorMartinezRubio@gmail.com>
name: opentelemetry
type: notification
short_description: Create distributed traces with OpenTelemetry
version_added: 3.7.0
description:
  - This callback creates distributed traces for each Ansible task with OpenTelemetry.
  - You can configure the OpenTelemetry exporter and SDK with environment variables.
  - See U(https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html).
  - See
    U(https://opentelemetry-python.readthedocs.io/en/latest/sdk/environment_variables.html#opentelemetry-sdk-environment-variables).
options:
  hide_task_arguments:
    default: false
    type: bool
    description:
      - Hide the arguments for a task.
    env:
      - name: ANSIBLE_OPENTELEMETRY_HIDE_TASK_ARGUMENTS
    ini:
      - section: callback_opentelemetry
        key: hide_task_arguments
        version_added: 5.3.0
  enable_from_environment:
    type: str
    description:
      - Whether to enable this callback only if the given environment variable exists and it is set to V(true).
      - This is handy when you use Configuration as Code and want to send distributed traces if running in the CI rather when
        running Ansible locally.
      - For such, it evaluates the given O(enable_from_environment) value as environment variable and if set to V(true) this
        plugin is enabled.
    env:
      - name: ANSIBLE_OPENTELEMETRY_ENABLE_FROM_ENVIRONMENT
    ini:
      - section: callback_opentelemetry
        key: enable_from_environment
        version_added: 5.3.0
    version_added: 3.8.0
  otel_service_name:
    default: ansible
    type: str
    description:
      - The service name resource attribute.
    env:
      - name: OTEL_SERVICE_NAME
    ini:
      - section: callback_opentelemetry
        key: otel_service_name
        version_added: 5.3.0
  traceparent:
    default: None
    type: str
    description:
      - The L(W3C Trace Context header traceparent,https://www.w3.org/TR/trace-context-1/#traceparent-header).
    env:
      - name: TRACEPARENT
  disable_logs:
    default: false
    type: bool
    description:
      - Disable sending logs.
    env:
      - name: ANSIBLE_OPENTELEMETRY_DISABLE_LOGS
    ini:
      - section: callback_opentelemetry
        key: disable_logs
    version_added: 5.8.0
  disable_attributes_in_logs:
    default: false
    type: bool
    description:
      - Disable populating span attributes to the logs.
    env:
      - name: ANSIBLE_OPENTELEMETRY_DISABLE_ATTRIBUTES_IN_LOGS
    ini:
      - section: callback_opentelemetry
        key: disable_attributes_in_logs
    version_added: 7.1.0
  store_spans_in_file:
    type: str
    description:
      - It stores the exported spans in the given file.
    env:
      - name: ANSIBLE_OPENTELEMETRY_STORE_SPANS_IN_FILE
    ini:
      - section: callback_opentelemetry
        key: store_spans_in_file
    version_added: 9.0.0
  otel_exporter_otlp_traces_protocol:
    type: str
    description:
      - E(OTEL_EXPORTER_OTLP_TRACES_PROTOCOL) represents the transport protocol for spans.
      - See
        U(https://opentelemetry-python.readthedocs.io/en/latest/sdk/environment_variables.html#envvar-OTEL_EXPORTER_OTLP_TRACES_PROTOCOL).
    default: grpc
    choices:
      - grpc
      - http/protobuf
    env:
      - name: OTEL_EXPORTER_OTLP_TRACES_PROTOCOL
    ini:
      - section: callback_opentelemetry
        key: otel_exporter_otlp_traces_protocol
    version_added: 9.0.0
requirements:
  - opentelemetry-api (Python library)
  - opentelemetry-exporter-otlp (Python library)
  - opentelemetry-sdk (Python library)
"""


EXAMPLES = r"""
examples: |-
  Enable the plugin in ansible.cfg:
    [defaults]
    callbacks_enabled = community.general.opentelemetry
    [callback_opentelemetry]
    enable_from_environment = ANSIBLE_OPENTELEMETRY_ENABLED

  Set the environment variable:
    export OTEL_EXPORTER_OTLP_ENDPOINT=<your endpoint (OTLP/HTTP)>
    export OTEL_EXPORTER_OTLP_HEADERS="authorization=Bearer your_otel_token"
    export OTEL_SERVICE_NAME=your_service_name
    export ANSIBLE_OPENTELEMETRY_ENABLED=true
"""

import getpass
import json
import os
import socket
import uuid
from collections import OrderedDict
from os.path import basename
from time import time_ns
from urllib.parse import urlparse

from ansible.errors import AnsibleError
from ansible.module_utils.ansible_release import __version__ as ansible_version
from ansible.plugins.callback import CallbackBase

OTEL_LIBRARY_IMPORT_ERROR: ImportError | None
try:
    from opentelemetry import trace
    from opentelemetry.trace import SpanKind
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GRPCOTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HTTPOTLPSpanExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.trace.status import Status, StatusCode
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
except ImportError as imp_exc:
    OTEL_LIBRARY_IMPORT_ERROR = imp_exc
else:
    OTEL_LIBRARY_IMPORT_ERROR = None


class TaskData:
    """
    Data about an individual task.
    """

    def __init__(self, uuid, name, path, play, action, args):
        self.uuid = uuid
        self.name = name
        self.path = path
        self.play = play
        self.host_data = OrderedDict()
        self.start = time_ns()
        self.action = action
        self.args = args
        self.dump = None

    def add_host(self, host):
        if host.uuid in self.host_data:
            if host.status == "included":
                # concatenate task include output from multiple items
                host.result = f"{self.host_data[host.uuid].result}\n{host.result}"
            else:
                return

        self.host_data[host.uuid] = host


class HostData:
    """
    Data about an individual host.
    """

    def __init__(self, uuid, name, status, result):
        self.uuid = uuid
        self.name = name
        self.status = status
        self.result = result
        self.finish = time_ns()


class OpenTelemetrySource:
    def __init__(self, display):
        self.ansible_playbook = ""
        self.session = str(uuid.uuid4())
        self.host = socket.gethostname()
        try:
            self.ip_address = socket.gethostbyname(socket.gethostname())
        except Exception:
            self.ip_address = None
        self.user = getpass.getuser()

        self._display = display

    def traceparent_context(self, traceparent):
        carrier = dict()
        carrier["traceparent"] = traceparent
        return TraceContextTextMapPropagator().extract(carrier=carrier)

    def start_task(self, tasks_data, hide_task_arguments, play_name, task):
        """record the start of a task for one or more hosts"""

        uuid = task._uuid

        if uuid in tasks_data:
            return

        name = task.get_name().strip()
        path = task.get_path()
        action = task.action
        args = None

        if not task.no_log and not hide_task_arguments:
            args = task.args

        tasks_data[uuid] = TaskData(uuid, name, path, play_name, action, args)

    def finish_task(self, tasks_data, status, result, dump):
        """record the results of a task for a single host"""

        task_uuid = result._task._uuid

        if hasattr(result, "_host") and result._host is not None:
            host_uuid = result._host._uuid
            host_name = result._host.name
        else:
            host_uuid = "include"
            host_name = "include"

        task = tasks_data[task_uuid]

        task.dump = dump
        task.add_host(HostData(host_uuid, host_name, status, result))

    def generate_distributed_traces(
        self,
        otel_service_name,
        ansible_playbook,
        tasks_data,
        status,
        traceparent,
        disable_logs,
        disable_attributes_in_logs,
        otel_exporter_otlp_traces_protocol,
        store_spans_in_file,
    ):
        """generate distributed traces from the collected TaskData and HostData"""

        tasks = []
        parent_start_time = None
        for task_uuid, task in tasks_data.items():
            if parent_start_time is None:
                parent_start_time = task.start
            tasks.append(task)

        trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: otel_service_name})))

        otel_exporter = None
        if store_spans_in_file:
            otel_exporter = InMemorySpanExporter()
            processor = SimpleSpanProcessor(otel_exporter)
        else:
            if otel_exporter_otlp_traces_protocol == "grpc":
                otel_exporter = GRPCOTLPSpanExporter()
            else:
                otel_exporter = HTTPOTLPSpanExporter()
            processor = BatchSpanProcessor(otel_exporter)

        trace.get_tracer_provider().add_span_processor(processor)

        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span(
            ansible_playbook,
            context=self.traceparent_context(traceparent),
            start_time=parent_start_time,
            kind=SpanKind.SERVER,
        ) as parent:
            parent.set_status(status)
            # Populate trace metadata attributes
            parent.set_attribute("ansible.version", ansible_version)
            parent.set_attribute("ansible.session", self.session)
            parent.set_attribute("ansible.host.name", self.host)
            if self.ip_address is not None:
                parent.set_attribute("ansible.host.ip", self.ip_address)
            parent.set_attribute("ansible.host.user", self.user)
            for task in tasks:
                for host_uuid, host_data in task.host_data.items():
                    with tracer.start_as_current_span(task.name, start_time=task.start, end_on_exit=False) as span:
                        self.update_span_data(task, host_data, span, disable_logs, disable_attributes_in_logs)

        return otel_exporter

    def update_span_data(self, task_data, host_data, span, disable_logs, disable_attributes_in_logs):
        """update the span with the given TaskData and HostData"""

        name = f"[{host_data.name}] {task_data.play}: {task_data.name}"

        message = "success"
        res = {}
        rc = 0
        status = Status(status_code=StatusCode.OK)
        if host_data.status != "included":
            # Support loops
            enriched_error_message = None
            if "results" in host_data.result._result:
                if host_data.status == "failed":
                    message = self.get_error_message_from_results(host_data.result._result["results"], task_data.action)
                    enriched_error_message = self.enrich_error_message_from_results(
                        host_data.result._result["results"], task_data.action
                    )
            else:
                res = host_data.result._result
                rc = res.get("rc", 0)
                if host_data.status == "failed":
                    message = self.get_error_message(res)
                    enriched_error_message = self.enrich_error_message(res)

            if host_data.status == "failed":
                status = Status(status_code=StatusCode.ERROR, description=message)
                # Record an exception with the task message
                span.record_exception(BaseException(enriched_error_message))
            elif host_data.status == "skipped":
                message = res["skip_reason"] if "skip_reason" in res else "skipped"
                status = Status(status_code=StatusCode.UNSET)
            elif host_data.status == "ignored":
                status = Status(status_code=StatusCode.UNSET)

        span.set_status(status)

        # Create the span and log attributes
        attributes = {
            "ansible.task.module": task_data.action,
            "ansible.task.message": message,
            "ansible.task.name": name,
            "ansible.task.result": rc,
            "ansible.task.host.name": host_data.name,
            "ansible.task.host.status": host_data.status,
        }
        if isinstance(task_data.args, dict) and "gather_facts" not in task_data.action:
            names = tuple(self.transform_ansible_unicode_to_str(k) for k in task_data.args.keys())
            values = tuple(self.transform_ansible_unicode_to_str(k) for k in task_data.args.values())
            attributes[("ansible.task.args.name")] = names
            attributes[("ansible.task.args.value")] = values

        self.set_span_attributes(span, attributes)

        # This will allow to enrich the service map
        self.add_attributes_for_service_map_if_possible(span, task_data)
        # Send logs
        if not disable_logs:
            # This will avoid populating span attributes to the logs
            span.add_event(task_data.dump, attributes={} if disable_attributes_in_logs else attributes)
        # Close span always
        span.end(end_time=host_data.finish)

    def set_span_attributes(self, span, attributes):
        """update the span attributes with the given attributes if not None"""

        if span is None and self._display is not None:
            self._display.warning("span object is None. Please double check if that is expected.")
        else:
            if attributes is not None:
                span.set_attributes(attributes)

    def add_attributes_for_service_map_if_possible(self, span, task_data):
        """Update the span attributes with the service that the task interacted with, if possible."""

        redacted_url = self.parse_and_redact_url_if_possible(task_data.args)
        if redacted_url:
            span.set_attribute("http.url", redacted_url.geturl())

    @staticmethod
    def parse_and_redact_url_if_possible(args):
        """Parse and redact the url, if possible."""

        try:
            parsed_url = urlparse(OpenTelemetrySource.url_from_args(args))
        except ValueError:
            return None

        if OpenTelemetrySource.is_valid_url(parsed_url):
            return OpenTelemetrySource.redact_user_password(parsed_url)
        return None

    @staticmethod
    def url_from_args(args):
        # the order matters
        url_args = (
            "url",
            "api_url",
            "baseurl",
            "repo",
            "server_url",
            "chart_repo_url",
            "registry_url",
            "endpoint",
            "uri",
            "updates_url",
        )
        for arg in url_args:
            if args is not None and args.get(arg):
                return args.get(arg)
        return ""

    @staticmethod
    def redact_user_password(url):
        return url._replace(netloc=url.hostname) if url.password else url

    @staticmethod
    def is_valid_url(url):
        if all([url.scheme, url.netloc, url.hostname]):
            return "{{" not in url.hostname
        return False

    @staticmethod
    def transform_ansible_unicode_to_str(value):
        parsed_url = urlparse(str(value))
        if OpenTelemetrySource.is_valid_url(parsed_url):
            return OpenTelemetrySource.redact_user_password(parsed_url).geturl()
        return str(value)

    @staticmethod
    def get_error_message(result):
        if result.get("exception") is not None:
            return OpenTelemetrySource._last_line(result["exception"])
        return result.get("msg", "failed")

    @staticmethod
    def get_error_message_from_results(results, action):
        for result in results:
            if result.get("failed", False):
                return f"{action}({result.get('item', 'none')}) - {OpenTelemetrySource.get_error_message(result)}"

    @staticmethod
    def _last_line(text):
        lines = text.strip().split("\n")
        return lines[-1]

    @staticmethod
    def enrich_error_message(result):
        message = result.get("msg", "failed")
        exception = result.get("exception")
        stderr = result.get("stderr")
        return f'message: "{message}"\nexception: "{exception}"\nstderr: "{stderr}"'

    @staticmethod
    def enrich_error_message_from_results(results, action):
        message = ""
        for result in results:
            if result.get("failed", False):
                message = f"{action}({result.get('item', 'none')}) - {OpenTelemetrySource.enrich_error_message(result)}\n{message}"
        return message


class CallbackModule(CallbackBase):
    """
    This callback creates distributed traces.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "community.general.opentelemetry"
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self, display=None):
        super().__init__(display=display)
        self.hide_task_arguments = None
        self.disable_attributes_in_logs = None
        self.disable_logs = None
        self.otel_service_name = None
        self.ansible_playbook = None
        self.play_name = None
        self.tasks_data = None
        self.errors = 0
        self.disabled = False
        self.traceparent = False
        self.store_spans_in_file = False
        self.otel_exporter_otlp_traces_protocol = None

        if OTEL_LIBRARY_IMPORT_ERROR:
            raise AnsibleError(
                "The `opentelemetry-api`, `opentelemetry-exporter-otlp` or `opentelemetry-sdk` must be installed to use this plugin"
            ) from OTEL_LIBRARY_IMPORT_ERROR

        self.tasks_data = OrderedDict()

        self.opentelemetry = OpenTelemetrySource(display=self._display)

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super().set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        environment_variable = self.get_option("enable_from_environment")
        if environment_variable is not None and os.environ.get(environment_variable, "false").lower() != "true":
            self.disabled = True
            self._display.warning(
                f"The `enable_from_environment` option has been set and {environment_variable} is not enabled. Disabling the `opentelemetry` callback plugin."
            )

        self.hide_task_arguments = self.get_option("hide_task_arguments")

        self.disable_attributes_in_logs = self.get_option("disable_attributes_in_logs")

        self.disable_logs = self.get_option("disable_logs")

        self.store_spans_in_file = self.get_option("store_spans_in_file")

        self.otel_service_name = self.get_option("otel_service_name")

        if not self.otel_service_name:
            self.otel_service_name = "ansible"

        # See https://github.com/open-telemetry/opentelemetry-specification/issues/740
        self.traceparent = self.get_option("traceparent")

        self.otel_exporter_otlp_traces_protocol = self.get_option("otel_exporter_otlp_traces_protocol")

    def dump_results(self, task, result):
        """dump the results if disable_logs is not enabled"""
        if self.disable_logs:
            return ""
        # ansible.builtin.uri contains the response in the json field
        save = dict(result._result)

        if "json" in save and task.action in ("ansible.builtin.uri", "ansible.legacy.uri", "uri"):
            save.pop("json")
        # ansible.builtin.slurp contains the response in the content field
        if "content" in save and task.action in ("ansible.builtin.slurp", "ansible.legacy.slurp", "slurp"):
            save.pop("content")
        return self._dump_results(save)

    def v2_playbook_on_start(self, playbook):
        self.ansible_playbook = basename(playbook._file_name)

    def v2_playbook_on_play_start(self, play):
        self.play_name = play.get_name()

    def v2_runner_on_no_hosts(self, task):
        self.opentelemetry.start_task(self.tasks_data, self.hide_task_arguments, self.play_name, task)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.opentelemetry.start_task(self.tasks_data, self.hide_task_arguments, self.play_name, task)

    def v2_playbook_on_cleanup_task_start(self, task):
        self.opentelemetry.start_task(self.tasks_data, self.hide_task_arguments, self.play_name, task)

    def v2_playbook_on_handler_task_start(self, task):
        self.opentelemetry.start_task(self.tasks_data, self.hide_task_arguments, self.play_name, task)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if ignore_errors:
            status = "ignored"
        else:
            status = "failed"
            self.errors += 1

        self.opentelemetry.finish_task(
            self.tasks_data, status, result, self.dump_results(self.tasks_data[result._task._uuid], result)
        )

    def v2_runner_on_ok(self, result):
        self.opentelemetry.finish_task(
            self.tasks_data, "ok", result, self.dump_results(self.tasks_data[result._task._uuid], result)
        )

    def v2_runner_on_skipped(self, result):
        self.opentelemetry.finish_task(
            self.tasks_data, "skipped", result, self.dump_results(self.tasks_data[result._task._uuid], result)
        )

    def v2_playbook_on_include(self, included_file):
        self.opentelemetry.finish_task(self.tasks_data, "included", included_file, "")

    def v2_playbook_on_stats(self, stats):
        if self.errors == 0:
            status = Status(status_code=StatusCode.OK)
        else:
            status = Status(status_code=StatusCode.ERROR)
        otel_exporter = self.opentelemetry.generate_distributed_traces(
            self.otel_service_name,
            self.ansible_playbook,
            self.tasks_data,
            status,
            self.traceparent,
            self.disable_logs,
            self.disable_attributes_in_logs,
            self.otel_exporter_otlp_traces_protocol,
            self.store_spans_in_file,
        )

        if self.store_spans_in_file:
            spans = [json.loads(span.to_json()) for span in otel_exporter.get_finished_spans()]
            with open(self.store_spans_in_file, "w", encoding="utf-8") as output:
                json.dump({"spans": spans}, output, indent=4)

    def v2_runner_on_async_failed(self, result, **kwargs):
        self.errors += 1

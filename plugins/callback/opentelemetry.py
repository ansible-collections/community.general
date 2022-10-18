# -*- coding: utf-8 -*-
# Copyright (c) 2021, Victor Martinez <VictorMartinezRubio@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Victor Martinez (@v1v)  <VictorMartinezRubio@gmail.com>
    name: opentelemetry
    type: notification
    short_description: Create distributed traces with OpenTelemetry
    version_added: 3.7.0
    description:
      - This callback creates distributed traces for each Ansible task with OpenTelemetry.
      - You can configure the OpenTelemetry exporter and SDK with environment variables.
      - See U(https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html).
      - See U(https://opentelemetry-python.readthedocs.io/en/latest/sdk/environment_variables.html#opentelemetry-sdk-environment-variables).
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
          - Whether to enable this callback only if the given environment variable exists and it is set to C(true).
          - This is handy when you use Configuration as Code and want to send distributed traces
            if running in the CI rather when running Ansible locally.
          - For such, it evaluates the given I(enable_from_environment) value as environment variable
            and if set to true this plugin will be enabled.
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
    requirements:
      - opentelemetry-api (Python library)
      - opentelemetry-exporter-otlp (Python library)
      - opentelemetry-sdk (Python library)
'''


EXAMPLES = '''
examples: |
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
'''

import getpass
import os
import socket
import sys
import time
import uuid

from collections import OrderedDict
from os.path import basename

from ansible.errors import AnsibleError
from ansible.module_utils.six import raise_from
from ansible.module_utils.six.moves.urllib.parse import urlparse
from ansible.plugins.callback import CallbackBase

try:
    from opentelemetry import trace
    from opentelemetry.trace import SpanKind
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.trace.status import Status, StatusCode
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor
    )

    # Support for opentelemetry-api <= 1.12
    try:
        from opentelemetry.util._time import _time_ns
    except ImportError as imp_exc:
        OTEL_LIBRARY_TIME_NS_ERROR = imp_exc
    else:
        OTEL_LIBRARY_TIME_NS_ERROR = None

except ImportError as imp_exc:
    OTEL_LIBRARY_IMPORT_ERROR = imp_exc
    OTEL_LIBRARY_TIME_NS_ERROR = imp_exc
else:
    OTEL_LIBRARY_IMPORT_ERROR = None


if sys.version_info >= (3, 7):
    time_ns = time.time_ns
elif not OTEL_LIBRARY_TIME_NS_ERROR:
    time_ns = _time_ns
else:
    def time_ns():
        # Support versions older than 3.7 with opentelemetry-api > 1.12
        return int(time.time() * 1e9)


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
            if host.status == 'included':
                # concatenate task include output from multiple items
                host.result = '%s\n%s' % (self.host_data[host.uuid].result, host.result)
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


class OpenTelemetrySource(object):
    def __init__(self, display):
        self.ansible_playbook = ""
        self.ansible_version = None
        self.session = str(uuid.uuid4())
        self.host = socket.gethostname()
        try:
            self.ip_address = socket.gethostbyname(socket.gethostname())
        except Exception as e:
            self.ip_address = None
        self.user = getpass.getuser()

        self._display = display

    def traceparent_context(self, traceparent):
        carrier = dict()
        carrier['traceparent'] = traceparent
        return TraceContextTextMapPropagator().extract(carrier=carrier)

    def start_task(self, tasks_data, hide_task_arguments, play_name, task):
        """ record the start of a task for one or more hosts """

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
        """ record the results of a task for a single host """

        task_uuid = result._task._uuid

        if hasattr(result, '_host') and result._host is not None:
            host_uuid = result._host._uuid
            host_name = result._host.name
        else:
            host_uuid = 'include'
            host_name = 'include'

        task = tasks_data[task_uuid]

        if self.ansible_version is None and hasattr(result, '_task_fields') and result._task_fields['args'].get('_ansible_version'):
            self.ansible_version = result._task_fields['args'].get('_ansible_version')

        task.dump = dump
        task.add_host(HostData(host_uuid, host_name, status, result))

    def generate_distributed_traces(self, otel_service_name, ansible_playbook, tasks_data, status, traceparent, disable_logs):
        """ generate distributed traces from the collected TaskData and HostData """

        tasks = []
        parent_start_time = None
        for task_uuid, task in tasks_data.items():
            if parent_start_time is None:
                parent_start_time = task.start
            tasks.append(task)

        trace.set_tracer_provider(
            TracerProvider(
                resource=Resource.create({SERVICE_NAME: otel_service_name})
            )
        )

        processor = BatchSpanProcessor(OTLPSpanExporter())

        trace.get_tracer_provider().add_span_processor(processor)

        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span(ansible_playbook, context=self.traceparent_context(traceparent),
                                          start_time=parent_start_time, kind=SpanKind.SERVER) as parent:
            parent.set_status(status)
            # Populate trace metadata attributes
            if self.ansible_version is not None:
                parent.set_attribute("ansible.version", self.ansible_version)
            parent.set_attribute("ansible.session", self.session)
            parent.set_attribute("ansible.host.name", self.host)
            if self.ip_address is not None:
                parent.set_attribute("ansible.host.ip", self.ip_address)
            parent.set_attribute("ansible.host.user", self.user)
            for task in tasks:
                for host_uuid, host_data in task.host_data.items():
                    with tracer.start_as_current_span(task.name, start_time=task.start, end_on_exit=False) as span:
                        self.update_span_data(task, host_data, span, disable_logs)

    def update_span_data(self, task_data, host_data, span, disable_logs):
        """ update the span with the given TaskData and HostData """

        name = '[%s] %s: %s' % (host_data.name, task_data.play, task_data.name)

        message = 'success'
        res = {}
        rc = 0
        status = Status(status_code=StatusCode.OK)
        if host_data.status != 'included':
            # Support loops
            if 'results' in host_data.result._result:
                if host_data.status == 'failed':
                    message = self.get_error_message_from_results(host_data.result._result['results'], task_data.action)
                    enriched_error_message = self.enrich_error_message_from_results(host_data.result._result['results'], task_data.action)
            else:
                res = host_data.result._result
                rc = res.get('rc', 0)
                if host_data.status == 'failed':
                    message = self.get_error_message(res)
                    enriched_error_message = self.enrich_error_message(res)

            if host_data.status == 'failed':
                status = Status(status_code=StatusCode.ERROR, description=message)
                # Record an exception with the task message
                span.record_exception(BaseException(enriched_error_message))
            elif host_data.status == 'skipped':
                message = res['skip_reason'] if 'skip_reason' in res else 'skipped'
                status = Status(status_code=StatusCode.UNSET)
            elif host_data.status == 'ignored':
                status = Status(status_code=StatusCode.UNSET)

        span.set_status(status)
        if isinstance(task_data.args, dict) and "gather_facts" not in task_data.action:
            names = tuple(self.transform_ansible_unicode_to_str(k) for k in task_data.args.keys())
            values = tuple(self.transform_ansible_unicode_to_str(k) for k in task_data.args.values())
            self.set_span_attribute(span, ("ansible.task.args.name"), names)
            self.set_span_attribute(span, ("ansible.task.args.value"), values)
        self.set_span_attribute(span, "ansible.task.module", task_data.action)
        self.set_span_attribute(span, "ansible.task.message", message)
        self.set_span_attribute(span, "ansible.task.name", name)
        self.set_span_attribute(span, "ansible.task.result", rc)
        self.set_span_attribute(span, "ansible.task.host.name", host_data.name)
        self.set_span_attribute(span, "ansible.task.host.status", host_data.status)
        # This will allow to enrich the service map
        self.add_attributes_for_service_map_if_possible(span, task_data)
        # Send logs
        if not disable_logs:
            span.add_event(task_data.dump)
        span.end(end_time=host_data.finish)

    def set_span_attribute(self, span, attributeName, attributeValue):
        """ update the span attribute with the given attribute and value if not None """

        if span is None and self._display is not None:
            self._display.warning('span object is None. Please double check if that is expected.')
        else:
            if attributeValue is not None:
                span.set_attribute(attributeName, attributeValue)

    def add_attributes_for_service_map_if_possible(self, span, task_data):
        """Update the span attributes with the service that the task interacted with, if possible."""

        redacted_url = self.parse_and_redact_url_if_possible(task_data.args)
        if redacted_url:
            self.set_span_attribute(span, "http.url", redacted_url.geturl())

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
        url_args = ("url", "api_url", "baseurl", "repo", "server_url", "chart_repo_url", "registry_url", "endpoint", "uri", "updates_url")
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
        if result.get('exception') is not None:
            return OpenTelemetrySource._last_line(result['exception'])
        return result.get('msg', 'failed')

    @staticmethod
    def get_error_message_from_results(results, action):
        for result in results:
            if result.get('failed', False):
                return ('{0}({1}) - {2}').format(action, result.get('item', 'none'), OpenTelemetrySource.get_error_message(result))

    @staticmethod
    def _last_line(text):
        lines = text.strip().split('\n')
        return lines[-1]

    @staticmethod
    def enrich_error_message(result):
        message = result.get('msg', 'failed')
        exception = result.get('exception')
        stderr = result.get('stderr')
        return ('message: "{0}"\nexception: "{1}"\nstderr: "{2}"').format(message, exception, stderr)

    @staticmethod
    def enrich_error_message_from_results(results, action):
        message = ""
        for result in results:
            if result.get('failed', False):
                message = ('{0}({1}) - {2}\n{3}').format(action, result.get('item', 'none'), OpenTelemetrySource.enrich_error_message(result), message)
        return message


class CallbackModule(CallbackBase):
    """
    This callback creates distributed traces.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'community.general.opentelemetry'
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.hide_task_arguments = None
        self.disable_logs = None
        self.otel_service_name = None
        self.ansible_playbook = None
        self.play_name = None
        self.tasks_data = None
        self.errors = 0
        self.disabled = False
        self.traceparent = False

        if OTEL_LIBRARY_IMPORT_ERROR:
            raise_from(
                AnsibleError('The `opentelemetry-api`, `opentelemetry-exporter-otlp` or `opentelemetry-sdk` must be installed to use this plugin'),
                OTEL_LIBRARY_IMPORT_ERROR)

        self.tasks_data = OrderedDict()

        self.opentelemetry = OpenTelemetrySource(display=self._display)

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys,
                                                var_options=var_options,
                                                direct=direct)

        environment_variable = self.get_option('enable_from_environment')
        if environment_variable is not None and os.environ.get(environment_variable, 'false').lower() != 'true':
            self.disabled = True
            self._display.warning("The `enable_from_environment` option has been set and {0} is not enabled. "
                                  "Disabling the `opentelemetry` callback plugin.".format(environment_variable))

        self.hide_task_arguments = self.get_option('hide_task_arguments')

        self.disable_logs = self.get_option('disable_logs')

        self.otel_service_name = self.get_option('otel_service_name')

        if not self.otel_service_name:
            self.otel_service_name = 'ansible'

        # See https://github.com/open-telemetry/opentelemetry-specification/issues/740
        self.traceparent = self.get_option('traceparent')

    def v2_playbook_on_start(self, playbook):
        self.ansible_playbook = basename(playbook._file_name)

    def v2_playbook_on_play_start(self, play):
        self.play_name = play.get_name()

    def v2_runner_on_no_hosts(self, task):
        self.opentelemetry.start_task(
            self.tasks_data,
            self.hide_task_arguments,
            self.play_name,
            task
        )

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.opentelemetry.start_task(
            self.tasks_data,
            self.hide_task_arguments,
            self.play_name,
            task
        )

    def v2_playbook_on_cleanup_task_start(self, task):
        self.opentelemetry.start_task(
            self.tasks_data,
            self.hide_task_arguments,
            self.play_name,
            task
        )

    def v2_playbook_on_handler_task_start(self, task):
        self.opentelemetry.start_task(
            self.tasks_data,
            self.hide_task_arguments,
            self.play_name,
            task
        )

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if ignore_errors:
            status = 'ignored'
        else:
            status = 'failed'
            self.errors += 1

        self.opentelemetry.finish_task(
            self.tasks_data,
            status,
            result,
            self._dump_results(result._result)
        )

    def v2_runner_on_ok(self, result):
        self.opentelemetry.finish_task(
            self.tasks_data,
            'ok',
            result,
            self._dump_results(result._result)
        )

    def v2_runner_on_skipped(self, result):
        self.opentelemetry.finish_task(
            self.tasks_data,
            'skipped',
            result,
            self._dump_results(result._result)
        )

    def v2_playbook_on_include(self, included_file):
        self.opentelemetry.finish_task(
            self.tasks_data,
            'included',
            included_file,
            ""
        )

    def v2_playbook_on_stats(self, stats):
        if self.errors == 0:
            status = Status(status_code=StatusCode.OK)
        else:
            status = Status(status_code=StatusCode.ERROR)
        self.opentelemetry.generate_distributed_traces(
            self.otel_service_name,
            self.ansible_playbook,
            self.tasks_data,
            status,
            self.traceparent,
            self.disable_logs
        )

    def v2_runner_on_async_failed(self, result, **kwargs):
        self.errors += 1

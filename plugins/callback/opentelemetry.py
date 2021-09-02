# (C) 2021, Victor Martinez <VictorMartinezRubio@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Victor Martinez (@v1v)  <VictorMartinezRubio@gmail.com>
    name: opentelemetry
    type: notification
    short_description: Create distributed traces with OpenTelemetry
    version_added: 3.5.0
    description:
      - This callback create distributed traces for each Ansible task with OpenTelemetry.
      - You can configure the OTEL exporter with environment variables. See U(https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html).
    options:
      include_setup_tasks:
        default: true
        description:
          - Should the setup tasks be included in the distributed traces.
        env:
          - name: OPENTELEMETRY_INCLUDE_SETUP_TASKS
      hide_task_arguments:
        default: false
        description:
          - Hide the arguments for a task.
        env:
          - name: OPENTELEMETRY_HIDE_TASK_ARGUMENTS
      console_output:
        default: false
        description:
          - Print distributed traces in the terminal.
        env:
          - name: OPENTELEMETRY_CONSOLE_OUTPUT
      otel_service_name:
        default: ansible
        description:
          - The service name resource attribute.
        env:
          - name: OTEL_SERVICE_NAME
    requirements:
      - opentelemetry-api (python lib)
      - opentelemetry-exporter-otlp (python lib)
      - opentelemetry-sdk (python lib)
'''


EXAMPLES = '''
examples: |
  Whitelist the plugin in ansible.cfg:
    [defaults]
    callback_whitelist = community.general.opentelemetry

  Set the environment variable:
    export OTEL_EXPORTER_OTLP_ENDPOINT=<your endpoint (OTLP/HTTP)>
    export OTEL_EXPORTER_OTLP_HEADERS="authorization=Bearer your_otel_token"
    export OTEL_SERVICE_NAME=your_service_name
'''

import getpass
import os
import socket
import sys
import time
import uuid

from os.path import basename

from ansible import constants as C
from ansible.plugins.callback import CallbackBase

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.trace.status import Status, StatusCode
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        ConsoleSpanExporter,
        SimpleSpanProcessor,
        BatchSpanProcessor
    )
    from opentelemetry.util._time import _time_ns
    HAS_OTEL = True
except ImportError:
    HAS_OTEL = False

try:
    from collections import OrderedDict
    HAS_ORDERED_DICT = True
except ImportError:
    try:
        from ordereddict import OrderedDict
        HAS_ORDERED_DICT = True
    except ImportError:
        HAS_ORDERED_DICT = False


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
            args = ', '.join(('%s=%s' % a for a in task.args.items()))

        tasks_data[uuid] = TaskData(uuid, name, path, play_name, action, args)

    def finish_task(self, tasks_data, status, result):
        """ record the results of a task for a single host """

        task_uuid = result._task._uuid

        if hasattr(result, '_host') and result._host is not None:
            host_uuid = result._host._uuid
            host_name = result._host.name
        else:
            host_uuid = 'include'
            host_name = 'include'

        task = tasks_data[task_uuid]

        if self.ansible_version is None and result._task_fields['args'].get('_ansible_version'):
            self.ansible_version = result._task_fields['args'].get('_ansible_version')

        # ignore failure if expected and toggle result if asked for
        if status == 'failed' and 'EXPECTED FAILURE' in task.name:
            status = 'ok'
        elif 'TOGGLE RESULT' in task.name:
            if status == 'failed':
                status = 'ok'
            elif status == 'ok':
                status = 'failed'

        task.add_host(HostData(host_uuid, host_name, status, result))

    def generate_distributed_traces(self, insecure_otel_exporter, include_setup_tasks, otel_service_name, console_output, ansible_playbook, tasks_data, status):
        """ generate distributed traces from the collected TaskData and HostData """

        tasks = []
        parent_start_time = None
        for task_uuid, task in tasks_data.items():
            if parent_start_time is None:
                parent_start_time = task.start
            if not include_setup_tasks and task.action == 'setup':
                # if task.action in C._ACTION_SETUP:  supported from 2.11.0
                continue
            tasks.append(task)

        trace.set_tracer_provider(
            TracerProvider(
                resource=Resource.create({SERVICE_NAME: otel_service_name})
            )
        )

        if console_output:
            processor = SimpleSpanProcessor(ConsoleSpanExporter())
        else:
            processor = BatchSpanProcessor(OTLPSpanExporter(insecure=insecure_otel_exporter))

        trace.get_tracer_provider().add_span_processor(processor)

        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span(ansible_playbook, start_time=parent_start_time) as parent:
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
                        self.update_span_data(task, host_data, span)

    def update_span_data(self, task_data, host_data, span):
        """ update the span with the given TaskData and HostData """

        name = '[%s] %s: %s' % (host_data.name, task_data.play, task_data.name)

        message = 'success'
        status = Status(status_code=StatusCode.OK)
        if host_data.status == 'included':
            rc = 0
        else:
            res = host_data.result._result
            rc = res.get('rc', 0)
            if host_data.status == 'failed':
                if 'exception' in res:
                    message = res['exception'].strip().split('\n')[-1]
                elif 'msg' in res:
                    message = res['msg']
                else:
                    message = 'failed'
                status = Status(status_code=StatusCode.ERROR)
            elif host_data.status == 'skipped':
                if 'skip_reason' in res:
                    message = res['skip_reason']
                else:
                    message = 'skipped'
                status = Status(status_code=StatusCode.UNSET)

        span.set_status(status)
        self.set_span_attribute(span, "ansible.task.args", task_data.args)
        self.set_span_attribute(span, "ansible.task.module", task_data.action)
        self.set_span_attribute(span, "ansible.task.message", message)
        self.set_span_attribute(span, "ansible.task.name", name)
        self.set_span_attribute(span, "ansible.task.result", rc)
        self.set_span_attribute(span, "ansible.task.host.name", host_data.name)
        self.set_span_attribute(span, "ansible.task.host.status", host_data.status)
        span.end(end_time=host_data.finish)

    def set_span_attribute(self, span, attributeName, attributeValue):
        """ update the span attribute with the given attribute and value if not None """

        if span is None and self._display is not None:
            self._display.warning('span object is None. Please double check if that is expected.')
        else:
            if attributeValue is not None:
                span.set_attribute(attributeName, attributeValue)


class CallbackModule(CallbackBase):
    """
    This callback creates distributed traces.
    This plugin makes use of the following environment variables:
        OPENTELEMETRY_INCLUDE_SETUP_TASKS (optional): Should the setup tasks be included in the distributed traces
                                     Default: true
        OPENTELEMETRY_HIDE_TASK_ARGUMENTS (optional): Hide the arguments for a task
                                     Default: false
        OTEL_SERVICE_NAME (optional): The service name resource attribute.
                                     Default: ansible
        OTEL_CONSOLE_OUTPUT (optional): Print distributed traces in the terminal.
                                     Default: true
    Requires:
        opentelemetry-api
        opentelemetry-exporter-otlp
        opentelemetry-sdk
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'community.general.opentelemetry'
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.include_setup_tasks = None
        self.hide_task_arguments = None
        self.otel_service_name = None
        self.console_output = None
        self.insecure_otel_exporter = None
        self.ansible_playbook = None
        self.play_name = None
        self.tasks_data = None
        self.errors = 0
        self.disabled = False

        if not HAS_OTEL:
            self.disabled = True
            self._display.warning('The `opentelemetry-api`, `opentelemetry-exporter-otlp` or `opentelemetry-sdk` python modules are not installed. '
                                  'Disabling the `opentelemetry` callback plugin.')

        if HAS_ORDERED_DICT:
            self.tasks_data = OrderedDict()
        else:
            self.disabled = True
            self._display.warning('The `ordereddict` python module is not installed. '
                                  'Disabling the `opentelemetry` callback plugin.')

        self.opentelemetry = OpenTelemetrySource(display=self._display)

    def transform_option_to_boolean_or_default(self, option_name, default):
        """ Look for the given option and if a string boolean then convert to a boolean type """

        value = self.get_option(option_name)
        if value is None:
            return default
        if isinstance(value, str):
            return value.lower() in ['true']
        return value

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys,
                                                var_options=var_options,
                                                direct=direct)

        self.include_setup_tasks = self.transform_option_to_boolean_or_default('include_setup_tasks', True)

        self.hide_task_arguments = self.transform_option_to_boolean_or_default('hide_task_arguments', False)

        self.otel_service_name = self.get_option('otel_service_name')

        if self.otel_service_name is None:
            self.otel_service_name = 'ansible'

        self.console_output = self.transform_option_to_boolean_or_default('console_output', False)

        # See https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/exporter.md#configuration-options
        self.insecure_otel_exporter = os.getenv('OTEL_EXPORTER_OTLP_INSECURE', 'false').lower() == 'true'

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
        self.errors += 1
        self.opentelemetry.finish_task(
            self.tasks_data,
            'failed',
            result
        )

    def v2_runner_on_ok(self, result):
        self.opentelemetry.finish_task(
            self.tasks_data,
            'ok',
            result
        )

    def v2_runner_on_skipped(self, result):
        self.opentelemetry.finish_task(
            self.tasks_data,
            'skipped',
            result
        )

    def v2_playbook_on_include(self, included_file):
        self.opentelemetry.finish_task(
            self.tasks_data,
            'included',
            included_file
        )

    def v2_playbook_on_stats(self, stats):
        if self.errors == 0:
            status = Status(status_code=StatusCode.OK)
        else:
            status = Status(status_code=StatusCode.ERROR)
        self.opentelemetry.generate_distributed_traces(
            self.insecure_otel_exporter,
            self.include_setup_tasks,
            self.otel_service_name,
            self.console_output,
            self.ansible_playbook,
            self.tasks_data,
            status
        )

    def v2_runner_on_async_failed(self, result, **kwargs):
        self.errors += 1


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
        if sys.version_info >= (3, 7):
            self.start = time.time_ns()
        else:
            self.start = _time_ns()
        self.action = action
        self.args = args

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
        if sys.version_info >= (3, 7):
            self.finish = time.time_ns()
        else:
            self.finish = _time_ns()

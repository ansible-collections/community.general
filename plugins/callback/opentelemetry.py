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
    options:
      include_setup_tasks:
        default: true
        description:
          - Should the setup tasks be included in the distributed traces
        env:
          - name: OPENTELEMETRY_INCLUDE_SETUP_TASKS
      hide_task_arguments:
        default: false
        description:
          - Hide the arguments for a task
        env:
          - name: OPENTELEMETRY_HIDE_TASK_ARGUMENTS
      service_name:
        default: ansible
        description:
          - Hide the arguments for a task
        env:
          - name: OTEL_SERVICE_NAME
      otel_exporter:
        default: false
        description:
          - Use the OTEL exporter and its environment variables. See U(https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html).
        env:
          - name: OTEL_EXPORTER
      insecure_otel_exporter:
        default: false
        description:
          - Use insecure connection.
        env:
          - name: OTEL_EXPORTER_INSECURE
    requirements:
      - opentelemetry-api (python lib)
      - opentelemetry-exporter-otlp (python lib)
      - opentelemetry-sdk (python lib)
'''

import os
import sys
import time

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


class CallbackModule(CallbackBase):
    """
    This callback creates distributed traces.
    This plugin makes use of the following environment variables:
        OPENTELEMETRY_INCLUDE_SETUP_TASKS (optional): Should the setup tasks be included
                                     Default: true
        OPENTELEMETRY_HIDE_TASK_ARGUMENTS (optional): Hide the arguments for a task
                                     Default: false
        OTEL_SERVICE_NAME (optional): The service name
                                     Default: ansible
        OTEL_EXPORTER (optional): Use the OTEL exporter and its environment variables. https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html
                                     Default: false
        OTEL_EXPORTER_INSECURE (optional): Insecure connection
                                     Default: false
    Requires:
        opentelemetry-api
        opentelemetry-exporter-otlp
        opentelemetry-sdk
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'community.general.opentelemetry'
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self):
        super(CallbackModule, self).__init__()

        self._include_setup_tasks = os.getenv('OPENTELEMETRY_INCLUDE_SETUP_TASKS', 'true').lower() == 'true'
        self._hide_task_arguments = os.getenv('OPENTELEMETRY_HIDE_TASK_ARGUMENTS', 'false').lower() == 'true'
        self._service = os.getenv('OTEL_SERVICE_NAME', 'ansible').lower()
        self._otel_exporter = os.getenv('OTEL_EXPORTER', 'false').lower() == 'true'
        self._insecure_otel_exporter = os.getenv('OTEL_EXPORTER_INSECURE', 'false').lower() == 'true'
        self._playbook_path = None
        self._playbook_name = None
        self._play_name = None
        self._task_data = None
        self.errors = 0
        self.disabled = False

        if not HAS_OTEL:
            self.disabled = True
            self._display.warning('The `opentelemetry-api`, `opentelemetry-exporter-otlp` or `opentelemetry-sdk` python modules are not installed. '
                                  'Disabling the `opentelemetry` callback plugin.')

        if not self._otel_exporter:
            self.disabled = True
            self._display.warning('The `OTEL_EXPORTER` has been set to False.'
                                  'Disabling the `opentelemetry` callback plugin.')

        if HAS_ORDERED_DICT:
            self._task_data = OrderedDict()
        else:
            self.disabled = True
            self._display.warning('The `ordereddict` python module is not installed. '
                                  'Disabling the `opentelemetry` callback plugin.')


    def _start_task(self, task):
        """ record the start of a task for one or more hosts """

        uuid = task._uuid

        if uuid in self._task_data:
            return

        play = self._play_name
        name = task.get_name().strip()
        path = task.get_path()
        action = task.action
        args = None

        if not task.no_log and not self._hide_task_arguments:
            args = ', '.join(('%s=%s' % a for a in task.args.items()))

        self._task_data[uuid] = TaskData(uuid, name, path, play, action, args)

    def _finish_task(self, status, result):
        """ record the results of a task for a single host """

        task_uuid = result._task._uuid

        if hasattr(result, '_host'):
            host_uuid = result._host._uuid
            host_name = result._host.name
        else:
            host_uuid = 'include'
            host_name = 'include'

        task_data = self._task_data[task_uuid]

        # ignore failure if expected and toggle result if asked for
        if status == 'failed' and 'EXPECTED FAILURE' in task_data.name:
            status = 'ok'
        elif 'TOGGLE RESULT' in task_data.name:
            if status == 'failed':
                status = 'ok'
            elif status == 'ok':
                status = 'failed'

        task_data.add_host(HostData(host_uuid, host_name, status, result))

    def _update_span_data(self, task_data, host_data, span):
        """ update the span with the given TaskData and HostData """

        name = '[%s] %s: %s' % (host_data.name, task_data.play, task_data.name)

        message = "success"
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
        self._set_span_attribute(span, "ansible.task.args", task_data.args)
        self._set_span_attribute(span, "ansible.task.module", task_data.action)
        self._set_span_attribute(span, "ansible.task.message", message)
        self._set_span_attribute(span, "ansible.task.name", name)
        self._set_span_attribute(span, "ansible.task.result", rc)
        self._set_span_attribute(span, "ansible.task.host.name", host_data.name)
        self._set_span_attribute(span, "ansible.task.host.status", host_data.status)
        span.end(end_time=host_data.finish)

    def _set_span_attribute(self, span, attributeName, attributeValue):
        """ update the span attribute with the given attribute and value if not None """

        if span is None:
            self._display.warning('span object is None. Please double check if that is expected.')
        else:
            if not attributeValue is None:
                span.set_attribute(attributeName, attributeValue)

    def _generate_distributed_traces(self, status):
        """ generate distributed traces from the collected TaskData and HostData """

        tasks = []
        parent_start_time = None
        for task_uuid, task_data in self._task_data.items():
            if parent_start_time is None:
                parent_start_time = task_data.start
            if not self._include_setup_tasks and task_data.action == 'setup':
                ##if task_data.action in C._ACTION_SETUP:  supported from 2.11.0
                continue
            tasks.append(task_data)

        trace.set_tracer_provider(
            TracerProvider(
                resource=Resource.create({SERVICE_NAME: self._service})
            )
        )
        processor = SimpleSpanProcessor(ConsoleSpanExporter())

        if self._otel_exporter:
            processor = BatchSpanProcessor(OTLPSpanExporter(insecure=self._insecure_otel_exporter))

        trace.get_tracer_provider().add_span_processor(processor)

        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span(self._playbook_name, start_time=parent_start_time) as parent:
            parent.set_status(status)
            for task_data in tasks:
                for host_uuid, host_data in task_data.host_data.items():
                    with tracer.start_as_current_span(task_data.name, start_time=task_data.start, end_on_exit=False) as span:
                        self._update_span_data(task_data, host_data, span)

    def v2_playbook_on_start(self, playbook):
        self._playbook_path = playbook._file_name
        self._playbook_name = os.path.splitext(os.path.basename(self._playbook_path))[0]

    def v2_playbook_on_play_start(self, play):
        self._play_name = play.get_name()

    def v2_runner_on_no_hosts(self, task):
        self._start_task(task)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._start_task(task)

    def v2_playbook_on_cleanup_task_start(self, task):
        self._start_task(task)

    def v2_playbook_on_handler_task_start(self, task):
        self._start_task(task)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.errors += 1
        self._finish_task('failed', result)

    def v2_runner_on_ok(self, result):
        self._finish_task('ok', result)

    def v2_runner_on_skipped(self, result):
        self._finish_task('skipped', result)

    def v2_playbook_on_include(self, included_file):
        self._finish_task('included', included_file)

    def v2_playbook_on_stats(self, stats):
        if self.errors == 0:
            status = Status(status_code=StatusCode.OK)
        else:
            status = Status(status_code=StatusCode.ERROR)
        self._generate_distributed_traces(status)

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

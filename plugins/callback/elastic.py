# Copyright (c) 2021, Victor Martinez <VictorMartinezRubio@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Victor Martinez (@v1v)  <VictorMartinezRubio@gmail.com>
name: elastic
type: notification
short_description: Create distributed traces for each Ansible task in Elastic APM
version_added: 3.8.0
description:
  - This callback creates distributed traces for each Ansible task in Elastic APM.
  - You can configure the plugin with environment variables.
  - See U(https://www.elastic.co/guide/en/apm/agent/python/current/configuration.html).
options:
  hide_task_arguments:
    default: false
    type: bool
    description:
      - Hide the arguments for a task.
    env:
      - name: ANSIBLE_OPENTELEMETRY_HIDE_TASK_ARGUMENTS
  apm_service_name:
    default: ansible
    type: str
    description:
      - The service name resource attribute.
    env:
      - name: ELASTIC_APM_SERVICE_NAME
  apm_server_url:
    type: str
    description:
      - Use the APM server and its environment variables.
    env:
      - name: ELASTIC_APM_SERVER_URL
  apm_secret_token:
    type: str
    description:
      - Use the APM server token.
    env:
      - name: ELASTIC_APM_SECRET_TOKEN
  apm_api_key:
    type: str
    description:
      - Use the APM API key.
    env:
      - name: ELASTIC_APM_API_KEY
  apm_verify_server_cert:
    default: true
    type: bool
    description:
      - Verifies the SSL certificate if an HTTPS connection.
    env:
      - name: ELASTIC_APM_VERIFY_SERVER_CERT
  traceparent:
    type: str
    description:
      - The L(W3C Trace Context header traceparent,https://www.w3.org/TR/trace-context-1/#traceparent-header).
    env:
      - name: TRACEPARENT
requirements:
  - elastic-apm (Python library)
"""


EXAMPLES = r"""
examples: |-
  Enable the plugin in ansible.cfg:
    [defaults]
    callbacks_enabled = community.general.elastic

  Set the environment variable:
    export ELASTIC_APM_SERVER_URL=<your APM server URL)>
    export ELASTIC_APM_SERVICE_NAME=your_service_name
    export ELASTIC_APM_API_KEY=your_APM_API_KEY
"""

import getpass
import socket
import time
import uuid

from collections import OrderedDict
from contextlib import closing
from os.path import basename

from ansible.errors import AnsibleError, AnsibleRuntimeError
from ansible.module_utils.six import raise_from
from ansible.plugins.callback import CallbackBase

try:
    from elasticapm import Client, capture_span, trace_parent_from_string, instrument, label
except ImportError as imp_exc:
    ELASTIC_LIBRARY_IMPORT_ERROR = imp_exc
else:
    ELASTIC_LIBRARY_IMPORT_ERROR = None


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
        self.start = time.time()
        self.action = action
        self.args = args

    def add_host(self, host):
        if host.uuid in self.host_data:
            if host.status == 'included':
                # concatenate task include output from multiple items
                host.result = f'{self.host_data[host.uuid].result}\n{host.result}'
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
        self.finish = time.time()


class ElasticSource(object):
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
            args = ', '.join((f'{k}={v}' for k, v in task.args.items()))

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

        task.add_host(HostData(host_uuid, host_name, status, result))

    def generate_distributed_traces(self, tasks_data, status, end_time, traceparent, apm_service_name,
                                    apm_server_url, apm_verify_server_cert, apm_secret_token, apm_api_key):
        """ generate distributed traces from the collected TaskData and HostData """

        tasks = []
        parent_start_time = None
        for task_uuid, task in tasks_data.items():
            if parent_start_time is None:
                parent_start_time = task.start
            tasks.append(task)

        apm_cli = self.init_apm_client(apm_server_url, apm_service_name, apm_verify_server_cert, apm_secret_token, apm_api_key)
        if apm_cli:
            with closing(apm_cli):
                instrument()  # Only call this once, as early as possible.
                if traceparent:
                    parent = trace_parent_from_string(traceparent)
                    apm_cli.begin_transaction("Session", trace_parent=parent, start=parent_start_time)
                else:
                    apm_cli.begin_transaction("Session", start=parent_start_time)
                # Populate trace metadata attributes
                if self.ansible_version is not None:
                    label(ansible_version=self.ansible_version)
                label(ansible_session=self.session, ansible_host_name=self.host, ansible_host_user=self.user)
                if self.ip_address is not None:
                    label(ansible_host_ip=self.ip_address)

                for task_data in tasks:
                    for host_uuid, host_data in task_data.host_data.items():
                        self.create_span_data(apm_cli, task_data, host_data)

                apm_cli.end_transaction(name=__name__, result=status, duration=end_time - parent_start_time)

    def create_span_data(self, apm_cli, task_data, host_data):
        """ create the span with the given TaskData and HostData """

        name = f'[{host_data.name}] {task_data.play}: {task_data.name}'

        message = "success"
        status = "success"
        enriched_error_message = None
        if host_data.status == 'included':
            rc = 0
        else:
            res = host_data.result._result
            rc = res.get('rc', 0)
            if host_data.status == 'failed':
                message = self.get_error_message(res)
                enriched_error_message = self.enrich_error_message(res)
                status = "failure"
            elif host_data.status == 'skipped':
                if 'skip_reason' in res:
                    message = res['skip_reason']
                else:
                    message = 'skipped'
                status = "unknown"

        with capture_span(task_data.name,
                          start=task_data.start,
                          span_type="ansible.task.run",
                          duration=host_data.finish - task_data.start,
                          labels={"ansible.task.args": task_data.args,
                                  "ansible.task.message": message,
                                  "ansible.task.module": task_data.action,
                                  "ansible.task.name": name,
                                  "ansible.task.result": rc,
                                  "ansible.task.host.name": host_data.name,
                                  "ansible.task.host.status": host_data.status}) as span:
            span.outcome = status
            if 'failure' in status:
                exception = AnsibleRuntimeError(message=f"{task_data.action}: {name} failed with error message {enriched_error_message}")
                apm_cli.capture_exception(exc_info=(type(exception), exception, exception.__traceback__), handled=True)

    def init_apm_client(self, apm_server_url, apm_service_name, apm_verify_server_cert, apm_secret_token, apm_api_key):
        if apm_server_url:
            return Client(service_name=apm_service_name,
                          server_url=apm_server_url,
                          verify_server_cert=False,
                          secret_token=apm_secret_token,
                          api_key=apm_api_key,
                          use_elastic_traceparent_header=True,
                          debug=True)

    @staticmethod
    def get_error_message(result):
        if result.get('exception') is not None:
            return ElasticSource._last_line(result['exception'])
        return result.get('msg', 'failed')

    @staticmethod
    def _last_line(text):
        lines = text.strip().split('\n')
        return lines[-1]

    @staticmethod
    def enrich_error_message(result):
        message = result.get('msg', 'failed')
        exception = result.get('exception')
        stderr = result.get('stderr')
        return f"message: \"{message}\"\nexception: \"{exception}\"\nstderr: \"{stderr}\""


class CallbackModule(CallbackBase):
    """
    This callback creates distributed traces with Elastic APM.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'community.general.elastic'
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.hide_task_arguments = None
        self.apm_service_name = None
        self.ansible_playbook = None
        self.traceparent = False
        self.play_name = None
        self.tasks_data = None
        self.errors = 0
        self.disabled = False

        if ELASTIC_LIBRARY_IMPORT_ERROR:
            raise_from(
                AnsibleError('The `elastic-apm` must be installed to use this plugin'),
                ELASTIC_LIBRARY_IMPORT_ERROR)

        self.tasks_data = OrderedDict()

        self.elastic = ElasticSource(display=self._display)

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys,
                                                var_options=var_options,
                                                direct=direct)

        self.hide_task_arguments = self.get_option('hide_task_arguments')

        self.apm_service_name = self.get_option('apm_service_name')
        if not self.apm_service_name:
            self.apm_service_name = 'ansible'

        self.apm_server_url = self.get_option('apm_server_url')
        self.apm_secret_token = self.get_option('apm_secret_token')
        self.apm_api_key = self.get_option('apm_api_key')
        self.apm_verify_server_cert = self.get_option('apm_verify_server_cert')
        self.traceparent = self.get_option('traceparent')

    def v2_playbook_on_start(self, playbook):
        self.ansible_playbook = basename(playbook._file_name)

    def v2_playbook_on_play_start(self, play):
        self.play_name = play.get_name()

    def v2_runner_on_no_hosts(self, task):
        self.elastic.start_task(
            self.tasks_data,
            self.hide_task_arguments,
            self.play_name,
            task
        )

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.elastic.start_task(
            self.tasks_data,
            self.hide_task_arguments,
            self.play_name,
            task
        )

    def v2_playbook_on_cleanup_task_start(self, task):
        self.elastic.start_task(
            self.tasks_data,
            self.hide_task_arguments,
            self.play_name,
            task
        )

    def v2_playbook_on_handler_task_start(self, task):
        self.elastic.start_task(
            self.tasks_data,
            self.hide_task_arguments,
            self.play_name,
            task
        )

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.errors += 1
        self.elastic.finish_task(
            self.tasks_data,
            'failed',
            result
        )

    def v2_runner_on_ok(self, result):
        self.elastic.finish_task(
            self.tasks_data,
            'ok',
            result
        )

    def v2_runner_on_skipped(self, result):
        self.elastic.finish_task(
            self.tasks_data,
            'skipped',
            result
        )

    def v2_playbook_on_include(self, included_file):
        self.elastic.finish_task(
            self.tasks_data,
            'included',
            included_file
        )

    def v2_playbook_on_stats(self, stats):
        if self.errors == 0:
            status = "success"
        else:
            status = "failure"
        self.elastic.generate_distributed_traces(
            self.tasks_data,
            status,
            time.time(),
            self.traceparent,
            self.apm_service_name,
            self.apm_server_url,
            self.apm_verify_server_cert,
            self.apm_secret_token,
            self.apm_api_key
        )

    def v2_runner_on_async_failed(self, result, **kwargs):
        self.errors += 1

# -*- coding: utf-8 -*-
# Copyright (c) 2020, Yevhen Khmelenko <ujenmr@gmail.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
    author: Yevhen Khmelenko (@ujenmr)
    name: logstash
    type: notification
    short_description: Sends events to Logstash
    description:
      - This callback will report facts and task events to Logstash U(https://www.elastic.co/products/logstash).
    requirements:
      - whitelisting in configuration
      - logstash (Python library)
    options:
      server:
        description: Address of the Logstash server.
        env:
          - name: LOGSTASH_SERVER
        ini:
          - section: callback_logstash
            key: server
            version_added: 1.0.0
        default: localhost
      port:
        description: Port on which logstash is listening.
        env:
            - name: LOGSTASH_PORT
        ini:
          - section: callback_logstash
            key: port
            version_added: 1.0.0
        default: 5000
      type:
        description: Message type.
        env:
          - name: LOGSTASH_TYPE
        ini:
          - section: callback_logstash
            key: type
            version_added: 1.0.0
        default: ansible
      pre_command:
        description: Executes command before run and its result is added to the C(ansible_pre_command_output) logstash field.
        version_added: 2.0.0
        ini:
          - section: callback_logstash
            key: pre_command
        env:
          - name: LOGSTASH_PRE_COMMAND
      format_version:
        description: Logging format.
        type: str
        version_added: 2.0.0
        ini:
          - section: callback_logstash
            key: format_version
        env:
          - name: LOGSTASH_FORMAT_VERSION
        default: v1
        choices:
          - v1
          - v2

'''

EXAMPLES = r'''
ansible.cfg: |
    # Enable Callback plugin
    [defaults]
        callback_whitelist = community.general.logstash

    [callback_logstash]
        server = logstash.example.com
        port = 5000
        pre_command = git rev-parse HEAD
        type = ansible

11-input-tcp.conf: |
    # Enable Logstash TCP Input
    input {
            tcp {
                port => 5000
                codec => json
                add_field => { "[@metadata][beat]" => "notify" }
                add_field => { "[@metadata][type]" => "ansible" }
            }
        }
'''

import os
import json
from ansible import context
import socket
import uuid
import logging

try:
    import logstash
    HAS_LOGSTASH = True
except ImportError:
    HAS_LOGSTASH = False

from ansible.plugins.callback import CallbackBase

from ansible_collections.community.general.plugins.module_utils.datetime import (
    now,
)


class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'community.general.logstash'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()

        if not HAS_LOGSTASH:
            self.disabled = True
            self._display.warning("The required python-logstash/python3-logstash is not installed. "
                                  "pip install python-logstash for Python 2"
                                  "pip install python3-logstash for Python 3")

        self.start_time = now()

    def _init_plugin(self):
        if not self.disabled:
            self.logger = logging.getLogger('python-logstash-logger')
            self.logger.setLevel(logging.DEBUG)

            self.handler = logstash.TCPLogstashHandler(
                self.ls_server,
                self.ls_port,
                version=1,
                message_type=self.ls_type
            )

            self.logger.addHandler(self.handler)
            self.hostname = socket.gethostname()
            self.session = str(uuid.uuid4())
            self.errors = 0

            self.base_data = {
                'session': self.session,
                'host': self.hostname
            }

            if self.ls_pre_command is not None:
                self.base_data['ansible_pre_command_output'] = os.popen(
                    self.ls_pre_command).read()

            if context.CLIARGS is not None:
                self.base_data['ansible_checkmode'] = context.CLIARGS.get('check')
                self.base_data['ansible_tags'] = context.CLIARGS.get('tags')
                self.base_data['ansible_skip_tags'] = context.CLIARGS.get('skip_tags')
                self.base_data['inventory'] = context.CLIARGS.get('inventory')

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.ls_server = self.get_option('server')
        self.ls_port = int(self.get_option('port'))
        self.ls_type = self.get_option('type')
        self.ls_pre_command = self.get_option('pre_command')
        self.ls_format_version = self.get_option('format_version')

        self._init_plugin()

    def v2_playbook_on_start(self, playbook):
        data = self.base_data.copy()
        data['ansible_type'] = "start"
        data['status'] = "OK"
        data['ansible_playbook'] = playbook._file_name

        if (self.ls_format_version == "v2"):
            self.logger.info(
                "START PLAYBOOK | %s", data['ansible_playbook'], extra=data
            )
        else:
            self.logger.info("ansible start", extra=data)

    def v2_playbook_on_stats(self, stats):
        end_time = now()
        runtime = end_time - self.start_time
        summarize_stat = {}
        for host in stats.processed.keys():
            summarize_stat[host] = stats.summarize(host)

        if self.errors == 0:
            status = "OK"
        else:
            status = "FAILED"

        data = self.base_data.copy()
        data['ansible_type'] = "finish"
        data['status'] = status
        data['ansible_playbook_duration'] = runtime.total_seconds()
        data['ansible_result'] = json.dumps(summarize_stat)  # deprecated field

        if (self.ls_format_version == "v2"):
            self.logger.info(
                "FINISH PLAYBOOK | %s", json.dumps(summarize_stat), extra=data
            )
        else:
            self.logger.info("ansible stats", extra=data)

    def v2_playbook_on_play_start(self, play):
        self.play_id = str(play._uuid)

        if play.name:
            self.play_name = play.name

        data = self.base_data.copy()
        data['ansible_type'] = "start"
        data['status'] = "OK"
        data['ansible_play_id'] = self.play_id
        data['ansible_play_name'] = self.play_name

        if (self.ls_format_version == "v2"):
            self.logger.info("START PLAY | %s", self.play_name, extra=data)
        else:
            self.logger.info("ansible play", extra=data)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.task_id = str(task._uuid)

    '''
    Tasks and handler tasks are dealt with here
    '''

    def v2_runner_on_ok(self, result, **kwargs):
        task_name = str(result._task).replace('TASK: ', '').replace('HANDLER: ', '')

        data = self.base_data.copy()
        if task_name == 'setup':
            data['ansible_type'] = "setup"
            data['status'] = "OK"
            data['ansible_host'] = result._host.name
            data['ansible_play_id'] = self.play_id
            data['ansible_play_name'] = self.play_name
            data['ansible_task'] = task_name
            data['ansible_facts'] = self._dump_results(result._result)

            if (self.ls_format_version == "v2"):
                self.logger.info(
                    "SETUP FACTS | %s", self._dump_results(result._result), extra=data
                )
            else:
                self.logger.info("ansible facts", extra=data)
        else:
            if 'changed' in result._result.keys():
                data['ansible_changed'] = result._result['changed']
            else:
                data['ansible_changed'] = False

            data['ansible_type'] = "task"
            data['status'] = "OK"
            data['ansible_host'] = result._host.name
            data['ansible_play_id'] = self.play_id
            data['ansible_play_name'] = self.play_name
            data['ansible_task'] = task_name
            data['ansible_task_id'] = self.task_id
            data['ansible_result'] = self._dump_results(result._result)

            if (self.ls_format_version == "v2"):
                self.logger.info(
                    "TASK OK | %s | RESULT | %s",
                    task_name, self._dump_results(result._result), extra=data
                )
            else:
                self.logger.info("ansible ok", extra=data)

    def v2_runner_on_skipped(self, result, **kwargs):
        task_name = str(result._task).replace('TASK: ', '').replace('HANDLER: ', '')

        data = self.base_data.copy()
        data['ansible_type'] = "task"
        data['status'] = "SKIPPED"
        data['ansible_host'] = result._host.name
        data['ansible_play_id'] = self.play_id
        data['ansible_play_name'] = self.play_name
        data['ansible_task'] = task_name
        data['ansible_task_id'] = self.task_id
        data['ansible_result'] = self._dump_results(result._result)

        if (self.ls_format_version == "v2"):
            self.logger.info("TASK SKIPPED | %s", task_name, extra=data)
        else:
            self.logger.info("ansible skipped", extra=data)

    def v2_playbook_on_import_for_host(self, result, imported_file):
        data = self.base_data.copy()
        data['ansible_type'] = "import"
        data['status'] = "IMPORTED"
        data['ansible_host'] = result._host.name
        data['ansible_play_id'] = self.play_id
        data['ansible_play_name'] = self.play_name
        data['imported_file'] = imported_file

        if (self.ls_format_version == "v2"):
            self.logger.info("IMPORT | %s", imported_file, extra=data)
        else:
            self.logger.info("ansible import", extra=data)

    def v2_playbook_on_not_import_for_host(self, result, missing_file):
        data = self.base_data.copy()
        data['ansible_type'] = "import"
        data['status'] = "NOT IMPORTED"
        data['ansible_host'] = result._host.name
        data['ansible_play_id'] = self.play_id
        data['ansible_play_name'] = self.play_name
        data['imported_file'] = missing_file

        if (self.ls_format_version == "v2"):
            self.logger.info("NOT IMPORTED | %s", missing_file, extra=data)
        else:
            self.logger.info("ansible import", extra=data)

    def v2_runner_on_failed(self, result, **kwargs):
        task_name = str(result._task).replace('TASK: ', '').replace('HANDLER: ', '')

        data = self.base_data.copy()
        if 'changed' in result._result.keys():
            data['ansible_changed'] = result._result['changed']
        else:
            data['ansible_changed'] = False

        data['ansible_type'] = "task"
        data['status'] = "FAILED"
        data['ansible_host'] = result._host.name
        data['ansible_play_id'] = self.play_id
        data['ansible_play_name'] = self.play_name
        data['ansible_task'] = task_name
        data['ansible_task_id'] = self.task_id
        data['ansible_result'] = self._dump_results(result._result)

        self.errors += 1
        if (self.ls_format_version == "v2"):
            self.logger.error(
                "TASK FAILED | %s | HOST | %s | RESULT | %s",
                task_name, self.hostname,
                self._dump_results(result._result), extra=data
            )
        else:
            self.logger.error("ansible failed", extra=data)

    def v2_runner_on_unreachable(self, result, **kwargs):
        task_name = str(result._task).replace('TASK: ', '').replace('HANDLER: ', '')

        data = self.base_data.copy()
        data['ansible_type'] = "task"
        data['status'] = "UNREACHABLE"
        data['ansible_host'] = result._host.name
        data['ansible_play_id'] = self.play_id
        data['ansible_play_name'] = self.play_name
        data['ansible_task'] = task_name
        data['ansible_task_id'] = self.task_id
        data['ansible_result'] = self._dump_results(result._result)

        self.errors += 1
        if (self.ls_format_version == "v2"):
            self.logger.error(
                "UNREACHABLE | %s | HOST | %s | RESULT | %s",
                task_name, self.hostname,
                self._dump_results(result._result), extra=data
            )
        else:
            self.logger.error("ansible unreachable", extra=data)

    def v2_runner_on_async_failed(self, result, **kwargs):
        task_name = str(result._task).replace('TASK: ', '').replace('HANDLER: ', '')

        data = self.base_data.copy()
        data['ansible_type'] = "task"
        data['status'] = "FAILED"
        data['ansible_host'] = result._host.name
        data['ansible_play_id'] = self.play_id
        data['ansible_play_name'] = self.play_name
        data['ansible_task'] = task_name
        data['ansible_task_id'] = self.task_id
        data['ansible_result'] = self._dump_results(result._result)

        self.errors += 1
        if (self.ls_format_version == "v2"):
            self.logger.error(
                "ASYNC FAILED | %s | HOST | %s | RESULT | %s",
                task_name, self.hostname,
                self._dump_results(result._result), extra=data
            )
        else:
            self.logger.error("ansible async", extra=data)

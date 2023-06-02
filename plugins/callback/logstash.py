# (C) 2016, Ievgen Khmelenko <ujenmr@gmail.com>
# (C) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Unknown (!UNKNOWN)
    callback: logstash
    type: notification
    short_description: Sends events to Logstash
    description:
      - This callback will report facts and task events to Logstash https://www.elastic.co/products/logstash
    requirements:
      - whitelisting in configuration
      - logstash (python library)
    options:
      server:
        description: Address of the Logstash server
        env:
          - name: LOGSTASH_SERVER
        ini:
          - section: callback_logstash
            key: server
            version_added: 1.0.0
        default: localhost
      port:
        description: Port on which logstash is listening
        env:
            - name: LOGSTASH_PORT
        ini:
          - section: callback_logstash
            key: port
            version_added: 1.0.0
        default: 5000
      type:
        description: Message type
        env:
          - name: LOGSTASH_TYPE
        ini:
          - section: callback_logstash
            key: type
            version_added: 1.0.0
        default: ansible
'''

import os
import json
import socket
import uuid
from datetime import datetime

import logging

try:
    import logstash
    HAS_LOGSTASH = True
except ImportError:
    HAS_LOGSTASH = False

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    ansible logstash callback plugin
    ansible.cfg:
        callback_plugins   = <path_to_callback_plugins_folder>
        callback_whitelist = logstash
    and put the plugin in <path_to_callback_plugins_folder>

    logstash config:
        input {
            tcp {
                port => 5000
                codec => json
            }
        }

    Requires:
        python-logstash

    This plugin makes use of the following environment variables or ini config:
        LOGSTASH_SERVER   (optional): defaults to localhost
        LOGSTASH_PORT     (optional): defaults to 5000
        LOGSTASH_TYPE     (optional): defaults to ansible
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'community.general.logstash'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)

        if not HAS_LOGSTASH:
            self.disabled = True
            self._display.warning("The required python-logstash is not installed. "
                                  "pip install python-logstash")

        self.start_time = datetime.utcnow()

    def set_options(self, task_keys=None, var_options=None, direct=None):

        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.logger = logging.getLogger('python-logstash-logger')
        self.logger.setLevel(logging.DEBUG)

        self.logstash_server = self.get_option('server')
        self.logstash_port = self.get_option('port')
        self.logstash_type = self.get_option('type')
        self.handler = logstash.TCPLogstashHandler(
            self.logstash_server,
            int(self.logstash_port),
            version=1,
            message_type=self.logstash_type
        )
        self.logger.addHandler(self.handler)
        self.hostname = socket.gethostname()
        self.session = str(uuid.uuid1())
        self.errors = 0

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook._file_name
        data = {
            'status': "OK",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "start",
            'ansible_playbook': self.playbook,
        }
        self.logger.info("ansible start", extra=data)

    def v2_playbook_on_stats(self, stats):
        end_time = datetime.utcnow()
        runtime = end_time - self.start_time
        summarize_stat = {}
        for host in stats.processed.keys():
            summarize_stat[host] = stats.summarize(host)

        if self.errors == 0:
            status = "OK"
        else:
            status = "FAILED"

        data = {
            'status': status,
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "finish",
            'ansible_playbook': self.playbook,
            'ansible_playbook_duration': runtime.total_seconds(),
            'ansible_result': json.dumps(summarize_stat),
        }
        self.logger.info("ansible stats", extra=data)

    def v2_runner_on_ok(self, result, **kwargs):
        data = {
            'status': "OK",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task,
            'ansible_result': self._dump_results(result._result)
        }
        self.logger.info("ansible ok", extra=data)

    def v2_runner_on_skipped(self, result, **kwargs):
        data = {
            'status': "SKIPPED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_task': result._task,
            'ansible_host': result._host.name
        }
        self.logger.info("ansible skipped", extra=data)

    def v2_playbook_on_import_for_host(self, result, imported_file):
        data = {
            'status': "IMPORTED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "import",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'imported_file': imported_file
        }
        self.logger.info("ansible import", extra=data)

    def v2_playbook_on_not_import_for_host(self, result, missing_file):
        data = {
            'status': "NOT IMPORTED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "import",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'missing_file': missing_file
        }
        self.logger.info("ansible import", extra=data)

    def v2_runner_on_failed(self, result, **kwargs):
        data = {
            'status': "FAILED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task,
            'ansible_result': self._dump_results(result._result)
        }
        self.errors += 1
        self.logger.error("ansible failed", extra=data)

    def v2_runner_on_unreachable(self, result, **kwargs):
        data = {
            'status': "UNREACHABLE",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task,
            'ansible_result': self._dump_results(result._result)
        }
        self.logger.error("ansible unreachable", extra=data)

    def v2_runner_on_async_failed(self, result, **kwargs):
        data = {
            'status': "FAILED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task,
            'ansible_result': self._dump_results(result._result)
        }
        self.errors += 1
        self.logger.error("ansible async", extra=data)

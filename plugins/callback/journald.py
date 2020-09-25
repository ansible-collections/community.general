# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: journald
    type: notification
    short_description: Sends events to systemd journal (journald)
    description:
      - This callback will report facts and task events to systemd journal (journald)
    requirements:
      - whitelisting in configuration
      - systemd-python (python library)
'''

import json
import socket
import uuid
from datetime import datetime

import logging

try:
    from systemd.journal import JournalHandler
    HAS_SYSTEMD = True
except ImportError:
    HAS_SYSTEMD = False

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    ansible systemd journal (journald) callback plugin
    ansible.cfg:
        callback_plugins   = <path_to_callback_plugins_folder>
        callback_whitelist = journald
    and put the plugin in <path_to_callback_plugins_folder>

    Requires:
        systemd-python
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'community.general.journald'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)

        if not HAS_SYSTEMD:
            self.disabled = True
            self._display.warning("The required systemd-python is not installed. "
                                  "pip install systemd-python")

        self.start_time = datetime.utcnow()

    def _log_format(self, event, data):
        data_ = {'event': event}
        data_.update(data)
        return json.dumps(data_)

    def set_options(self, task_keys=None, var_options=None, direct=None):

        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.logger = logging.getLogger('python-journald-logger')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(JournalHandler())

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
        self.logger.info(self._log_format("ansible start", data))

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
        self.logger.info(self._log_format("ansible stats", data))

    def v2_runner_on_ok(self, result, **kwargs):
        data = {
            'status': "OK",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task.get_name(),
            'ansible_result': self._dump_results(result._result)
        }
        self.logger.info(self._log_format("ansible ok", data))

    def v2_runner_on_skipped(self, result, **kwargs):
        data = {
            'status': "SKIPPED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_task': result._task.get_name(),
            'ansible_host': result._host.name
        }
        self.logger.info(self._log_format("ansible skipped", data))

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
        self.logger.info(self._log_format("ansible import", data))

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
        self.logger.info(self._log_format("ansible import", data))

    def v2_runner_on_failed(self, result, **kwargs):
        data = {
            'status': "FAILED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task.get_name(),
            'ansible_result': self._dump_results(result._result)
        }
        self.errors += 1
        self.logger.error(self._log_format("ansible failed", data))

    def v2_runner_on_unreachable(self, result, **kwargs):
        data = {
            'status': "UNREACHABLE",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task.get_name(),
            'ansible_result': self._dump_results(result._result)
        }
        self.logger.error(self._log_format("ansible unreachable", data))

    def v2_runner_on_async_failed(self, result, **kwargs):
        data = {
            'status': "FAILED",
            'host': self.hostname,
            'session': self.session,
            'ansible_type': "task",
            'ansible_playbook': self.playbook,
            'ansible_host': result._host.name,
            'ansible_task': result._task.get_name(),
            'ansible_result': self._dump_results(result._result)
        }
        self.errors += 1
        self.logger.error(self._log_format("ansible async", data))

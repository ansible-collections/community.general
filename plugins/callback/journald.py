# Copyright: (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
    callback: journald
    type: notification
    short_description: Sends play events to systemd's journal
    description:
      - This is an ansible callback plugin that sends status updates to the system journal during playbook execution.
    requirements:
      - Whitelist in configuration
      - systemd-python (Python library)
    options:
      logger_name:
        required: False
        description: unit name the logs are written against
        env:
          - name: JOURNALD_LOGGER_NAME
        ini:
          - section: callback_journald
            key: logger_name
      logger_level:
        required: False
        description:
        - Logging levels
        - Valid values are 'notset', 'debug', 'info', 'warning', 'error', and 'critical'
        - Default value is set to 'info'
        env:
          - name: JOURNALD_LOGGER_LEVEL
        ini:
          - section: callback_journald
            key: logger_level
'''

import logging
import getpass
import os
import uuid

try:
    from systemd.journal import JournalHandler
    HAS_SYSTEMD = True
except ImportError:
    HAS_SYSTEMD = False

from ansible.plugins.callback import CallbackBase
from ansible.playbook.task_include import TaskInclude


class CallbackModule(CallbackBase):
    """
    logs playbook results using journald
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_NAME = 'community.general.journald'
    CALLBACK_TYPE = 'notification'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.disabled = True
        self.logger = None
        self.logger_name = None
        self.username = getpass.getuser()
        self.playbook_name = None
        self.logger_level = None

        # use a random uuid to identify each playbook run
        self.playbook_id = uuid.uuid4()

    def get_logger_level(self, level):
        return {
            'notset': 0,
            'debug': 10,
            'info': 20,
            'warning': 30,
            'error': 40,
            'critical': 50,
        }.get(level, 20)

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys,
                                                var_options=var_options,
                                                direct=direct)

        if HAS_SYSTEMD:
            self.logger_name = self.get_option('logger_name') or 'ansible'
            self.logger = logging.getLogger(self.logger_name)
            self.logger.addHandler(JournalHandler())
            self.logger.setLevel(self.get_logger_level(self.get_option('logger_level').lower()))
            self.logger_method = self.get_logger_method(self.get_option)
            self.disabled = False
        else:
            self.disabled = True
            self._display.warning('WARNING:\nPlease, install systemd Python Package: `pip install systemd-python`')

    def _send_log(self, status, message):
        if HAS_SYSTEMD:
            self.logger.info('%s - PlaybookId[%s] %s: %s', self.username, self.playbook_id, status, message)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if ignore_errors:
            return
        host = result._host
        self._send_log('failed: ', '[%s]' % (host.get_name()))

    def v2_runner_on_ok(self, _result):
        host = _result._host
        task = _result._task
        result = _result._result

        if isinstance(task, TaskInclude):
            return
        elif result.get('changed', False):
            status = 'changed'
        else:
            status = 'ok'

        delegated_vars = result.get('_ansible_delegated_vars', None)
        if delegated_vars:
            msg = "[%s -> %s]" % (host.get_name(), delegated_vars['ansible_host'])
        else:
            msg = "[%s]" % (host.get_name())

        if task.loop and 'results' in result:
            self._process_items(_result)
        else:
            self._clean_results(result, task.action)

            if (self._display.verbosity > 0 or '_ansible_verbose_always' in result) \
                    and '_ansible_verbose_override' not in result:
                msg += " => %s" % (result)
        self._send_log(status, msg)

    def v2_runner_on_skipped(self, result):
        host = result._host
        self._send_log('skipped: ', '[%s]' % host.get_name())

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self._send_log('unreachable: ', '[%s]' % host.get_name())

    def v2_playbook_on_start(self, playbook):
        self.playbook_name = os.path.basename(playbook._file_name)
        self._send_log('playbook started', self.playbook_name)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._send_log('task started', task)

    def v2_playbook_on_play_start(self, play):
        name = play.name or 'Play name not specified'
        self._send_log('play started', name)

    def v2_runner_item_on_failed(self, result):
        host = result._host
        self._send_log('item failed', '[%s]' % (host.get_name()))

    def v2_runner_item_on_skipped(self, result):
        host = result._host
        self._send_log('item skipped', '[%s]' % (host.get_name()))

    def v2_runner_retry(self, result):
        host = result._host
        self._send_log('retry', '[%s]' % (host.get_name()))

    def v2_playbook_on_stats(self, stats):
        """Display info about playbook statistics"""
        hosts = sorted(stats.processed.keys())
        ok = changed = failed = unreachable = rescued = ignored = 0
        for h in hosts:
            s = stats.summarize(h)
            ok += s['ok']
            changed += s['changed']
            failed += s['failures']
            unreachable += s['unreachable']
            rescued += s['rescued']
            ignored += s['ignored']

        status_line = 'OK:%s CHANGED:%s FAILED:%s UNREACHABLE:%s RESCUED:%s IGNORED:%s' % (
            ok, changed, failed, unreachable, rescued, ignored
        )

        if failed or unreachable:
            final_status = 'Failed'
        else:
            final_status = 'Succeeded'

        self._send_log('COMPLETE', 'Playbook %s. %s' % (final_status, status_line))

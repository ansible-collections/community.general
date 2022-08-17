# -*- coding: utf-8 -*-
# Copyright (c) 2012, Michael DeHaan, <michael.dehaan@gmail.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Unknown (!UNKNOWN)
    name: log_plays
    type: notification
    short_description: write playbook output to log file
    description:
      - This callback writes playbook output to a file per host in the C(/var/log/ansible/hosts) directory
    requirements:
     - Whitelist in configuration
     - A writeable /var/log/ansible/hosts directory by the user executing Ansible on the controller
    options:
      log_folder:
        default: /var/log/ansible/hosts
        description: The folder where log files will be created.
        env:
          - name: ANSIBLE_LOG_FOLDER
        ini:
          - section: callback_log_plays
            key: log_folder
'''

import os
import time
import json

from ansible.utils.path import makedirs_safe
from ansible.module_utils.common.text.converters import to_bytes
from ansible.module_utils.common._collections_compat import MutableMapping
from ansible.parsing.ajson import AnsibleJSONEncoder
from ansible.plugins.callback import CallbackBase


# NOTE: in Ansible 1.2 or later general logging is available without
# this plugin, just set ANSIBLE_LOG_PATH as an environment variable
# or log_path in the DEFAULTS section of your ansible configuration
# file.  This callback is an example of per hosts logging for those
# that want it.


class CallbackModule(CallbackBase):
    """
    logs playbook results, per host, in /var/log/ansible/hosts
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'community.general.log_plays'
    CALLBACK_NEEDS_WHITELIST = True

    TIME_FORMAT = "%b %d %Y %H:%M:%S"
    MSG_FORMAT = "%(now)s - %(playbook)s - %(task_name)s - %(task_action)s - %(category)s - %(data)s\n\n"

    def __init__(self):

        super(CallbackModule, self).__init__()

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.log_folder = self.get_option("log_folder")

        if not os.path.exists(self.log_folder):
            makedirs_safe(self.log_folder)

    def log(self, result, category):
        data = result._result
        if isinstance(data, MutableMapping):
            if '_ansible_verbose_override' in data:
                # avoid logging extraneous data
                data = 'omitted'
            else:
                data = data.copy()
                invocation = data.pop('invocation', None)
                data = json.dumps(data, cls=AnsibleJSONEncoder)
                if invocation is not None:
                    data = json.dumps(invocation) + " => %s " % data

        path = os.path.join(self.log_folder, result._host.get_name())
        now = time.strftime(self.TIME_FORMAT, time.localtime())

        msg = to_bytes(
            self.MSG_FORMAT
            % dict(
                now=now,
                playbook=self.playbook,
                task_name=result._task.name,
                task_action=result._task.action,
                category=category,
                data=data,
            )
        )
        with open(path, "ab") as fd:
            fd.write(msg)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.log(result, 'FAILED')

    def v2_runner_on_ok(self, result):
        self.log(result, 'OK')

    def v2_runner_on_skipped(self, result):
        self.log(result, 'SKIPPED')

    def v2_runner_on_unreachable(self, result):
        self.log(result, 'UNREACHABLE')

    def v2_runner_on_async_failed(self, result):
        self.log(result, 'ASYNC_FAILED')

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook._file_name

    def v2_playbook_on_import_for_host(self, result, imported_file):
        self.log(result, 'IMPORTED', imported_file)

    def v2_playbook_on_not_import_for_host(self, result, missing_file):
        self.log(result, 'NOTIMPORTED', missing_file)

#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Tim Rightnour <thegarbledone@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: syslogger
short_description: Log messages in the syslog
description:
  - Uses syslog to add log entries to the host.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  msg:
    type: str
    description:
      - This is the message to place in syslog.
    required: true
  priority:
    type: str
    description:
      - Set the log priority.
    choices: ["emerg", "alert", "crit", "err", "warning", "notice", "info", "debug"]
    default: "info"
  facility:
    type: str
    description:
      - Set the log facility.
    choices:
      - kern
      - user
      - mail
      - daemon
      - auth
      - lpr
      - news
      - uucp
      - cron
      - syslog
      - local0
      - local1
      - local2
      - local3
      - local4
      - local5
      - local6
      - local7
    default: "daemon"
  log_pid:
    description:
      - Log the PID in brackets.
    type: bool
    default: false
  ident:
    description:
      - Specify the name of application name which is sending the log to syslog.
    type: str
    default: 'ansible_syslogger'
    version_added: '0.2.0'
author:
  - Tim Rightnour (@garbled1)
"""

EXAMPLES = r"""
- name: Simple Usage
  community.general.syslogger:
    msg: "I will end up as daemon.info"

- name: Send a log message with err priority and user facility with log_pid
  community.general.syslogger:
    msg: "Hello from Ansible"
    priority: "err"
    facility: "user"
    log_pid: true

- name: Specify the name of application which is sending log message
  community.general.syslogger:
    ident: "MyApp"
    msg: "I want to believe"
    priority: "alert"
"""

RETURN = r"""
ident:
  description: Name of application sending the message to log.
  returned: always
  type: str
  sample: "ansible_syslogger"
  version_added: '0.2.0'
priority:
  description: Priority level.
  returned: always
  type: str
  sample: "daemon"
facility:
  description: Syslog facility.
  returned: always
  type: str
  sample: "info"
log_pid:
  description: Log PID status.
  returned: always
  type: bool
  sample: true
msg:
  description: Message sent to syslog.
  returned: always
  type: str
  sample: "Hello from Ansible"
"""

import syslog
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


def get_facility(facility):
    return {
        'kern': syslog.LOG_KERN,
        'user': syslog.LOG_USER,
        'mail': syslog.LOG_MAIL,
        'daemon': syslog.LOG_DAEMON,
        'auth': syslog.LOG_AUTH,
        'lpr': syslog.LOG_LPR,
        'news': syslog.LOG_NEWS,
        'uucp': syslog.LOG_UUCP,
        'cron': syslog.LOG_CRON,
        'syslog': syslog.LOG_SYSLOG,
        'local0': syslog.LOG_LOCAL0,
        'local1': syslog.LOG_LOCAL1,
        'local2': syslog.LOG_LOCAL2,
        'local3': syslog.LOG_LOCAL3,
        'local4': syslog.LOG_LOCAL4,
        'local5': syslog.LOG_LOCAL5,
        'local6': syslog.LOG_LOCAL6,
        'local7': syslog.LOG_LOCAL7
    }.get(facility, syslog.LOG_DAEMON)


def get_priority(priority):
    return {
        'emerg': syslog.LOG_EMERG,
        'alert': syslog.LOG_ALERT,
        'crit': syslog.LOG_CRIT,
        'err': syslog.LOG_ERR,
        'warning': syslog.LOG_WARNING,
        'notice': syslog.LOG_NOTICE,
        'info': syslog.LOG_INFO,
        'debug': syslog.LOG_DEBUG
    }.get(priority, syslog.LOG_INFO)


def main():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        ident=dict(type='str', default='ansible_syslogger'),
        msg=dict(type='str', required=True),
        priority=dict(type='str',
                      choices=["emerg", "alert", "crit", "err", "warning",
                               "notice", "info", "debug"],
                      default='info'),
        facility=dict(type='str',
                      choices=["kern", "user", "mail", "daemon", "auth",
                               "lpr", "news", "uucp", "cron", "syslog",
                               "local0", "local1", "local2", "local3",
                               "local4", "local5", "local6", "local7"],
                      default='daemon'),
        log_pid=dict(type='bool', default=False)
    )

    module = AnsibleModule(
        argument_spec=module_args,
    )

    result = dict(
        changed=False,
        ident=module.params['ident'],
        priority=module.params['priority'],
        facility=module.params['facility'],
        log_pid=module.params['log_pid'],
        msg=module.params['msg']
    )

    # do the logging
    try:
        syslog.openlog(module.params['ident'],
                       syslog.LOG_PID if module.params['log_pid'] else 0,
                       get_facility(module.params['facility']))
        syslog.syslog(get_priority(module.params['priority']),
                      module.params['msg'])
        syslog.closelog()
        result['changed'] = True

    except Exception as exc:
        module.fail_json(error='Failed to write to syslog %s' % to_native(exc), exception=traceback.format_exc(), **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

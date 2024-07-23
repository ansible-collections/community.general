#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is largely copied from the Nagios module included in the
# Func project. Original copyright follows:
#
# func-nagios - Schedule downtime and enables/disable notifications
# Copyright 2011, Red Hat, Inc.
# Tim Bielawa <tbielawa@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: nagios
short_description: Perform common tasks in Nagios related to downtime and notifications
description:
  - "The C(nagios) module has two basic functions: scheduling downtime and toggling alerts for services or hosts."
  - The C(nagios) module is not idempotent.
  - All actions require the O(host) parameter to be given explicitly. In playbooks you can use the C({{inventory_hostname}}) variable to refer
    to the host the playbook is currently running on.
  - You can specify multiple services at once by separating them with commas, .e.g. O(services=httpd,nfs,puppet).
  - When specifying what service to handle there is a special service value, O(host), which will handle alerts/downtime/acknowledge for the I(host itself),
    for example O(services=host). This keyword may not be given with other services at the same time.
    B(Setting alerts/downtime/acknowledge for a host does not affect alerts/downtime/acknowledge for any of the services running on it.)
    To schedule downtime for all services on particular host use keyword "all", for example O(services=all).
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  action:
    description:
      - Action to take.
      - The V(acknowledge) and V(forced_check) actions were added in community.general 1.2.0.
    required: true
    choices: [ "downtime", "delete_downtime", "enable_alerts", "disable_alerts", "silence", "unsilence",
               "silence_nagios", "unsilence_nagios", "command", "servicegroup_service_downtime",
               "servicegroup_host_downtime", "acknowledge", "forced_check" ]
    type: str
  host:
    description:
      - Host to operate on in Nagios.
    type: str
  cmdfile:
    description:
      - Path to the nagios I(command file) (FIFO pipe).
        Only required if auto-detection fails.
    type: str
  author:
    description:
     - Author to leave downtime comments as.
       Only used when O(action) is V(downtime) or V(acknowledge).
    type: str
    default: Ansible
  comment:
    description:
     - Comment when O(action) is V(downtime) or V(acknowledge).
    type: str
    default: Scheduling downtime
  start:
    description:
      - When downtime should start, in C(time_t) format (epoch seconds).
    version_added: '0.2.0'
    type: str
  minutes:
    description:
      - Minutes to schedule downtime for.
      - Only usable with O(action=downtime).
    type: int
    default: 30
  services:
    description:
      - What to manage downtime/alerts for. Separate multiple services with commas.
      - "B(Required) option when O(action) is one of: V(downtime), V(acknowledge), V(forced_check), V(enable_alerts), V(disable_alerts)."
    aliases: [ "service" ]
    type: str
  servicegroup:
    description:
      - The Servicegroup we want to set downtimes/alerts for.
      - B(Required) option when using the V(servicegroup_service_downtime) and V(servicegroup_host_downtime) O(action).
    type: str
  command:
    description:
      - The raw command to send to nagios, which should not include the submitted time header or the line-feed.
      - B(Required) option when using the V(command) O(action).
    type: str

author: "Tim Bielawa (@tbielawa)"
'''

EXAMPLES = '''
- name: Set 30 minutes of apache downtime
  community.general.nagios:
    action: downtime
    minutes: 30
    service: httpd
    host: '{{ inventory_hostname }}'

- name: Schedule an hour of HOST downtime
  community.general.nagios:
    action: downtime
    minutes: 60
    service: host
    host: '{{ inventory_hostname }}'

- name: Schedule an hour of HOST downtime starting at 2019-04-23T02:00:00+00:00
  community.general.nagios:
    action: downtime
    start: 1555984800
    minutes: 60
    service: host
    host: '{{ inventory_hostname }}'

- name: Schedule an hour of HOST downtime, with a comment describing the reason
  community.general.nagios:
    action: downtime
    minutes: 60
    service: host
    host: '{{ inventory_hostname }}'
    comment: Rebuilding machine

- name: Schedule downtime for ALL services on HOST
  community.general.nagios:
    action: downtime
    minutes: 45
    service: all
    host: '{{ inventory_hostname }}'

- name: Schedule downtime for a few services
  community.general.nagios:
    action: downtime
    services: frob,foobar,qeuz
    host: '{{ inventory_hostname }}'

- name: Set 30 minutes downtime for all services in servicegroup foo
  community.general.nagios:
    action: servicegroup_service_downtime
    minutes: 30
    servicegroup: foo
    host: '{{ inventory_hostname }}'

- name: Set 30 minutes downtime for all host in servicegroup foo
  community.general.nagios:
    action: servicegroup_host_downtime
    minutes: 30
    servicegroup: foo
    host: '{{ inventory_hostname }}'

- name: Delete all downtime for a given host
  community.general.nagios:
    action: delete_downtime
    host: '{{ inventory_hostname }}'
    service: all

- name: Delete all downtime for HOST with a particular comment
  community.general.nagios:
    action: delete_downtime
    host: '{{ inventory_hostname }}'
    service: host
    comment: Planned maintenance

- name: Acknowledge an HOST with a particular comment
  community.general.nagios:
    action: acknowledge
    service: host
    host: '{{ inventory_hostname }}'
    comment: 'power outage - see casenr 12345'

- name: Acknowledge an active service problem for the httpd service with a particular comment
  community.general.nagios:
    action: acknowledge
    service: httpd
    host: '{{ inventory_hostname }}'
    comment: 'service crashed - see casenr 12345'

- name: Reset a passive service check for snmp trap
  community.general.nagios:
    action: forced_check
    service: snmp
    host: '{{ inventory_hostname }}'

- name: Force an active service check for the httpd service
  community.general.nagios:
    action: forced_check
    service: httpd
    host: '{{ inventory_hostname }}'

- name: Force an active service check for all services of a particular host
  community.general.nagios:
    action: forced_check
    service: all
    host: '{{ inventory_hostname }}'

- name: Force an active service check for a particular host
  community.general.nagios:
    action: forced_check
    service: host
    host: '{{ inventory_hostname }}'

- name: Enable SMART disk alerts
  community.general.nagios:
    action: enable_alerts
    service: smart
    host: '{{ inventory_hostname }}'

- name: Disable httpd and nfs alerts
  community.general.nagios:
    action: disable_alerts
    service: httpd,nfs
    host: '{{ inventory_hostname }}'

- name: Disable HOST alerts
  community.general.nagios:
    action: disable_alerts
    service: host
    host: '{{ inventory_hostname }}'

- name: Silence ALL alerts
  community.general.nagios:
    action: silence
    host: '{{ inventory_hostname }}'

- name: Unsilence all alerts
  community.general.nagios:
    action: unsilence
    host: '{{ inventory_hostname }}'

- name: Shut up nagios
  community.general.nagios:
    action: silence_nagios

- name: Annoy me negios
  community.general.nagios:
    action: unsilence_nagios

- name: Command something
  community.general.nagios:
    action: command
    command: DISABLE_FAILURE_PREDICTION
'''

import time
import os.path
import stat

from ansible.module_utils.basic import AnsibleModule


def which_cmdfile():
    locations = [
        # rhel
        '/etc/nagios/nagios.cfg',
        # debian
        '/etc/nagios3/nagios.cfg',
        # older debian
        '/etc/nagios2/nagios.cfg',
        # bsd, solaris
        '/usr/local/etc/nagios/nagios.cfg',
        # groundwork it monitoring
        '/usr/local/groundwork/nagios/etc/nagios.cfg',
        # open monitoring distribution
        '/omd/sites/oppy/tmp/nagios/nagios.cfg',
        # ???
        '/usr/local/nagios/etc/nagios.cfg',
        '/usr/local/nagios/nagios.cfg',
        '/opt/nagios/etc/nagios.cfg',
        '/opt/nagios/nagios.cfg',
        # icinga on debian/ubuntu
        '/etc/icinga/icinga.cfg',
        # icinga installed from source (default location)
        '/usr/local/icinga/etc/icinga.cfg',
    ]

    for path in locations:
        if os.path.exists(path):
            for line in open(path):
                if line.startswith('command_file'):
                    return line.split('=')[1].strip()

    return None


def main():
    ACTION_CHOICES = [
        'downtime',
        'delete_downtime',
        'silence',
        'unsilence',
        'enable_alerts',
        'disable_alerts',
        'silence_nagios',
        'unsilence_nagios',
        'command',
        'servicegroup_host_downtime',
        'servicegroup_service_downtime',
        'acknowledge',
        'forced_check',
    ]

    module = AnsibleModule(
        argument_spec=dict(
            action=dict(type='str', required=True, choices=ACTION_CHOICES),
            author=dict(type='str', default='Ansible'),
            comment=dict(type='str', default='Scheduling downtime'),
            host=dict(type='str'),
            servicegroup=dict(type='str'),
            start=dict(type='str'),
            minutes=dict(type='int', default=30),
            cmdfile=dict(type='str', default=which_cmdfile()),
            services=dict(type='str', aliases=['service']),
            command=dict(type='str'),
        ),
        required_if=[
            ('action', 'downtime', ['host', 'services']),
            ('action', 'delete_downtime', ['host', 'services']),
            ('action', 'silence', ['host']),
            ('action', 'unsilence', ['host']),
            ('action', 'enable_alerts', ['host', 'services']),
            ('action', 'disable_alerts', ['host', 'services']),
            ('action', 'command', ['command']),
            ('action', 'servicegroup_host_downtime', ['host', 'servicegroup']),
            ('action', 'servicegroup_service_downtime', ['host', 'servicegroup']),
            ('action', 'acknowledge', ['host', 'services']),
            ('action', 'forced_check', ['host', 'services']),
        ],
    )

    if not module.params['cmdfile']:
        module.fail_json(msg='unable to locate nagios.cfg')

    ansible_nagios = Nagios(module, **module.params)
    if module.check_mode:
        module.exit_json(changed=True)
    else:
        ansible_nagios.act()


class Nagios(object):
    """
    Perform common tasks in Nagios related to downtime and
    notifications.

    The complete set of external commands Nagios handles is documented
    on their website:

    http://old.nagios.org/developerinfo/externalcommands/commandlist.php

    Note that in the case of `schedule_svc_downtime`,
    `enable_svc_notifications`, and `disable_svc_notifications`, the
    service argument should be passed as a list.
    """

    def __init__(self, module, **kwargs):
        self.module = module
        self.action = kwargs['action']
        self.author = kwargs['author']
        self.comment = kwargs['comment']
        self.host = kwargs['host']
        self.servicegroup = kwargs['servicegroup']
        if kwargs['start'] is not None:
            self.start = int(kwargs['start'])
        else:
            self.start = None
        self.minutes = kwargs['minutes']
        self.cmdfile = kwargs['cmdfile']
        self.command = kwargs['command']

        if (kwargs['services'] is None) or (kwargs['services'] == 'host') or (kwargs['services'] == 'all'):
            self.services = kwargs['services']
        else:
            self.services = kwargs['services'].split(',')

        self.command_results = []

    def _now(self):
        """
        The time in seconds since 12:00:00AM Jan 1, 1970
        """

        return int(time.time())

    def _write_command(self, cmd):
        """
        Write the given command to the Nagios command file
        """

        if not os.path.exists(self.cmdfile):
            self.module.fail_json(msg='nagios command file does not exist',
                                  cmdfile=self.cmdfile)
        if not stat.S_ISFIFO(os.stat(self.cmdfile).st_mode):
            self.module.fail_json(msg='nagios command file is not a fifo file',
                                  cmdfile=self.cmdfile)
        try:
            with open(self.cmdfile, 'w') as fp:
                fp.write(cmd)
                fp.flush()
            self.command_results.append(cmd.strip())
        except IOError:
            self.module.fail_json(msg='unable to write to nagios command file',
                                  cmdfile=self.cmdfile)

    def _fmt_dt_str(self, cmd, host, duration, author=None,
                    comment=None, start=None,
                    svc=None, fixed=1, trigger=0):
        """
        Format an external-command downtime string.

        cmd - Nagios command ID
        host - Host schedule downtime on
        duration - Minutes to schedule downtime for
        author - Name to file the downtime as
        comment - Reason for running this command (upgrade, reboot, etc)
        start - Start of downtime in seconds since 12:00AM Jan 1 1970
          Default is to use the entry time (now)
        svc - Service to schedule downtime for, omit when for host downtime
        fixed - Start now if 1, start when a problem is detected if 0
        trigger - Optional ID of event to start downtime from. Leave as 0 for
          fixed downtime.

        Syntax: [submitted] COMMAND;<host_name>;[<service_description>]
        <start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;
        <comment>
        """

        entry_time = self._now()
        if start is None:
            start = entry_time

        hdr = "[%s] %s;%s;" % (entry_time, cmd, host)
        duration_s = (duration * 60)
        end = start + duration_s

        if not author:
            author = self.author

        if not comment:
            comment = self.comment

        if svc is not None:
            dt_args = [svc, str(start), str(end), str(fixed), str(trigger),
                       str(duration_s), author, comment]
        else:
            # Downtime for a host if no svc specified
            dt_args = [str(start), str(end), str(fixed), str(trigger),
                       str(duration_s), author, comment]

        dt_arg_str = ";".join(dt_args)
        dt_str = hdr + dt_arg_str + "\n"

        return dt_str

    def _fmt_ack_str(self, cmd, host, author=None,
                     comment=None, svc=None, sticky=0, notify=1, persistent=0):
        """
        Format an external-command acknowledge string.

        cmd - Nagios command ID
        host - Host schedule downtime on
        author - Name to file the downtime as
        comment - Reason for running this command (upgrade, reboot, etc)
        svc - Service to schedule downtime for, omit when for host downtime
        sticky - the acknowledgement will remain until the host returns to an UP state if set to 1
        notify -  a notification will be sent out to contacts
        persistent - survive across restarts of the Nagios process

        Syntax: [submitted] COMMAND;<host_name>;[<service_description>]
        <sticky>;<notify>;<persistent>;<author>;<comment>
        """

        entry_time = self._now()
        hdr = "[%s] %s;%s;" % (entry_time, cmd, host)

        if not author:
            author = self.author

        if not comment:
            comment = self.comment

        if svc is not None:
            ack_args = [svc, str(sticky), str(notify), str(persistent), author, comment]
        else:
            # Downtime for a host if no svc specified
            ack_args = [str(sticky), str(notify), str(persistent), author, comment]

        ack_arg_str = ";".join(ack_args)
        ack_str = hdr + ack_arg_str + "\n"

        return ack_str

    def _fmt_dt_del_str(self, cmd, host, svc=None, start=None, comment=None):
        """
        Format an external-command downtime deletion string.

        cmd - Nagios command ID
        host - Host to remove scheduled downtime from
        comment - Reason downtime was added (upgrade, reboot, etc)
        start - Start of downtime in seconds since 12:00AM Jan 1 1970
        svc - Service to remove downtime for, omit to remove all downtime for the host

        Syntax: [submitted] COMMAND;<host_name>;
        [<service_desription>];[<start_time>];[<comment>]
        """

        entry_time = self._now()
        hdr = "[%s] %s;%s;" % (entry_time, cmd, host)

        if comment is None:
            comment = self.comment

        dt_del_args = []
        if svc is not None:
            dt_del_args.append(svc)
        else:
            dt_del_args.append('')

        if start is not None:
            dt_del_args.append(str(start))
        else:
            dt_del_args.append('')

        if comment is not None:
            dt_del_args.append(comment)
        else:
            dt_del_args.append('')

        dt_del_arg_str = ";".join(dt_del_args)
        dt_del_str = hdr + dt_del_arg_str + "\n"

        return dt_del_str

    def _fmt_chk_str(self, cmd, host, svc=None, start=None):
        """
        Format an external-command forced host or service check string.

        cmd - Nagios command ID
        host - Host to check service from
        svc - Service to check
        start - check time

        Syntax: [submitted] COMMAND;<host_name>;[<service_description>];<check_time>
        """

        entry_time = self._now()
        hdr = "[%s] %s;%s;" % (entry_time, cmd, host)

        if start is None:
            start = entry_time + 3

        if svc is None:
            chk_args = [str(start)]
        else:
            chk_args = [svc, str(start)]

        chk_arg_str = ";".join(chk_args)
        chk_str = hdr + chk_arg_str + "\n"

        return chk_str

    def _fmt_notif_str(self, cmd, host=None, svc=None):
        """
        Format an external-command notification string.

        cmd - Nagios command ID.
        host - Host to en/disable notifications on.. A value is not required
          for global downtime
        svc - Service to schedule downtime for. A value is not required
          for host downtime.

        Syntax: [submitted] COMMAND;<host_name>[;<service_description>]
        """

        entry_time = self._now()
        notif_str = "[%s] %s" % (entry_time, cmd)
        if host is not None:
            notif_str += ";%s" % host

            if svc is not None:
                notif_str += ";%s" % svc

        notif_str += "\n"

        return notif_str

    def schedule_svc_downtime(self, host, services=None, minutes=30, start=None):
        """
        This command is used to schedule downtime for a particular
        service.

        During the specified downtime, Nagios will not send
        notifications out about the service.

        Syntax: SCHEDULE_SVC_DOWNTIME;<host_name>;<service_description>
        <start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;
        <comment>
        """

        cmd = "SCHEDULE_SVC_DOWNTIME"

        if services is None:
            services = []

        for service in services:
            dt_cmd_str = self._fmt_dt_str(cmd, host, minutes, start=start, svc=service)
            self._write_command(dt_cmd_str)

    def schedule_host_downtime(self, host, minutes=30, start=None):
        """
        This command is used to schedule downtime for a particular
        host.

        During the specified downtime, Nagios will not send
        notifications out about the host.

        Syntax: SCHEDULE_HOST_DOWNTIME;<host_name>;<start_time>;<end_time>;
        <fixed>;<trigger_id>;<duration>;<author>;<comment>
        """

        cmd = "SCHEDULE_HOST_DOWNTIME"
        dt_cmd_str = self._fmt_dt_str(cmd, host, minutes, start=start)
        self._write_command(dt_cmd_str)

    def acknowledge_svc_problem(self, host, services=None):
        """
        This command is used to acknowledge a particular
        service problem.

        By acknowledging the current problem, future notifications
        for the same servicestate are disabled

        Syntax: ACKNOWLEDGE_SVC_PROBLEM;<host_name>;<service_description>;
        <sticky>;<notify>;<persistent>;<author>;<comment>
        """

        cmd = "ACKNOWLEDGE_SVC_PROBLEM"

        if services is None:
            services = []

        for service in services:
            ack_cmd_str = self._fmt_ack_str(cmd, host, svc=service)
            self._write_command(ack_cmd_str)

    def acknowledge_host_problem(self, host):
        """
        This command is used to acknowledge a particular
        host problem.

        By acknowledging the current problem, future notifications
        for the same servicestate are disabled

        Syntax: ACKNOWLEDGE_HOST_PROBLEM;<host_name>;<sticky>;<notify>;
        <persistent>;<author>;<comment>
        """

        cmd = "ACKNOWLEDGE_HOST_PROBLEM"
        ack_cmd_str = self._fmt_ack_str(cmd, host)
        self._write_command(ack_cmd_str)

    def schedule_forced_host_check(self, host):
        """
        This command schedules a forced active check for a particular host.

        Syntax: SCHEDULE_FORCED_HOST_CHECK;<host_name>;<check_time>
        """

        cmd = "SCHEDULE_FORCED_HOST_CHECK"

        chk_cmd_str = self._fmt_chk_str(cmd, host, svc=None)
        self._write_command(chk_cmd_str)

    def schedule_forced_host_svc_check(self, host):
        """
        This command schedules a forced active check for all services
        associated with a particular host.

        Syntax: SCHEDULE_FORCED_HOST_SVC_CHECKS;<host_name>;<check_time>
        """

        cmd = "SCHEDULE_FORCED_HOST_SVC_CHECKS"

        chk_cmd_str = self._fmt_chk_str(cmd, host, svc=None)
        self._write_command(chk_cmd_str)

    def schedule_forced_svc_check(self, host, services=None):
        """
        This command schedules a forced active check for a particular
        service.

        Syntax: SCHEDULE_FORCED_SVC_CHECK;<host_name>;<service_description>;<check_time>
        """

        cmd = "SCHEDULE_FORCED_SVC_CHECK"

        if services is None:
            services = []

        for service in services:
            chk_cmd_str = self._fmt_chk_str(cmd, host, svc=service)
            self._write_command(chk_cmd_str)

    def schedule_host_svc_downtime(self, host, minutes=30, start=None):
        """
        This command is used to schedule downtime for
        all services associated with a particular host.

        During the specified downtime, Nagios will not send
        notifications out about the host.

        SCHEDULE_HOST_SVC_DOWNTIME;<host_name>;<start_time>;<end_time>;
        <fixed>;<trigger_id>;<duration>;<author>;<comment>
        """

        cmd = "SCHEDULE_HOST_SVC_DOWNTIME"
        dt_cmd_str = self._fmt_dt_str(cmd, host, minutes, start=start)
        self._write_command(dt_cmd_str)

    def delete_host_downtime(self, host, services=None, comment=None):
        """
        This command is used to remove scheduled downtime for a particular
        host.

        Syntax: DEL_DOWNTIME_BY_HOST_NAME;<host_name>;
        [<service_desription>];[<start_time>];[<comment>]
        """

        cmd = "DEL_DOWNTIME_BY_HOST_NAME"

        if services is None:
            dt_del_cmd_str = self._fmt_dt_del_str(cmd, host, comment=comment)
            self._write_command(dt_del_cmd_str)
        else:
            for service in services:
                dt_del_cmd_str = self._fmt_dt_del_str(cmd, host, svc=service, comment=comment)
                self._write_command(dt_del_cmd_str)

    def schedule_hostgroup_host_downtime(self, hostgroup, minutes=30, start=None):
        """
        This command is used to schedule downtime for all hosts in a
        particular hostgroup.

        During the specified downtime, Nagios will not send
        notifications out about the hosts.

        Syntax: SCHEDULE_HOSTGROUP_HOST_DOWNTIME;<hostgroup_name>;<start_time>;
        <end_time>;<fixed>;<trigger_id>;<duration>;<author>;<comment>
        """

        cmd = "SCHEDULE_HOSTGROUP_HOST_DOWNTIME"
        dt_cmd_str = self._fmt_dt_str(cmd, hostgroup, minutes, start=start)
        self._write_command(dt_cmd_str)

    def schedule_hostgroup_svc_downtime(self, hostgroup, minutes=30, start=None):
        """
        This command is used to schedule downtime for all services in
        a particular hostgroup.

        During the specified downtime, Nagios will not send
        notifications out about the services.

        Note that scheduling downtime for services does not
        automatically schedule downtime for the hosts those services
        are associated with.

        Syntax: SCHEDULE_HOSTGROUP_SVC_DOWNTIME;<hostgroup_name>;<start_time>;
        <end_time>;<fixed>;<trigger_id>;<duration>;<author>;<comment>
        """

        cmd = "SCHEDULE_HOSTGROUP_SVC_DOWNTIME"
        dt_cmd_str = self._fmt_dt_str(cmd, hostgroup, minutes, start=start)
        self._write_command(dt_cmd_str)

    def schedule_servicegroup_host_downtime(self, servicegroup, minutes=30, start=None):
        """
        This command is used to schedule downtime for all hosts in a
        particular servicegroup.

        During the specified downtime, Nagios will not send
        notifications out about the hosts.

        Syntax: SCHEDULE_SERVICEGROUP_HOST_DOWNTIME;<servicegroup_name>;
        <start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;
        <comment>
        """

        cmd = "SCHEDULE_SERVICEGROUP_HOST_DOWNTIME"
        dt_cmd_str = self._fmt_dt_str(cmd, servicegroup, minutes, start=start)
        self._write_command(dt_cmd_str)

    def schedule_servicegroup_svc_downtime(self, servicegroup, minutes=30, start=None):
        """
        This command is used to schedule downtime for all services in
        a particular servicegroup.

        During the specified downtime, Nagios will not send
        notifications out about the services.

        Note that scheduling downtime for services does not
        automatically schedule downtime for the hosts those services
        are associated with.

        Syntax: SCHEDULE_SERVICEGROUP_SVC_DOWNTIME;<servicegroup_name>;
        <start_time>;<end_time>;<fixed>;<trigger_id>;<duration>;<author>;
        <comment>
        """

        cmd = "SCHEDULE_SERVICEGROUP_SVC_DOWNTIME"
        dt_cmd_str = self._fmt_dt_str(cmd, servicegroup, minutes, start=start)
        self._write_command(dt_cmd_str)

    def disable_host_svc_notifications(self, host):
        """
        This command is used to prevent notifications from being sent
        out for all services on the specified host.

        Note that this command does not disable notifications from
        being sent out about the host.

        Syntax: DISABLE_HOST_SVC_NOTIFICATIONS;<host_name>
        """

        cmd = "DISABLE_HOST_SVC_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, host)
        self._write_command(notif_str)

    def disable_host_notifications(self, host):
        """
        This command is used to prevent notifications from being sent
        out for the specified host.

        Note that this command does not disable notifications for
        services associated with this host.

        Syntax: DISABLE_HOST_NOTIFICATIONS;<host_name>
        """

        cmd = "DISABLE_HOST_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, host)
        self._write_command(notif_str)

    def disable_svc_notifications(self, host, services=None):
        """
        This command is used to prevent notifications from being sent
        out for the specified service.

        Note that this command does not disable notifications from
        being sent out about the host.

        Syntax: DISABLE_SVC_NOTIFICATIONS;<host_name>;<service_description>
        """

        cmd = "DISABLE_SVC_NOTIFICATIONS"

        if services is None:
            services = []

        for service in services:
            notif_str = self._fmt_notif_str(cmd, host, svc=service)
            self._write_command(notif_str)

    def disable_servicegroup_host_notifications(self, servicegroup):
        """
        This command is used to prevent notifications from being sent
        out for all hosts in the specified servicegroup.

        Note that this command does not disable notifications for
        services associated with hosts in this service group.

        Syntax: DISABLE_SERVICEGROUP_HOST_NOTIFICATIONS;<servicegroup_name>
        """

        cmd = "DISABLE_SERVICEGROUP_HOST_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, servicegroup)
        self._write_command(notif_str)

    def disable_servicegroup_svc_notifications(self, servicegroup):
        """
        This command is used to prevent notifications from being sent
        out for all services in the specified servicegroup.

        Note that this does not prevent notifications from being sent
        out about the hosts in this servicegroup.

        Syntax: DISABLE_SERVICEGROUP_SVC_NOTIFICATIONS;<servicegroup_name>
        """

        cmd = "DISABLE_SERVICEGROUP_SVC_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, servicegroup)
        self._write_command(notif_str)

    def disable_hostgroup_host_notifications(self, hostgroup):
        """
        Disables notifications for all hosts in a particular
        hostgroup.

        Note that this does not disable notifications for the services
        associated with the hosts in the hostgroup - see the
        DISABLE_HOSTGROUP_SVC_NOTIFICATIONS command for that.

        Syntax: DISABLE_HOSTGROUP_HOST_NOTIFICATIONS;<hostgroup_name>
        """

        cmd = "DISABLE_HOSTGROUP_HOST_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, hostgroup)
        self._write_command(notif_str)

    def disable_hostgroup_svc_notifications(self, hostgroup):
        """
        Disables notifications for all services associated with hosts
        in a particular hostgroup.

        Note that this does not disable notifications for the hosts in
        the hostgroup - see the DISABLE_HOSTGROUP_HOST_NOTIFICATIONS
        command for that.

        Syntax: DISABLE_HOSTGROUP_SVC_NOTIFICATIONS;<hostgroup_name>
        """

        cmd = "DISABLE_HOSTGROUP_SVC_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, hostgroup)
        self._write_command(notif_str)

    def enable_host_notifications(self, host):
        """
        Enables notifications for a particular host.

        Note that this command does not enable notifications for
        services associated with this host.

        Syntax: ENABLE_HOST_NOTIFICATIONS;<host_name>
        """

        cmd = "ENABLE_HOST_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, host)
        self._write_command(notif_str)

    def enable_host_svc_notifications(self, host):
        """
        Enables notifications for all services on the specified host.

        Note that this does not enable notifications for the host.

        Syntax: ENABLE_HOST_SVC_NOTIFICATIONS;<host_name>
        """

        cmd = "ENABLE_HOST_SVC_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, host)
        nagios_return = self._write_command(notif_str)

        if nagios_return:
            return notif_str
        else:
            return "Fail: could not write to the command file"

    def enable_svc_notifications(self, host, services=None):
        """
        Enables notifications for a particular service.

        Note that this does not enable notifications for the host.

        Syntax: ENABLE_SVC_NOTIFICATIONS;<host_name>;<service_description>
        """

        cmd = "ENABLE_SVC_NOTIFICATIONS"

        if services is None:
            services = []

        nagios_return = True
        return_str_list = []
        for service in services:
            notif_str = self._fmt_notif_str(cmd, host, svc=service)
            nagios_return = self._write_command(notif_str) and nagios_return
            return_str_list.append(notif_str)

        if nagios_return:
            return return_str_list
        else:
            return "Fail: could not write to the command file"

    def enable_hostgroup_host_notifications(self, hostgroup):
        """
        Enables notifications for all hosts in a particular hostgroup.

        Note that this command does not enable notifications for
        services associated with the hosts in this hostgroup.

        Syntax: ENABLE_HOSTGROUP_HOST_NOTIFICATIONS;<hostgroup_name>
        """

        cmd = "ENABLE_HOSTGROUP_HOST_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, hostgroup)
        nagios_return = self._write_command(notif_str)

        if nagios_return:
            return notif_str
        else:
            return "Fail: could not write to the command file"

    def enable_hostgroup_svc_notifications(self, hostgroup):
        """
        Enables notifications for all services that are associated
        with hosts in a particular hostgroup.

        Note that this does not enable notifications for the hosts in
        this hostgroup.

        Syntax: ENABLE_HOSTGROUP_SVC_NOTIFICATIONS;<hostgroup_name>
        """

        cmd = "ENABLE_HOSTGROUP_SVC_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, hostgroup)
        nagios_return = self._write_command(notif_str)

        if nagios_return:
            return notif_str
        else:
            return "Fail: could not write to the command file"

    def enable_servicegroup_host_notifications(self, servicegroup):
        """
        Enables notifications for all hosts that have services that
        are members of a particular servicegroup.

        Note that this command does not enable notifications for
        services associated with the hosts in this servicegroup.

        Syntax: ENABLE_SERVICEGROUP_HOST_NOTIFICATIONS;<servicegroup_name>
        """

        cmd = "ENABLE_SERVICEGROUP_HOST_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, servicegroup)
        nagios_return = self._write_command(notif_str)

        if nagios_return:
            return notif_str
        else:
            return "Fail: could not write to the command file"

    def enable_servicegroup_svc_notifications(self, servicegroup):
        """
        Enables notifications for all services that are members of a
        particular servicegroup.

        Note that this does not enable notifications for the hosts in
        this servicegroup.

        Syntax: ENABLE_SERVICEGROUP_SVC_NOTIFICATIONS;<servicegroup_name>
        """

        cmd = "ENABLE_SERVICEGROUP_SVC_NOTIFICATIONS"
        notif_str = self._fmt_notif_str(cmd, servicegroup)
        nagios_return = self._write_command(notif_str)

        if nagios_return:
            return notif_str
        else:
            return "Fail: could not write to the command file"

    def silence_host(self, host):
        """
        This command is used to prevent notifications from being sent
        out for the host and all services on the specified host.

        This is equivalent to calling disable_host_svc_notifications
        and disable_host_notifications.

        Syntax: DISABLE_HOST_SVC_NOTIFICATIONS;<host_name>
        Syntax: DISABLE_HOST_NOTIFICATIONS;<host_name>
        """

        cmd = [
            "DISABLE_HOST_SVC_NOTIFICATIONS",
            "DISABLE_HOST_NOTIFICATIONS"
        ]
        nagios_return = True
        return_str_list = []
        for c in cmd:
            notif_str = self._fmt_notif_str(c, host)
            nagios_return = self._write_command(notif_str) and nagios_return
            return_str_list.append(notif_str)

        if nagios_return:
            return return_str_list
        else:
            return "Fail: could not write to the command file"

    def unsilence_host(self, host):
        """
        This command is used to enable notifications for the host and
        all services on the specified host.

        This is equivalent to calling enable_host_svc_notifications
        and enable_host_notifications.

        Syntax: ENABLE_HOST_SVC_NOTIFICATIONS;<host_name>
        Syntax: ENABLE_HOST_NOTIFICATIONS;<host_name>
        """

        cmd = [
            "ENABLE_HOST_SVC_NOTIFICATIONS",
            "ENABLE_HOST_NOTIFICATIONS"
        ]
        nagios_return = True
        return_str_list = []
        for c in cmd:
            notif_str = self._fmt_notif_str(c, host)
            nagios_return = self._write_command(notif_str) and nagios_return
            return_str_list.append(notif_str)

        if nagios_return:
            return return_str_list
        else:
            return "Fail: could not write to the command file"

    def silence_nagios(self):
        """
        This command is used to disable notifications for all hosts and services
        in nagios.

        This is a 'SHUT UP, NAGIOS' command
        """
        cmd = 'DISABLE_NOTIFICATIONS'
        self._write_command(self._fmt_notif_str(cmd))

    def unsilence_nagios(self):
        """
        This command is used to enable notifications for all hosts and services
        in nagios.

        This is a 'OK, NAGIOS, GO'' command
        """
        cmd = 'ENABLE_NOTIFICATIONS'
        self._write_command(self._fmt_notif_str(cmd))

    def nagios_cmd(self, cmd):
        """
        This sends an arbitrary command to nagios

        It prepends the submitted time and appends a \n

        You just have to provide the properly formatted command
        """

        pre = '[%s]' % int(time.time())

        post = '\n'
        cmdstr = '%s %s%s' % (pre, cmd, post)
        self._write_command(cmdstr)

    def act(self):
        """
        Figure out what you want to do from ansible, and then do the
        needful (at the earliest).
        """
        # host or service downtime?
        if self.action == 'downtime':
            if self.services == 'host':
                self.schedule_host_downtime(self.host, minutes=self.minutes,
                                            start=self.start)
            elif self.services == 'all':
                self.schedule_host_svc_downtime(self.host, minutes=self.minutes,
                                                start=self.start)
            else:
                self.schedule_svc_downtime(self.host,
                                           services=self.services,
                                           minutes=self.minutes,
                                           start=self.start)

        elif self.action == 'acknowledge':
            if self.services == 'host':
                self.acknowledge_host_problem(self.host)
            else:
                self.acknowledge_svc_problem(self.host, services=self.services)

        elif self.action == 'delete_downtime':
            if self.services == 'host':
                self.delete_host_downtime(self.host)
            elif self.services == 'all':
                self.delete_host_downtime(self.host, comment='')
            else:
                self.delete_host_downtime(self.host, services=self.services)

        elif self.action == 'forced_check':
            if self.services == 'host':
                self.schedule_forced_host_check(self.host)
            elif self.services == 'all':
                self.schedule_forced_host_svc_check(self.host)
            else:
                self.schedule_forced_svc_check(self.host, services=self.services)

        elif self.action == "servicegroup_host_downtime":
            if self.servicegroup:
                self.schedule_servicegroup_host_downtime(servicegroup=self.servicegroup, minutes=self.minutes, start=self.start)
        elif self.action == "servicegroup_service_downtime":
            if self.servicegroup:
                self.schedule_servicegroup_svc_downtime(servicegroup=self.servicegroup, minutes=self.minutes, start=self.start)

        # toggle the host AND service alerts
        elif self.action == 'silence':
            self.silence_host(self.host)

        elif self.action == 'unsilence':
            self.unsilence_host(self.host)

        # toggle host/svc alerts
        elif self.action == 'enable_alerts':
            if self.services == 'host':
                self.enable_host_notifications(self.host)
            elif self.services == 'all':
                self.enable_host_svc_notifications(self.host)
            else:
                self.enable_svc_notifications(self.host,
                                              services=self.services)

        elif self.action == 'disable_alerts':
            if self.services == 'host':
                self.disable_host_notifications(self.host)
            elif self.services == 'all':
                self.disable_host_svc_notifications(self.host)
            else:
                self.disable_svc_notifications(self.host,
                                               services=self.services)
        elif self.action == 'silence_nagios':
            self.silence_nagios()

        elif self.action == 'unsilence_nagios':
            self.unsilence_nagios()

        elif self.action == 'command':
            self.nagios_cmd(self.command)

        # wtf?
        else:
            self.module.fail_json(msg="unknown action specified: '%s'" %
                                      self.action)

        self.module.exit_json(nagios_commands=self.command_results,
                              changed=True)


if __name__ == '__main__':
    main()

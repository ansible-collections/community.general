#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright: (c) 2017, Nathan Davison <ndavison85@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: listen_ports_facts
author:
    - Nathan Davison (@ndavison)
description:
    - Gather facts on processes listening on TCP and UDP ports using the C(netstat) or C(ss) commands.
    - This module currently supports Linux only.
requirements:
  - netstat or ss
short_description: Gather facts on processes listening on TCP and UDP ports.
notes:
  - |
    C(ss) returns all processes for each listen address and port.
    This plugin will return each of them, so multiple entries for the same listen address and port are likely in results.
options:
  command:
    description:
      - Override which command to use for fetching listen ports.
      - 'By default module will use first found supported command on the system (in alphanumerical order).'
    type: str
    choices:
      - netstat
      - ss
    version_added: 4.1.0
'''

EXAMPLES = r'''
- name: Gather facts on listening ports
  community.general.listen_ports_facts:

- name: TCP whitelist violation
  ansible.builtin.debug:
    msg: TCP port {{ item.port }} by pid {{ item.pid }} violates the whitelist
  vars:
    tcp_listen_violations: "{{ ansible_facts.tcp_listen | selectattr('port', 'in', tcp_whitelist) | list }}"
    tcp_whitelist:
      - 22
      - 25
  loop: "{{ tcp_listen_violations }}"

- name: List TCP ports
  ansible.builtin.debug:
    msg: "{{ ansible_facts.tcp_listen  | map(attribute='port') | sort | list }}"

- name: List UDP ports
  ansible.builtin.debug:
    msg: "{{ ansible_facts.udp_listen | map(attribute='port') | sort | list }}"

- name: List all ports
  ansible.builtin.debug:
    msg: "{{ (ansible_facts.tcp_listen + ansible_facts.udp_listen) | map(attribute='port') | unique | sort | list }}"
'''

RETURN = r'''
ansible_facts:
  description: Dictionary containing details of TCP and UDP ports with listening servers
  returned: always
  type: complex
  contains:
    tcp_listen:
      description: A list of processes that are listening on a TCP port.
      returned: if TCP servers were found
      type: list
      contains:
        address:
          description: The address the server is listening on.
          returned: always
          type: str
          sample: "0.0.0.0"
        name:
          description: The name of the listening process.
          returned: if user permissions allow
          type: str
          sample: "mysqld"
        pid:
          description: The pid of the listening process.
          returned: always
          type: int
          sample: 1223
        port:
          description: The port the server is listening on.
          returned: always
          type: int
          sample: 3306
        protocol:
          description: The network protocol of the server.
          returned: always
          type: str
          sample: "tcp"
        stime:
          description: The start time of the listening process.
          returned: always
          type: str
          sample: "Thu Feb  2 13:29:45 2017"
        user:
          description: The user who is running the listening process.
          returned: always
          type: str
          sample: "mysql"
    udp_listen:
      description: A list of processes that are listening on a UDP port.
      returned: if UDP servers were found
      type: list
      contains:
        address:
          description: The address the server is listening on.
          returned: always
          type: str
          sample: "0.0.0.0"
        name:
          description: The name of the listening process.
          returned: if user permissions allow
          type: str
          sample: "rsyslogd"
        pid:
          description: The pid of the listening process.
          returned: always
          type: int
          sample: 609
        port:
          description: The port the server is listening on.
          returned: always
          type: int
          sample: 514
        protocol:
          description: The network protocol of the server.
          returned: always
          type: str
          sample: "udp"
        stime:
          description: The start time of the listening process.
          returned: always
          type: str
          sample: "Thu Feb  2 13:29:45 2017"
        user:
          description: The user who is running the listening process.
          returned: always
          type: str
          sample: "root"
'''

import re
import platform
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.basic import AnsibleModule


def split_pid_name(pid_name: str):
    """
    Split the entry PID/Program name into the PID (int) and the name (str)
    :param pid_name:  PID/Program String seperated with a dash. E.g 51/sshd: returns pid = 51 and name = sshd
    :return: PID (int) and the program name (str)
    """
    try:
        pid, name = pid_name.split("/", 1)
    except ValueError:
        # likely unprivileged user, so add empty name & pid
        return 0, ""
    else:
        name = name.rstrip(":")
        return int(pid), name


def netStatParse(raw:str):
    """
    The netstat result can be either split in 6,7 or 8 elements depending on the values of state, process and name.
    For UDP the state is always empty. For UDP and TCP the process can be empty.
    So these cases have to be checked.
    :param raw: Netstat raw output. First line explains the format, each following line contains a connection.
    :return: List of dicts, each dict contains protocol, state, local address, foreign address, port, name, pid for one
     connection.
    """
    results = list()
    for line in raw.splitlines():
        if line.startswith(("tcp", "udp")):
            # set variables to default state, in case they are not specified
            state = ""
            pid_and_name = ""
            process = ""
            formatted_line = line.split()
            protocol, recv_q, send_q, local_address, foreign_address, rest = \
                formatted_line[0], formatted_line[1], formatted_line[2], formatted_line[3], formatted_line[4], formatted_line[5:]
            local_address, port = local_address.rsplit(":", 1)

            if protocol.startswith("tcp"):
                if len(rest) == 3:
                    state, pid_and_name, process = rest
                if len(rest) == 2:
                    state, pid_and_name = rest

            if protocol.startswith("udp"):
                if len(rest) == 2:
                    pid_and_name, process = rest
                if len(rest) == 1:
                    pid_and_name = rest[0]

            pid, name = split_pid_name(pid_name=pid_and_name)
            result = {
                'protocol': protocol,
                'state': state,
                'local address': local_address,
                'foreign address': foreign_address,
                'port': int(port),
                'name': name,
                'pid': int(pid),
            }
            if result not in results:
                results.append(result)
            else:
                raise EnvironmentError('Could not get process information for the listening ports.')
    return results


def ss_parse(raw):
    """
    The ss_parse result can be either split in 6 or 7 elements depending on the process column,
    e.g. due to unprivileged user.
    :param raw: ss raw output. First line explains the format, each following line contains a connection.
    :return: List of dicts, each dict contains protocol, state, local address, foreign address, port, name, pid for one
     connection.
    """
    results = list()
    regex_conns = re.compile(pattern=r'\[?(.+?)\]?:([0-9]+)$')
    regex_pid = re.compile(pattern=r'"(.*?)",pid=(\d+)')

    lines = raw.splitlines()

    if len(lines) == 0 or not lines[0].startswith('Netid '):
        # unexpected stdout from ss
        raise EnvironmentError('Unknown stdout format of `ss`: {0}'.format(raw))

    # skip headers (-H arg is not present on e.g. Ubuntu 16)
    lines = lines[1:]

    for line in lines:
        cells = line.split(None, 6)
        try:
            if len(cells) == 6:
                # no process column, e.g. due to unprivileged user
                process = str()
                protocol, state, recv_q, send_q, local_addr_port, peer_addr_port = cells
            else:
                protocol, state, recv_q, send_q, local_addr_port, peer_addr_port, process = cells
        except ValueError:
            # unexpected stdout from ss
            raise EnvironmentError(
                'Expected `ss` table layout "Netid, State, Recv-Q, Send-Q, Local Address:Port, Peer Address:Port" and \
                 optionally "Process", but got something else: {0}'.format(line)
            )

        try:
            name, pid = regex_pid.findall(process)[0]
        except IndexError:
            # likely unprivileged user, so add empty name & pid
            # as we do in netstat logic to be consistent with output
            pid = 0
            name = ""

        conns = regex_conns.search(local_addr_port)
        address = conns.group(1)
        port = conns.group(2)
        result = {
            'protocol': protocol,
            'state': state,
            'local address': address,
            'foreign address': peer_addr_port,
            'port': int(port),
            'name': name,
            'pid': int(pid),
        }
        results.append(result)
    return results


def main():
    commands_map = {
        'netstat': {
            'args': [
                '-p',
                '-a',
                '-u',
                '-n',
                '-t',
            ],
            'parse_func': netStatParse
        },
        'ss': {
            'args': [
                '-p',
                '-a',
                '-u',
                '-n',
                '-t',
            ],
            'parse_func': ss_parse
        },
    }
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(type='str', choices=list(sorted(commands_map)))
        ),
        supports_check_mode=True,
    )

    if platform.system() != 'Linux':
        module.fail_json(msg='This module requires Linux.')

    def getPidSTime(pid):
        ps_cmd = module.get_bin_path('ps', True)
        rc, ps_output, stderr = module.run_command([ps_cmd, '-o', 'lstart', '-p', str(pid)])
        stime = ''
        if rc == 0:
            for line in ps_output.splitlines():
                if 'started' not in line:
                    stime = line
        return stime

    def getPidUser(pid):
        ps_cmd = module.get_bin_path('ps', True)
        rc, ps_output, stderr = module.run_command([ps_cmd, '-o', 'user', '-p', str(pid)])
        user = ''
        if rc == 0:
            for line in ps_output.splitlines():
                if line != 'USER':
                    user = line
        return user

    result = {
        'changed': False,
        'ansible_facts': {
            'tcp_listen': [],
            'udp_listen': [],
        },
    }

    try:
        command = None
        bin_path = None
        if module.params['command'] is not None:
            command = module.params['command']
            bin_path = module.get_bin_path(command, required=True)
        else:
            for c in sorted(commands_map):
                bin_path = module.get_bin_path(c, required=False)
                if bin_path is not None:
                    command = c
                    break

        if bin_path is None:
            raise EnvironmentError(msg='Unable to find any of the supported commands in PATH: {0}'.format(", ".join(sorted(commands_map))))

        # which ports are listening for connections?
        args = commands_map[command]['args']
        rc, stdout, stderr = module.run_command([bin_path] + args)
        if rc == 0:
            parse_func = commands_map[command]['parse_func']
            results = parse_func(stdout)

            for p in results:
                p['stime'] = getPidSTime(p['pid'])
                p['user'] = getPidUser(p['pid'])
                if p['protocol'].startswith('tcp'):
                    result['ansible_facts']['tcp_listen'].append(p)
                elif p['protocol'].startswith('udp'):
                    result['ansible_facts']['udp_listen'].append(p)
    except (KeyError, EnvironmentError) as e:
        module.fail_json(msg=to_native(e))

    module.exit_json(**result)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, quidame <quidame@poivron.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: iptables_state
short_description: Save iptables state into a file or restore it from a file
version_added: '1.1.0'
author: quidame (@quidame)
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.flow
description:
  - C(iptables) is used to set up, maintain, and inspect the tables of IP
    packet filter rules in the Linux kernel.
  - This module handles the saving and/or loading of rules. This is the same
    as the behaviour of the C(iptables-save) and C(iptables-restore) (or
    C(ip6tables-save) and C(ip6tables-restore) for IPv6) commands which this
    module uses internally.
  - Modifying the state of the firewall remotely may lead to loose access to
    the host in case of mistake in new ruleset. This module embeds a rollback
    feature to avoid this, by telling the host to restore previous rules if a
    cookie is still there after a given delay, and all this time telling the
    controller to try to remove this cookie on the host through a new
    connection.
notes:
  - The rollback feature is not a module option and depends on task's
    attributes. To enable it, the module must be played asynchronously, i.e.
    by setting task attributes C(poll) to V(0), and C(async) to a value less
    or equal to C(ANSIBLE_TIMEOUT). If C(async) is greater, the rollback will
    still happen if it shall happen, but you will experience a connection
    timeout instead of more relevant info returned by the module after its
    failure.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
  action:
    support: full
  async:
    support: full
options:
  counters:
    description:
      - Save or restore the values of all packet and byte counters.
      - When V(true), the module is not idempotent.
    type: bool
    default: false
  ip_version:
    description:
      - Which version of the IP protocol this module should apply to.
    type: str
    choices: [ ipv4, ipv6 ]
    default: ipv4
  modprobe:
    description:
      - Specify the path to the C(modprobe) program internally used by iptables
        related commands to load kernel modules.
      - By default, V(/proc/sys/kernel/modprobe) is inspected to determine the
        executable's path.
    type: path
  noflush:
    description:
      - For O(state=restored), ignored otherwise.
      - If V(false), restoring iptables rules from a file flushes (deletes)
        all previous contents of the respective table(s). If V(true), the
        previous rules are left untouched (but policies are updated anyway,
        for all built-in chains).
    type: bool
    default: false
  path:
    description:
      - The file the iptables state should be saved to.
      - The file the iptables state should be restored from.
    type: path
    required: true
  state:
    description:
      - Whether the firewall state should be saved (into a file) or restored
        (from a file).
    type: str
    choices: [ saved, restored ]
    required: true
  table:
    description:
      - When O(state=restored), restore only the named table even if the input
        file contains other tables. Fail if the named table is not declared in
        the file.
      - When O(state=saved), restrict output to the specified table. If not
        specified, output includes all active tables.
    type: str
    choices: [ filter, nat, mangle, raw, security ]
  wait:
    description:
      - Wait N seconds for the xtables lock to prevent instant failure in case
        multiple instances of the program are running concurrently.
    type: int
requirements: [iptables, ip6tables]
'''

EXAMPLES = r'''
# This will apply to all loaded/active IPv4 tables.
- name: Save current state of the firewall in system file
  community.general.iptables_state:
    state: saved
    path: /etc/sysconfig/iptables

# This will apply only to IPv6 filter table.
- name: save current state of the firewall in system file
  community.general.iptables_state:
    ip_version: ipv6
    table: filter
    state: saved
    path: /etc/iptables/rules.v6

# This will load a state from a file, with a rollback in case of access loss
- name: restore firewall state from a file
  community.general.iptables_state:
    state: restored
    path: /run/iptables.apply
  async: "{{ ansible_timeout }}"
  poll: 0

# This will load new rules by appending them to the current ones
- name: restore firewall state from a file
  community.general.iptables_state:
    state: restored
    path: /run/iptables.apply
    noflush: true
  async: "{{ ansible_timeout }}"
  poll: 0

# This will only retrieve information
- name: get current state of the firewall
  community.general.iptables_state:
    state: saved
    path: /tmp/iptables
  check_mode: true
  changed_when: false
  register: iptables_state

- name: show current state of the firewall
  ansible.builtin.debug:
    var: iptables_state.initial_state
'''

RETURN = r'''
applied:
  description: Whether or not the wanted state has been successfully restored.
  type: bool
  returned: always
  sample: true
initial_state:
  description: The current state of the firewall when module starts.
  type: list
  elements: str
  returned: always
  sample: [
      "# Generated by xtables-save v1.8.2",
      "*filter",
      ":INPUT ACCEPT [0:0]",
      ":FORWARD ACCEPT [0:0]",
      ":OUTPUT ACCEPT [0:0]",
      "COMMIT",
      "# Completed"
    ]
restored:
  description: The state the module restored, whenever it is finally applied or not.
  type: list
  elements: str
  returned: always
  sample: [
      "# Generated by xtables-save v1.8.2",
      "*filter",
      ":INPUT DROP [0:0]",
      ":FORWARD DROP [0:0]",
      ":OUTPUT ACCEPT [0:0]",
      "-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT",
      "-A INPUT -m conntrack --ctstate INVALID -j DROP",
      "-A INPUT -i lo -j ACCEPT",
      "-A INPUT -p icmp -j ACCEPT",
      "-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT",
      "COMMIT",
      "# Completed"
    ]
saved:
  description: The iptables state the module saved.
  type: list
  elements: str
  returned: always
  sample: [
      "# Generated by xtables-save v1.8.2",
      "*filter",
      ":INPUT ACCEPT [0:0]",
      ":FORWARD DROP [0:0]",
      ":OUTPUT ACCEPT [0:0]",
      "COMMIT",
      "# Completed"
    ]
tables:
  description:
    - The iptables on the system before the module has run, separated by table.
    - If the option O(table) is used, only this table is included.
  type: dict
  contains:
    table:
      description: Policies and rules for all chains of the named table.
      type: list
      elements: str
  sample: |-
    {
      "filter": [
        ":INPUT ACCEPT",
        ":FORWARD ACCEPT",
        ":OUTPUT ACCEPT",
        "-A INPUT -i lo -j ACCEPT",
        "-A INPUT -p icmp -j ACCEPT",
        "-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT",
        "-A INPUT -j REJECT --reject-with icmp-host-prohibited"
      ],
      "nat": [
        ":PREROUTING ACCEPT",
        ":INPUT ACCEPT",
        ":OUTPUT ACCEPT",
        ":POSTROUTING ACCEPT"
      ]
    }
  returned: always
'''


import re
import os
import time
import tempfile
import filecmp
import shutil

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes, to_native


IPTABLES = dict(
    ipv4='iptables',
    ipv6='ip6tables',
)

SAVE = dict(
    ipv4='iptables-save',
    ipv6='ip6tables-save',
)

RESTORE = dict(
    ipv4='iptables-restore',
    ipv6='ip6tables-restore',
)

TABLES = ['filter', 'mangle', 'nat', 'raw', 'security']


def read_state(b_path):
    '''
    Read a file and store its content in a variable as a list.
    '''
    with open(b_path, 'r') as f:
        text = f.read()
    return [t for t in text.splitlines() if t != '']


def write_state(b_path, lines, changed):
    '''
    Write given contents to the given path, and return changed status.
    '''
    # Populate a temporary file
    tmpfd, tmpfile = tempfile.mkstemp()
    with os.fdopen(tmpfd, 'w') as f:
        f.write("{0}\n".format("\n".join(lines)))

    # Prepare to copy temporary file to the final destination
    if not os.path.exists(b_path):
        b_destdir = os.path.dirname(b_path)
        destdir = to_native(b_destdir, errors='surrogate_or_strict')
        if b_destdir and not os.path.exists(b_destdir) and not module.check_mode:
            try:
                os.makedirs(b_destdir)
            except Exception as err:
                module.fail_json(
                    msg='Error creating %s: %s' % (destdir, to_native(err)),
                    initial_state=lines)
        changed = True

    elif not filecmp.cmp(tmpfile, b_path):
        changed = True

    # Do it
    if changed and not module.check_mode:
        try:
            shutil.copyfile(tmpfile, b_path)
        except Exception as err:
            path = to_native(b_path, errors='surrogate_or_strict')
            module.fail_json(
                msg='Error saving state into %s: %s' % (path, to_native(err)),
                initial_state=lines)

    return changed


def initialize_from_null_state(initializer, initcommand, fallbackcmd, table):
    '''
    This ensures iptables-state output is suitable for iptables-restore to roll
    back to it, i.e. iptables-save output is not empty. This also works for the
    iptables-nft-save alternative.
    '''
    if table is None:
        table = 'filter'

    commandline = list(initializer)
    commandline += ['-t', table]
    dummy = module.run_command(commandline, check_rc=True)
    (rc, out, err) = module.run_command(initcommand, check_rc=True)
    if '*%s' % table not in out.splitlines():
        # The last resort.
        iptables_input = '*%s\n:OUTPUT ACCEPT\nCOMMIT\n' % table
        dummy = module.run_command(fallbackcmd, data=iptables_input, check_rc=True)
        (rc, out, err) = module.run_command(initcommand, check_rc=True)

    return rc, out, err


def filter_and_format_state(string):
    '''
    Remove timestamps to ensure idempotence between runs. Also remove counters
    by default. And return the result as a list.
    '''
    string = re.sub(r'((^|\n)# (Generated|Completed)[^\n]*) on [^\n]*', r'\1', string)
    if not module.params['counters']:
        string = re.sub(r'\[[0-9]+:[0-9]+\]', r'[0:0]', string)
    lines = [line for line in string.splitlines() if line != '']
    return lines


def parse_per_table_state(all_states_dump):
    '''
    Convert raw iptables-save output into usable datastructure, for reliable
    comparisons between initial and final states.
    '''
    lines = filter_and_format_state(all_states_dump)
    tables = dict()
    current_table = ''
    current_list = list()
    for line in lines:
        if re.match(r'^[*](filter|mangle|nat|raw|security)$', line):
            current_table = line[1:]
            continue
        if line == 'COMMIT':
            tables[current_table] = current_list
            current_table = ''
            current_list = list()
            continue
        if line.startswith('# '):
            continue
        current_list.append(line)
    return tables


def main():

    global module

    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True),
            state=dict(type='str', choices=['saved', 'restored'], required=True),
            table=dict(type='str', choices=['filter', 'nat', 'mangle', 'raw', 'security']),
            noflush=dict(type='bool', default=False),
            counters=dict(type='bool', default=False),
            modprobe=dict(type='path'),
            ip_version=dict(type='str', choices=['ipv4', 'ipv6'], default='ipv4'),
            wait=dict(type='int'),
            _timeout=dict(type='int'),
            _back=dict(type='path'),
        ),
        required_together=[
            ['_timeout', '_back'],
        ],
        supports_check_mode=True,
    )

    # We'll parse iptables-restore stderr
    module.run_command_environ_update = dict(LANG='C', LC_MESSAGES='C')

    path = module.params['path']
    state = module.params['state']
    table = module.params['table']
    noflush = module.params['noflush']
    counters = module.params['counters']
    modprobe = module.params['modprobe']
    ip_version = module.params['ip_version']
    wait = module.params['wait']
    _timeout = module.params['_timeout']
    _back = module.params['_back']

    bin_iptables = module.get_bin_path(IPTABLES[ip_version], True)
    bin_iptables_save = module.get_bin_path(SAVE[ip_version], True)
    bin_iptables_restore = module.get_bin_path(RESTORE[ip_version], True)

    os.umask(0o077)
    changed = False
    COMMANDARGS = []
    INITCOMMAND = [bin_iptables_save]
    INITIALIZER = [bin_iptables, '-L', '-n']
    TESTCOMMAND = [bin_iptables_restore, '--test']
    FALLBACKCMD = [bin_iptables_restore]

    if counters:
        COMMANDARGS.append('--counters')

    if table is not None:
        COMMANDARGS.extend(['--table', table])

    if wait is not None:
        TESTCOMMAND.extend(['--wait', '%s' % wait])

    if modprobe is not None:
        b_modprobe = to_bytes(modprobe, errors='surrogate_or_strict')
        if not os.path.exists(b_modprobe):
            module.fail_json(msg="modprobe %s not found" % modprobe)
        if not os.path.isfile(b_modprobe):
            module.fail_json(msg="modprobe %s not a file" % modprobe)
        if not os.access(b_modprobe, os.R_OK):
            module.fail_json(msg="modprobe %s not readable" % modprobe)
        if not os.access(b_modprobe, os.X_OK):
            module.fail_json(msg="modprobe %s not executable" % modprobe)
        COMMANDARGS.extend(['--modprobe', modprobe])
        INITIALIZER.extend(['--modprobe', modprobe])
        INITCOMMAND.extend(['--modprobe', modprobe])
        TESTCOMMAND.extend(['--modprobe', modprobe])
        FALLBACKCMD.extend(['--modprobe', modprobe])

    SAVECOMMAND = list(COMMANDARGS)
    SAVECOMMAND.insert(0, bin_iptables_save)

    b_path = to_bytes(path, errors='surrogate_or_strict')

    if state == 'restored':
        if not os.path.exists(b_path):
            module.fail_json(msg="Source %s not found" % path)
        if not os.path.isfile(b_path):
            module.fail_json(msg="Source %s not a file" % path)
        if not os.access(b_path, os.R_OK):
            module.fail_json(msg="Source %s not readable" % path)
        state_to_restore = read_state(b_path)
    else:
        cmd = ' '.join(SAVECOMMAND)

    (rc, stdout, stderr) = module.run_command(INITCOMMAND, check_rc=True)

    # The issue comes when wanting to restore state from empty iptable-save's
    # output... what happens when, say:
    # - no table is specified, and iptables-save's output is only nat table;
    # - we give filter's ruleset to iptables-restore, that locks ourselves out
    #   of the host;
    # then trying to roll iptables state back to the previous (working) setup
    # doesn't override current filter table because no filter table is stored
    # in the backup ! So we have to ensure tables to be restored have a backup
    # in case of rollback.
    if table is None:
        if state == 'restored':
            for t in TABLES:
                if '*%s' % t in state_to_restore:
                    if len(stdout) == 0 or '*%s' % t not in stdout.splitlines():
                        (rc, stdout, stderr) = initialize_from_null_state(INITIALIZER, INITCOMMAND, FALLBACKCMD, t)
        elif len(stdout) == 0:
            (rc, stdout, stderr) = initialize_from_null_state(INITIALIZER, INITCOMMAND, FALLBACKCMD, 'filter')

    elif state == 'restored' and '*%s' % table not in state_to_restore:
        module.fail_json(msg="Table %s to restore not defined in %s" % (table, path))

    elif len(stdout) == 0 or '*%s' % table not in stdout.splitlines():
        (rc, stdout, stderr) = initialize_from_null_state(INITIALIZER, INITCOMMAND, FALLBACKCMD, table)

    initial_state = filter_and_format_state(stdout)
    if initial_state is None:
        module.fail_json(msg="Unable to initialize firewall from NULL state.")

    # Depending on the value of 'table', initref_state may differ from
    # initial_state.
    (rc, stdout, stderr) = module.run_command(SAVECOMMAND, check_rc=True)
    tables_before = parse_per_table_state(stdout)
    initref_state = filter_and_format_state(stdout)

    if state == 'saved':
        changed = write_state(b_path, initref_state, changed)
        module.exit_json(
            changed=changed,
            cmd=cmd,
            tables=tables_before,
            initial_state=initial_state,
            saved=initref_state)

    #
    # All remaining code is for state=restored
    #

    MAINCOMMAND = list(COMMANDARGS)
    MAINCOMMAND.insert(0, bin_iptables_restore)

    if wait is not None:
        MAINCOMMAND.extend(['--wait', '%s' % wait])

    if _back is not None:
        b_back = to_bytes(_back, errors='surrogate_or_strict')
        dummy = write_state(b_back, initref_state, changed)
        BACKCOMMAND = list(MAINCOMMAND)
        BACKCOMMAND.append(_back)

    if noflush:
        MAINCOMMAND.append('--noflush')

    MAINCOMMAND.append(path)
    cmd = ' '.join(MAINCOMMAND)

    TESTCOMMAND = list(MAINCOMMAND)
    TESTCOMMAND.insert(1, '--test')
    error_msg = "Source %s is not suitable for input to %s" % (path, os.path.basename(bin_iptables_restore))

    # Due to a bug in iptables-nft-restore --test, we have to validate tables
    # one by one (https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=960003).
    for t in tables_before:
        testcommand = list(TESTCOMMAND)
        testcommand.extend(['--table', t])
        (rc, stdout, stderr) = module.run_command(testcommand)

        if 'Another app is currently holding the xtables lock' in stderr:
            error_msg = stderr

        if rc != 0:
            cmd = ' '.join(testcommand)
            module.fail_json(
                msg=error_msg,
                cmd=cmd,
                rc=rc,
                stdout=stdout,
                stderr=stderr,
                tables=tables_before,
                initial_state=initial_state,
                restored=state_to_restore,
                applied=False)

    if module.check_mode:
        tmpfd, tmpfile = tempfile.mkstemp()
        with os.fdopen(tmpfd, 'w') as f:
            f.write("{0}\n".format("\n".join(initial_state)))

        if filecmp.cmp(tmpfile, b_path):
            restored_state = initial_state
        else:
            restored_state = state_to_restore

    else:
        # Let time enough to the plugin to retrieve async status of the module
        # in case of bad option type/value and the like.
        if _back is not None:
            b_starter = to_bytes('%s.starter' % _back, errors='surrogate_or_strict')
            while True:
                if os.path.exists(b_starter):
                    os.remove(b_starter)
                    break
                time.sleep(0.01)

        (rc, stdout, stderr) = module.run_command(MAINCOMMAND)
        if 'Another app is currently holding the xtables lock' in stderr:
            module.fail_json(
                msg=stderr,
                cmd=cmd,
                rc=rc,
                stdout=stdout,
                stderr=stderr,
                tables=tables_before,
                initial_state=initial_state,
                restored=state_to_restore,
                applied=False)

        (rc, stdout, stderr) = module.run_command(SAVECOMMAND, check_rc=True)
        restored_state = filter_and_format_state(stdout)
    tables_after = parse_per_table_state('\n'.join(restored_state))
    if restored_state not in (initref_state, initial_state):
        for table_name, table_content in tables_after.items():
            if table_name not in tables_before:
                # Would initialize a table, which doesn't exist yet
                changed = True
                break
            if tables_before[table_name] != table_content:
                # Content of some table changes
                changed = True
                break

    if _back is None or module.check_mode:
        module.exit_json(
            changed=changed,
            cmd=cmd,
            tables=tables_before,
            initial_state=initial_state,
            restored=restored_state,
            applied=True)

    # The rollback implementation currently needs:
    # Here:
    # * test existence of the backup file, exit with success if it doesn't exist
    # * otherwise, restore iptables from this file and return failure
    # Action plugin:
    # * try to remove the backup file
    # * wait async task is finished and retrieve its final status
    # * modify it and return the result
    # Task:
    # * task attribute 'async' set to the same value (or lower) than ansible
    #   timeout
    # * task attribute 'poll' equals 0
    #
    for dummy in range(_timeout):
        if os.path.exists(b_back):
            time.sleep(1)
            continue
        module.exit_json(
            changed=changed,
            cmd=cmd,
            tables=tables_before,
            initial_state=initial_state,
            restored=restored_state,
            applied=True)

    # Here we are: for whatever reason, but probably due to the current ruleset,
    # the action plugin (i.e. on the controller) was unable to remove the backup
    # cookie, so we restore initial state from it.
    (rc, stdout, stderr) = module.run_command(BACKCOMMAND, check_rc=True)
    os.remove(b_back)

    (rc, stdout, stderr) = module.run_command(SAVECOMMAND, check_rc=True)
    tables_rollback = parse_per_table_state(stdout)

    msg = (
        "Failed to confirm state restored from %s after %ss. "
        "Firewall has been rolled back to its initial state." % (path, _timeout)
    )

    module.fail_json(
        changed=(tables_before != tables_rollback),
        msg=msg,
        cmd=cmd,
        tables=tables_before,
        initial_state=initial_state,
        restored=restored_state,
        applied=False)


if __name__ == '__main__':
    main()

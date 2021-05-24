#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020-2021, quidame <quidame@poivron.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: iptables_state
short_description: Save iptables state into a file or restore it from a file
version_added: '1.1.0'
author: quidame (@quidame)
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
    by setting task attributes I(poll) to C(0), and I(async) to a value less
    or equal to C(ANSIBLE_TIMEOUT). If I(async) is greater, the rollback will
    still happen if it shall happen, but you will experience a connection
    timeout instead of more relevant info returned by the module after its
    failure.
  - This module supports C(check_mode) and C(diff).
options:
  counters:
    description:
      - Save or restore the values of all packet and byte counters.
      - When C(true), the module is not idempotent.
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
      - By default, C(/proc/sys/kernel/modprobe) is inspected to determine the
        executable's path.
    type: path
  noflush:
    description:
      - For I(state=restored), ignored otherwise.
      - If C(false), restoring iptables rules from a file flushes (deletes)
        all previous contents of the respective table(s). If C(true), the
        previous rules are left untouched (but policies are updated anyway,
        for all built-in chains).
    type: bool
    default: false
  path:
    description:
      - The file the iptables state should be saved to.
      - The file the iptables state should be restored from.
    type: path
    required: yes
  state:
    description:
      - Whether the firewall state should be saved (into a file) or restored
        (from a file).
    type: str
    choices: [ saved, restored ]
    required: yes
  table:
    description:
      - When I(state=restored), restore only the named table even if the input
        file contains other tables. Fail if the named table is not declared in
        the file.
      - When I(state=saved), restrict output to the specified table. If not
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
  check_mode: yes
  changed_when: false
  register: iptables_state

- name: show current state of the firewall
  ansible.builtin.debug:
    var: iptables_state.initial_state
'''

RETURN = r'''
applied:
  description: Whether or not the wanted state has been successfully restored. Always C(false) when C(check_mode=true).
  type: bool
  returned: when I(state=restored)
  sample: true
rollback_succeeded:
  description: Whether or not iptables state has been successfully rolled back to its initial state.
  type: bool
  returned: when failed and I(state=restored)
  sample: true
final_rules:
  description: Datastructure describing the actual state of the firewall when module exits.
  type: dict
  returned: when I(state=restored)
  contains:
    table:
      description: A table name among C(filter), C(nat), C(mangle), C(raw) and C(security).
      type: dict
      contains:
        CHAIN:
          description: A chain name within the table.
          type: dict
          contains:
            policy:
              description: The default policy to apply to packets not matching any rule in the chain.
              type: str
              sample: "ACCEPT"
            rules:
              description: List of the ordered rules packets are checked against.
              type: list
              elements: str
  sample:
    filter:
      FORWARD:
        policy: "DROP"
        rules: []
      INPUT:
        policy: "ACCEPT"
        rules: []
      OUTPUT:
        policy": "ACCEPT"
        rules": []
final_state:
  description: The actual state of the firewall when module exits.
  type: list
  elements: str
  returned: when I(state=restored)
  sample:
    - "# Generated by xtables-save v1.8.2"
    - "*filter"
    - ":INPUT ACCEPT [0:0]"
    - ":FORWARD DROP [0:0]"
    - ":OUTPUT ACCEPT [0:0]"
    - "COMMIT"
    - "# Completed"
initial_rules:
  description: Datastructure describing the actual state of the firewall when module starts.
  type: complex
  returned: always
  contains:
    table:
      description: A table name among C(filter), C(nat), C(mangle), C(raw) and C(security).
      type: dict
      contains:
        CHAIN:
          description: A chain name within the table.
          type: dict
          contains:
            policy:
              description: The default policy to apply to packets not matching any rule in the chain.
              type: str
              sample: "ACCEPT"
            rules:
              description: List of the ordered rules packets are checked against.
              type: list
              elements: str
  sample:
    filter:
      FORWARD:
        policy: "ACCEPT"
        rules: []
      INPUT:
        policy: "ACCEPT"
        rules": []
      OUTPUT:
        policy: "ACCEPT"
        rules: []
initial_state:
  description: The actual state of the firewall when module starts.
  type: list
  elements: str
  returned: always
  sample:
    - "# Generated by xtables-save v1.8.2"
    - "*filter"
    - ":INPUT ACCEPT [0:0]"
    - ":FORWARD ACCEPT [0:0]"
    - ":OUTPUT ACCEPT [0:0]"
    - "COMMIT"
    - "# Completed"
restored:
  description: The state the module restored, whenever it is finally applied or not.
  type: list
  elements: str
  returned: when I(state=restored)
  sample:
    - "# Generated by xtables-save v1.8.2"
    - "*filter"
    - ":INPUT DROP [0:0]"
    - ":FORWARD DROP [0:0]"
    - ":OUTPUT ACCEPT [0:0]"
    - "-A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT"
    - "-A INPUT -m conntrack --ctstate INVALID -j DROP"
    - "-A INPUT -i lo -j ACCEPT"
    - "-A INPUT -p icmp -j ACCEPT"
    - "-A INPUT -p tcp -m tcp --dport 22 -j ACCEPT"
    - "COMMIT"
    - "# Completed"
saved:
  description: The iptables state the module saved.
  type: list
  elements: str
  returned: when I(state=saved)
  sample:
    - "# Generated by xtables-save v1.8.2"
    - "*filter"
    - ":INPUT ACCEPT [0:0]"
    - ":FORWARD DROP [0:0]"
    - ":OUTPUT ACCEPT [0:0]"
    - "COMMIT"
    - "# Completed"
tables:
  description: The tables to which the module is applied.
  type: list
  elements: str
  returned: always
  sample:
    - filter
    - nat
'''


import re
import os
import time
import tempfile
import filecmp

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native


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
    """Read a file and return its content as a list."""
    with open(b_path, 'r') as f:
        return f.read().splitlines()


def flat_to_structured_ruleset(ruleset):
    """Convert a flat iptables ruleset (list or string) into a datastructure.
       Tables order, or policies order within a table may slighly vary in
       iptables-save outputs, from one invocation or alternative to the other.
       See RETURN.
    """
    table = None
    tables = dict()
    if isinstance(ruleset, list):
        stream = '\n'.join(ruleset)
        lines = ruleset
    elif isinstance(ruleset, str):
        stream = ruleset
        lines = ruleset.splitlines()
    else:
        msg = "module error: invalid data type (%s), 'list' or 'str' is required"
        module.fail_json(msg=msg % type(ruleset).__name__)

    for line in lines:
        line = line.strip()

        if line.startswith('#') or not line:
            continue
        if line == 'COMMIT':
            if not table:
                module.fail_json(msg="module error: no table to commit: %s" % stream)
            table = None
            continue
        if line.startswith('*'):
            if table:
                module.fail_json(msg="module error: uncommitted table (%s): %s" % (table, stream))
            table = line.split('*')[1]
            if table not in TABLES:
                module.fail_json(msg="module error: table (%s) must be one of %s: %s" % (table, ', '.join(TABLES), stream))
            tables[table] = dict()
            continue
        if line.startswith(':'):
            chain = line.split()[0].split(':')[1]
            policy = line.split()[1]
            if not tables[table].get(chain, None):
                tables[table][chain] = dict(rules=list())
            tables[table][chain]['policy'] = policy
            continue
        if line.startswith('['):
            line = ' '.join(line.split()[1:])
        if line.split()[0] not in ('-A', '-I'):
            module.fail_json(msg='module error: invalid rule found: %s' % line)

        chain = line.split()[1]
        if not tables[table].get(chain, None):
            tables[table][chain] = dict(rules=list())
        tables[table][chain]['rules'] += [line]

    return tables


def structured_to_flat_ruleset(ruleset, header, string=False):
    """Rebuild a flat ruleset from a datastructure to generate a fancy diff
       when state=restored.
    """
    if not isinstance(ruleset, dict):
        msg = "module error: invalid data type (%s), 'dict' is required"
        module.fail_json(msg=msg % type(ruleset).__name__)

    lines = list()
    tables = [t for t in TABLES if t in ruleset.keys()]
    for table in tables:
        lines += [header, '*%s' % table]
        for chain in ruleset[table]:
            lines += [':%s %s [0:0]' % (chain, ruleset[table][chain]['policy'])]
        for chain in ruleset[table]:
            lines += ruleset[table][chain]['rules']
        lines += ['COMMIT', '# Completed']

    ruleset = lines
    if string:
        ruleset = '\n'.join(lines) + '\n'

    return ruleset


def extract_table(ruleset, table):
    """Extract a single table from a ruleset (list) and return it."""
    keep = list()
    header = ruleset[0] if ruleset[0].startswith('#') else '# Generated by Ansible'
    for line in ruleset:
        if line == '*%s' % table:
            keep += [header, '*%s' % table]
            continue
        if not keep:
            continue
        if line == 'COMMIT':
            keep += ['COMMIT', '# Completed']
            break
        keep += [line]
    return keep


def save_state(b_path, lines, changed, diff):
    """Write given contents to the given path, and return changed status."""
    path = to_native(b_path, errors='surrogate_or_strict')

    # module.atomic_move can replace /dev/null by a regular file. We can't.
    if path == os.devnull:
        return changed

    diff_before = ''
    diff_after = '\n'.join(lines) + '\n'

    # Populate a temporary file
    tmpfd, tmpfile = tempfile.mkstemp()
    with os.fdopen(tmpfd, 'w') as f:
        for line in lines:
            f.write('%s\n' % line)

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
    else:
        with open(b_path, 'r') as f:
            diff_before = f.read()
        if not filecmp.cmp(tmpfile, b_path):
            changed = True

    diff += [dict(before=diff_before, before_header=b_path,
                  after=diff_after, after_header=tmpfile)]

    # Do it
    if changed and not module.check_mode:
        try:
            module.atomic_move(tmpfile, b_path)
        except IOError as err:
            module.fail_json(
                msg='Error saving state into %s: %s' % (path, to_native(err)),
                initial_state=lines)
    else:
        os.remove(tmpfile)

    return changed


def initialize_from_null_state(initializer, initcommand, fallbackcmd, table=None):
    """This ensures iptables-state output is suitable for iptables-restore to
       roll back to it, i.e. iptables-save output is not empty. This also works
       for the iptables-nft-save alternative.
    """
    if table is None:
        table = 'filter'

    commandline = list(initializer)
    commandline += ['-t', table]
    dummy = module.run_command(commandline, check_rc=True)
    (rc, out, err) = module.run_command(initcommand, check_rc=True)
    if not out:
        # For iptables-nft >= 1.8.7, use iptables-save output as direct input
        # for iptables-restore:
        commandline = list(initcommand)
        commandline += ['-t', table]
        initialized = module.run_command(commandline, check_rc=True)[1]
        dummy = module.run_command(fallbackcmd, data=initialized, check_rc=True)
        (rc, out, err) = module.run_command(initcommand, check_rc=True)
    return rc, out, err


def filter_and_format_state(string):
    """Remove timestamps to ensure idempotency between runs. Also remove
       counters by default. Return the result as a list.
    """
    string = re.sub(r'((^|\n)# (Generated|Completed)[^\n]*) on [^\n]*', r'\1', string)
    if not module.params['counters']:
        string = re.sub(r'\[[0-9]+:[0-9]+\]', r'[0:0]', string)
    lines = [line for line in string.splitlines() if line]
    return lines


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

    diff = []

    bin_iptables = module.get_bin_path(IPTABLES[ip_version], True)
    bin_iptables_save = module.get_bin_path(SAVE[ip_version], True)
    bin_iptables_restore = module.get_bin_path(RESTORE[ip_version], True)

    os.umask(0o077)
    changed = False
    COMMANDARGS = []
    INITCOMMAND = [bin_iptables_save]
    INITIALIZER = [bin_iptables, '-L', '-n']
    TESTCOMMAND = [bin_iptables_restore, '--test']

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
        from_state = read_state(b_path)
        state_to_restore = from_state if table is None else extract_table(from_state, table)
        rules_to_restore = flat_to_structured_ruleset(state_to_restore)
    else:
        cmd = ' '.join(SAVECOMMAND)

    (rc, stdout, stderr) = module.run_command(INITCOMMAND, check_rc=True)

    # The issue comes when wanting to restore state from empty iptable-save's
    # output... what happens when, say:
    # - no table is specified, and iptables-save's output is only nat table;
    # - we give filter's ruleset to iptables-restore, that locks ourselve out
    #   of the host;
    # then trying to roll iptables state back to the previous (working) setup
    # doesn't override current filter table because no filter table is stored
    # in the backup ! So we have to ensure tables to be restored have a backup
    # in case of rollback.
    FALLBACKCMD = [bin_iptables_restore]
    if table is None:
        if state == 'restored':
            for t in TABLES:
                if '*%s' % t in state_to_restore:
                    if len(stdout) == 0 or '*%s' % t not in stdout.splitlines():
                        (rc, stdout, stderr) = initialize_from_null_state(INITIALIZER, INITCOMMAND, FALLBACKCMD, t)
        elif len(stdout) == 0:
            (rc, stdout, stderr) = initialize_from_null_state(INITIALIZER, INITCOMMAND, FALLBACKCMD)

    elif state == 'restored' and '*%s' % table not in state_to_restore:
        module.fail_json(msg="Table %s to restore not defined in %s" % (table, path))

    elif len(stdout) == 0 or '*%s' % table not in stdout.splitlines():
        (rc, stdout, stderr) = initialize_from_null_state(INITIALIZER, INITCOMMAND, FALLBACKCMD, table)

    # initial_state is the state of the firewall when the module started, plus
    # the table(s) required by the user, if missing at first INITCOMMAND call.
    if rc or stderr or not stdout:
        module.fail_json(msg="Unable to initialize firewall from NULL state")
    initial_state = filter_and_format_state(stdout)
    initial_rules = flat_to_structured_ruleset(stdout)
    header = initial_state[0]

    # initref_state is a subset of initial_state (only the table(s) we have
    # interest for). It is suitable as input for iptables-restore, but not
    # reliable for comparisons between states (order of tables or policies may
    # vary from one invocation or alternative of iptables-save to the other).
    (rc, stdout, stderr) = module.run_command(SAVECOMMAND, check_rc=True)
    initref_state = filter_and_format_state(stdout)
    initref_rules = flat_to_structured_ruleset(stdout)

    if state == 'saved':
        changed = save_state(b_path, initref_state, changed, diff)
        result = dict(changed=changed, cmd=cmd, saved=initref_state,
                      initial_rules=initial_rules, initial_state=initial_state,
                      tables=initref_rules.keys())
        if module._diff:
            result['diff'] = diff
        module.exit_json(**result)

    #
    # All remaining code is for state=restored
    #
    diff_rules = dict(**initial_rules)
    diff_before = structured_to_flat_ruleset(initial_rules, header, True)

    MAINCOMMAND = list(COMMANDARGS)
    MAINCOMMAND.insert(0, bin_iptables_restore)

    if wait is not None:
        MAINCOMMAND.extend(['--wait', '%s' % wait])

    if _back is not None:
        b_back = to_bytes(_back, errors='surrogate_or_strict')
        dummy = save_state(b_back, initref_state, changed, diff)
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
    for t in rules_to_restore:
        testcommand = list(TESTCOMMAND)
        testcommand.extend(['--table', t])
        (rc, stdout, stderr) = module.run_command(testcommand)

        if 'Another app is currently holding the xtables lock' in stderr:
            error_msg = stderr

        if rc != 0:
            cmd = ' '.join(testcommand)
            dummy, out, dummy = module.run_command(INITCOMMAND, check_rc=True)
            final_state = filter_and_format_state(out)
            final_rules = flat_to_structured_ruleset(out)
            module.fail_json(msg=error_msg, cmd=cmd, rc=rc, stdout=stdout, stderr=stderr,
                             initial_rules=initial_rules, initial_state=initial_state,
                             final_rules=final_rules, final_state=final_state,
                             tables=rules_to_restore.keys(), applied=False)

        # For diff accuracy in check_mode: build the expected diff by replacing
        # table(s) in the initial rules.
        if module.check_mode:
            diff_rules[t] = rules_to_restore[t]

    if not module.check_mode:
        # Let time enough to the plugin to retrieve async status of the module
        # in case of bad option type/value and the like.
        if _back is not None:
            b_starter = to_bytes('%s.starter' % _back, errors='surrogate_or_strict')
            while True:
                if os.path.exists(b_starter):
                    os.remove(b_starter)
                    break
                time.sleep(0.01)

        # Do it
        (rc, stdout, stderr) = module.run_command(MAINCOMMAND)
        if 'Another app is currently holding the xtables lock' in stderr:
            dummy, out, dummy = module.run_command(INITCOMMAND, check_rc=True)
            final_state = filter_and_format_state(out)
            final_rules = flat_to_structured_ruleset(out)
            module.fail_json(msg=stderr, cmd=cmd, rc=rc, stdout=stdout, stderr=stderr,
                             initial_rules=initial_rules, initial_state=initial_state,
                             final_rules=final_rules, final_state=final_state,
                             tables=rules_to_restore.keys(), applied=False)

    dummy, out, dummy = module.run_command(INITCOMMAND, check_rc=True)
    final_state = filter_and_format_state(out)
    final_rules = flat_to_structured_ruleset(out)

    if module.check_mode:
        diff_after = structured_to_flat_ruleset(diff_rules, header, True)
        restored_state = state_to_restore
        if restored_state[0].startswith('#'):
            restored_state[0] = header
        else:
            restored_state.insert(0, header)
        if restored_state[-1].startswith('#'):
            restored_state[-1] = '# Completed'
        else:
            restored_state.append('# Completed')
    else:
        diff_after = structured_to_flat_ruleset(final_rules, header, True)
        dummy, out, dummy = module.run_command(SAVECOMMAND, check_rc=True)
        restored_state = filter_and_format_state(out)
    if diff_after != diff_before:
        changed = True

    diff += [dict(before=diff_before, before_header='initial iptables state',
                  after=diff_after, after_header='final iptables state')]

    result = dict(changed=changed, cmd=cmd, restored=restored_state,
                  initial_rules=initial_rules, initial_state=initial_state,
                  final_rules=final_rules, final_state=final_state,
                  tables=rules_to_restore.keys(), applied=(not module.check_mode))

    if module._diff:
        result['diff'] = diff

    if _back is None or module.check_mode:
        module.exit_json(**result)

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
        module.exit_json(**result)

    # Here we are: for whatever reason, but probably due to the current ruleset,
    # the action plugin (i.e. on the controller) was unable to remove the backup
    # cookie, so we restore initial state from it.
    dummy = module.run_command(BACKCOMMAND, check_rc=True)
    os.remove(b_back)

    dummy, stdout, dummy = module.run_command(INITCOMMAND, check_rc=True)
    result['final_state'] = filter_and_format_state(stdout)
    result['final_rules'] = flat_to_structured_ruleset(stdout)
    result['rollback_succeeded'] = (result['final_rules'] == initial_rules)
    result['applied'] = False
    result['msg'] = ("Failed to confirm state restored from %s after %ss. "
                     "Firewall has been rolled back to its initial state." % (path, _timeout))

    module.fail_json(**result)


if __name__ == '__main__':
    main()

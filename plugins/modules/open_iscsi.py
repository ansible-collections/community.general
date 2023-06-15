#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Serge van Ginderachter <serge@vanginderachter.be>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: open_iscsi
author:
    - Serge van Ginderachter (@srvg)
short_description: Manage iSCSI targets with Open-iSCSI
description:
    - Discover targets on given portal, (dis)connect targets, mark targets to
      manually or auto start, return device nodes of connected targets.
requirements:
    - open_iscsi library and tools (iscsiadm)
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    portal:
        description:
        - The domain name or IP address of the iSCSI target.
        type: str
        aliases: [ ip ]
    port:
        description:
        - The port on which the iSCSI target process listens.
        type: str
        default: '3260'
    target:
        description:
        - The iSCSI target name.
        type: str
        aliases: [ name, targetname ]
    login:
        description:
        - Whether the target node should be connected.
        type: bool
        aliases: [ state ]
    node_auth:
        description:
        - The value for C(node.session.auth.authmethod).
        type: str
        default: CHAP
    node_user:
        description:
        - The value for C(node.session.auth.username).
        type: str
    node_pass:
        description:
        - The value for C(node.session.auth.password).
        type: str
    node_user_in:
        description:
        - The value for C(node.session.auth.username_in).
        type: str
        version_added: 3.8.0
    node_pass_in:
        description:
        - The value for C(node.session.auth.password_in).
        type: str
        version_added: 3.8.0
    auto_node_startup:
        description:
        - Whether the target node should be automatically connected at startup.
        type: bool
        aliases: [ automatic ]
    auto_portal_startup:
        description:
        - Whether the target node portal should be automatically connected at startup.
        type: bool
        version_added: 3.2.0
    discover:
        description:
        - Whether the list of target nodes on the portal should be
          (re)discovered and added to the persistent iSCSI database.
        - Keep in mind that C(iscsiadm) discovery resets configuration, like C(node.startup)
          to manual, hence combined with O(auto_node_startup=true) will always return
          a changed state.
        type: bool
        default: false
    show_nodes:
        description:
        - Whether the list of nodes in the persistent iSCSI database should be returned by the module.
        type: bool
        default: false
    rescan:
        description:
        - Rescan an established session for discovering new targets.
        - When O(target) is omitted, will rescan all sessions.
        type: bool
        default: false
        version_added: 4.1.0

'''

EXAMPLES = r'''
- name: Perform a discovery on sun.com and show available target nodes
  community.general.open_iscsi:
    show_nodes: true
    discover: true
    portal: sun.com

- name: Perform a discovery on 10.1.2.3 and show available target nodes
  community.general.open_iscsi:
    show_nodes: true
    discover: true
    ip: 10.1.2.3

# NOTE: Only works if exactly one target is exported to the initiator
- name: Discover targets on portal and login to the one available
  community.general.open_iscsi:
    portal: '{{ iscsi_target }}'
    login: true
    discover: true

- name: Connect to the named target, after updating the local persistent database (cache)
  community.general.open_iscsi:
    login: true
    target: iqn.1986-03.com.sun:02:f8c1f9e0-c3ec-ec84-c9c9-8bfb0cd5de3d

- name: Disconnect from the cached named target
  community.general.open_iscsi:
    login: false
    target: iqn.1986-03.com.sun:02:f8c1f9e0-c3ec-ec84-c9c9-8bfb0cd5de3d

- name: Override and disable automatic portal login on specific portal
  community.general.open_iscsi:
    login: false
    portal: 10.1.1.250
    auto_portal_startup: false
    target: iqn.1986-03.com.sun:02:f8c1f9e0-c3ec-ec84-c9c9-8bfb0cd5de3d

- name: Rescan one or all established sessions to discover new targets (omit target for all sessions)
  community.general.open_iscsi:
    rescan: true
    target: iqn.1986-03.com.sun:02:f8c1f9e0-c3ec-ec84-c9c9-8bfb0cd5de3d
'''

import glob
import os
import re
import socket
import time

from ansible.module_utils.basic import AnsibleModule

ISCSIADM = 'iscsiadm'
iscsiadm_cmd = None


def compare_nodelists(l1, l2):
    l1.sort()
    l2.sort()
    return l1 == l2


def iscsi_get_cached_nodes(module, portal=None):
    cmd = [iscsiadm_cmd, '--mode', 'node']
    rc, out, err = module.run_command(cmd)

    nodes = []
    if rc == 0:
        lines = out.splitlines()
        for line in lines:
            # line format is "ip:port,target_portal_group_tag targetname"
            parts = line.split()
            if len(parts) > 2:
                module.fail_json(msg='error parsing output', cmd=cmd)
            target = parts[1]
            parts = parts[0].split(':')
            target_portal = parts[0]

            if portal is None or portal == target_portal:
                nodes.append(target)

    # older versions of scsiadm don't have nice return codes
    # for newer versions see iscsiadm(8); also usr/iscsiadm.c for details
    # err can contain [N|n]o records...
    elif rc == 21 or (rc == 255 and "o records found" in err):
        pass
    else:
        module.fail_json(cmd=cmd, rc=rc, msg=err)

    return nodes


def iscsi_discover(module, portal, port):
    cmd = [iscsiadm_cmd, '--mode', 'discovery', '--type', 'sendtargets', '--portal', '%s:%s' % (portal, port)]
    module.run_command(cmd, check_rc=True)


def iscsi_rescan(module, target=None):
    if target is None:
        cmd = [iscsiadm_cmd, '--mode', 'session', '--rescan']
    else:
        cmd = [iscsiadm_cmd, '--mode', 'node', '--rescan', '-T', target]
    rc, out, err = module.run_command(cmd)
    return out


def target_loggedon(module, target, portal=None, port=None):
    cmd = [iscsiadm_cmd, '--mode', 'session']
    rc, out, err = module.run_command(cmd)

    if portal is None:
        portal = ""
    if port is None:
        port = ""

    if rc == 0:
        search_re = "%s:%s.*%s" % (re.escape(portal), port, re.escape(target))
        return re.search(search_re, out) is not None
    elif rc == 21:
        return False
    else:
        module.fail_json(cmd=cmd, rc=rc, msg=err)


def target_login(module, target, portal=None, port=None):
    node_auth = module.params['node_auth']
    node_user = module.params['node_user']
    node_pass = module.params['node_pass']
    node_user_in = module.params['node_user_in']
    node_pass_in = module.params['node_pass_in']

    if node_user:
        params = [('node.session.auth.authmethod', node_auth),
                  ('node.session.auth.username', node_user),
                  ('node.session.auth.password', node_pass)]
        for (name, value) in params:
            cmd = [iscsiadm_cmd, '--mode', 'node', '--targetname', target, '--op=update', '--name', name, '--value', value]
            module.run_command(cmd, check_rc=True)

    if node_user_in:
        params = [('node.session.auth.username_in', node_user_in),
                  ('node.session.auth.password_in', node_pass_in)]
        for (name, value) in params:
            cmd = '%s --mode node --targetname %s --op=update --name %s --value %s' % (iscsiadm_cmd, target, name, value)
            module.run_command(cmd, check_rc=True)

    cmd = [iscsiadm_cmd, '--mode', 'node', '--targetname', target, '--login']
    if portal is not None and port is not None:
        cmd.append('--portal')
        cmd.append('%s:%s' % (portal, port))

    module.run_command(cmd, check_rc=True)


def target_logout(module, target):
    cmd = [iscsiadm_cmd, '--mode', 'node', '--targetname', target, '--logout']
    module.run_command(cmd, check_rc=True)


def target_device_node(target):
    # if anyone know a better way to find out which devicenodes get created for
    # a given target...

    devices = glob.glob('/dev/disk/by-path/*%s*' % target)
    devdisks = []
    for dev in devices:
        # exclude partitions
        if "-part" not in dev:
            devdisk = os.path.realpath(dev)
            # only add once (multi-path?)
            if devdisk not in devdisks:
                devdisks.append(devdisk)
    return devdisks


def target_isauto(module, target, portal=None, port=None):
    cmd = [iscsiadm_cmd, '--mode', 'node', '--targetname', target]

    if portal is not None and port is not None:
        cmd.append('--portal')
        cmd.append('%s:%s' % (portal, port))

    dummy, out, dummy = module.run_command(cmd, check_rc=True)

    lines = out.splitlines()
    for line in lines:
        if 'node.startup' in line:
            return 'automatic' in line
    return False


def target_setauto(module, target, portal=None, port=None):
    cmd = [iscsiadm_cmd, '--mode', 'node', '--targetname', target, '--op=update', '--name', 'node.startup', '--value', 'automatic']

    if portal is not None and port is not None:
        cmd.append('--portal')
        cmd.append('%s:%s' % (portal, port))

    module.run_command(cmd, check_rc=True)


def target_setmanual(module, target, portal=None, port=None):
    cmd = [iscsiadm_cmd, '--mode', 'node', '--targetname', target, '--op=update', '--name', 'node.startup', '--value', 'manual']

    if portal is not None and port is not None:
        cmd.append('--portal')
        cmd.append('%s:%s' % (portal, port))

    module.run_command(cmd, check_rc=True)


def main():
    # load ansible module object
    module = AnsibleModule(
        argument_spec=dict(

            # target
            portal=dict(type='str', aliases=['ip']),
            port=dict(type='str', default='3260'),
            target=dict(type='str', aliases=['name', 'targetname']),
            node_auth=dict(type='str', default='CHAP'),
            node_user=dict(type='str'),
            node_pass=dict(type='str', no_log=True),
            node_user_in=dict(type='str'),
            node_pass_in=dict(type='str', no_log=True),

            # actions
            login=dict(type='bool', aliases=['state']),
            auto_node_startup=dict(type='bool', aliases=['automatic']),
            auto_portal_startup=dict(type='bool'),
            discover=dict(type='bool', default=False),
            show_nodes=dict(type='bool', default=False),
            rescan=dict(type='bool', default=False),
        ),

        required_together=[['node_user', 'node_pass'], ['node_user_in', 'node_pass_in']],
        required_if=[('discover', True, ['portal'])],
        supports_check_mode=True,
    )

    global iscsiadm_cmd
    iscsiadm_cmd = module.get_bin_path('iscsiadm', required=True)

    # parameters
    portal = module.params['portal']
    if portal:
        try:
            portal = socket.getaddrinfo(portal, None)[0][4][0]
        except socket.gaierror:
            module.fail_json(msg="Portal address is incorrect")

    target = module.params['target']
    port = module.params['port']
    login = module.params['login']
    automatic = module.params['auto_node_startup']
    automatic_portal = module.params['auto_portal_startup']
    discover = module.params['discover']
    show_nodes = module.params['show_nodes']
    rescan = module.params['rescan']

    check = module.check_mode

    cached = iscsi_get_cached_nodes(module, portal)

    # return json dict
    result = {'changed': False}

    if discover:
        if check:
            nodes = cached
        else:
            iscsi_discover(module, portal, port)
            nodes = iscsi_get_cached_nodes(module, portal)
        if not compare_nodelists(cached, nodes):
            result['changed'] |= True
            result['cache_updated'] = True
    else:
        nodes = cached

    if login is not None or automatic is not None:
        if target is None:
            if len(nodes) > 1:
                module.fail_json(msg="Need to specify a target")
            else:
                target = nodes[0]
        else:
            # check given target is in cache
            check_target = False
            for node in nodes:
                if node == target:
                    check_target = True
                    break
            if not check_target:
                module.fail_json(msg="Specified target not found")

    if show_nodes:
        result['nodes'] = nodes

    if login is not None:
        loggedon = target_loggedon(module, target, portal, port)
        if (login and loggedon) or (not login and not loggedon):
            result['changed'] |= False
            if login:
                result['devicenodes'] = target_device_node(target)
        elif not check:
            if login:
                target_login(module, target, portal, port)
                # give udev some time
                time.sleep(1)
                result['devicenodes'] = target_device_node(target)
            else:
                target_logout(module, target)
            result['changed'] |= True
            result['connection_changed'] = True
        else:
            result['changed'] |= True
            result['connection_changed'] = True

    if automatic is not None:
        isauto = target_isauto(module, target)
        if (automatic and isauto) or (not automatic and not isauto):
            result['changed'] |= False
            result['automatic_changed'] = False
        elif not check:
            if automatic:
                target_setauto(module, target)
            else:
                target_setmanual(module, target)
            result['changed'] |= True
            result['automatic_changed'] = True
        else:
            result['changed'] |= True
            result['automatic_changed'] = True

    if automatic_portal is not None:
        isauto = target_isauto(module, target, portal, port)
        if (automatic_portal and isauto) or (not automatic_portal and not isauto):
            result['changed'] |= False
            result['automatic_portal_changed'] = False
        elif not check:
            if automatic_portal:
                target_setauto(module, target, portal, port)
            else:
                target_setmanual(module, target, portal, port)
            result['changed'] |= True
            result['automatic_portal_changed'] = True
        else:
            result['changed'] |= True
            result['automatic_portal_changed'] = True

    if rescan is not False:
        result['changed'] = True
        result['sessions'] = iscsi_rescan(module, target)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

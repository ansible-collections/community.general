#!/usr/bin/env python
"""
Multipass external inventory script.
Automatically finds the IP of canonical/multipass vm(s),
and returns it under the host group 'multipass'
"""
# Copyright (C) 2020  Florent Madiot <scodeman@scode.io>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from subprocess import Popen, PIPE

import json


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


MULTIPASS = "multipass"


def get_hosts(host=None):

    returned = {}

    try:
        if host:
            p = Popen([MULTIPASS, 'info', '--format', 'json', host], stdout=PIPE, stderr=PIPE)
        else:
            returned = {'all': set(), '_metadata': {}}
            p = Popen([MULTIPASS, 'info', '--format', 'json', '--all'], stdout=PIPE, stderr=PIPE)
    except Exception:
        sys.exit(1)

    hostvars = {}
    prevkey = pref_k = ''

    data = json.loads(p.communicate()[0])
    returned['multipass'] = set()

    for hostname, hostinfo in data.get('info',{}).items():
        hostvars[hostname] = {}
        hostvars[hostname]['ansible_ssh_host'] = hostinfo['ipv4'][0].strip()
        returned['multipass'].add(hostname)
        if not host:
          returned['all'].add(hostname)

    if not host:
        returned['_metadata']['hostvars'] = hostvars
    else:
        returned = hostvars[host]
    return returned


if __name__ == '__main__':

    inventory = {}
    hostname = None

    if len(sys.argv) > 1:
        if sys.argv[1] == "--host":
            hostname = sys.argv[2]

    if hostname:
        inventory = get_hosts(hostname)
    else:
        inventory = get_hosts()

    sys.stdout.write(json.dumps(inventory, indent=2, cls=SetEncoder))

#!/usr/bin/env python

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


VBOX = "VBoxManage"


def get_hosts(host=None):

    returned = {}
    try:
        if host:
            p = Popen([VBOX, 'showvminfo', host], stdout=PIPE)
        else:
            returned = {'all': set(), '_metadata': {}}
            p = Popen([VBOX, 'list', '-l', 'vms'], stdout=PIPE)
    except Exception:
        sys.exit(1)

    hostvars = {}
    prevkey = pref_k = ''

    for line in p.stdout.readlines():

        try:
            k, v = line.split(':', 1)
        except Exception:
            continue

        if k == '':
            continue

        v = v.strip()
        if k.startswith('Name'):
            if v not in hostvars:
                curname = v
                hostvars[curname] = {}
                try:  # try to get network info
                    x = Popen([VBOX, 'guestproperty', 'get', curname, "/VirtualBox/GuestInfo/Net/0/V4/IP"], stdout=PIPE)
                    ipinfo = x.stdout.read()
                    if 'Value' in ipinfo:
                        a, ip = ipinfo.split(':', 1)
                        hostvars[curname]['ansible_ssh_host'] = ip.strip()
                except Exception:
                    pass

            continue

        if not host:
            if k == 'Groups':
                for group in v.split('/'):
                    if group:
                        if group not in returned:
                            returned[group] = set()
                        returned[group].add(curname)
                    returned['all'].add(curname)
                continue

        pref_k = 'vbox_' + k.strip().replace(' ', '_')
        if k.startswith(' '):
            if prevkey not in hostvars[curname]:
                hostvars[curname][prevkey] = {}
            hostvars[curname][prevkey][pref_k] = v
        else:
            if v != '':
                hostvars[curname][pref_k] = v

        prevkey = pref_k

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

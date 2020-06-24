#!/usr/bin/env python

# (c) 2015, Dagobert Michelsen <dam@baltic-online.de>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from subprocess import Popen, PIPE
import sys
import json

result = {}
result['all'] = {}

pipe = Popen(['zoneadm', 'list', '-ip'], stdout=PIPE, universal_newlines=True)
result['all']['hosts'] = []
for l in pipe.stdout.readlines():
    # 1:work:running:/zones/work:3126dc59-9a07-4829-cde9-a816e4c5040e:native:shared
    s = l.split(':')
    if s[1] != 'global':
        result['all']['hosts'].append(s[1])

result['all']['vars'] = {}
result['all']['vars']['ansible_connection'] = 'zone'

if len(sys.argv) == 2 and sys.argv[1] == '--list':
    print(json.dumps(result))
elif len(sys.argv) == 3 and sys.argv[1] == '--host':
    print(json.dumps({'ansible_connection': 'zone'}))
else:
    sys.stderr.write("Need an argument, either --list or --host <host>\n")

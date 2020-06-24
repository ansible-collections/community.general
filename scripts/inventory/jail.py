#!/usr/bin/env python

# (c) 2013, Michael Scherer <misc@zarb.org>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from subprocess import Popen, PIPE
import sys
import json

result = {}
result['all'] = {}

pipe = Popen(['jls', '-q', 'name'], stdout=PIPE, universal_newlines=True)
result['all']['hosts'] = [x[:-1] for x in pipe.stdout.readlines()]
result['all']['vars'] = {}
result['all']['vars']['ansible_connection'] = 'jail'

if len(sys.argv) == 2 and sys.argv[1] == '--list':
    print(json.dumps(result))
elif len(sys.argv) == 3 and sys.argv[1] == '--host':
    print(json.dumps({'ansible_connection': 'jail'}))
else:
    sys.stderr.write("Need an argument, either --list or --host <host>\n")

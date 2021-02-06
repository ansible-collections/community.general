#!/usr/bin/env python3

"""
Vagrant external inventory script. Automatically finds the IP of the booted vagrant vm(s), and
returns it under the host group 'vagrant' with the directory name as ansible hostname.

# Copyright (C) 2013  Mark Mandel <mark@compoundtheory.com>
#               2015  Igor Khomyakov <homyakov@gmail.com>
                2021  Christopher Hornberger github.com/horni23
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

#
# Thanks to the spacewalk.py inventory script for giving me the basic structure
# of this.
#

import sys
import os.path
import subprocess
import re
from paramiko import SSHConfig
from optparse import OptionParser
from collections import defaultdict
import json
import io

from ansible.module_utils._text import to_text
from ansible.module_utils.six.moves import StringIO


_group = 'vagrant'  # a default group
_ssh_to_ansible = [('user', 'ansible_user'),
                   ('hostname', 'ansible_host'),
                   ('identityfile', 'ansible_private_key_file'),
                   ('port', 'ansible_port')]

# Options
# ------------------------------

parser = OptionParser(usage="%prog [options] --list | --host <machine>")
parser.add_option('--list', default=False, dest="list", action="store_true",
                  help="Produce a JSON consumable grouping of Vagrant servers for Ansible")
parser.add_option('--host', default=None, dest="host",
                  help="Generate additional host specific details for given host for Ansible")
(options, args) = parser.parse_args()

#
# helper functions
#
# get all the ssh configs for all boxes in an array of dictionaries.
# list all the running boxes

output = to_text(subprocess.check_output(["vagrant", "global-status", "--prune"]), errors='surrogate_or_strict').split('\n')

boxes = []
names = []
mapping = {}

for line in output:
    matchname = re.search(r"(running.+?)([^\/]+$)",line)
    matcher   = re.search(r"^\s*([a-zA-Z0-9]+).*running",line)
    if matcher and matchname:
        boxes = str(matcher.group(1))
        boxname = str(matchname.group(2))
        boxname = boxname.strip()
        mapping[boxes] = boxname

def get_ssh_config():
    return dict((k, get_a_ssh_config(k)) for k in mapping)

# get the ssh config for a single box
def get_a_ssh_config(box_name):
    """Gives back a map of all the machine's ssh configurations"""

    output = to_text(subprocess.check_output(["vagrant", "ssh-config", box_name]), errors='surrogate_or_strict')
    config = SSHConfig()
    config.parse(StringIO(output))
    host_config = config.lookup("default")

    # man 5 ssh_config:
    # > It is possible to have multiple identity files ...
    # > all these identities will be tried in sequence.

    for id in host_config['identityfile']:
        if os.path.isfile(id):
            host_config['identityfile'] = id

    return dict((v, host_config[k]) for k, v in _ssh_to_ansible)

# List out servers that vagrant has running
# ------------------------------
if options.list:
    ssh_config   = get_ssh_config()
    list_names = []
    meta = defaultdict(dict)

    for host in ssh_config:
        pretty_name = mapping[host].strip()
        pretty_name = str(pretty_name)
        meta['hostvars'][pretty_name] = ssh_config[host]

    print(json.dumps({_group: list(mapping.values()), '_meta': meta}, indent=4))
    sys.exit(0)

# Get out the host details
# ------------------------------
elif options.host:
    host = list(mapping.keys())[list(mapping.values()).index(options.host)]
    host = host.strip("[]")
    host = host.strip("\'")
    print(json.dumps(get_a_ssh_config(host),indent=4))
    sys.exit(0)

# Print out help
# ------------------------------
else:
    parser.print_help()
    sys.exit(0)
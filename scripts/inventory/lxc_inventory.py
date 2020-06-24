#!/usr/bin/env python
#
# (c) 2015-16 Florian Haas, hastexo Professional Services GmbH
# <florian@hastexo.com>
# Based in part on:
# libvirt_lxc.py, (c) 2013, Michael Scherer <misc@zarb.org>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Ansible inventory script for LXC containers. Requires Python
bindings for LXC API.

In LXC, containers can be grouped by setting the lxc.group option,
which may be found more than once in a container's
configuration. So, we enumerate all containers, fetch their list
of groups, and then build the dictionary in the way Ansible expects
it.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import lxc
import json


def build_dict():
    """Returns a dictionary keyed to the defined LXC groups. All
    containers, including the ones not in any group, are included in the
    "all" group."""
    # Enumerate all containers, and list the groups they are in. Also,
    # implicitly add every container to the 'all' group.
    containers = dict([(c,
                        ['all'] +
                        (lxc.Container(c).get_config_item('lxc.group') or []))
                       for c in lxc.list_containers()])

    # Extract the groups, flatten the list, and remove duplicates
    groups = set(sum([g for g in containers.values()], []))

    # Create a dictionary for each group (including the 'all' group
    return dict([(g, {'hosts': [k for k, v in containers.items() if g in v],
                      'vars': {'ansible_connection': 'lxc'}}) for g in groups])


def main(argv):
    """Returns a JSON dictionary as expected by Ansible"""
    result = build_dict()
    if len(argv) == 2 and argv[1] == '--list':
        json.dump(result, sys.stdout)
    elif len(argv) == 3 and argv[1] == '--host':
        json.dump({'ansible_connection': 'lxc'}, sys.stdout)
    else:
        print("Need an argument, either --list or --host <host>", file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv)

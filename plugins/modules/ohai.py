#!/usr/bin/python

# Copyright (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: ohai
short_description: Returns inventory data from I(Ohai)
description:
  - Similar to the M(community.general.facter_facts) module, this runs the I(Ohai) discovery program (U(https://docs.chef.io/ohai.html))
    on the remote host and returns JSON inventory data. I(Ohai) data is a bit more verbose and nested than I(facter).
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options: {}
notes: []
requirements: ["ohai"]
author:
  - "Ansible Core Team"
  - "Michael DeHaan (@mpdehaan)"
"""

EXAMPLES = r"""
ansible webservers -m ohai --tree=/tmp/ohaidata
...
"""
import json

from ansible.module_utils.basic import AnsibleModule


def main():
    module = AnsibleModule(argument_spec=dict())
    cmd = ["/usr/bin/env", "ohai"]
    rc, out, err = module.run_command(cmd, check_rc=True)
    module.exit_json(**json.loads(out))


if __name__ == "__main__":
    main()

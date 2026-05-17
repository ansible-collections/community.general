#!/usr/bin/python

# Copyright (c) 2025, Francisco Pereira (@Francisco-Xiq)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: apache2_site
author:
  - Francisco Pereira (@Francisco-Xiq)
short_description: Enables/disables a site of the Apache2 webserver
description:
  - Enables or disables a specified site of the Apache2 webserver.
  - Uses C(a2ensite) and C(a2dissite) under the hood.
notes:
  - This module is only available on Debian/Ubuntu-based systems,
    as it depends on C(a2ensite) and C(a2dissite).
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    type: str
    description:
      - Name of the site to enable/disable as given to C(a2ensite)/C(a2dissite).
      - The name should not include the C(.conf) extension.
    required: true
  state:
    type: str
    description:
      - Desired state of the site.
    choices: [present, absent]
    required: true
"""

EXAMPLES = r"""
- name: Enable my_cool_site
  community.general.apache2_site:
    state: present
    name: my_cool_site

- name: Disable old site
  community.general.apache2_site:
    state: absent
    name: very_old_site
"""

RETURN = r"""
name:
  description: Name of the site.
  returned: success
  type: str
  sample: my_cool_site
"""

import os
from ansible.module_utils.basic import AnsibleModule


def site_is_enabled(name):
    return os.path.islink(f"/etc/apache2/sites-enabled/{name}.conf")


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            state=dict(type="str", required=True, choices=["present", "absent"]),
        ),
        supports_check_mode=True,
    )

    name = module.params["name"]
    state = module.params["state"]
    want_enabled = state == "present"
    is_enabled = site_is_enabled(name)

    changed = False

    if want_enabled and not is_enabled:
        changed = True
        if not module.check_mode:
            a2ensite = module.get_bin_path("a2ensite", required=True)
            rc, stdout, stderr = module.run_command([a2ensite, name])
            if rc != 0:
                module.fail_json(
                    msg=f"Failed to enable site {name}: {stderr}",
                    rc=rc, stdout=stdout, stderr=stderr
                )

    elif not want_enabled and is_enabled:
        changed = True
        if not module.check_mode:
            a2dissite = module.get_bin_path("a2dissite", required=True)
            rc, stdout, stderr = module.run_command([a2dissite, name])
            if rc != 0:
                module.fail_json(
                    msg=f"Failed to disable site {name}: {stderr}",
                    rc=rc, stdout=stdout, stderr=stderr
                )

    module.exit_json(changed=changed, name=name)


if __name__ == "__main__":
    main()

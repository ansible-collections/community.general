# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._authselect.authselect import (
    Authselect,
)


def main() -> None:
    module = AnsibleModule(
        argument_spec={
            "name": {
                "type": "str",
                "required": True,
            },
        },
    )

    try:
        Authselect().restore_profile_backup(module.params["name"])
    except Exception as exception:
        module.fail_json(msg=str(exception))

    module.exit_json(changed=True)


if __name__ == "__main__":
    main()

# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Luke Murphy @decentral1se
#
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

from ansible.module_utils.ansible_release import __version__ as ansible_version


def get_user_agent(module):
    """Retrieve a user-agent to send with LinodeClient requests."""
    return f"Ansible-{module}/{ansible_version}"

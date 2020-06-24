# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Luke Murphy @decentral1se
#
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


def get_user_agent(module):
    """Retrieve a user-agent to send with LinodeClient requests."""
    try:
        from ansible.module_utils.ansible_release import __version__ as ansible_version
    except ImportError:
        ansible_version = 'unknown'
    return 'Ansible-%s/%s' % (module, ansible_version)

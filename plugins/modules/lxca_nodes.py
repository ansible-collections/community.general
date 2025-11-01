#!/usr/bin/python
# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
#
from __future__ import annotations


DOCUMENTATION = r"""
author:
  - Naval Patel (@navalkp)
  - Prashant Bhosale (@prabhosa)
module: lxca_nodes
short_description: Custom module for lxca nodes inventory utility
description:
  - This module returns/displays a inventory details of nodes.
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none

options:
  uuid:
    description: UUID of device, this is string with length greater than 16.
    type: str

  command_options:
    description: Options to filter nodes information.
    default: nodes
    choices:
      - nodes
      - nodes_by_uuid
      - nodes_by_chassis_uuid
      - nodes_status_managed
      - nodes_status_unmanaged
    type: str

  chassis:
    description: UUID of chassis, this is string with length greater than 16.
    type: str

extends_documentation_fragment:
  - community.general.lxca_common
  - community.general.attributes
"""

EXAMPLES = r"""
# get all nodes info
- name: Get nodes data from LXCA
  community.general.lxca_nodes:
    login_user: USERID
    login_password: Password
    auth_url: "https://10.243.15.168"
    command_options: nodes

# get specific nodes info by uuid
- name: Get nodes data from LXCA
  community.general.lxca_nodes:
    login_user: USERID
    login_password: Password
    auth_url: "https://10.243.15.168"
    uuid: "3C737AA5E31640CE949B10C129A8B01F"
    command_options: nodes_by_uuid

# get specific nodes info by chassis uuid
- name: Get nodes data from LXCA
  community.general.lxca_nodes:
    login_user: USERID
    login_password: Password
    auth_url: "https://10.243.15.168"
    chassis: "3C737AA5E31640CE949B10C129A8B01F"
    command_options: nodes_by_chassis_uuid

# get managed nodes
- name: Get nodes data from LXCA
  community.general.lxca_nodes:
    login_user: USERID
    login_password: Password
    auth_url: "https://10.243.15.168"
    command_options: nodes_status_managed

# get unmanaged nodes
- name: Get nodes data from LXCA
  community.general.lxca_nodes:
    login_user: USERID
    login_password: Password
    auth_url: "https://10.243.15.168"
    command_options: nodes_status_unmanaged
"""

RETURN = r"""
result:
  description: Nodes detail from lxca.
  returned: always
  type: dict
  sample:
    nodeList:
      - machineType: '6241'
        model: 'AC1'
        type: 'Rack-TowerServer'
        uuid: '118D2C88C8FD11E4947B6EAE8B4BDCDF'
          # bunch of properties
      - machineType: '8871'
        model: 'AC1'
        type: 'Rack-TowerServer'
        uuid: '223D2C88C8FD11E4947B6EAE8B4BDCDF'
          # bunch of properties
        # Multiple nodes details
"""

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.remote_management.lxca.common import (
    LXCA_COMMON_ARGS,
    has_pylxca,
    connection_object,
)

try:
    from pylxca import nodes
except ImportError:
    pass


UUID_REQUIRED = "UUID of device is required for nodes_by_uuid command."
CHASSIS_UUID_REQUIRED = "UUID of chassis is required for nodes_by_chassis_uuid command."
SUCCESS_MSG = "Success %s result"


def _nodes(module, lxca_con):
    return nodes(lxca_con)


def _nodes_by_uuid(module, lxca_con):
    if not module.params["uuid"]:
        module.fail_json(msg=UUID_REQUIRED)
    return nodes(lxca_con, module.params["uuid"])


def _nodes_by_chassis_uuid(module, lxca_con):
    if not module.params["chassis"]:
        module.fail_json(msg=CHASSIS_UUID_REQUIRED)
    return nodes(lxca_con, chassis=module.params["chassis"])


def _nodes_status_managed(module, lxca_con):
    return nodes(lxca_con, status="managed")


def _nodes_status_unmanaged(module, lxca_con):
    return nodes(lxca_con, status="unmanaged")


def setup_module_object():
    """
    this function merge argument spec and create ansible module object
    :return:
    """
    args_spec = dict(LXCA_COMMON_ARGS)
    args_spec.update(INPUT_ARG_SPEC)
    module = AnsibleModule(argument_spec=args_spec, supports_check_mode=False)

    return module


FUNC_DICT = {
    "nodes": _nodes,
    "nodes_by_uuid": _nodes_by_uuid,
    "nodes_by_chassis_uuid": _nodes_by_chassis_uuid,
    "nodes_status_managed": _nodes_status_managed,
    "nodes_status_unmanaged": _nodes_status_unmanaged,
}


INPUT_ARG_SPEC = dict(
    command_options=dict(
        default="nodes",
        choices=["nodes", "nodes_by_uuid", "nodes_by_chassis_uuid", "nodes_status_managed", "nodes_status_unmanaged"],
    ),
    uuid=dict(),
    chassis=dict(),
)


def execute_module(module):
    """
    This function invoke commands
    :param module: Ansible module object
    """
    try:
        with connection_object(module) as lxca_con:
            result = FUNC_DICT[module.params["command_options"]](module, lxca_con)
            module.exit_json(changed=False, msg=SUCCESS_MSG % module.params["command_options"], result=result)
    except Exception as exception:
        error_msg = "; ".join(exception.args)
        module.fail_json(msg=error_msg, exception=traceback.format_exc())


def main():
    module = setup_module_object()
    has_pylxca(module)
    execute_module(module)


if __name__ == "__main__":
    main()

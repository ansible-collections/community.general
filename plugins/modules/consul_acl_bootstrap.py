#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Florian Apolloner (@apollo13)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: consul_acl_bootstrap
short_description: Bootstrap ACLs in Consul
version_added: 8.3.0
description:
  - Allows bootstrapping of ACLs in a Consul cluster, see U(https://developer.hashicorp.com/consul/api-docs/acl#bootstrap-acls)
    for details.
author:
  - Florian Apolloner (@apollo13)
extends_documentation_fragment:
  - community.general.consul
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  state:
    description:
      - Whether the token should be present or absent.
    choices: ['present', 'bootstrapped']
    default: present
    type: str
  bootstrap_secret:
    description:
      - The secret to be used as secret ID for the initial token.
      - Needs to be an UUID.
    type: str
"""

EXAMPLES = r"""
- name: Bootstrap the ACL system
  community.general.consul_acl_bootstrap:
    bootstrap_secret: 22eaeed1-bdbd-4651-724e-42ae6c43e387
"""

RETURN = r"""
result:
  description:
    - The bootstrap result as returned by the Consul HTTP API.
    - B(Note:) If O(bootstrap_secret) has been specified the C(SecretID) and C(ID) do not contain the secret but C(VALUE_SPECIFIED_IN_NO_LOG_PARAMETER).
      If you pass O(bootstrap_secret), make sure your playbook/role does not depend on this return value!
  returned: changed
  type: dict
  sample:
    AccessorID: 834a5881-10a9-a45b-f63c-490e28743557
    CreateIndex: 25
    CreateTime: '2024-01-21T20:26:27.114612038+01:00'
    Description: Bootstrap Token (Global Management)
    Hash: X2AgaFhnQGRhSSF/h0m6qpX1wj/HJWbyXcxkEM/5GrY=
    ID: VALUE_SPECIFIED_IN_NO_LOG_PARAMETER
    Local: false
    ModifyIndex: 25
    Policies:
      - ID: 00000000-0000-0000-0000-000000000001
        Name: global-management
    SecretID: VALUE_SPECIFIED_IN_NO_LOG_PARAMETER
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.consul import (
    AUTH_ARGUMENTS_SPEC,
    RequestError,
    _ConsulModule,
)

_ARGUMENT_SPEC = {
    "state": dict(type="str", choices=["present", "bootstrapped"], default="present"),
    "bootstrap_secret": dict(type="str", no_log=True),
}
_ARGUMENT_SPEC.update(AUTH_ARGUMENTS_SPEC)
_ARGUMENT_SPEC.pop("token")


def main():
    module = AnsibleModule(_ARGUMENT_SPEC)
    consul_module = _ConsulModule(module)

    data = {}
    if "bootstrap_secret" in module.params:
        data["BootstrapSecret"] = module.params["bootstrap_secret"]

    try:
        response = consul_module.put("acl/bootstrap", data=data)
    except RequestError as e:
        if e.status == 403 and b"ACL bootstrap no longer allowed" in e.response_data:
            return module.exit_json(changed=False)
        raise
    else:
        return module.exit_json(changed=True, result=response)


if __name__ == "__main__":
    main()

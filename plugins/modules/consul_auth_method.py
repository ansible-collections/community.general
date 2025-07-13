#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Florian Apolloner (@apollo13)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: consul_auth_method
short_description: Manipulate Consul auth methods
version_added: 8.3.0
description:
  - Allows the addition, modification and deletion of auth methods in a Consul cluster using the agent. For more details on
    using and configuring ACLs, see U(https://www.consul.io/docs/guides/acl.html).
author:
  - Florian Apolloner (@apollo13)
extends_documentation_fragment:
  - community.general.consul
  - community.general.consul.actiongroup_consul
  - community.general.consul.token
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: partial
    details:
      - In check mode the diff misses operational attributes.
options:
  state:
    description:
      - Whether the token should be present or absent.
    choices: ['present', 'absent']
    default: present
    type: str
  name:
    description:
      - Specifies a name for the ACL auth method.
      - The name can contain alphanumeric characters, dashes C(-), and underscores C(_).
    type: str
    required: true
  type:
    description:
      - The type of auth method being configured.
      - This field is immutable.
      - Required when the auth method is created.
    type: str
    choices: ['kubernetes', 'jwt', 'oidc', 'aws-iam']
  description:
    description:
      - Free form human readable description of the auth method.
    type: str
  display_name:
    description:
      - An optional name to use instead of O(name) when displaying information about this auth method.
    type: str
  max_token_ttl:
    description:
      - This specifies the maximum life of any token created by this auth method.
      - Can be specified in the form of V(60s) or V(5m) (that is, 60 seconds or 5 minutes, respectively).
    type: str
  token_locality:
    description:
      - Defines the kind of token that this auth method should produce.
    type: str
    choices: ['local', 'global']
  config:
    description:
      - The raw configuration to use for the chosen auth method.
      - Contents vary depending upon the O(type) chosen.
      - Required when the auth method is created.
    type: dict
"""

EXAMPLES = r"""
- name: Create an auth method
  community.general.consul_auth_method:
    name: test
    type: jwt
    config:
      jwt_validation_pubkeys:
        - |
          -----BEGIN PUBLIC KEY-----
          MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCozMxH2Mo
          4lgOEePzNm0tRgeLezV6ffAt0gunVTLw7onLRnrq0/IzW7yWR7QkrmBL7jTKEn5u
          +qKhbwKfBstIs+bMY2Zkp18gnTxKLxoS2tFczGkPLPgizskuemMghRniWaoLcyeh
          kd3qqGElvW/VDL5AaWTg0nLVkjRo9z+40RQzuVaE8AkAFmxZzow3x+VJYKdjykkJ
          0iT9wCS0DRTXu269V264Vf/3jvredZiKRkgwlL9xNAwxXFg0x/XFw005UWVRIkdg
          cKWTjpBP2dPwVZ4WWC+9aGVd+Gyn1o0CLelf4rEjGoXbAAEgAqeGUxrcIlbjXfbc
          mwIDAQAB
          -----END PUBLIC KEY-----
    token: "{{ consul_management_token }}"

- name: Delete auth method
  community.general.consul_auth_method:
    name: test
    state: absent
    token: "{{ consul_management_token }}"
"""

RETURN = r"""
auth_method:
  description: The auth method as returned by the Consul HTTP API.
  returned: always
  type: dict
  sample:
    Config:
      JWTValidationPubkeys:
        - |-
          -----BEGIN PUBLIC KEY-----
          MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu1SU1LfVLPHCozMxH2Mo
          4lgOEePzNm0tRgeLezV6ffAt0gunVTLw7onLRnrq0/IzW7yWR7QkrmBL7jTKEn5u
          +qKhbwKfBstIs+bMY2Zkp18gnTxKLxoS2tFczGkPLPgizskuemMghRniWaoLcyeh
          kd3qqGElvW/VDL5AaWTg0nLVkjRo9z+40RQzuVaE8AkAFmxZzow3x+VJYKdjykkJ
          0iT9wCS0DRTXu269V264Vf/3jvredZiKRkgwlL9xNAwxXFg0x/XFw005UWVRIkdg
          cKWTjpBP2dPwVZ4WWC+9aGVd+Gyn1o0CLelf4rEjGoXbAAEgAqeGUxrcIlbjXfbc
          mwIDAQAB
          -----END PUBLIC KEY-----
    CreateIndex: 416
    ModifyIndex: 487
    Name: test
    Type: jwt
operation:
  description: The operation performed.
  returned: changed
  type: str
  sample: update
"""

import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.consul import (
    AUTH_ARGUMENTS_SPEC,
    _ConsulModule,
    camel_case_key,
)


def normalize_ttl(ttl):
    matches = re.findall(r"(\d+)(:h|m|s)", ttl)
    ttl = 0
    for value, unit in matches:
        value = int(value)
        if unit == "m":
            value *= 60
        elif unit == "h":
            value *= 60 * 60
        ttl += value

    new_ttl = ""
    hours, remainder = divmod(ttl, 3600)
    if hours:
        new_ttl += "{0}h".format(hours)
    minutes, seconds = divmod(remainder, 60)
    if minutes:
        new_ttl += "{0}m".format(minutes)
    if seconds:
        new_ttl += "{0}s".format(seconds)
    return new_ttl


class ConsulAuthMethodModule(_ConsulModule):
    api_endpoint = "acl/auth-method"
    result_key = "auth_method"
    unique_identifiers = ["name"]

    def map_param(self, k, v, is_update):
        if k == "config" and v:
            v = {camel_case_key(k2): v2 for k2, v2 in v.items()}
        return super(ConsulAuthMethodModule, self).map_param(k, v, is_update)

    def needs_update(self, api_obj, module_obj):
        if "MaxTokenTTL" in module_obj:
            module_obj["MaxTokenTTL"] = normalize_ttl(module_obj["MaxTokenTTL"])
        return super(ConsulAuthMethodModule, self).needs_update(api_obj, module_obj)


_ARGUMENT_SPEC = {
    "name": dict(type="str", required=True),
    "type": dict(type="str", choices=["kubernetes", "jwt", "oidc", "aws-iam"]),
    "description": dict(type="str"),
    "display_name": dict(type="str"),
    "max_token_ttl": dict(type="str", no_log=False),
    "token_locality": dict(type="str", choices=["local", "global"]),
    "config": dict(type="dict"),
    "state": dict(default="present", choices=["present", "absent"]),
}
_ARGUMENT_SPEC.update(AUTH_ARGUMENTS_SPEC)


def main():
    module = AnsibleModule(
        _ARGUMENT_SPEC,
        supports_check_mode=True,
    )
    consul_module = ConsulAuthMethodModule(module)
    consul_module.execute()


if __name__ == "__main__":
    main()

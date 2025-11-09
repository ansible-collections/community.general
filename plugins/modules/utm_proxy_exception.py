#!/usr/bin/python

# Copyright (c) 2018, Sebastian Schenzel <sebastian.schenzel@mailbox.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: utm_proxy_exception

author:
  - Sebastian Schenzel (@RickS-C137)

short_description: Create, update or destroy reverse_proxy exception entry in Sophos UTM

description:
  - Create, update or destroy a reverse_proxy exception entry in SOPHOS UTM.
  - This module needs to have the REST Ability of the UTM to be activated.
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none

options:
  name:
    description:
      - The name of the object that identifies the entry.
    required: true
    type: str
  op:
    description:
      - The operand to be used with the entries of the path parameter.
    default: 'AND'
    choices:
      - 'AND'
      - 'OR'
    type: str
  path:
    description:
      - The paths the exception in the reverse proxy is defined for.
    type: list
    elements: str
    default: []
  skip_custom_threats_filters:
    description:
      - A list of threats to be skipped.
    type: list
    elements: str
    default: []
  skip_threats_filter_categories:
    description:
      - Define which categories of threats are skipped.
    type: list
    elements: str
    default: []
  skipav:
    description:
      - Skip the Antivirus Scanning.
    default: false
    type: bool
  skipbadclients:
    description:
      - Block clients with bad reputation.
    default: false
    type: bool
  skipcookie:
    description:
      - Skip the Cookie Signing check.
    default: false
    type: bool
  skipform:
    description:
      - Enable form hardening.
    default: false
    type: bool
  skipform_missingtoken:
    description:
      - Enable form hardening with missing tokens.
    default: false
    type: bool
  skiphtmlrewrite:
    description:
      - Protection against SQL.
    default: false
    type: bool
  skiptft:
    description:
      - Enable true file type control.
    default: false
    type: bool
  skipurl:
    description:
      - Enable static URL hardening.
    default: false
    type: bool
  source:
    description:
      - Define which categories of threats are skipped.
    type: list
    elements: str
    default: []
  status:
    description:
      - Status of the exception rule set.
    default: true
    type: bool

extends_documentation_fragment:
  - community.general.utm
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Create UTM proxy_exception
  community.general.utm_proxy_exception:
    utm_host: sophos.host.name
    utm_token: abcdefghijklmno1234
    name: TestExceptionEntry
    backend: REF_OBJECT_STRING
    state: present

- name: Remove UTM proxy_exception
  community.general.utm_proxy_exception:
    utm_host: sophos.host.name
    utm_token: abcdefghijklmno1234
    name: TestExceptionEntry
    state: absent
"""

RETURN = r"""
result:
  description: The utm object that was created.
  returned: success
  type: complex
  contains:
    _ref:
      description: The reference name of the object.
      type: str
    _locked:
      description: Whether or not the object is currently locked.
      type: bool
    _type:
      description: The type of the object.
      type: str
    name:
      description: The name of the object.
      type: str
    comment:
      description: The optional comment string.
      type: str
    op:
      description: The operand to be used with the entries of the path parameter.
      type: str
    path:
      description: The paths the exception in the reverse proxy is defined for.
      type: list
    skip_custom_threats_filters:
      description: A list of threats to be skipped.
      type: list
    skip_threats_filter_categories:
      description: Define which categories of threats are skipped.
      type: list
    skipav:
      description: Skip the Antivirus Scanning.
      type: bool
    skipbadclients:
      description: Block clients with bad reputation.
      type: bool
    skipcookie:
      description: Skip the Cookie Signing check.
      type: bool
    skipform:
      description: Enable form hardening.
      type: bool
    skipform_missingtoken:
      description: Enable form hardening with missing tokens.
      type: bool
    skiphtmlrewrite:
      description: Protection against SQL.
      type: bool
    skiptft:
      description: Enable true file type control.
      type: bool
    skipurl:
      description: Enable static URL hardening.
      type: bool
    source:
      description: Define which categories of threats are skipped.
      type: list
"""

from ansible_collections.community.general.plugins.module_utils.utm_utils import UTM, UTMModule
from ansible.module_utils.common.text.converters import to_native


def main():
    endpoint = "reverse_proxy/exception"
    key_to_check_for_changes = [
        "op",
        "path",
        "skip_custom_threats_filters",
        "skip_threats_filter_categories",
        "skipav",
        "comment",
        "skipbadclients",
        "skipcookie",
        "skipform",
        "status",
        "skipform_missingtoken",
        "skiphtmlrewrite",
        "skiptft",
        "skipurl",
        "source",
    ]
    module = UTMModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
            op=dict(type="str", default="AND", choices=["AND", "OR"]),
            path=dict(type="list", elements="str", default=[]),
            skip_custom_threats_filters=dict(type="list", elements="str", default=[]),
            skip_threats_filter_categories=dict(type="list", elements="str", default=[]),
            skipav=dict(type="bool", default=False),
            skipbadclients=dict(type="bool", default=False),
            skipcookie=dict(type="bool", default=False),
            skipform=dict(type="bool", default=False),
            skipform_missingtoken=dict(type="bool", default=False),
            skiphtmlrewrite=dict(type="bool", default=False),
            skiptft=dict(type="bool", default=False),
            skipurl=dict(type="bool", default=False),
            source=dict(type="list", elements="str", default=[]),
            status=dict(type="bool", default=True),
        )
    )
    try:
        UTM(module, endpoint, key_to_check_for_changes).execute()
    except Exception as e:
        module.fail_json(msg=to_native(e))


if __name__ == "__main__":
    main()

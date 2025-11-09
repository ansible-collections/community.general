#!/usr/bin/python
#
# Copyright (c) 2018, Simon Weald <ansible@simonweald.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: memset_memstore_info
author: "Simon Weald (@glitchcrab)"
short_description: Retrieve Memstore product usage information
notes:
  - An API key generated using the Memset customer control panel is needed with the following minimum scope - C(memstore.usage).
description:
  - Retrieve Memstore product usage information.
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
attributes:
  check_mode:
    version_added: 3.3.0
    # This was backported to 2.5.4 and 1.3.11 as well, since this was a bugfix
options:
  api_key:
    required: true
    type: str
    description:
      - The API key obtained from the Memset control panel.
  name:
    required: true
    type: str
    description:
      - The Memstore product name (that is, V(mstestyaa1)).
"""

EXAMPLES = r"""
- name: Get usage for mstestyaa1
  community.general.memset_memstore_info:
    name: mstestyaa1
    api_key: 5eb86c9896ab03919abcf03857163741
  delegate_to: localhost
"""

RETURN = r"""
memset_api:
  description: Info from the Memset API.
  returned: always
  type: complex
  contains:
    cdn_bandwidth:
      description: Dictionary of CDN bandwidth facts.
      returned: always
      type: complex
      contains:
        bytes_out:
          description: Outbound CDN bandwidth for the last 24 hours in bytes.
          returned: always
          type: int
          sample: 1000
        requests:
          description: Number of requests in the last 24 hours.
          returned: always
          type: int
          sample: 10
        bytes_in:
          description: Inbound CDN bandwidth for the last 24 hours in bytes.
          returned: always
          type: int
          sample: 1000
    containers:
      description: Number of containers.
      returned: always
      type: int
      sample: 10
    bytes:
      description: Space used in bytes.
      returned: always
      type: int
      sample: 3860997965
    objs:
      description: Number of objects.
      returned: always
      type: int
      sample: 1000
    bandwidth:
      description: Dictionary of CDN bandwidth facts.
      returned: always
      type: complex
      contains:
        bytes_out:
          description: Outbound bandwidth for the last 24 hours in bytes.
          returned: always
          type: int
          sample: 1000
        requests:
          description: Number of requests in the last 24 hours.
          returned: always
          type: int
          sample: 10
        bytes_in:
          description: Inbound bandwidth for the last 24 hours in bytes.
          returned: always
          type: int
          sample: 1000
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.memset import memset_api_call


def get_facts(args=None):
    """
    Performs a simple API call and returns a JSON blob.
    """
    retvals, payload = dict(), dict()
    has_changed, has_failed = False, False

    payload["name"] = args["name"]

    api_method = "memstore.usage"
    has_failed, msg, response = memset_api_call(api_key=args["api_key"], api_method=api_method, payload=payload)

    if has_failed:
        # this is the first time the API is called; incorrect credentials will
        # manifest themselves at this point so we need to ensure the user is
        # informed of the reason.
        retvals["failed"] = has_failed
        retvals["msg"] = msg
        if response.status_code is not None:
            retvals["stderr"] = f"API returned an error: {response.status_code}"
        else:
            retvals["stderr"] = f"{response.stderr}"
        return retvals

    # we don't want to return the same thing twice
    memset_api = response.json()

    retvals["changed"] = has_changed
    retvals["failed"] = has_failed
    retvals["msg"] = None
    retvals["memset_api"] = memset_api

    return retvals


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(api_key=dict(required=True, type="str", no_log=True), name=dict(required=True, type="str")),
        supports_check_mode=True,
    )

    # populate the dict with the user-provided vars.
    args = dict(module.params)

    retvals = get_facts(args)

    if retvals["failed"]:
        module.fail_json(**retvals)
    else:
        module.exit_json(**retvals)


if __name__ == "__main__":
    main()

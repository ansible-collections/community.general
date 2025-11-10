#!/usr/bin/python
#
# Copyright (c) Seth Edwards, 2014
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: librato_annotation
short_description: Create an annotation in Librato
description:
  - Create an annotation event on the given annotation stream O(name). If the annotation stream does not exist, it creates
    one automatically.
author: "Seth Edwards (@Sedward)"
requirements: []
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  user:
    type: str
    description:
      - Librato account username.
    required: true
  api_key:
    type: str
    description:
      - Librato account API key.
    required: true
  name:
    type: str
    description:
      - The annotation stream name.
      - If the annotation stream does not exist, it creates one automatically.
  title:
    type: str
    description:
      - The title of an annotation is a string and may contain spaces.
      - The title should be a short, high-level summary of the annotation for example V(v45 Deployment).
    required: true
  source:
    type: str
    description:
      - A string which describes the originating source of an annotation when that annotation is tracked across multiple members
        of a population.
  description:
    type: str
    description:
      - The description contains extra metadata about a particular annotation.
      - The description should contain specifics on the individual annotation for example V(Deployed 9b562b2 shipped new feature
        foo!).
  start_time:
    type: int
    description:
      - The unix timestamp indicating the time at which the event referenced by this annotation started.
  end_time:
    type: int
    description:
      - The unix timestamp indicating the time at which the event referenced by this annotation ended.
      - For events that have a duration, this is a useful way to annotate the duration of the event.
  links:
    type: list
    elements: dict
    description:
      - See examples.
"""

EXAMPLES = r"""
- name: Create a simple annotation event with a source
  community.general.librato_annotation:
    user: user@example.com
    api_key: XXXXXXXXXXXXXXXXX
    title: App Config Change
    source: foo.bar
    description: This is a detailed description of the config change

- name: Create an annotation that includes a link
  community.general.librato_annotation:
    user: user@example.com
    api_key: XXXXXXXXXXXXXXXXXX
    name: code.deploy
    title: app code deploy
    description: this is a detailed description of a deployment
    links:
      - rel: example
        href: http://www.example.com/deploy

- name: Create an annotation with a start_time and end_time
  community.general.librato_annotation:
    user: user@example.com
    api_key: XXXXXXXXXXXXXXXXXX
    name: maintenance
    title: Maintenance window
    description: This is a detailed description of maintenance
    start_time: 1395940006
    end_time: 1395954406
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url


def post_annotation(module):
    user = module.params["user"]
    api_key = module.params["api_key"]
    name = module.params["name"]
    title = module.params["title"]

    url = f"https://metrics-api.librato.com/v1/annotations/{name}"
    params = {}
    params["title"] = title

    if module.params["source"] is not None:
        params["source"] = module.params["source"]
    if module.params["description"] is not None:
        params["description"] = module.params["description"]
    if module.params["start_time"] is not None:
        params["start_time"] = module.params["start_time"]
    if module.params["end_time"] is not None:
        params["end_time"] = module.params["end_time"]
    if module.params["links"] is not None:
        params["links"] = module.params["links"]

    json_body = module.jsonify(params)

    headers = {}
    headers["Content-Type"] = "application/json"

    # Hack send parameters the way fetch_url wants them
    module.params["url_username"] = user
    module.params["url_password"] = api_key
    response, info = fetch_url(module, url, data=json_body, headers=headers)
    response_code = str(info["status"])
    response_body = info["body"]
    if info["status"] != 201:
        if info["status"] >= 400:
            module.fail_json(msg=f"Request Failed. Response code: {response_code} Response body: {response_body}")
        else:
            module.fail_json(msg=f"Request Failed. Response code: {response_code}")
    response = response.read()
    module.exit_json(changed=True, annotation=response)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            user=dict(required=True),
            api_key=dict(required=True, no_log=True),
            name=dict(),
            title=dict(required=True),
            source=dict(),
            description=dict(),
            start_time=dict(type="int"),
            end_time=dict(type="int"),
            links=dict(type="list", elements="dict"),
        )
    )

    post_annotation(module)


if __name__ == "__main__":
    main()

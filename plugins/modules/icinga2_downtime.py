#!/usr/bin/python

# Copyright (c) Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Ansible Project

from __future__ import annotations

DOCUMENTATION = r"""
module: icinga2_downtime
short_description: Manages Icinga 2 downtimes
version_added: "12.4.0"
description:
  - Manages downtimes in Icinga 2 through its REST API.
  - Options as described at U(https://icinga.com/docs/icinga-2/latest/doc/12-icinga2-api/#schedule-downtime).
author:
  - Christoph Fiehe (@cfiehe)
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  url:
    description:
      - URL of the Icinga 2 API.
    type: str
    required: true
  ca_path:
    description:
      - CA certificates bundle to use to verify the Icinga 2 server certificate.
    type: path
  validate_certs:
    description:
      - If V(false), SSL certificates will not be validated.
      - This should only be used on personally controlled sites using self-signed certificates.
    type: bool
    default: true
  timeout:
    description:
      - How long to wait for the server to send data before giving up.
    type: int
    default: 10
  all_services:
    description:
      - Whether downtimes should be set for all services of the matched host objects.
      - If omitted, Icinga 2 does not create downtimes for all services of the matched host objects by default.
    type: bool
  author:
    description:
      - Name of the author.
    type: str
    default: "Ansible"
  comment:
    description:
      - A descriptive comment.
    type: str
    default: Downtime scheduled by Ansible
  child_options:
    description:
      - Schedule child downtimes.
    type: str
    choices: ["DowntimeNoChildren", "DowntimeTriggeredChildren", "DowntimeNonTriggeredChildren"]
  duration:
    description:
      - Duration of the downtime.
      - Required in case of a flexible downtime.
    type: int
  end_time:
    description:
      - End time of the downtime as unix timestamp.
    type: int
  filter_vars:
    description:
      - Variable names and values used in the filter expression.
    type: dict
  filter:
    description:
      - Filter expression limiting the objects to operate on.
    type: str
  fixed:
    description:
      - Whether this downtime is fixed or flexible.
      - If omitted, Icinga 2 creates a fixed downtime by default.
    type: bool
  name:
    description:
      - Name of the downtime.
      - This option has no effect for states other than V(absent).
    type: str
  object_type:
    description:
      - Use V(Host) for a host downtime and V(Service) for a service downtime.
      - Use V(Downtime) and give the name of the downtime you want to remove.
    type: str
    choices: ["Service", "Host", "Downtime"]
    default: Host
  start_time:
    description:
      - Start time of the downtime as unix timestamp.
    type: int
  state:
    description:
      - State of the downtime.
    type: str
    choices: ["present", "absent"]
    default: present
  trigger_name:
    description:
      - Name of the downtime trigger.
    type: str
extends_documentation_fragment:
  - ansible.builtin.url
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Schedule a host downtime
  community.general.icinga2_downtime:
    url: "https://icinga2.example.com:5665"
    url_username: icingadmin
    url_password: secret
    state: present
    author: Ansible
    comment: Scheduled downtime for test purposes.
    all_services: true
    start_time: "{{ downtime_start_time }}"
    end_time: "{{ downtime_end_time }}"
    duration: "{{ downtime_duration }}"
    fixed: true
    object_type: Host
    filter: |-
      host.name=="host.example.com"
  delegate_to: localhost
  register: icinga2_downtime_response
  vars:
    downtime_start_time: "{{ ansible_date_time['epoch'] | int }}"
    downtime_end_time: "{{ downtime_start_time | int + 3600 }}"
    downtime_duration: "{{ downtime_end_time | int - downtime_start_time | int }}"

- name: Remove scheduled host downtime
  edloc.general.icinga2_downtime:
    url: "https://icinga2.example.com:5665"
    url_username: icingadmin
    url_password: secret
    state: absent
    author: Ansible
    object_type: Downtime
    name: "{{ icinga2_downtime_response.results[0].name }}"
  delegate_to: localhost
  when: icinga2_downtime_response.results | default([]) | length > 0
"""

RETURN = r"""
# Returns the results of downtime scheduling as a list of JSON dictionaries from the Icinga 2 API under the C(downtimes) key.
# Refer to https://icinga.com/docs/icinga-2/latest/doc/12-icinga2-api/#schedule-downtime for more details.
results:
  description: Results of downtime scheduling or removal
  type: list
  returned: success
  elements: dict
  contains:
    code:
      description: Success or error code of downtime scheduling.
      returned: always
      type: int
      sample: 200
    legacy_id:
      description: Legacy id of the scheduled downtime.
      returned: if a downtime was scheduled successfully
      type: int
      sample: 28911
    name:
      description: Name of the scheduled downtime.
      returned: if a downtime was scheduled successfully
      type: str
      sample: host.example.com!e19c705a-54c2-49c5-8014-70ff624f9e51
    status:
      description: Human-readable message describing the result of downtime scheduling.
      returned: always
      type: str
      sample: Successfully scheduled downtime 'host.example.com!e19c705a-54c2-49c5-8014-70ff624f9e51' for object 'host.example.com'.
  sample:
    [
      {
        "code": 200,
        "legacy_id": 28911,
        "name": "host.example.com!e19c705a-54c2-49c5-8014-70ff624f9e51",
        "status": "Successfully scheduled downtime 'host.example.com!e19c705a-54c2-49c5-8014-70ff624f9e51' for object 'host.example.com'.",
      }
    ]
error:
  description: Error message as JSON dictionary returned from the Icinga 2 API.
  type: dict
  returned: if downtime scheduling or removal did not succeed.
  sample:
    {
      "error": 404,
      "status": "No objects found."
    }
"""

import typing as t

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.icinga2 import (
    Icinga2Client,
    icinga2_argument_spec,
)


def main() -> None:
    argument_spec = icinga2_argument_spec()
    argument_spec.update(
        all_services=dict(type="bool"),
        author=dict(type="str", default="Ansible"),
        comment=dict(type="str", default="Downtime scheduled by Ansible"),
        child_options=dict(
            type="str",
            choices=[
                "DowntimeNoChildren",
                "DowntimeTriggeredChildren",
                "DowntimeNonTriggeredChildren",
            ],
        ),
        duration=dict(type="int"),
        end_time=dict(type="int"),
        filter_vars=dict(type="dict"),
        filter=dict(type="str"),
        fixed=dict(type="bool"),
        name=dict(type="str"),
        object_type=dict(type="str", choices=["Service", "Host", "Downtime"], default="Host"),
        start_time=dict(type="int"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        trigger_name=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_if=(
            ("state", "present", ["comment", "start_time", "end_time", "filter"]),
            ("fixed", False, ["duration"]),
        ),
        required_one_of=[["filter", "name"]],
    )

    client = Icinga2Client(
        module=module, url=module.params["url"], ca_path=module.params["ca_path"], timeout=module.params.get("timeout")
    )

    if module.params["state"] == "present":
        schedule_downtime(module, client)
    elif module.params["state"] == "absent":
        remove_downtime(module, client)


def schedule_downtime(module: AnsibleModule, client: Icinga2Client) -> None:
    duration = module.params.get("duration")
    end_time = module.params.get("end_time")
    start_time = module.params.get("start_time")

    if end_time <= start_time:
        module.fail_json(msg="The end time must be later than the start time.")

    if duration is None:
        duration = end_time - start_time

    response, info = client.actions.schedule_downtime(
        all_services=module.params.get("all_services"),
        author=module.params.get("author"),
        child_options=module.params.get("child_options"),
        comment=module.params.get("comment"),
        duration=duration,
        end_time=end_time,
        filter_vars=module.params.get("filter_vars"),
        filter=module.params.get("filter"),
        fixed=module.params.get("fixed"),
        object_type=module.params.get("object_type"),
        start_time=start_time,
        trigger_name=module.params.get("trigger_name"),
    )

    status_code = info["status"]
    result: dict[str, t.Any] = {
        "changed": False,
        "failed": False,
    }

    if 200 <= status_code <= 299:
        result["changed"] = True
        msg = "Successfully scheduled downtime."
        try:
            result["results"] = module.from_json(response.read())["results"]
        except (ValueError, KeyError):
            # As a precaution, catch key and value error in case of a malformed response message.
            msg += "\nWarning: Malformed response received from server. Skipping content."

        result["msg"] = msg
        module.exit_json(**result)  # type:ignore[arg-type]
    else:
        result["failed"] = True
        result["msg"] = "Unable to schedule downtime."
        if status_code >= 400:
            try:
                result["error"] = module.from_json(info.get("body"))
            except ValueError:
                pass
        module.fail_json(**result)  # type:ignore[arg-type]


def remove_downtime(module: AnsibleModule, client: Icinga2Client) -> None:
    response, info = client.actions.remove_downtime(
        filter_vars=module.params.get("filter_vars"),
        filter=module.params.get("filter"),
        name=module.params.get("name"),
        object_type=module.params.get("object_type"),
    )

    status_code = info["status"]
    result: dict[str, t.Any] = {
        "changed": False,
        "failed": False,
    }

    if 200 <= status_code <= 299:
        result["changed"] = True
        msg = "Successfully removed downtime."
        try:
            result["results"] = module.from_json(response.read())["results"]
        except (ValueError, KeyError):
            # As a precaution, catch key and value error in case of a malformed response message.
            msg += "\nWarning: Malformed response received from server. Skipping content."

        result["msg"] = msg
        module.exit_json(**result)  # type:ignore[arg-type]
    else:
        if status_code == 404:
            result["msg"] = "No matching downtime found."
            module.exit_json(**result)  # type:ignore[arg-type]
        else:
            if status_code >= 400:
                try:
                    result["error"] = module.from_json(info.get("body"))
                except ValueError:
                    pass
            result["failed"] = True
            result["msg"] = "Unable to remove downtime."
            module.fail_json(**result)  # type:ignore[arg-type]


if __name__ == "__main__":
    main()

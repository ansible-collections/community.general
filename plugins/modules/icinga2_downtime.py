#!/usr/bin/python
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Christoph Fiehe <christoph.fiehe@gmail.com>

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
    details:
      - In case of a complex filter expression, it may become very complex to decide
        whether downtime creation or removal will succeed and trigger a change.
  diff_mode:
    support: none
options:
  all_services:
    description:
      - Whether downtimes should be created for all services of the matched host objects.
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
      - End time of the downtime as UNIX timestamp.
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
      - Whether the downtime is fixed or flexible.
      - If omitted, Icinga 2 creates a fixed downtime by default.
    type: bool
  name:
    description:
      - Name of the downtime object.
      - This option has no effect for states other than V(absent).
    type: str
  object_type:
    description:
      - Use V(Host) for a host downtime and V(Service) for a service downtime.
      - Use V(Downtime) and give the name of the downtime object you want to remove.
    type: str
    choices: ["Service", "Host", "Downtime"]
    default: Host
  start_time:
    description:
      - Start time of the downtime as UNIX timestamp.
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
  - community.general._icinga2_api
  - community.general.attributes
  - ansible.builtin.url
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
    filter: host.name=="host.example.com"
  delegate_to: localhost
  register: icinga2_downtime_response
  vars:
    downtime_start_time: "{{ ansible_date_time['epoch'] | int }}"
    downtime_end_time: "{{ downtime_start_time | int + 3600 }}"
    downtime_duration: "{{ downtime_end_time | int - downtime_start_time | int }}"

- name: Remove scheduled host downtime
  community.general.icinga2_downtime:
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
# Returns the results of downtime scheduling as a list of JSON dictionaries from the Icinga 2 API under the C(results) key.
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
      description: Legacy id of the downtime object.
      returned: if a downtime was scheduled successfully
      type: int
      sample: 28911
    name:
      description: Name of the downtime object.
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
  returned: if downtime scheduling or removal did not succeed
  sample:
    {
      "error": 404,
      "status": "No objects found."
    }
"""

import json
from contextlib import suppress

from ansible_collections.community.general.plugins.module_utils._icinga2 import (
    Icinga2Client,
    icinga2_argument_spec,
)
from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper


class Icinga2Downtime(StateModuleHelper):
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
    module = dict(
        argument_spec=argument_spec,
        supports_check_mode=False,
        required_if=(
            (
                "state",
                "present",
                ["comment", "start_time", "end_time", "filter"],
            ),
            ("fixed", False, ["duration"]),
        ),
        required_one_of=[["filter", "name"]],
    )

    def __init_module__(self) -> None:
        self.client = Icinga2Client(
            module=self.module,  # type:ignore[arg-type]
            url=self.vars.url,
            ca_path=self.vars.ca_path,
            timeout=self.vars.timeout,
        )

    def state_present(self) -> None:
        duration = self.vars.duration
        end_time = self.vars.end_time
        start_time = self.vars.start_time

        if end_time <= start_time:
            self.do_raise(msg="The end time must be later than the start time.")

        if duration is None:
            duration = end_time - start_time

        response, info = self.client.actions.schedule_downtime(
            all_services=self.vars.all_services,
            author=self.vars.author,
            child_options=self.vars.child_options,
            comment=self.vars.comment,
            duration=duration,
            end_time=end_time,
            filter_vars=self.vars.filter_vars,
            filter=self.vars.filter,
            fixed=self.vars.fixed,
            object_type=self.vars.object_type,
            start_time=start_time,
            trigger_name=self.vars.trigger_name,
        )

        status_code = info["status"]

        if 200 <= status_code <= 299:
            self.vars.set("results", json.loads(response.read())["results"], output=True)
            self.vars.msg = "Successfully scheduled downtime."
            self.changed = True
        elif status_code >= 400:
            with suppress(KeyError, ValueError):
                self.vars.set("error", json.loads(info["body"]))  # type:ignore[arg-type]

            self.do_raise(msg="Unable to schedule downtime.")

    def state_absent(self) -> None:
        response, info = self.client.actions.remove_downtime(
            filter_vars=self.vars.filter_vars,
            filter=self.vars.filter,
            name=self.vars.name,
            object_type=self.vars.object_type,
        )

        status_code = info["status"]

        if 200 <= status_code <= 299:
            self.vars.set("results", json.loads(response.read())["results"], output=True)
            self.vars.msg = "Successfully removed downtime."
            self.changed = True
        elif status_code == 404:
            self.vars.msg = "No matching downtime object found."
        elif status_code >= 400:
            with suppress(KeyError, ValueError):
                self.vars.set("error", json.loads(info["body"]))  # type:ignore[arg-type]

            self.do_raise(msg="Unable to remove downtime.")


def main():
    Icinga2Downtime.execute()


if __name__ == "__main__":
    main()

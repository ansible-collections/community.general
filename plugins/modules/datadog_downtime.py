#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Datadog, Inc
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: datadog_downtime
short_description: Manages Datadog downtimes
version_added: 2.0.0
description:
  - Manages downtimes within Datadog.
  - Options as described on U(https://docs.datadoghq.com/api/v1/downtimes/).
author:
  - Datadog (@Datadog)
requirements:
  - datadog-api-client
  - Python 3.6+
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  api_key:
    description:
      - Your Datadog API key.
    required: true
    type: str
  api_host:
    description:
      - The URL to the Datadog API.
      - This value can also be set with the E(DATADOG_HOST) environment variable.
    required: false
    default: https://api.datadoghq.com
    type: str
  app_key:
    description:
      - Your Datadog app key.
    required: true
    type: str
  state:
    description:
      - The designated state of the downtime.
    required: false
    choices: ["present", "absent"]
    default: present
    type: str
  id:
    description:
      - The identifier of the downtime.
      - If empty, a new downtime gets created, otherwise it is either updated or deleted depending of the O(state).
      - To keep your playbook idempotent, you should save the identifier in a file and read it in a lookup.
    type: int
  monitor_tags:
    description:
      - A list of monitor tags to which the downtime applies.
      - The resulting downtime applies to monitors that match ALL provided monitor tags.
    type: list
    elements: str
  scope:
    description:
      - A list of scopes to which the downtime applies.
      - The resulting downtime applies to sources that matches ALL provided scopes.
    type: list
    elements: str
  monitor_id:
    description:
      - The ID of the monitor to mute. If not provided, the downtime applies to all monitors.
    type: int
  downtime_message:
    description:
      - A message to include with notifications for this downtime.
      - Email notifications can be sent to specific users by using the same "@username" notation as events.
    type: str
  start:
    type: int
    description:
      - POSIX timestamp to start the downtime. If not provided, the downtime starts the moment it is created.
  end:
    type: int
    description:
      - POSIX timestamp to end the downtime. If not provided, the downtime is in effect until you cancel it.
  timezone:
    description:
      - The timezone for the downtime.
    type: str
  rrule:
    description:
      - The C(RRULE) standard for defining recurring events.
      - For example, to have a recurring event on the first day of each month, select a type of rrule and set the C(FREQ)
        to C(MONTHLY) and C(BYMONTHDAY) to C(1).
      - Most common rrule options from the iCalendar Spec are supported.
      - Attributes specifying the duration in C(RRULE) are not supported (for example C(DTSTART), C(DTEND), C(DURATION)).
    type: str
"""

EXAMPLES = r"""
- name: Create a downtime
  register: downtime_var
  community.general.datadog_downtime:
    state: present
    monitor_tags:
      - "foo:bar"
    downtime_message: "Downtime for foo:bar"
    scope: "test"
    api_key: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    app_key: "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    # Lookup the id in the file and ignore errors if the file doesn't exits, so downtime gets created
    id: "{{ lookup('file', inventory_hostname ~ '_downtime_id.txt', errors='ignore') }}"
- name: Save downtime id to file for later updates and idempotence
  delegate_to: localhost
  copy:
    content: "{{ downtime.downtime.id }}"
    dest: "{{ inventory_hostname ~ '_downtime_id.txt' }}"
"""

RETURN = r"""
# Returns the downtime JSON dictionary from the API response under the C(downtime) key.
# See https://docs.datadoghq.com/api/v1/downtimes/#schedule-a-downtime for more details.
downtime:
  description: The downtime returned by the API.
  type: dict
  returned: always
  sample:
    {
      "active": true,
      "canceled": null,
      "creator_id": 1445416,
      "disabled": false,
      "downtime_type": 2,
      "end": null,
      "id": 1055751000,
      "message": "Downtime for foo:bar",
      "monitor_id": null,
      "monitor_tags": [
        "foo:bar"
      ],
      "parent_id": null,
      "recurrence": null,
      "scope": [
        "test"
      ],
      "start": 1607015009,
      "timezone": "UTC",
      "updater_id": null
    }
"""

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
# Import Datadog

DATADOG_IMP_ERR = None
HAS_DATADOG = True
try:
    from datadog_api_client.v1 import Configuration, ApiClient, ApiException
    from datadog_api_client.v1.api.downtimes_api import DowntimesApi
    from datadog_api_client.v1.model.downtime import Downtime
    from datadog_api_client.v1.model.downtime_recurrence import DowntimeRecurrence
except ImportError:
    DATADOG_IMP_ERR = traceback.format_exc()
    HAS_DATADOG = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(required=True, no_log=True),
            api_host=dict(required=False, default="https://api.datadoghq.com"),
            app_key=dict(required=True, no_log=True),
            state=dict(required=False, choices=["present", "absent"], default="present"),
            monitor_tags=dict(required=False, type="list", elements="str"),
            scope=dict(required=False, type="list", elements="str"),
            monitor_id=dict(required=False, type="int"),
            downtime_message=dict(required=False, no_log=True),
            start=dict(required=False, type="int"),
            end=dict(required=False, type="int"),
            timezone=dict(required=False, type="str"),
            rrule=dict(required=False, type="str"),
            id=dict(required=False, type="int"),
        )
    )

    # Prepare Datadog
    if not HAS_DATADOG:
        module.fail_json(msg=missing_required_lib("datadog-api-client"), exception=DATADOG_IMP_ERR)

    configuration = Configuration(
        host=module.params["api_host"],
        api_key={
            "apiKeyAuth": module.params["api_key"],
            "appKeyAuth": module.params["app_key"]
        }
    )
    with ApiClient(configuration) as api_client:
        api_client.user_agent = "ansible_collection/community_general (module_name datadog_downtime) {0}".format(
            api_client.user_agent
        )
        api_instance = DowntimesApi(api_client)

        # Validate api and app keys
        try:
            api_instance.list_downtimes(current_only=True)
        except ApiException as e:
            module.fail_json(msg="Failed to connect Datadog server using given app_key and api_key: {0}".format(e))

        if module.params["state"] == "present":
            schedule_downtime(module, api_client)
        elif module.params["state"] == "absent":
            cancel_downtime(module, api_client)


def _get_downtime(module, api_client):
    api = DowntimesApi(api_client)
    downtime = None
    if module.params["id"]:
        try:
            downtime = api.get_downtime(module.params["id"])
        except ApiException as e:
            module.fail_json(msg="Failed to retrieve downtime with id {0}: {1}".format(module.params["id"], e))
    return downtime


def build_downtime(module):
    downtime = Downtime()
    if module.params["monitor_tags"]:
        downtime.monitor_tags = module.params["monitor_tags"]
    if module.params["scope"]:
        downtime.scope = module.params["scope"]
    if module.params["monitor_id"]:
        downtime.monitor_id = module.params["monitor_id"]
    if module.params["downtime_message"]:
        downtime.message = module.params["downtime_message"]
    if module.params["start"]:
        downtime.start = module.params["start"]
    if module.params["end"]:
        downtime.end = module.params["end"]
    if module.params["timezone"]:
        downtime.timezone = module.params["timezone"]
    if module.params["rrule"]:
        downtime.recurrence = DowntimeRecurrence(
            rrule=module.params["rrule"],
            type="rrule",
        )
    return downtime


def _post_downtime(module, api_client):
    api = DowntimesApi(api_client)
    downtime = build_downtime(module)
    try:
        resp = api.create_downtime(downtime)
        module.params["id"] = resp.id
        module.exit_json(changed=True, downtime=resp.to_dict())
    except ApiException as e:
        module.fail_json(msg="Failed to create downtime: {0}".format(e))


def _equal_dicts(a, b, ignore_keys):
    ka = set(a).difference(ignore_keys)
    kb = set(b).difference(ignore_keys)
    return ka == kb and all(a[k] == b[k] for k in ka)


def _update_downtime(module, current_downtime, api_client):
    api = DowntimesApi(api_client)
    downtime = build_downtime(module)
    try:
        if current_downtime.disabled:
            resp = api.create_downtime(downtime)
        else:
            resp = api.update_downtime(module.params["id"], downtime)
        if _equal_dicts(
                resp.to_dict(),
                current_downtime.to_dict(),
                ["active", "creator_id", "updater_id"]
        ):
            module.exit_json(changed=False, downtime=resp.to_dict())
        else:
            module.exit_json(changed=True, downtime=resp.to_dict())
    except ApiException as e:
        module.fail_json(msg="Failed to update downtime: {0}".format(e))


def schedule_downtime(module, api_client):
    downtime = _get_downtime(module, api_client)
    if downtime is None:
        _post_downtime(module, api_client)
    else:
        _update_downtime(module, downtime, api_client)


def cancel_downtime(module, api_client):
    downtime = _get_downtime(module, api_client)
    api = DowntimesApi(api_client)
    if downtime is None:
        module.exit_json(changed=False)
    try:
        api.cancel_downtime(downtime["id"])
    except ApiException as e:
        module.fail_json(msg="Failed to create downtime: {0}".format(e))

    module.exit_json(changed=True)


if __name__ == "__main__":
    main()

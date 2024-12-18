#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2020, Datadog, Inc
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

DOCUMENTATION = """
---
module: datadog_downtime
short_description: Manages Datadog downtimes
version_added: 2.0.0
description:
  - Manages downtimes within Datadog.
  - Options as described on U(https://docs.datadoghq.com/api/v2/downtimes/).
author:
  - Datadog (@Datadog)
requirements:
  - datadog-api-client
  - Python 3.7+
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
          - A scope to which the downtime applies.
          - For example, 'host:app2' or 'env:staging'
        type: str
    duration:
        description:
          - The duration of the downtime.
        type: str
    monitor_identifier:
        description:
          - The monitor identifier configuration.
        type: dict
    monitor_id:
        description:
          - The ID of the monitor to mute. If not provided, the downtime applies to all monitors.
        type: int
    downtime_message:
        description:
          - A message to include with notifications for this downtime.
          - Email notifications can be sent to specific users by using the same "@username" notation as events.
        type: str
    mute_first_recovery_notification:
        description:
          - If true, mutes the first recovery notification.
        type: bool
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
          - For example, to have a recurring event on the first day of each month,
            select a type of rrule and set the C(FREQ) to C(MONTHLY) and C(BYMONTHDAY) to C(1).
          - Most common rrule options from the iCalendar Spec are supported.
          - Attributes specifying the duration in C(RRULE) are not supported (for example C(DTSTART), C(DTEND), C(DURATION)).
        type: str
"""

EXAMPLES = """
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

RETURN = """
# Returns the downtime JSON dictionary from the API response under the C(downtime) key.
# See https://docs.datadoghq.com/api/v2/downtimes/#schedule-a-downtime for more details.
downtime:
    description: The downtime returned by the API.
    type: dict
    returned: always
    sample:
        active: true
        canceled: null
        creator_id: 1445416
        disabled: false
        downtime_type: 2
        end: null
        id: 1055751000
        message: "Downtime for foo:bar"
        monitor_id: null
        monitor_tags:
            - "foo:bar"
        parent_id: null
        recurrence: null
        scope:
            - "test"
        start: 1607015009
        timezone: "UTC"
        updater_id: null
        monitor_identifier:
            monitor_id: 12345
        mute_first_recovery_notification: false
        schedule:
            start: 1607015009
            end: null
            timezone: "UTC"
            recurrences:
                - type: "rrule"
                  rrule: "FREQ=MONTHLY;BYMONTHDAY=1"
                  duration: "PT1H"
"""

__metaclass__ = type
import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib

# Import Datadog

DATADOG_IMP_ERR = None
HAS_DATADOG = True
try:
    from datadog_api_client.v2.api.downtimes_api import DowntimesApi
    from datadog_api_client.api_client import ApiClient
    from datadog_api_client.configuration import Configuration
    from datadog_api_client.exceptions import ApiException
    from datadog_api_client.v2.model.downtime_create_request_attributes import DowntimeCreateRequestAttributes
    from datadog_api_client.v2.model.downtime_create_request_data import DowntimeCreateRequestData
    from datadog_api_client.v2.model.downtime_create_request import DowntimeCreateRequest
    from datadog_api_client.v2.model.downtime_schedule_recurrence_create_update_request import (
        DowntimeScheduleRecurrenceCreateUpdateRequest
    )
except ImportError:
    DATADOG_IMP_ERR = traceback.format_exc()
    HAS_DATADOG = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(required=True, no_log=True),
            api_host=dict(required=False, default="https://api.datadoghq.com"),
            app_key=dict(required=True, no_log=True),
            state=dict(required=False, choices=[
                       "present", "absent"], default="present"),
            monitor_tags=dict(required=False, type="list", elements="str"),
            scope=dict(required=False, type="str"),
            monitor_id=dict(required=False, type="int"),
            monitor_identifier=dict(required=False, type="dict"),
            downtime_message=dict(required=False, no_log=True),
            mute_first_recovery_notification=dict(required=False, type="bool"),
            start=dict(required=False, type="int"),
            end=dict(required=False, type="int"),
            timezone=dict(required=False, type="str"),
            rrule=dict(required=False, type="str"),
            duration=dict(required=False, type="str"),
            id=dict(required=False, type="int"),
        )
    )

    if not HAS_DATADOG:
        module.fail_json(msg=missing_required_lib(
            "datadog-api-client"), exception=DATADOG_IMP_ERR)

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

        try:
            api_instance.list_downtimes(current_only=True)
        except ApiException as e:
            module.fail_json(
                msg="Failed to connect Datadog server using given app_key and api_key: {0}".format(e))

        schedule_downtime(module, api_instance)


def _get_downtime(module, api_instance):
    downtime_id = module.params.get("id")

    if not downtime_id:
        return None

    try:
        downtime = api_instance.get_downtime(downtime_id=str(downtime_id))
        if downtime.data.attributes.status == 'disabled':
            return None
        return downtime
    except ApiException as e:
        if e.status == 404:
            return None
        else:
            module.fail_json(
                msg="Failed to get downtime %s: %s" % (downtime_id, e))


def build_downtime(module):
    recurrence = None
    if module.params.get("rrule"):
        recurrence = DowntimeScheduleRecurrenceCreateUpdateRequest(
            type="rrule",
            rrule=module.params.get("rrule"),
            duration=module.params.get("duration")
        )
    body = DowntimeCreateRequest(
        data=DowntimeCreateRequestData(
            attributes=DowntimeCreateRequestAttributes(
                message=module.params.get("downtime_message"),
                monitor_identifier={"monitor_id": module.params.get(
                    "monitor_id")} if module.params.get("monitor_id") else None,
                mute_first_recovery_notification=module.params.get(
                    "mute_first_recovery_notification"),
                scope=module.params.get("scope"),
                monitor_tags=module.params.get("monitor_tags"),
                schedule={
                    "start": module.params.get("start"),
                    "end": module.params.get("end"),
                    "timezone": module.params.get("timezone"),
                    "recurrences": [recurrence] if recurrence else None
                }
            ),
            type="downtime"
        )
    )
    return body


def _post_downtime(module, api_instance):
    downtime = build_downtime(module)
    try:
        resp = api_instance.create_downtime(body=downtime)
        module.params["id"] = resp.data.id
        module.exit_json(changed=True, downtime=resp.data.to_dict())
    except ApiException as e:
        module.fail_json(msg="Failed to create downtime: {0}".format(e))


def _equal_dicts(a, b, ignore_keys=None):
    if ignore_keys is None:
        ignore_keys = set()

    if isinstance(a, dict) and isinstance(b, dict):
        ka = set(a).difference(ignore_keys)
        kb = set(b).difference(ignore_keys)
        if ka != kb:
            return False
        for k in ka:
            if not _equal_dicts(a[k], b[k], ignore_keys):
                return False
        return True

    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        return all(_equal_dicts(x, y, ignore_keys) for x, y in zip(a, b))

    else:
        return a == b


def _update_downtime(module, current_downtime, api_instance):
    downtime = build_downtime(module)
    try:
        are_equal = _equal_dicts(
            downtime.data.attributes.to_dict(),
            current_downtime.data.attributes.to_dict(),
            {"active", "creator_id", "updater_id", "status"}
        )
        if are_equal:
            module.exit_json(
                changed=False, downtime=current_downtime.to_dict())
        else:
            resp = api_instance.update_downtime(
                downtime_id=module.params["id"], body=downtime)
            module.exit_json(changed=True, downtime=resp.to_dict())
    except ApiException as e:

        module.fail_json(msg="Failed to update downtime: %s" % (e,))


def schedule_downtime(module, api_instance):
    downtime = _get_downtime(module, api_instance)

    if module.params["state"] == "absent":
        if downtime is None:
            module.exit_json(
                changed=False,
                msg="Downtime %s does not exist" % (module.params['id'],)
            )
        else:
            cancel_downtime(module, api_instance)
    else:
        if downtime is None:
            _post_downtime(module, api_instance)
        else:
            _update_downtime(module, downtime, api_instance)


def cancel_downtime(module, api_instance):
    downtime_id = module.params["id"]

    if not downtime_id:
        module.fail_json(msg="id parameter is required for state=absent")

    try:
        api_instance.cancel_downtime(downtime_id=str(downtime_id))
        module.exit_json(
            changed=True,
            id=downtime_id,
            msg="Downtime %s cancelled successfully" % (downtime_id,)
        )
    except ApiException as e:
        if e.status == 404:
            module.exit_json(
                changed=False,
                msg="Downtime %s does not exist" % (downtime_id)
            )
        module.fail_json(
            msg="Failed to cancel downtime %s: %s") % (downtime_id, e)


if __name__ == "__main__":
    main()

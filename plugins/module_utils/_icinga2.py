# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Christoph Fiehe <christoph.fiehe@gmail.com>

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import json
import typing as t

from ansible.module_utils.common.text.converters import to_bytes
from ansible.module_utils.urls import fetch_url, url_argument_spec

if t.TYPE_CHECKING:
    from http.client import HTTPResponse
    from urllib.error import HTTPError

    from ansible.module_utils.basic import AnsibleModule


class Icinga2Client:
    def __init__(
        self,
        module: AnsibleModule,
        url: str,
        ca_path: str | None = None,
        timeout: int | float | None = None,
    ) -> None:
        self.module = module
        self.url = url.rstrip("/")
        self.ca_path = ca_path
        self.timeout = timeout
        self.actions = Actions(client=self)

    def send_request(
        self, method: str, path: str, data: dict[str, t.Any] | None = None
    ) -> tuple[HTTPResponse | HTTPError, dict[str, t.Any]]:
        url = f"{self.url}/{path}"
        headers = {
            "X-HTTP-Method-Override": method.upper(),
            "Accept": "application/json",
        }
        return fetch_url(
            module=self.module,
            url=url,
            ca_path=self.ca_path,
            data=to_bytes(json.dumps(data)),
            headers=headers,
            timeout=self.timeout,
        )


class Actions:
    base_path = "v1/actions"

    def __init__(self, client: Icinga2Client) -> None:
        self.client = client

    def schedule_downtime(
        self,
        object_type: str,
        filter: str,
        author: str,
        comment: str,
        start_time: int,
        end_time: int,
        duration: int,
        filter_vars: dict[str, t.Any] | None = None,
        fixed: bool | None = None,
        all_services: bool | None = None,
        trigger_name: str | None = None,
        child_options: str | None = None,
    ) -> tuple[HTTPResponse | HTTPError, dict[str, t.Any]]:
        path = f"{self.base_path}/schedule-downtime"

        data: dict[str, t.Any] = {
            "type": object_type,
            "filter": filter,
            "author": author,
            "comment": comment,
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration,
        }
        if filter_vars is not None:
            data["filter_vars"] = filter_vars
        if fixed is not None:
            data["fixed"] = fixed
        if all_services is not None:
            data["all_services"] = all_services
        if trigger_name is not None:
            data["trigger_name"] = trigger_name
        if child_options is not None:
            data["child_options"] = child_options

        return self.client.send_request(method="POST", path=path, data=data)

    def remove_downtime(
        self,
        object_type: str,
        name: str | None = None,
        filter: str | None = None,
        filter_vars: dict[str, t.Any] | None = None,
    ) -> tuple[HTTPResponse | HTTPError, dict[str, t.Any]]:
        path = f"{self.base_path}/remove-downtime"

        data: dict[str, t.Any] = {"type": object_type}
        if name is not None:
            data[object_type.lower()] = name
        if filter is not None:
            data["filter"] = filter
        if filter_vars is not None:
            data["filter_vars"] = filter_vars

        return self.client.send_request(method="POST", path=path, data=data)


def icinga2_argument_spec() -> dict[str, t.Any]:
    argument_spec = url_argument_spec()
    argument_spec.update(
        url=dict(type="str", required=True),
        ca_path=dict(type="path"),
        timeout=dict(type="int", default=10),
    )
    return argument_spec

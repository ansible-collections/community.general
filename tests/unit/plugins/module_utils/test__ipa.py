# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.community.general.plugins.module_utils import _ipa


class FailJson(Exception):
    pass


GROUP = {"cn": ["mygroup"], "member_user": ["alice"]}


def post_json(response):
    module = MagicMock()
    module.params = {"ipa_timeout": 10}
    module.fail_json.side_effect = FailJson
    client = _ipa.IPAClient(module, "ipa.example.com", 443, "https")
    resp = MagicMock()
    resp.headers.get_content_charset.return_value = "utf-8"
    resp.read.return_value = json.dumps(response).encode("utf-8")
    with patch.object(_ipa, "fetch_url", return_value=(resp, {"status": 200})):
        return client._post_json(method="group_add_member", name="mygroup", item={"user": ["alice"]}), module


@pytest.mark.parametrize(
    "failed",
    [
        None,
        {},
        {"member": {"host": [], "hostgroup": []}},
        {"member": {"user": [], "group": [], "service": [], "idoverrideuser": []}},
        {"memberuser": {"user": [], "group": []}, "memberhost": {"host": [], "hostgroup": []}},
    ],
)
def test_post_json_succeeds_when_failed_has_no_entries(failed):
    response = {"error": None, "result": {"result": GROUP, "failed": failed, "completed": 1}}
    result, module = post_json(response)
    assert result == GROUP
    module.fail_json.assert_not_called()


@pytest.mark.parametrize(
    "failed",
    [
        {"member": {"user": [["bob", "no such entry"]], "group": []}},
        {"memberuser": {"user": [], "group": [["admins", "This entry is already a member"]]}},
    ],
)
def test_post_json_fails_when_failed_has_entries(failed):
    response = {"error": None, "result": {"result": GROUP, "failed": failed, "completed": 0}}
    with pytest.raises(FailJson):
        post_json(response)

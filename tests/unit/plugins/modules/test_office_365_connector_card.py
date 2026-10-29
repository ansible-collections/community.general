# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import office_365_connector_card

WEBHOOK = "https://example.invalid/webhook"


class TestOffice365ConnectorCardModule(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.module = office_365_connector_card

    def test_without_required_parameters(self):
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                self.module.main()

    def _run(self, status, msg="OK"):
        with set_module_args({"webhook": WEBHOOK, "text": "hello"}):
            with patch.object(office_365_connector_card, "fetch_url") as fetch_url_mock:
                fetch_url_mock.return_value = (None, {"status": status, "msg": msg})
                with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
                    self.module.main()
        assert fetch_url_mock.call_count == 1
        assert fetch_url_mock.call_args[1]["url"] == WEBHOOK
        assert json.loads(fetch_url_mock.call_args[1]["data"])["text"] == "hello"
        return exc

    def test_success_200(self):
        exc = self._run(200)
        assert exc.type is AnsibleExitJson
        assert exc.value.args[0]["changed"] is True

    def test_success_202_power_automate(self):
        exc = self._run(202, "Accepted")
        assert exc.type is AnsibleExitJson
        assert exc.value.args[0]["changed"] is True

    def test_failure_status(self):
        exc = self._run(500, "Internal Server Error")
        assert exc.type is AnsibleFailJson
        assert "Internal Server Error" in exc.value.args[0]["msg"]

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import MagicMock, patch

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import icinga2_host

MODULE_ARGS = {
    "url": "https://icinga:5665",
    "url_username": "user",
    "url_password": "password",
    "state": "present",
    "name": "test.domain",
    "ip": "10.1.1.1",
    "validate_certs": False,
    "variables": {},
}


def closed_response():
    # Simulates the response object fetch_url() returns for HTTP errors: it has
    # already been read and closed internally, so a second .read() yields "".
    rsp = MagicMock()
    rsp.closed = True
    rsp.read.return_value = ""
    return rsp


class TestIcinga2HostCallUrl(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.module = icinga2_host

    def test_error_status_with_json_body_is_surfaced(self):
        # Regression test for https://github.com/ansible-collections/community.general/issues/4948
        # An error response's body must be read from info["body"], not from rsp.read()
        # (which is already exhausted), or the module crashes with a JSONDecodeError
        # instead of reporting the actual failure.
        with set_module_args(MODULE_ARGS):
            with patch.object(icinga2_host, "fetch_url") as fetch_url_mock:
                fetch_url_mock.return_value = (
                    closed_response(),
                    {"status": 500, "body": '{"error": "Object already exists."}'},
                )
                with self.assertRaises(AnsibleFailJson) as ctx:
                    self.module.main()

        msg = ctx.exception.args[0]["msg"]
        assert "Object already exists." in msg
        assert "Expecting value" not in msg

    def test_error_status_with_non_json_body_is_surfaced(self):
        with set_module_args(MODULE_ARGS):
            with patch.object(icinga2_host, "fetch_url") as fetch_url_mock:
                fetch_url_mock.return_value = (
                    closed_response(),
                    {"status": 502, "body": "Bad Gateway"},
                )
                with self.assertRaises(AnsibleFailJson) as ctx:
                    self.module.main()

        msg = ctx.exception.args[0]["msg"]
        assert "Bad Gateway" in msg
        assert "Expecting value" not in msg

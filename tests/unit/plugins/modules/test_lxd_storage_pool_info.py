# Copyright (c) 2025, Sean McAvoy (@smcavoy) <seanmcavoy@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import patch

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import lxd_storage_pool_info as module


class FakeLXDClient:
    responses: dict[tuple[str, str], dict] = {}

    def __init__(self, url, key_file=None, cert_file=None, debug=False, **kwargs):
        self.url = url
        self.key_file = key_file
        self.cert_file = cert_file
        self.debug = debug
        self.logs = [{"type": "fake-request"}] if debug else []

    def authenticate(self, trust_password):
        self.trust_password = trust_password

    def do(self, method, url, ok_error_codes=None, **kwargs):
        try:
            return self.responses[(method, url)]
        except KeyError as exc:
            raise AssertionError(f"Unexpected call: {method} {url}") from exc


class TestLXDStoragePoolInfo(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.module = module

    def test_returns_storage_pools(self):
        """Pool metadata from the API is returned unchanged using recursion."""
        FakeLXDClient.responses = {
            ("GET", "/1.0/storage-pools?recursion=1"): {
                "type": "sync",
                "metadata": [
                    {"name": "default", "driver": "dir"},
                    {"name": "fast", "driver": "zfs"},
                ],
            },
        }

        with patch.object(self.module, "LXDClient", FakeLXDClient):
            with patch.object(self.module.os.path, "exists", return_value=False):
                with self.assertRaises(AnsibleExitJson) as exc:
                    with set_module_args({}):
                        self.module.main()

        result = exc.exception.args[0]
        assert result["storage_pools"] == [
            {"name": "default", "driver": "dir"},
            {"name": "fast", "driver": "zfs"},
        ]

    def test_returns_specific_storage_pool(self):
        """When name is specified, only that pool is returned."""
        FakeLXDClient.responses = {
            ("GET", "/1.0/storage-pools/default"): {"type": "sync", "metadata": {"name": "default", "driver": "dir"}},
        }

        with patch.object(self.module, "LXDClient", FakeLXDClient):
            with patch.object(self.module.os.path, "exists", return_value=False):
                with self.assertRaises(AnsibleExitJson) as exc:
                    with set_module_args({"name": "default"}):
                        self.module.main()

        result = exc.exception.args[0]
        assert result["storage_pools"] == [
            {"name": "default", "driver": "dir"},
        ]

    def test_filters_storage_pools_by_type(self):
        """Pools can be filtered by driver type using recursion."""
        FakeLXDClient.responses = {
            ("GET", "/1.0/storage-pools?recursion=1"): {
                "type": "sync",
                "metadata": [
                    {"name": "default", "driver": "dir"},
                    {"name": "fast", "driver": "zfs"},
                ],
            },
        }

        with patch.object(self.module, "LXDClient", FakeLXDClient):
            with patch.object(self.module.os.path, "exists", return_value=False):
                with self.assertRaises(AnsibleExitJson) as exc:
                    with set_module_args({"type": ["zfs"]}):
                        self.module.main()

        result = exc.exception.args[0]
        assert result["storage_pools"] == [
            {"name": "fast", "driver": "zfs"},
        ]

    def test_error_code_returned_on_failure(self):
        """Failures surface the LXD error code for easier debugging."""
        FakeLXDClient.responses = {
            ("GET", "/1.0/storage-pools?recursion=1"): {
                "type": "error",
                "error": "unavailable",
                "error_code": 503,
            }
        }

        with patch.object(self.module, "LXDClient", FakeLXDClient):
            with patch.object(self.module.os.path, "exists", return_value=False):
                with self.assertRaises(AnsibleFailJson) as exc:
                    with set_module_args({}):
                        self.module.main()

        result = exc.exception.args[0]
        assert result["error_code"] == 503
        assert "Failed to retrieve storage pools" in result["msg"]

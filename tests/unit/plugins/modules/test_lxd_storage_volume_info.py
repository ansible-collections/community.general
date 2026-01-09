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

from ansible_collections.community.general.plugins.modules import lxd_storage_volume_info as module


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


class TestLXDStorageVolumeInfo(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.module = module

    def test_returns_all_volumes_for_pool(self):
        """Volume metadata is returned for every volume in the pool using recursion."""
        FakeLXDClient.responses = {
            ("GET", "/1.0/storage-pools/default"): {"type": "sync", "metadata": {"name": "default"}},
            ("GET", "/1.0/storage-pools/default/volumes?recursion=1"): {
                "type": "sync",
                "metadata": [
                    {"name": "data", "type": "custom"},
                    {"name": "web", "type": "container"},
                ],
            },
        }

        with patch.object(self.module, "LXDClient", FakeLXDClient):
            with patch.object(self.module.os.path, "exists", return_value=False):
                with self.assertRaises(AnsibleExitJson) as exc:
                    with set_module_args({"pool": "default"}):
                        self.module.main()

        result = exc.exception.args[0]
        assert result["storage_volumes"] == [
            {"name": "data", "type": "custom"},
            {"name": "web", "type": "container"},
        ]

    def test_returns_specific_storage_volume(self):
        """When name is specified without type, recursion is used to find it."""
        FakeLXDClient.responses = {
            ("GET", "/1.0/storage-pools/default"): {"type": "sync", "metadata": {"name": "default"}},
            ("GET", "/1.0/storage-pools/default/volumes?recursion=1"): {
                "type": "sync",
                "metadata": [
                    {"name": "data", "type": "custom"},
                    {"name": "web", "type": "container"},
                ],
            },
        }

        with patch.object(self.module, "LXDClient", FakeLXDClient):
            with patch.object(self.module.os.path, "exists", return_value=False):
                with self.assertRaises(AnsibleExitJson) as exc:
                    with set_module_args({"pool": "default", "name": "data"}):
                        self.module.main()

        result = exc.exception.args[0]
        assert result["storage_volumes"] == [
            {"name": "data", "type": "custom"},
        ]

    def test_filters_storage_volumes_by_type(self):
        """Volumes can be filtered by type using recursion."""
        FakeLXDClient.responses = {
            ("GET", "/1.0/storage-pools/default"): {"type": "sync", "metadata": {"name": "default"}},
            ("GET", "/1.0/storage-pools/default/volumes?recursion=1"): {
                "type": "sync",
                "metadata": [
                    {"name": "data", "type": "custom"},
                    {"name": "web", "type": "container"},
                ],
            },
        }

        with patch.object(self.module, "LXDClient", FakeLXDClient):
            with patch.object(self.module.os.path, "exists", return_value=False):
                with self.assertRaises(AnsibleExitJson) as exc:
                    with set_module_args({"pool": "default", "type": "container"}):
                        self.module.main()

        result = exc.exception.args[0]
        assert result["storage_volumes"] == [
            {"name": "web", "type": "container"},
        ]

    def test_returns_specific_volume_with_type_using_direct_request(self):
        """When both name and type are specified, a direct API call is made (no recursion)."""
        FakeLXDClient.responses = {
            ("GET", "/1.0/storage-pools/default"): {"type": "sync", "metadata": {"name": "default"}},
            ("GET", "/1.0/storage-pools/default/volumes/custom/data"): {
                "type": "sync",
                "metadata": {"name": "data", "type": "custom", "config": {"size": "10GiB"}},
            },
        }

        with patch.object(self.module, "LXDClient", FakeLXDClient):
            with patch.object(self.module.os.path, "exists", return_value=False):
                with self.assertRaises(AnsibleExitJson) as exc:
                    with set_module_args({"pool": "default", "name": "data", "type": "custom"}):
                        self.module.main()

        result = exc.exception.args[0]
        assert result["storage_volumes"] == [
            {"name": "data", "type": "custom", "config": {"size": "10GiB"}},
        ]

    def test_error_code_returned_when_listing_volumes_fails(self):
        """Errors from LXD are surfaced with the numeric code."""
        FakeLXDClient.responses = {
            ("GET", "/1.0/storage-pools/default"): {"type": "sync", "metadata": {"name": "default"}},
            ("GET", "/1.0/storage-pools/default/volumes?recursion=1"): {
                "type": "error",
                "error": "service unavailable",
                "error_code": 503,
            },
        }

        with patch.object(self.module, "LXDClient", FakeLXDClient):
            with patch.object(self.module.os.path, "exists", return_value=False):
                with self.assertRaises(AnsibleFailJson) as exc:
                    with set_module_args({"pool": "default"}):
                        self.module.main()

        result = exc.exception.args[0]
        assert result["error_code"] == 503
        assert "Failed to retrieve volumes from pool" in result["msg"]

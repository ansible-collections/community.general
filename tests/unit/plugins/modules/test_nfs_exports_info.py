# Copyright (c) 2026, Samaneh Yousefnezhad <s-yousefnezhad@um.ac.ir>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import hashlib
import sys
import pytest


@pytest.fixture
def fake_exports_content() -> str:
    return (
        "\n# Sample exports\n"
        "/srv/nfs1 192.168.1.10(rw,sync) 192.168.1.20(ro,sync)\n"
        "/srv/nfs2 192.168.1.30(rw,no_root_squash)\n"
    )


def calculate_expected_digests(content_string: str) -> dict:
    content_bytes = content_string.encode("utf-8")
    digests = {}
    for algo in ["sha256", "sha1", "md5"]:
        try:
            hasher = hashlib.new(algo)
            hasher.update(content_bytes)
            digests[algo] = hasher.hexdigest()
        except ValueError:
            pass
    return digests


def test_get_exports_ips_per_share(fake_exports_content: str) -> None:
    from ansible_collections.community.general.plugins.modules import nfs_exports_info
    from ansible_collections.community.internal_test_tools.tests.unit.compat import mock

    mock_module = mock.MagicMock()
    mock_module.params = {"output_format": "ips_per_share", "file_path": "/etc/exports"}
    mock_module.file_exists.return_value = True
    mock_module.warn.return_value = None
    mock_module.fail_json.side_effect = Exception("fail_json called")
    patch_target = "builtins.open" if sys.version_info[0] == 3 else "__builtin__.open"

    with mock.patch(patch_target, mock.mock_open(read_data=fake_exports_content)):
        result = nfs_exports_info.get_exports(mock_module)

    expected_info = {
        "/srv/nfs1": [
            {"ip": "192.168.1.10", "options": ["rw", "sync"]},
            {"ip": "192.168.1.20", "options": ["ro", "sync"]},
        ],
        "/srv/nfs2": [
            {"ip": "192.168.1.30", "options": ["rw", "no_root_squash"]}
        ],
    }

    expected_digests = calculate_expected_digests(fake_exports_content)
    assert result["exports_info"] == expected_info
    assert result["file_digest"] == expected_digests


def test_get_exports_shares_per_ip(fake_exports_content: str) -> None:
    from ansible_collections.community.general.plugins.modules import nfs_exports_info
    from ansible_collections.community.internal_test_tools.tests.unit.compat import mock

    mock_module = mock.MagicMock()
    mock_module.params = {"output_format": "shares_per_ip", "file_path": "/etc/exports"}
    mock_module.file_exists.return_value = True
    mock_module.warn.return_value = None
    mock_module.fail_json.side_effect = Exception("fail_json called")
    patch_target = "builtins.open" if sys.version_info[0] == 3 else "__builtin__.open"

    with mock.patch(patch_target, mock.mock_open(read_data=fake_exports_content)):
        result = nfs_exports_info.get_exports(mock_module)

    expected_info = {
        "192.168.1.10": [{"folder": "/srv/nfs1", "options": ["rw", "sync"]}],
        "192.168.1.20": [{"folder": "/srv/nfs1", "options": ["ro", "sync"]}],
        "192.168.1.30": [
            {"folder": "/srv/nfs2", "options": ["rw", "no_root_squash"]}
        ],
    }

    expected_digests = calculate_expected_digests(fake_exports_content)
    assert result["exports_info"] == expected_info
    assert result["file_digest"] == expected_digests

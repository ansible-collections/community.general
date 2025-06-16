# SPDX-FileCopyrightText: (c) 2025, Samaneh Yousefnezhad <s-yousefenzhad@um.ac.ir>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

try:
    from unittest.mock import mock_open, patch, MagicMock
except ImportError:

    from mock import mock_open, patch, MagicMock

import pytest
import sys
import os
import hashlib


sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../../plugins/modules')
))

from nfs_exports_info import get_exports


@pytest.fixture
def fake_exports_content():
    return """
# Sample exports
/srv/nfs1 192.168.1.10(rw,sync) 192.168.1.20(ro,sync)
/srv/nfs2 192.168.1.30(rw,no_root_squash)
"""


def calculate_expected_digests(content_string):
    content_bytes = content_string.encode('utf-8')
    digests = {}
    hash_algorithms = ['sha256', 'sha1', 'md5']
    for algo in hash_algorithms:
        try:
            hasher = hashlib.new(algo)
            hasher.update(content_bytes)
            digests[algo] = hasher.hexdigest()
        except ValueError:
            pass
    return digests


def test_get_exports_ips_per_share(fake_exports_content):
    mock_module = MagicMock()
    mock_module.file_exists.return_value = True
    mock_module.warn.return_value = None
    mock_module.fail_json.side_effect = Exception("fail_json called")
    patch_target = "builtins.open" if sys.version_info[0] == 3 else "__builtin__.open"

    with patch(patch_target, mock_open(read_data=fake_exports_content.encode('utf-8'))):
        result = get_exports(mock_module, "ips_per_share")

    expected_exports_info = {
        '/srv/nfs1': [
            {'ip': '192.168.1.10', 'options': ['rw', 'sync']},
            {'ip': '192.168.1.20', 'options': ['ro', 'sync']}
        ],
        '/srv/nfs2': [
            {'ip': '192.168.1.30', 'options': ['rw', 'no_root_squash']}
        ]
    }

    expected_file_digests = calculate_expected_digests(fake_exports_content)

    assert result['exports_info'] == expected_exports_info
    assert result['file_digest'] == expected_file_digests


def test_get_exports_shares_per_ip(fake_exports_content):
    mock_module = MagicMock()
    mock_module.file_exists.return_value = True
    mock_module.warn.return_value = None
    mock_module.fail_json.side_effect = Exception("fail_json called")
    patch_target = "builtins.open" if sys.version_info[0] == 3 else "__builtin__.open"

    with patch(patch_target, mock_open(read_data=fake_exports_content.encode('utf-8'))):
        result = get_exports(mock_module, "shares_per_ip")

    expected_exports_info = {
        '192.168.1.10': [
            {'folder': '/srv/nfs1', 'options': ['rw', 'sync']}
        ],
        '192.168.1.20': [
            {'folder': '/srv/nfs1', 'options': ['ro', 'sync']}
        ],
        '192.168.1.30': [
            {'folder': '/srv/nfs2', 'options': ['rw', 'no_root_squash']}
        ]
    }

    expected_file_digests = calculate_expected_digests(fake_exports_content)

    assert result['exports_info'] == expected_exports_info
    assert result['file_digest'] == expected_file_digests

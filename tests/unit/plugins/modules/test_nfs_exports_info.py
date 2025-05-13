from __future__ import absolute_import, division, print_function
__metaclass__ = type

try:
    from unittest.mock import mock_open, patch, MagicMock
except ImportError:
    from mock import mock_open, patch, MagicMock

import pytest
import sys
import os

# Add plugins/modules to path for direct import
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


def test_get_exports_ips_per_share(fake_exports_content):
    mock_module = MagicMock()
    mock_module.digest_from_file.return_value = "fake_sha1_digest"

    patch_target = "builtins.open" if sys.version_info[0] == 3 else "__builtin__.open"
    with patch(patch_target, mock_open(read_data=fake_exports_content)):
        result = get_exports(mock_module, "ips_per_share")

    expected = {
        '/srv/nfs1': [
            {'ip': '192.168.1.10', 'options': ['rw', 'sync']},
            {'ip': '192.168.1.20', 'options': ['ro', 'sync']}
        ],
        '/srv/nfs2': [
            {'ip': '192.168.1.30', 'options': ['rw', 'no_root_squash']}
        ]
    }

    assert result['exports_info'] == expected
    assert result['file_digest'] == "fake_sha1_digest"


def test_get_exports_shares_per_ip(fake_exports_content):
    mock_module = MagicMock()
    mock_module.digest_from_file.return_value = "fake_sha1_digest"

    patch_target = "builtins.open" if sys.version_info[0] == 3 else "__builtin__.open"
    with patch(patch_target, mock_open(read_data=fake_exports_content)):
        result = get_exports(mock_module, "shares_per_ip")

    expected = {
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

    assert result['exports_info'] == expected
    assert result['file_digest'] == "fake_sha1_digest"

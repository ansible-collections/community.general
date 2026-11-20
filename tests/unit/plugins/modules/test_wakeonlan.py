# Copyright (c) Contributors to the Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import patch

import pytest
from ansible.module_utils import basic
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    exit_json,
    fail_json,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import wakeonlan

MAC = "00:00:5e:00:53:01"
MAC_BYTES = bytes.fromhex("00005e005301")
MAGIC_PACKET_SIZE = 102


@pytest.fixture
def patch_module():
    with patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json):
        yield


@pytest.fixture
def mock_socket():
    with patch.object(wakeonlan.socket, "socket") as sock_cls:
        yield sock_cls.return_value


def test_magic_packet(patch_module, mock_socket):
    with set_module_args({"mac": MAC, "broadcast": "192.0.2.255", "port": 9}):
        with pytest.raises(AnsibleExitJson) as exc:
            wakeonlan.main()

    assert exc.value.args[0]["changed"] is True
    mock_socket.sendto.assert_called_once()
    data, address = mock_socket.sendto.call_args[0]
    assert address == ("192.0.2.255", 9)
    assert len(data) == MAGIC_PACKET_SIZE
    assert data == b"\xff" * 6 + MAC_BYTES * 16


def test_magic_packet_without_separators(patch_module, mock_socket):
    with set_module_args({"mac": "00005E005301"}):
        with pytest.raises(AnsibleExitJson):
            wakeonlan.main()

    data, address = mock_socket.sendto.call_args[0]
    assert address == ("255.255.255.255", 7)
    assert data == b"\xff" * 6 + MAC_BYTES * 16


def test_check_mode_does_not_send(patch_module, mock_socket):
    with set_module_args({"mac": MAC, "_ansible_check_mode": True}):
        with pytest.raises(AnsibleExitJson):
            wakeonlan.main()

    mock_socket.sendto.assert_not_called()


def test_invalid_mac(patch_module, mock_socket):
    with set_module_args({"mac": "00:00:5e:00:53:zz"}):
        with pytest.raises(AnsibleFailJson) as exc:
            wakeonlan.main()

    assert "Incorrect MAC address format" in exc.value.args[0]["msg"]

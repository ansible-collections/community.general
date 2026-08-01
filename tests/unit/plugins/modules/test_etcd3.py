# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.modules import etcd3 as etcd3_module

BASE_ARGS = {
    "key": "foo",
    "value": "bar",
    "state": "present",
    "host": "localhost",
    "port": 2379,
}


@pytest.fixture
def fake_etcd3(mocker):
    """Inject a mock etcd3 library into the module namespace and enable HAS_ETCD."""
    mock_lib = MagicMock()
    mocker.patch.object(etcd3_module, "etcd3", mock_lib, create=True)
    mocker.patch.object(etcd3_module, "HAS_ETCD", True)
    return mock_lib


def make_client(fake_etcd3, existing_value=None):
    """Configure fake_etcd3.client() to return a mock with get() returning the given value."""
    mock_client = MagicMock()
    if existing_value is not None:
        mock_client.get.return_value = (existing_value.encode(), MagicMock())
    else:
        mock_client.get.return_value = (None, None)
    fake_etcd3.client.return_value = mock_client
    return mock_client


# ---------------------------------------------------------------------------
# state=present
# ---------------------------------------------------------------------------


def test_present_new_key(capfd, fake_etcd3):
    """state=present with a new key: should put and report changed."""
    mock_client = make_client(fake_etcd3, existing_value=None)

    with pytest.raises(SystemExit), set_module_args(BASE_ARGS):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is True
    assert result["key"] == "foo"
    mock_client.put.assert_called_once_with("foo", "bar")


def test_present_same_value(capfd, fake_etcd3):
    """state=present with existing key and same value: no change."""
    mock_client = make_client(fake_etcd3, existing_value="bar")

    with pytest.raises(SystemExit), set_module_args(BASE_ARGS):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is False
    assert result["old_value"] == "bar"
    mock_client.put.assert_not_called()


def test_present_different_value(capfd, fake_etcd3):
    """state=present with existing key and different value: should put and report changed."""
    mock_client = make_client(fake_etcd3, existing_value="old_value")

    with pytest.raises(SystemExit), set_module_args(BASE_ARGS):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is True
    assert result["old_value"] == "old_value"
    mock_client.put.assert_called_once_with("foo", "bar")


# ---------------------------------------------------------------------------
# state=absent
# ---------------------------------------------------------------------------


def test_absent_existing_key(capfd, fake_etcd3):
    """state=absent with existing key: should delete and report changed."""
    mock_client = make_client(fake_etcd3, existing_value="bar")

    with pytest.raises(SystemExit), set_module_args(dict(BASE_ARGS, state="absent")):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is True
    mock_client.delete.assert_called_once_with("foo")


def test_absent_nonexistent_key(capfd, fake_etcd3):
    """state=absent with key not present: no change."""
    mock_client = make_client(fake_etcd3, existing_value=None)

    with pytest.raises(SystemExit), set_module_args(dict(BASE_ARGS, state="absent")):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is False
    mock_client.delete.assert_not_called()


# ---------------------------------------------------------------------------
# check mode
# ---------------------------------------------------------------------------


def test_present_check_mode_new_key(capfd, fake_etcd3):
    """state=present in check mode with new key: reports changed but no actual put."""
    mock_client = make_client(fake_etcd3, existing_value=None)

    with pytest.raises(SystemExit), set_module_args(dict(BASE_ARGS, _ansible_check_mode=True)):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is True
    mock_client.put.assert_not_called()


def test_present_check_mode_same_value(capfd, fake_etcd3):
    """state=present in check mode with same value: no change, no put."""
    mock_client = make_client(fake_etcd3, existing_value="bar")

    with pytest.raises(SystemExit), set_module_args(dict(BASE_ARGS, _ansible_check_mode=True)):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is False
    mock_client.put.assert_not_called()


def test_absent_check_mode_existing_key(capfd, fake_etcd3):
    """state=absent in check mode with existing key: reports changed but no actual delete."""
    mock_client = make_client(fake_etcd3, existing_value="bar")

    with pytest.raises(SystemExit), set_module_args(dict(BASE_ARGS, state="absent", _ansible_check_mode=True)):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is True
    mock_client.delete.assert_not_called()


def test_absent_check_mode_nonexistent_key(capfd, fake_etcd3):
    """state=absent in check mode with missing key: no change, no delete."""
    mock_client = make_client(fake_etcd3, existing_value=None)

    with pytest.raises(SystemExit), set_module_args(dict(BASE_ARGS, state="absent", _ansible_check_mode=True)):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is False
    mock_client.delete.assert_not_called()


# ---------------------------------------------------------------------------
# error paths
# ---------------------------------------------------------------------------


def test_connection_failure(capfd, fake_etcd3):
    """Connection to etcd cluster fails: module should fail."""
    fake_etcd3.client.side_effect = Exception("connection refused")

    with pytest.raises(SystemExit), set_module_args(BASE_ARGS):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["failed"] is True
    assert "Cannot connect to etcd cluster" in result["msg"]


def test_get_failure(capfd, fake_etcd3):
    """etcd.get() raises: module should fail."""
    mock_client = MagicMock()
    mock_client.get.side_effect = Exception("read timeout")
    fake_etcd3.client.return_value = mock_client

    with pytest.raises(SystemExit), set_module_args(BASE_ARGS):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["failed"] is True
    assert "Cannot reach data" in result["msg"]


def test_missing_library(capfd, mocker):
    """etcd3 library not installed: module should fail."""
    mocker.patch.object(etcd3_module, "HAS_ETCD", False)

    with pytest.raises(SystemExit), set_module_args(BASE_ARGS):
        etcd3_module.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert result["failed"] is True

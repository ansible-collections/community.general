# Copyright (c) 2025 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json

import pytest

from .FakeAnsibleModule import FakeAnsibleModule, FailJsonException
from ansible_collections.community.general.plugins.modules import xen_orchestra_instance


def _make_xo(module_params=None):
    if module_params is None:
        module_params = {}

    module = FakeAnsibleModule(params=module_params)
    xo = xen_orchestra_instance.XenOrchestra.__new__(xen_orchestra_instance.XenOrchestra)
    xo.module = module
    xo.counter = -1
    xo.conn = None
    return xo, module


def test_pointer_increments_sequentially():
    xo, mod = _make_xo()

    assert xo.pointer == 0
    assert xo.pointer == 1
    assert xo.pointer == 2


def test_login_success(mocker):
    xo, mod = _make_xo()
    mocker.patch.object(xo, "call", return_value={"result": {"token": "abc"}})

    result = xo.login("user", "password")

    assert result == {"token": "abc"}


def test_login_error_raises_fail_json(mocker):
    xo, module = _make_xo()
    mocker.patch.object(xo, "call", return_value={"error": {"message": "nope"}})

    with pytest.raises(FailJsonException) as exc:
        xo.login("user", "password")

    assert "Could not connect" in exc.value.args[0]


def test_create_vm_success(mocker):
    params = {
        "template": "tmpl-1",
        "label": "vm-label",
        "boot_after_create": True,
        "description": "some description",
    }
    xo, _ = _make_xo(params)
    mocker.patch.object(xo, "call", return_value={"result": "vm-uid-1"})

    result = xo.create_vm()

    xo.call.assert_called_once_with(
        "vm.create",
        {
            "template": "tmpl-1",
            "name_label": "vm-label",
            "bootAfterCreate": True,
            "name_description": "some description",
        },
    )
    assert result == "vm-uid-1"


def test_create_vm_error_raises_fail_json(mocker):
    params = {
        "template": "tmpl-1",
        "label": "vm-label",
    }
    xo, _ = _make_xo(params)
    mocker.patch.object(xo, "call", return_value={"error": {"message": "cannot create"}})

    with pytest.raises(FailJsonException) as exc:
        xo.create_vm()

    assert "Could not create vm" in exc.value.args[0]


@pytest.mark.parametrize(
    "method_name, rpc_method",
    [
        ("restart_vm", "vm.restart"),
        ("stop_vm", "vm.stop"),
        ("start_vm", "vm.start"),
        ("delete_vm", "vm.delete"),
    ],
)
def test_vm_actions_success(mocker, method_name, rpc_method):
    xo, mod = _make_xo()
    mock_call = mocker.patch.object(xo, "call", return_value={"result": True})

    method = getattr(xo, method_name)
    result = method("vm-uid-1")

    mock_call.assert_called_once_with(rpc_method, {"id": "vm-uid-1", **({"force": True} if rpc_method in {"vm.restart", "vm.stop"} else {})})
    assert result is True


@pytest.mark.parametrize(
    "method_name, code_constant, expected",
    [
        ("stop_vm", xen_orchestra_instance.VM_STATE_ERROR, False),
        ("start_vm", xen_orchestra_instance.VM_STATE_ERROR, False),
        ("delete_vm", xen_orchestra_instance.OBJECT_NOT_FOUND, False),
    ],
)
def test_vm_actions_special_error_codes_return_false(mocker, method_name, code_constant, expected):
    xo, mod = _make_xo()
    mocker.patch.object(xo, "call", return_value={"error": {"code": code_constant}})

    method = getattr(xo, method_name)
    result = method("vm-uid-1")

    assert result is expected


@pytest.mark.parametrize(
    "method_name, code_constant, error_snippet",
    [
        ("stop_vm", 999, "Could not stop vm"),
        ("start_vm", 999, "Could not start vm"),
        ("restart_vm", 999, "Could not restart vm"),
        ("delete_vm", 999, "Could not delete vm"),
    ],
)
def test_vm_actions_other_errors_raise_fail_json(mocker, method_name, code_constant, error_snippet):
    xo, mod = _make_xo()
    mocker.patch.object(xo, "call", return_value={"error": {"code": code_constant}})

    method = getattr(xo, method_name)

    with pytest.raises(FailJsonException) as exc:
        method("vm-uid-1")

    assert error_snippet in exc.value.args[0]


@pytest.mark.parametrize(
    "patch_ansible_module, method_name, state, expected_changed, extra_args",
    [
        (
            {
                "api_host": "xoa.local",
                "user": "user",
                "password": "pwd",
                "template": "tmpl-1",
                "label": "vm-label",
                "description": "desc",
            },
            "create_vm",
            "present",
            False,
            {"vm_uid": "vm-uid-1"},
        ),
        (
            {
                "api_host": "xoa.local",
                "user": "user",
                "password": "pwd",
                "vm_uid": "vm-uid-1",
                "state": "started",
            },
            "start_vm",
            "started",
            True,
            {},
        ),
        (
            {
                "api_host": "xoa.local",
                "user": "user",
                "password": "pwd",
                "vm_uid": "vm-uid-1",
                "state": "stopped",
            },
            "stop_vm",
            True,
            {},
        ),
        (
            {
                "api_host": "xoa.local",
                "user": "user",
                "password": "pwd",
                "vm_uid": "vm-uid-1",
                "state": "restarted",
            },
            "restart_vm",
            True,
            {},
        ),
        (
            {
                "api_host": "xoa.local",
                "user": "user",
                "password": "pwd",
                "vm_uid": "vm-uid-1",
                "state": "absent",
            },
            "delete_vm",
            True,
            {},
        ),
    ],
    ids=[
        "present-create-vm",
        "state-started",
        "state-stopped",
        "state-restarted",
        "state-absent",
    ],
    indirect=["patch_ansible_module"],
)
@pytest.mark.usefixtures("patch_ansible_module")
def test_main_state_dispatch(mocker, capfd, patch_ansible_module, method_name, state, expected_changed, extra_args):
    mocker.patch.object(xen_orchestra_instance, "HAS_WEBSOCKET", True)

    mock_xo_cls = mocker.patch.object(xen_orchestra_instance, "XenOrchestra")
    mock_xo = mock_xo_cls.return_value

    if state == "present":
        mock_xo.create_vm.return_value = "vm-uid-1"
    else:
        getattr(mock_xo, method_name).return_value = True

    with pytest.raises(SystemExit):
        xen_orchestra_instance.main()

    out, err = capfd.readouterr()
    result = json.loads(out)

    if state == "present":
        mock_xo.create_vm.assert_called_once_with()
        assert result["changed"] is expected_changed
        assert result["vm_uid"] == "vm-uid-1"
    else:
        getattr(mock_xo, method_name).assert_called_once_with("vm-uid-1")
        assert result["changed"] is expected_changed


@pytest.mark.parametrize(
    "patch_ansible_module",
    [
        {
            "api_host": "xoa.local",
            "user": "user",
            "password": "pwd",
        },
    ],
    ids=["missing-websocket"],
    indirect=True,
)
@pytest.mark.usefixtures("patch_ansible_module")
def test_main_missing_websocket_client(capfd, patch_ansible_module, monkeypatch):
    monkeypatch.setattr(xen_orchestra_instance, "HAS_WEBSOCKET", False)
    monkeypatch.setattr(xen_orchestra_instance, "WEBSOCKET_IMP_ERR", "import error")

    with pytest.raises(SystemExit):
        xen_orchestra_instance.main()

    out, err = capfd.readouterr()
    result = json.loads(out)

    assert result["failed"] is True
    assert "websocket-client" in result["msg"], result["msg"]

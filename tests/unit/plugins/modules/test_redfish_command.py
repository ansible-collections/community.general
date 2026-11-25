# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest
from ansible.module_utils import basic
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    exit_json,
    fail_json,
    set_module_args,
)

import ansible_collections.community.general.plugins.modules.redfish_command as module

ROOT_URI = "https://bmc.example.com"
MANAGER_URI = "/redfish/v1/Managers/BMC"
VIRTUAL_MEDIA_URI = f"{MANAGER_URI}/VirtualMedia"
CD_URI = f"{VIRTUAL_MEDIA_URI}/CD"
USB_URI = f"{VIRTUAL_MEDIA_URI}/USB"
FLOPPY_URI = f"{VIRTUAL_MEDIA_URI}/Floppy"
CD_IMAGE = "http://example.com/images/cd.iso"
USB_IMAGE = "http://example.com/images/usb.img"
CD_EJECT_TARGET = f"{CD_URI}/Actions/VirtualMedia.EjectMedia"


def slot(uri, image=None, with_eject_action=True):
    data = {"@odata.id": uri, "Image": image, "Inserted": image is not None}
    if with_eject_action:
        data["Actions"] = {"#VirtualMedia.EjectMedia": {"target": f"{uri}/Actions/VirtualMedia.EjectMedia"}}
    return data


SLOTS_INSERTED = {
    # ejected via the EjectMedia action
    CD_URI: slot(CD_URI, CD_IMAGE),
    # ejected via PATCH, no EjectMedia action
    USB_URI: slot(USB_URI, USB_IMAGE, with_eject_action=False),
    FLOPPY_URI: slot(FLOPPY_URI),
}

SLOTS_EMPTY = {
    CD_URI: slot(CD_URI),
    USB_URI: slot(USB_URI, with_eject_action=False),
}


def build_get_request(slots):
    responses = {
        f"{ROOT_URI}/redfish/v1/": {"Managers": {"@odata.id": "/redfish/v1/Managers"}},
        f"{ROOT_URI}/redfish/v1/Managers": {"Members": [{"@odata.id": MANAGER_URI}]},
        f"{ROOT_URI}{MANAGER_URI}": {
            "@odata.id": MANAGER_URI,
            "Id": "BMC",
            "VirtualMedia": {"@odata.id": VIRTUAL_MEDIA_URI},
        },
        f"{ROOT_URI}{VIRTUAL_MEDIA_URI}": {"Members": [{"@odata.id": uri} for uri in slots]},
    }
    responses.update({f"{ROOT_URI}{uri}": data for uri, data in slots.items()})

    def get_request(uri, *args, **kwargs):
        if uri in responses:
            return {"ret": True, "data": responses[uri], "headers": {}}
        return {"ret": False, "msg": f"HTTP Error 404 on GET request to '{uri}'", "status": 404}

    return get_request


@pytest.fixture
def patch_module(mocker):
    mocker.patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)


@pytest.fixture
def post_request(mocker):
    return mocker.patch.object(module.RedfishUtils, "post_request", return_value={"ret": True})


@pytest.fixture
def patch_request(mocker):
    return mocker.patch.object(module.RedfishUtils, "patch_request", return_value={"ret": True, "changed": True})


def mock_get_request(mocker, slots):
    mocker.patch.object(module.RedfishUtils, "get_request", side_effect=build_get_request(slots))


def module_args(command, **kwargs):
    args = {
        "category": "Manager",
        "command": [command],
        "baseuri": "bmc.example.com",
        "username": "root",
        "password": "secret",
        "resource_id": "BMC",
    }
    args.update(kwargs)
    return args


def test_eject_all_changed(mocker, patch_module, post_request, patch_request):
    mock_get_request(mocker, SLOTS_INSERTED)

    with set_module_args(module_args("VirtualMediaEjectAll")):
        with pytest.raises(AnsibleExitJson) as exc:
            module.main()

    assert exc.value.args[0]["changed"] is True
    post_request.assert_called_once_with(f"{ROOT_URI}{CD_EJECT_TARGET}", {})
    patch_request.assert_called_once_with(f"{ROOT_URI}{USB_URI}", {"Inserted": False, "Image": None}, check_pyld=True)


def test_eject_all_unchanged(mocker, patch_module, post_request, patch_request):
    mock_get_request(mocker, SLOTS_EMPTY)

    with set_module_args(module_args("VirtualMediaEjectAll")):
        with pytest.raises(AnsibleExitJson) as exc:
            module.main()

    assert exc.value.args[0]["changed"] is False
    post_request.assert_not_called()
    patch_request.assert_not_called()


def test_eject_all_failure_reports_ejected(mocker, patch_module, post_request, patch_request):
    mock_get_request(mocker, SLOTS_INSERTED)
    patch_request.return_value = {"ret": False, "changed": False, "msg": "Failed PATCH request"}

    with set_module_args(module_args("VirtualMediaEjectAll")):
        with pytest.raises(AnsibleFailJson) as exc:
            module.main()

    msg = exc.value.args[0]["msg"]
    assert "Failed PATCH request" in msg
    assert CD_IMAGE in msg
    post_request.assert_called_once_with(f"{ROOT_URI}{CD_EJECT_TARGET}", {})


def test_eject_by_image_url(mocker, patch_module, post_request, patch_request):
    mock_get_request(mocker, SLOTS_INSERTED)

    with set_module_args(module_args("VirtualMediaEject", virtual_media={"image_url": CD_IMAGE})):
        with pytest.raises(AnsibleExitJson) as exc:
            module.main()

    assert exc.value.args[0]["changed"] is True
    post_request.assert_called_once_with(f"{ROOT_URI}{CD_EJECT_TARGET}", {})
    patch_request.assert_not_called()

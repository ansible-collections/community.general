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

import ansible_collections.community.general.plugins.modules.idrac_redfish_config as module

ROOT_URI = "https://idrac.example.com"
MANAGER_URI = "/redfish/v1/Managers/iDRAC.Embedded.1"
DELL_ATTRIBUTES_URI = f"{MANAGER_URI}/Oem/Dell/DellAttributes"

COMMAND_ATTRIBUTES = {
    "SetManagerAttributes": (
        f"{DELL_ATTRIBUTES_URI}/iDRAC.Embedded.1",
        f"{MANAGER_URI}/Attributes",
        "Users.2.Enable",
    ),
    "SetLifecycleControllerAttributes": (
        f"{DELL_ATTRIBUTES_URI}/LifecycleController.Embedded.1",
        "/redfish/v1/Managers/LifecycleController.Embedded.1/Attributes",
        "LCAttributes.1.CollectSystemInventoryOnRestart",
    ),
    "SetSystemAttributes": (
        f"{DELL_ATTRIBUTES_URI}/System.Embedded.1",
        "/redfish/v1/Managers/System.Embedded.1/Attributes",
        "ServerOS.1.HostName",
    ),
}


def manager_data(with_links):
    data = {"@odata.id": MANAGER_URI, "Id": "iDRAC.Embedded.1"}
    if with_links:
        data["Links"] = {
            "Oem": {"Dell": {"DellAttributes": [{"@odata.id": uris[0]} for uris in COMMAND_ATTRIBUTES.values()]}}
        }
    return data


def build_get_request(attributes_uri, attributes, with_links=True):
    responses = {
        f"{ROOT_URI}/redfish/v1/": {"Managers": {"@odata.id": "/redfish/v1/Managers"}},
        f"{ROOT_URI}/redfish/v1/Managers": {"Members": [{"@odata.id": MANAGER_URI}]},
        f"{ROOT_URI}{MANAGER_URI}": manager_data(with_links),
        f"{ROOT_URI}{attributes_uri}": {"Attributes": attributes},
    }

    def get_request(uri, *args, **kwargs):
        if uri in responses:
            return {"ret": True, "data": responses[uri]}
        return {"ret": False, "msg": f"HTTP Error 404 on GET request to '{uri}'", "status": 404}

    return get_request


@pytest.fixture
def patch_module(mocker):
    mocker.patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)


@pytest.fixture
def patch_request(mocker):
    return mocker.patch.object(module.IdracRedfishUtils, "patch_request", return_value={"ret": True, "changed": True})


def module_args(command, attributes):
    return {
        "category": "Manager",
        "command": [command],
        "baseuri": "idrac.example.com",
        "username": "root",
        "password": "calvin",
        "manager_attributes": attributes,
    }


@pytest.mark.parametrize("with_links", [True, False], ids=["dell_attributes_links", "legacy_uri"])
@pytest.mark.parametrize("command", list(COMMAND_ATTRIBUTES))
def test_set_attributes_changed(mocker, patch_module, patch_request, command, with_links):
    dell_attributes_uri, legacy_uri, attr_name = COMMAND_ATTRIBUTES[command]
    attributes_uri = dell_attributes_uri if with_links else legacy_uri
    mocker.patch.object(
        module.IdracRedfishUtils,
        "get_request",
        side_effect=build_get_request(attributes_uri, {attr_name: "old"}, with_links=with_links),
    )

    with set_module_args(module_args(command, {attr_name: "new"})):
        with pytest.raises(AnsibleExitJson) as exc:
            module.main()

    assert exc.value.args[0]["changed"] is True
    patch_request.assert_called_once_with(f"{ROOT_URI}{attributes_uri}", {"Attributes": {attr_name: "new"}})


def test_set_attributes_unchanged(mocker, patch_module, patch_request):
    dell_attributes_uri = COMMAND_ATTRIBUTES["SetManagerAttributes"][0]
    attr_name = COMMAND_ATTRIBUTES["SetManagerAttributes"][2]
    mocker.patch.object(
        module.IdracRedfishUtils,
        "get_request",
        side_effect=build_get_request(dell_attributes_uri, {attr_name: "Enabled"}),
    )

    with set_module_args(module_args("SetManagerAttributes", {attr_name: "Enabled"})):
        with pytest.raises(AnsibleExitJson) as exc:
            module.main()

    assert exc.value.args[0]["changed"] is False
    patch_request.assert_not_called()


def test_set_attributes_not_found(mocker, patch_module, patch_request):
    # Neither the DellAttributes links nor the legacy URI are available
    mocker.patch.object(
        module.IdracRedfishUtils,
        "get_request",
        side_effect=build_get_request("/nonexistent", {}, with_links=False),
    )

    with set_module_args(module_args("SetManagerAttributes", {"Users.2.Enable": "Enabled"})):
        with pytest.raises(AnsibleFailJson) as exc:
            module.main()

    assert "404" in exc.value.args[0]["msg"]
    patch_request.assert_not_called()

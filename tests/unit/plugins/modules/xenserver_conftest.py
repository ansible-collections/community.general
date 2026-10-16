#
# Copyright (c) 2019, Bojan Vitnik <bvitnik@mainstream.rs>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import importlib

import pytest

from .FakeAnsibleModule import FakeAnsibleModule

XENSERVER_MODULE_UTILS_PATH = "ansible_collections.community.general.plugins.module_utils._xenserver"


@pytest.fixture
def fake_ansible_module(request):
    """Returns fake AnsibleModule with fake module params."""
    if hasattr(request, "param"):
        return FakeAnsibleModule(request.param)
    else:
        params = {
            "hostname": "somehost",
            "username": "someuser",
            "password": "somepwd",
            "validate_certs": True,
        }

        return FakeAnsibleModule(params)


@pytest.fixture(autouse=True)
def XenAPI(mocker):
    """Imports and returns fake XenAPI module."""

    # Import of fake XenAPI module is wrapped by fixture so that it does not
    # affect other unit tests which could potentially also use XenAPI module.
    fake_xenapi = importlib.import_module("ansible_collections.community.general.tests.unit.plugins.modules.FakeXenAPI")

    mocker.patch(f"{XENSERVER_MODULE_UTILS_PATH}.HAS_XENAPI", True)
    mocker.patch(f"{XENSERVER_MODULE_UTILS_PATH}.XenAPI", fake_xenapi, create=True)

    return fake_xenapi


@pytest.fixture
def xenserver_guest_info(XenAPI):
    """Imports and returns xenserver_guest_info module."""

    from ansible_collections.community.general.plugins.modules import xenserver_guest_info

    return xenserver_guest_info


@pytest.fixture
def xenserver_guest_powerstate(XenAPI):
    """Imports and returns xenserver_guest_powerstate module."""

    from ansible_collections.community.general.plugins.modules import xenserver_guest_powerstate

    return xenserver_guest_powerstate

# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.modules import ipa_host

FQDN = "client.example.com"

BASE_ARGS = {
    "fqdn": FQDN,
    "ipa_host": "ipa.example.com",
    "ipa_user": "admin",
    "ipa_pass": "topsecret",
}

OTP = "8Pj&0ddr;]B}r>pcb8tllp"


def ipa_host_entry(**attrs):
    entry = {
        "fqdn": [FQDN],
        "description": [FQDN],
        "dn": f"fqdn={FQDN},cn=computers,cn=accounts,dc=example,dc=com",
    }
    entry.update(attrs)
    return entry


@pytest.fixture
def post_json(mocker):
    mocker.patch.object(ipa_host.HostIPAClient, "login")
    return mocker.patch.object(ipa_host.HostIPAClient, "_post_json")


def run_module(capfd, post_json, args, existing_host, has_keytab=False, check_mode=False):
    def side_effect(method, name, item=None):
        if method == "host_find":
            return existing_host
        if method == "host_show":
            return ipa_host_entry(has_keytab=has_keytab, has_password=not has_keytab)
        if method in ("host_add", "host_mod"):
            response = {"fqdn": [name]}
            if item.get("random"):
                response["randompassword"] = OTP
            return response
        return {}

    post_json.side_effect = side_effect
    module_args = dict(BASE_ARGS, **args)
    if check_mode:
        module_args["_ansible_check_mode"] = True

    with pytest.raises(SystemExit), set_module_args(module_args):
        ipa_host.main()

    out, dummy = capfd.readouterr()
    return json.loads(out)


def called_methods(post_json):
    return [c.kwargs["method"] for c in post_json.call_args_list]


def test_present_unchanged_returns_password_attributes(capfd, post_json):
    result = run_module(capfd, post_json, {"description": FQDN}, ipa_host_entry())

    assert result["changed"] is False
    assert result["host"] == ipa_host_entry(has_keytab=False, has_password=True)
    assert called_methods(post_json) == ["host_find", "host_show"]


def test_present_random_password_existing_host(capfd, post_json):
    result = run_module(capfd, post_json, {"random_password": True}, ipa_host_entry(), has_keytab=True)

    assert result["changed"] is True
    assert result["host"] == ipa_host_entry(has_keytab=True, has_password=False, randompassword=OTP)
    assert called_methods(post_json) == ["host_find", "host_show", "host_disable", "host_mod", "host_show"]


@pytest.mark.parametrize(
    "random_password, expected_host",
    [
        (True, ipa_host_entry(has_keytab=False, has_password=True, randompassword=OTP)),
        (None, ipa_host_entry(has_keytab=False, has_password=True)),
    ],
)
def test_present_creates_host(capfd, post_json, random_password, expected_host):
    result = run_module(capfd, post_json, {"description": FQDN, "random_password": random_password}, {})

    assert result["changed"] is True
    assert result["host"] == expected_host
    assert called_methods(post_json) == ["host_find", "host_add", "host_show"]


def test_disabled_returns_host_after_disabling(capfd, post_json):
    result = run_module(capfd, post_json, {"state": "disabled"}, ipa_host_entry(), has_keytab=True)

    assert result["changed"] is True
    assert "has_keytab" in result["host"]
    assert called_methods(post_json) == ["host_find", "host_show", "host_disable", "host_show"]


def test_present_check_mode_changes_nothing(capfd, post_json):
    result = run_module(capfd, post_json, {"description": "new description"}, ipa_host_entry(), check_mode=True)

    assert result["changed"] is True
    assert result["host"] == ipa_host_entry(has_keytab=False, has_password=True)
    assert called_methods(post_json) == ["host_find", "host_show"]


def test_host_show_requests_all_attributes(capfd, post_json):
    run_module(capfd, post_json, {}, ipa_host_entry())

    show_calls = [c.kwargs for c in post_json.call_args_list if c.kwargs["method"] == "host_show"]
    assert show_calls == [{"method": "host_show", "name": FQDN, "item": {"all": True}}]

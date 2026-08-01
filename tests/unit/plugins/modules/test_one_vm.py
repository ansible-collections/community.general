# Copyright (c) 2023, Michal Opala <mopala@opennebula.io>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from collections import OrderedDict
from unittest.mock import MagicMock

import pytest

from ansible_collections.community.general.plugins.modules.one_vm import (
    _user_template_values_equal,
    check_update_attributes_values,
    parse_updateconf,
    update_vm_user_template,
    update_vms_user_template,
)

PARSE_UPDATECONF_VALID = [
    (
        {
            "CPU": 1,
            "OS": {"ARCH": 2},
        },
        {
            "OS": {"ARCH": 2},
        },
    ),
    (
        {
            "OS": {"ARCH": 1, "ASD": 2},  # "ASD" is an invalid attribute, we ignore it
        },
        {
            "OS": {"ARCH": 1},
        },
    ),
    (
        {
            "OS": {"ASD": 1},  # "ASD" is an invalid attribute, we ignore it
        },
        {},
    ),
    (
        {
            "MEMORY": 1,
            "CONTEXT": {
                "PASSWORD": 2,
                "SSH_PUBLIC_KEY": 3,
            },
        },
        {
            "CONTEXT": {
                "PASSWORD": 2,
                "SSH_PUBLIC_KEY": 3,
            },
        },
    ),
]


@pytest.mark.parametrize("vm_template,expected_result", PARSE_UPDATECONF_VALID)
def test_parse_updateconf(vm_template, expected_result):
    result = parse_updateconf(vm_template)
    assert result == expected_result, repr(result)


@pytest.mark.parametrize(
    "current,desired,expected",
    [
        (None, "head", False),
        ("head", "head", True),
        ("8080", 8080, True),
        (True, True, True),
        ("YES", True, False),  # str(True) is "True", not "YES"
        ({"A": "1"}, {"A": "1"}, True),
        ({"A": "1"}, {"A": "2"}, False),
    ],
)
def test_user_template_values_equal(current, desired, expected):
    assert _user_template_values_equal(current, desired) is expected


def test_check_update_attributes_values_rejects_null():
    module = MagicMock()

    check_update_attributes_values(module, {"SUBROLE": None})

    module.fail_json.assert_called_once()
    msg = module.fail_json.call_args.kwargs.get("msg") or module.fail_json.call_args[0][0]
    assert "cannot be null" in msg
    assert "SUBROLE" in msg


@pytest.mark.parametrize(
    "value,type_name",
    [
        (True, "bool"),
        (False, "bool"),
        (1.5, "float"),
        (["head"], "list"),
        ({"role": "head"}, "dict"),
    ],
)
def test_check_update_attributes_values_rejects_invalid_types(value, type_name):
    module = MagicMock()

    check_update_attributes_values(module, {"SUBROLE": value})

    module.fail_json.assert_called_once()
    msg = module.fail_json.call_args.kwargs.get("msg") or module.fail_json.call_args[0][0]
    assert "must be a string or integer" in msg
    assert "SUBROLE" in msg
    assert type_name in msg


@pytest.mark.parametrize("value", ["head", 8080])
def test_check_update_attributes_values_accepts_string_and_integer(value):
    module = MagicMock()

    check_update_attributes_values(module, {"SUBROLE": value})

    module.fail_json.assert_not_called()


def _module(check_mode=False):
    module = MagicMock()
    module.check_mode = check_mode
    return module


def _client_with_user_template(user_template, vm_id=42):
    client = MagicMock()
    info = MagicMock()
    info.USER_TEMPLATE = user_template
    client.vm.info.return_value = info
    vm = MagicMock()
    vm.ID = vm_id
    return client, vm


def test_update_vm_user_template_empty_dict_is_noop():
    module = _module()
    client, vm = _client_with_user_template({"ROLE": "k8s"})

    changed = update_vm_user_template(module, client, vm, {})

    assert changed is False
    client.vm.info.assert_not_called()
    client.vm.update.assert_not_called()


def test_update_vm_user_template_none_user_template_treated_as_empty():
    module = _module(check_mode=True)
    client, vm = _client_with_user_template(None)

    changed = update_vm_user_template(module, client, vm, {"SUBROLE": "head"})

    assert changed is True
    client.vm.update.assert_not_called()


def test_update_vm_user_template_check_mode_changed_when_missing():
    module = _module(check_mode=True)
    client, vm = _client_with_user_template({"ROLE": "k8s"})

    changed = update_vm_user_template(module, client, vm, {"SUBROLE": "head"})

    assert changed is True
    client.vm.update.assert_not_called()


def test_update_vm_user_template_check_mode_unchanged_when_match():
    module = _module(check_mode=True)
    client, vm = _client_with_user_template(OrderedDict([("SUBROLE", "head"), ("ROLE", "k8s")]))

    changed = update_vm_user_template(module, client, vm, {"SUBROLE": "head"})

    assert changed is False
    client.vm.update.assert_not_called()


def test_update_vm_user_template_live_calls_update_with_rendered_merge():
    module = _module(check_mode=False)
    client, vm = _client_with_user_template({"ROLE": "k8s"})

    changed = update_vm_user_template(module, client, vm, {"SUBROLE": "head"})

    assert changed is True
    client.vm.update.assert_called_once_with(42, 'SUBROLE="head"', 1)
    # Only the pre-flight info() call; no post-update info round-trip
    assert client.vm.info.call_count == 1


def test_update_vm_user_template_live_skips_api_when_already_match():
    module = _module(check_mode=False)
    client, vm = _client_with_user_template({"SUBROLE": "worker"})

    changed = update_vm_user_template(module, client, vm, {"SUBROLE": "worker"})

    assert changed is False
    client.vm.update.assert_not_called()


def test_update_vm_user_template_skips_api_when_int_matches_stored_string():
    module = _module(check_mode=False)
    client, vm = _client_with_user_template({"PORT": "8080"})

    changed = update_vm_user_template(module, client, vm, {"PORT": 8080})

    assert changed is False
    client.vm.update.assert_not_called()


def test_update_vms_user_template_any_changed():
    module = _module(check_mode=False)
    client = MagicMock()

    vm_a = MagicMock(ID=1)
    vm_b = MagicMock(ID=2)

    # First VM already has SUBROLE=head; second needs update
    info_a = MagicMock(USER_TEMPLATE={"SUBROLE": "head"})
    info_b_before = MagicMock(USER_TEMPLATE={})
    client.vm.info.side_effect = [info_a, info_b_before]

    changed = update_vms_user_template(module, client, [vm_a, vm_b], {"SUBROLE": "head"})

    assert changed is True
    assert client.vm.update.call_count == 1
    assert client.vm.update.call_args[0] == (2, 'SUBROLE="head"', 1)

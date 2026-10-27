# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import base64
import json

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.modules import ipa_user

BASE_ARGS = {
    "uid": "pinky",
    "ipa_host": "ipa.example.com",
    "ipa_user": "admin",
    "ipa_pass": "topsecret",
}

OLD_SSH_KEY = f"ssh-ed25519 {base64.b64encode(b'old-key').decode()} pinky@acme"
NEW_SSH_KEY = f"ssh-ed25519 {base64.b64encode(b'new-key').decode()} pinky@acme"


def ipa_user_entry(nsaccountlock=False, **attrs):
    entry = {
        "uid": ["pinky"],
        "givenname": ["Pinky"],
        "sn": ["Acme"],
        "loginshell": ["/bin/bash"],
        "nsaccountlock": nsaccountlock,
    }
    entry.update(attrs)
    return entry


@pytest.fixture
def post_json(mocker):
    mocker.patch.object(ipa_user.UserIPAClient, "login")
    return mocker.patch.object(ipa_user.UserIPAClient, "_post_json")


def run_module(capfd, post_json, args, existing_user, check_mode=False):
    def side_effect(method, name, item=None):
        if method == "user_find":
            return existing_user
        return {"uid": [name]}

    post_json.side_effect = side_effect
    module_args = dict(BASE_ARGS, **args)
    if check_mode:
        module_args["_ansible_check_mode"] = True

    with pytest.raises(SystemExit), set_module_args(module_args):
        ipa_user.main()

    out, dummy = capfd.readouterr()
    return json.loads(out)


def write_calls(post_json):
    return [c.kwargs for c in post_json.call_args_list if c.kwargs["method"] != "user_find"]


def test_present_modifies_only_changed_attributes(capfd, post_json):
    result = run_module(
        capfd,
        post_json,
        {"state": "present", "givenname": "Pinky", "loginshell": "/bin/zsh"},
        ipa_user_entry(),
    )

    assert result["changed"] is True
    assert write_calls(post_json) == [{"method": "user_mod", "name": "pinky", "item": {"loginshell": "/bin/zsh"}}]


def test_present_enables_disabled_user(capfd, post_json):
    result = run_module(
        capfd,
        post_json,
        {"state": "present", "loginshell": "/bin/zsh"},
        ipa_user_entry(nsaccountlock=True),
    )

    assert result["changed"] is True
    assert write_calls(post_json) == [
        {"method": "user_mod", "name": "pinky", "item": {"loginshell": "/bin/zsh", "nsaccountlock": False}}
    ]


def test_present_does_not_enable_disabled_user(capfd, post_json):
    result = run_module(
        capfd,
        post_json,
        {"state": "present", "enable_on_present": False, "loginshell": "/bin/zsh"},
        ipa_user_entry(nsaccountlock=True),
    )

    assert result["changed"] is True
    assert write_calls(post_json) == [{"method": "user_mod", "name": "pinky", "item": {"loginshell": "/bin/zsh"}}]


def test_present_disabled_user_unchanged(capfd, post_json):
    result = run_module(
        capfd,
        post_json,
        {"state": "present", "enable_on_present": False, "loginshell": "/bin/bash"},
        ipa_user_entry(nsaccountlock=True),
    )

    assert result["changed"] is False
    assert write_calls(post_json) == []


@pytest.mark.parametrize(
    "enable_on_present, expected_item",
    [
        (True, {"givenname": "Pinky", "nsaccountlock": False, "sn": "Acme"}),
        (False, {"givenname": "Pinky", "sn": "Acme"}),
    ],
)
def test_present_creates_user(capfd, post_json, enable_on_present, expected_item):
    result = run_module(
        capfd,
        post_json,
        {"state": "present", "enable_on_present": enable_on_present, "givenname": "Pinky", "sn": "Acme"},
        {},
    )

    assert result["changed"] is True
    assert write_calls(post_json) == [{"method": "user_add", "name": "pinky", "item": expected_item}]


@pytest.mark.parametrize(
    "state, current_lock, expected_lock",
    [
        ("enabled", True, False),
        ("disabled", False, True),
    ],
)
def test_enabled_disabled_change_nsaccountlock(capfd, post_json, state, current_lock, expected_lock):
    result = run_module(capfd, post_json, {"state": state}, ipa_user_entry(nsaccountlock=current_lock))

    assert result["changed"] is True
    assert write_calls(post_json) == [{"method": "user_mod", "name": "pinky", "item": {"nsaccountlock": expected_lock}}]


@pytest.mark.parametrize("state, current_lock", [("enabled", False), ("disabled", True)])
def test_enabled_disabled_unchanged(capfd, post_json, state, current_lock):
    result = run_module(capfd, post_json, {"state": state}, ipa_user_entry(nsaccountlock=current_lock))

    assert result["changed"] is False
    assert write_calls(post_json) == []


def test_sshpubkey_change_sends_keys(capfd, post_json):
    current = ipa_user_entry(sshpubkeyfp=[ipa_user.get_ssh_key_fingerprint(OLD_SSH_KEY)])
    result = run_module(
        capfd,
        post_json,
        {"state": "present", "loginshell": "/bin/bash", "sshpubkey": [NEW_SSH_KEY]},
        current,
    )

    assert result["changed"] is True
    assert write_calls(post_json) == [{"method": "user_mod", "name": "pinky", "item": {"ipasshpubkey": [NEW_SSH_KEY]}}]


def test_check_mode_does_not_modify(capfd, post_json):
    result = run_module(
        capfd,
        post_json,
        {"state": "present", "loginshell": "/bin/zsh"},
        ipa_user_entry(),
        check_mode=True,
    )

    assert result["changed"] is True
    assert write_calls(post_json) == []

# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json

import pytest

from ansible_collections.community.general.plugins.modules.homebrew_tap import (
    normalized_tap,
    set_trust,
    taps_to_change,
    trusted_taps,
)

BREW_PATH = "/usr/local/bin/brew"


def trust_output(*taps):
    """Builds the reply of `brew trust --json v1`."""
    return (0, json.dumps({"taps": list(taps), "formulae": [], "casks": [], "commands": []}), "")


def test_normalized_tap():
    assert normalized_tap("HasHicorp/TAp") == "hashicorp/tap"
    assert normalized_tap("telemachus/homebrew-brew") == "telemachus/brew"
    # Only the repository is prefixed with `homebrew-`, so a repository merely
    # containing that string keeps it.
    assert normalized_tap("telemachus/my-homebrew-tools") == "telemachus/my-homebrew-tools"


def test_trusted_taps(mocker):
    module = mocker.Mock()
    module.run_command.return_value = trust_output("hashicorp/tap", "telemachus/brew")

    assert trusted_taps(module, BREW_PATH) == {"hashicorp/tap", "telemachus/brew"}
    module.run_command.assert_called_once_with([BREW_PATH, "trust", "--json", "v1"])


def test_trusted_taps_requires_a_homebrew_providing_brew_trust(mocker):
    module = mocker.Mock()
    module.run_command.return_value = (1, "", "Unknown command: trust")
    module.fail_json.side_effect = SystemExit

    with pytest.raises(SystemExit):
        trusted_taps(module, BREW_PATH)

    assert "brew trust" in module.fail_json.call_args.kwargs["msg"]


@pytest.mark.parametrize(
    ("trust", "expected"),
    [
        (True, ["telemachus/homebrew-brew"]),
        (False, ["HasHicorp/TAp"]),
    ],
)
def test_taps_to_change_ignores_case_and_homebrew_prefix(mocker, trust, expected):
    module = mocker.Mock()
    module.run_command.return_value = trust_output("hashicorp/tap")

    taps = ["HasHicorp/TAp", "telemachus/homebrew-brew"]
    assert taps_to_change(module, BREW_PATH, taps, trust) == expected


def test_set_trust_does_nothing_when_already_trusted(mocker):
    module = mocker.Mock()
    module.check_mode = False
    module.run_command.return_value = trust_output("hashicorp/tap")

    assert set_trust(module, BREW_PATH, ["hashicorp/tap"], True) == (False, False, "trusted: 0, already trusted: 1")
    module.run_command.assert_called_once_with([BREW_PATH, "trust", "--json", "v1"])


def test_set_trust_only_passes_outstanding_taps(mocker):
    module = mocker.Mock()
    module.check_mode = False
    module.run_command.side_effect = [
        trust_output("hashicorp/tap"),
        (0, "Trusted tap: telemachus/brew", ""),
        trust_output("hashicorp/tap", "telemachus/brew"),
    ]

    taps = ["hashicorp/tap", "telemachus/brew"]
    assert set_trust(module, BREW_PATH, taps, True) == (False, True, "trusted: 1, already trusted: 1")
    assert module.run_command.call_args_list[1].args[0] == [BREW_PATH, "trust", "--tap", "telemachus/brew"]


def test_set_trust_untrusts(mocker):
    module = mocker.Mock()
    module.check_mode = False
    module.run_command.side_effect = [
        trust_output("hashicorp/tap"),
        (0, "Untrusted tap: hashicorp/tap", ""),
        trust_output(),
    ]

    assert set_trust(module, BREW_PATH, ["hashicorp/tap"], False) == (False, True, "untrusted: 1, already untrusted: 0")
    assert module.run_command.call_args_list[1].args[0] == [BREW_PATH, "untrust", "--tap", "hashicorp/tap"]


def test_set_trust_reports_a_tap_that_was_not_trusted(mocker):
    # `brew trust` exits successfully even when it changed nothing, so the
    # resulting state has to be read back.
    module = mocker.Mock()
    module.check_mode = False
    module.run_command.side_effect = [
        trust_output(),
        (0, "", "Warning: no such tap"),
        trust_output(),
    ]

    failed, changed, msg = set_trust(module, BREW_PATH, ["hashicorp/tap"], True)

    assert (failed, changed) == (True, False)
    assert "failed to trust: hashicorp/tap" in msg


def test_set_trust_in_check_mode_does_not_run_brew_trust(mocker):
    module = mocker.Mock()
    module.check_mode = True
    module.run_command.return_value = trust_output()
    module.exit_json.side_effect = SystemExit

    with pytest.raises(SystemExit):
        set_trust(module, BREW_PATH, ["hashicorp/tap"], True)

    module.exit_json.assert_called_once_with(changed=True)
    module.run_command.assert_called_once_with([BREW_PATH, "trust", "--json", "v1"])

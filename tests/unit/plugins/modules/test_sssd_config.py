# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.module_utils import _sssd_config
from ansible_collections.community.general.plugins.modules import sssd_config


@pytest.fixture
def config(mocker):
    config = mocker.Mock()
    config.opts = {"services": "nss"}
    config.has_section.return_value = True
    config.has_option.side_effect = lambda section, option: option in config.opts
    config.options.side_effect = lambda section: [{"name": name, "value": value} for name, value in config.opts.items()]
    config.strip_comments_empty.side_effect = lambda options: options
    config.set.side_effect = lambda section, option, value: config.opts.__setitem__(option, value)
    config.findOpts.return_value = (0, {"value": config.opts})
    config.delete_option_subtree.side_effect = lambda options, kind, name, all_matches: options.pop(name)

    section = config.get_service.return_value
    section.get_all_options.return_value = {"services": ["nss"], "config_file_version": 2}
    section.get_option.return_value = ["nss", "pam"]
    mocker.patch.object(_sssd_config, "SSSDConfig", create=True, return_value=config)
    with sssd_config.deps.declare("SSSDConfig"):
        pass
    yield config
    sssd_config.deps.clear()


@pytest.fixture
def run_module(capsys):
    def run(failed=False, **params):
        with set_module_args({"path": "/tmp/sssd-test.conf", **params}):
            with pytest.raises(SystemExit) as exc:
                sssd_config.main()
        assert exc.value.code == int(failed)
        result = json.loads(capsys.readouterr().out)
        assert result.get("failed", False) is failed
        return result

    return run


@pytest.mark.parametrize("check_mode", [False, True], ids=["apply", "check"])
def test_present_updates_existing_options(config, run_module, check_mode):
    result = run_module(options={"services": ["nss", "pam"]}, must_exist=True, _ansible_check_mode=check_mode)

    assert result["changed"] is True
    assert result["path"] == "/tmp/sssd-test.conf"
    assert result["section_name"] == "sssd"
    assert result["exists"] is True
    assert result["option_names"] == ["services"]
    assert not result.get("diff")
    config.import_config.assert_called_once_with("/tmp/sssd-test.conf")
    config.get_service.assert_called_once_with("sssd")
    config.set.assert_called_once_with("sssd", "services", "nss, pam")
    assert config.write.call_count == (0 if check_mode else 1)


def test_present_is_idempotent_after_normalization(config, run_module):
    config.get_service.return_value.get_option.return_value = ["nss"]

    result = run_module(options={"services": "nss"}, _ansible_diff=True)

    assert result["changed"] is False
    assert not result.get("diff")
    config.set.assert_not_called()
    config.write.assert_not_called()


@pytest.mark.parametrize("state", ["present", "absent"])
def test_empty_options_do_nothing(config, run_module, state):
    result = run_module(state=state, options={})

    assert result["changed"] is False
    assert config.opts == {"services": "nss"}
    config.write.assert_not_called()


def test_must_exist_rejects_an_implicit_default(config, run_module):
    result = run_module(failed=True, options={"config_file_version": 2}, must_exist=True)

    assert result["msg"] == "The following options must already exist: config_file_version"
    config.set.assert_not_called()
    config.write.assert_not_called()


@pytest.mark.parametrize("check_mode", [False, True], ids=["apply", "check"])
def test_absent_removes_only_requested_existing_options(config, run_module, check_mode):
    config.opts["debug_level"] = "0"
    result = run_module(
        state="absent",
        options={"debug_level": "ignored", "domains": None},
        _ansible_check_mode=check_mode,
        _ansible_diff=True,
    )

    assert result["changed"] is True
    assert result["option_names"] == ["services"]
    assert config.opts == {"services": "nss"}
    assert result["diff"]["before"]["option_names"] == ["debug_level", "services"]
    assert result["diff"]["after"]["option_names"] == ["services"]
    assert result["diff"]["after"]["changed_option_names"] == ["debug_level"]
    assert config.write.call_count == (0 if check_mode else 1)


def test_absent_is_idempotent_and_ignores_must_exist(config, run_module):
    result = run_module(state="absent", options={"domains": None}, must_exist=True)

    assert result["changed"] is False
    assert config.opts == {"services": "nss"}
    config.delete_option_subtree.assert_not_called()
    config.write.assert_not_called()


def test_diff_reports_added_and_updated_names_without_values(config, run_module):
    config.opts["domains"] = "old.example"
    section = config.get_service.return_value
    section.get_all_options.return_value = {"services": ["nss"], "domains": ["old.example"]}
    section.get_option.side_effect = {"domains": ["new.example"], "debug_level": 6}.__getitem__

    result = run_module(options={"domains": ["new.example"], "debug_level": 6}, _ansible_diff=True)

    assert result["changed"] is True
    assert result["diff"] == {
        "before": {
            "section_name": "sssd",
            "exists": True,
            "option_names": ["domains", "services"],
            "changed_option_names": [],
        },
        "after": {
            "section_name": "sssd",
            "exists": True,
            "option_names": ["debug_level", "domains", "services"],
            "changed_option_names": ["debug_level", "domains"],
        },
    }
    assert config.opts == {"services": "nss", "domains": "new.example", "debug_level": "6"}
    config.write.assert_called_once_with()


def test_missing_section_fails_without_writing(config, run_module):
    config.has_section.return_value = False

    result = run_module(failed=True, options={"services": ["nss"]})

    assert result["msg"] == "The sssd section does not exist"
    config.set.assert_not_called()
    config.write.assert_not_called()


def test_unreadable_configuration_fails_without_writing(config, run_module):
    config.import_config.side_effect = OSError("Cannot read configuration")

    result = run_module(failed=True, options={"services": ["nss"]})

    assert "Cannot read configuration" in result["msg"]
    config.set.assert_not_called()
    config.write.assert_not_called()


def test_invalid_option_value_fails_without_writing(config, run_module):
    config.get_service.return_value.set_option.side_effect = ValueError("Invalid debug_level")

    result = run_module(failed=True, options={"debug_level": "invalid"})

    assert "Invalid debug_level" in result["msg"]
    config.set.assert_not_called()
    config.write.assert_not_called()


def test_write_failure_is_reported(config, run_module):
    config.write.side_effect = OSError("Cannot write configuration")

    result = run_module(failed=True, options={"services": ["nss", "pam"]})

    assert "Cannot write configuration" in result["msg"]
    config.write.assert_called_once_with()


def test_missing_dependency_attempts_respawn_before_failing(config, run_module, mocker):
    with sssd_config.deps.declare("SSSDConfig"):
        raise ImportError("SSSDConfig is unavailable")
    respawn = mocker.patch.object(sssd_config, "_respawn_sssdconfig")

    result = run_module(failed=True, options={})

    assert "SSSDConfig" in result["msg"]
    respawn.assert_called_once_with()
    config.import_config.assert_not_called()
    config.write.assert_not_called()

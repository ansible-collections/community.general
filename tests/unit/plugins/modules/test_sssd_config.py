# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from ansible_collections.community.general.plugins.module_utils import (
    _sssd_config as sssd_config_utils,
)
from ansible_collections.community.general.plugins.modules import sssd_config


class ModuleRaisedError(Exception):
    """Stand-in exception used to stop execution after do_raise/fail_json."""


def make_helper(
    state="present",
    options=None,
    must_exist=False,
    path="/etc/sssd/sssd.conf",
    config=None,
    diff_mode=False,
):
    parsed_options = {} if options is None else options
    helper = object.__new__(sssd_config.SSSDConfigModule)
    helper.vars = SimpleNamespace(
        state=state,
        options=parsed_options,
        must_exist=must_exist,
        path=path,
    )
    helper.request = sssd_config._parse_request(
        state=state,
        path=path,
        options=parsed_options,
        must_exist=must_exist,
    )
    helper.sssd_config = config if config is not None else MagicMock()
    helper.module = MagicMock()
    helper.module._diff = diff_mode
    helper.changed = False
    helper.check_mode = False
    helper._result_diff = None
    return helper


class TestModuleDefinition(unittest.TestCase):
    def test_argument_spec_is_limited_to_the_sssd_section(self):
        argument_spec = sssd_config.SSSDConfigModule.module["argument_spec"]

        self.assertEqual(
            set(argument_spec),
            {"state", "must_exist", "path", "options"},
        )
        self.assertEqual(argument_spec["state"]["choices"], ["present", "absent"])
        self.assertEqual(argument_spec["state"]["default"], "present")
        self.assertFalse(argument_spec["must_exist"]["default"])
        self.assertEqual(argument_spec["path"]["default"], "/etc/sssd/sssd.conf")
        self.assertTrue(argument_spec["options"]["required"])
        self.assertTrue(sssd_config.SSSDConfigModule.module["supports_check_mode"])

    def test_section_name_and_activation_arguments_are_not_exposed(self):
        argument_spec = sssd_config.SSSDConfigModule.module["argument_spec"]

        self.assertNotIn("section", argument_spec)
        self.assertNotIn("name", argument_spec)
        self.assertNotIn("active", argument_spec)


class TestRequestParsing(unittest.TestCase):
    def test_present_arguments_become_ensure_present_request(self):
        request = sssd_config._parse_request(
            state="present",
            path="/tmp/sssd.conf",
            options={"services": ["nss", "pam"]},
            must_exist=True,
        )

        self.assertIsInstance(request, sssd_config_utils.EnsurePresent)
        self.assertEqual(request.target.path, "/tmp/sssd.conf")
        self.assertEqual(request.target.section, "sssd")
        self.assertIsNone(request.target.name)
        self.assertEqual(request.target.section_name, "sssd")
        self.assertEqual(request.options, {"services": ["nss", "pam"]})
        self.assertTrue(request.must_exist)
        self.assertIsNone(request.active)

    def test_present_options_are_copied(self):
        raw_options = {"services": ["nss", "pam"]}
        request = sssd_config._parse_request(
            state="present",
            path="/etc/sssd/sssd.conf",
            options=raw_options,
            must_exist=False,
        )

        raw_options["domains"] = ["example.com"]

        self.assertEqual(request.options, {"services": ["nss", "pam"]})

    def test_absent_arguments_become_remove_options_request(self):
        request = sssd_config._parse_request(
            state="absent",
            path="/tmp/sssd.conf",
            options={"debug_level": "ignored", "default_domain_suffix": None},
            must_exist=True,
        )

        self.assertIsInstance(request, sssd_config_utils.RemoveOptions)
        self.assertEqual(request.target.section_name, "sssd")
        self.assertEqual(
            request.option_names,
            ("debug_level", "default_domain_suffix"),
        )
        self.assertFalse(hasattr(request, "must_exist"))

    def test_absent_empty_mapping_is_remove_no_options(self):
        request = sssd_config._parse_request(
            state="absent",
            path="/etc/sssd/sssd.conf",
            options={},
            must_exist=False,
        )

        self.assertIsInstance(request, sssd_config_utils.RemoveOptions)
        self.assertEqual(request.option_names, ())


class TestModuleInitialization(unittest.TestCase):
    def test_missing_sssdconfig_library_fails(self):
        helper = make_helper(options={})
        helper.module.fail_json.side_effect = ModuleRaisedError

        with patch.object(sssd_config, "HAS_SSSD_LIB", False):
            with self.assertRaises(ModuleRaisedError):
                helper.__init_module__()

        kwargs = helper.module.fail_json.call_args.kwargs
        self.assertIn("SSSDConfig", kwargs["msg"])
        self.assertEqual(kwargs["exception"], sssd_config.SSSDCONFIG_IMPORT_ERROR)

    def test_initialization_imports_existing_sssd_configuration(self):
        helper = make_helper(
            path="/tmp/sssd.conf",
            options={"debug_level": 6},
        )
        config = MagicMock()
        config.has_section.return_value = True

        with patch.object(sssd_config, "HAS_SSSD_LIB", True):
            with patch.object(
                sssd_config,
                "create_sssd_config",
                return_value=config,
            ) as constructor:
                helper.__init_module__()

        constructor.assert_called_once_with()
        config.import_config.assert_called_once_with("/tmp/sssd.conf")
        config.has_section.assert_called_once_with("sssd")
        self.assertIs(helper.sssd_config, config)
        self.assertEqual(helper.request.options, {"debug_level": 6})

    def test_missing_sssd_section_fails(self):
        helper = make_helper(path="/tmp/sssd.conf", options={})
        helper.module.fail_json.side_effect = ModuleRaisedError
        config = MagicMock()
        config.has_section.return_value = False

        with patch.object(sssd_config, "HAS_SSSD_LIB", True):
            with patch.object(
                sssd_config,
                "create_sssd_config",
                return_value=config,
            ):
                with self.assertRaises(ModuleRaisedError):
                    helper.__init_module__()

        helper.module.fail_json.assert_called_once_with(msg="The sssd section does not exist")

    def test_initialization_captures_initial_diff_state_when_enabled(self):
        helper = make_helper(options={}, diff_mode=True)
        config = MagicMock()
        config.has_section.return_value = True
        before = {
            "section_name": "sssd",
            "exists": True,
            "option_names": ["services"],
        }
        before_options = {"services": "nss"}
        helper._get_diff_state = MagicMock(return_value=(before, before_options))

        with patch.object(sssd_config, "HAS_SSSD_LIB", True):
            with patch.object(
                sssd_config,
                "create_sssd_config",
                return_value=config,
            ):
                helper.__init_module__()

        helper._get_diff_state.assert_called_once_with()
        self.assertEqual(helper._diff_before, before)
        self.assertEqual(helper._diff_before_options, before_options)

    def test_initialization_skips_initial_diff_state_when_disabled(self):
        helper = make_helper(options={}, diff_mode=False)
        config = MagicMock()
        config.has_section.return_value = True
        helper._get_diff_state = MagicMock()

        with patch.object(sssd_config, "HAS_SSSD_LIB", True):
            with patch.object(
                sssd_config,
                "create_sssd_config",
                return_value=config,
            ):
                helper.__init_module__()

        helper._get_diff_state.assert_not_called()


class TestExplicitOptions(unittest.TestCase):
    def test_get_explicit_options_uses_sssd_target(self):
        helper = make_helper(options={})

        with patch.object(
            sssd_config,
            "get_explicit_options",
            return_value={"services": "nss, pam"},
        ) as get_options:
            result = helper._get_explicit_options()

        self.assertEqual(result, {"services": "nss, pam"})
        get_options.assert_called_once_with(helper.sssd_config, "sssd")


class TestStatePresent(unittest.TestCase):
    def test_must_exist_rejects_missing_options_in_sorted_order(self):
        helper = make_helper(
            options={
                "z_option": 1,
                "present_option": 2,
                "a_option": 3,
            },
            must_exist=True,
        )
        helper._get_explicit_options = MagicMock(return_value={"present_option": "2"})
        helper.do_raise = MagicMock(side_effect=ModuleRaisedError)

        with patch.object(sssd_config, "set_sssd_options") as set_options:
            with self.assertRaises(ModuleRaisedError):
                helper.state_present()

        helper.do_raise.assert_called_once_with("The following options must already exist: a_option, z_option")
        set_options.assert_not_called()
        self.assertFalse(helper.changed)

    def test_must_exist_allows_updating_explicit_options(self):
        requested_options = {"services": ["nss", "pam"]}
        helper = make_helper(
            options=requested_options,
            must_exist=True,
        )
        helper._get_explicit_options = MagicMock(return_value={"services": "nss"})

        with patch.object(
            sssd_config,
            "set_sssd_options",
            return_value=True,
        ) as set_options:
            helper.state_present()

        set_options.assert_called_once_with(
            helper.sssd_config,
            requested_options,
        )
        self.assertTrue(helper.changed)

    def test_changed_options_mark_module_changed(self):
        requested_options = {"debug_level": 6}
        helper = make_helper(options=requested_options)
        helper._get_explicit_options = MagicMock(return_value={})

        with patch.object(
            sssd_config,
            "set_sssd_options",
            return_value=True,
        ) as set_options:
            helper.state_present()

        set_options.assert_called_once_with(
            helper.sssd_config,
            requested_options,
        )
        self.assertTrue(helper.changed)

    def test_matching_options_are_idempotent(self):
        helper = make_helper(options={"debug_level": 6})
        helper._get_explicit_options = MagicMock(return_value={"debug_level": "6"})

        with patch.object(
            sssd_config,
            "set_sssd_options",
            return_value=False,
        ):
            helper.state_present()

        self.assertFalse(helper.changed)

    def test_state_handler_uses_parsed_request_instead_of_raw_arguments(self):
        helper = make_helper(options={"debug_level": 6})
        helper._get_explicit_options = MagicMock(return_value={})
        helper.vars = None

        with patch.object(
            sssd_config,
            "set_sssd_options",
            return_value=True,
        ) as set_options:
            helper.state_present()

        set_options.assert_called_once_with(
            helper.sssd_config,
            {"debug_level": 6},
        )


class TestStateAbsent(unittest.TestCase):
    def test_only_requested_explicit_options_are_removed(self):
        helper = make_helper(
            state="absent",
            options={
                "debug_level": "ignored",
                "default_domain_suffix": "ignored",
            },
        )
        helper._get_explicit_options = MagicMock(
            return_value={
                "debug_level": "6",
                "services": "nss, pam",
            }
        )

        with patch.object(
            sssd_config,
            "remove_sssd_options",
            return_value=True,
        ) as remove_options:
            helper.state_absent()

        remove_options.assert_called_once_with(
            helper.sssd_config,
            ("debug_level",),
        )
        self.assertTrue(helper.changed)

    def test_already_absent_options_are_idempotent(self):
        helper = make_helper(
            state="absent",
            options={"debug_level": "ignored"},
        )
        helper._get_explicit_options = MagicMock(return_value={"services": "nss, pam"})

        with patch.object(
            sssd_config,
            "remove_sssd_options",
            return_value=False,
        ) as remove_options:
            helper.state_absent()

        remove_options.assert_called_once_with(helper.sssd_config, ())
        self.assertFalse(helper.changed)

    def test_empty_options_mapping_is_idempotent(self):
        helper = make_helper(state="absent", options={})
        helper._get_explicit_options = MagicMock(return_value={"services": "nss, pam"})

        with patch.object(
            sssd_config,
            "remove_sssd_options",
            return_value=False,
        ) as remove_options:
            helper.state_absent()

        remove_options.assert_called_once_with(helper.sssd_config, ())
        self.assertFalse(helper.changed)

    def test_must_exist_has_no_effect_when_removing_options(self):
        helper = make_helper(
            state="absent",
            options={"missing_option": "ignored"},
            must_exist=True,
        )
        helper._get_explicit_options = MagicMock(return_value={})

        with patch.object(
            sssd_config,
            "remove_sssd_options",
            return_value=False,
        ) as remove_options:
            helper.state_absent()

        remove_options.assert_called_once_with(helper.sssd_config, ())
        self.assertFalse(helper.changed)

    def test_state_handler_uses_parsed_names_without_raw_arguments(self):
        helper = make_helper(
            state="absent",
            options={"debug_level": "ignored"},
        )
        helper._get_explicit_options = MagicMock(return_value={"debug_level": "6"})
        helper.vars = None

        with patch.object(
            sssd_config,
            "remove_sssd_options",
            return_value=True,
        ) as remove_options:
            helper.state_absent()

        remove_options.assert_called_once_with(
            helper.sssd_config,
            ("debug_level",),
        )


class TestDiffMode(unittest.TestCase):
    def test_get_diff_state_returns_explicit_option_names(self):
        helper = make_helper(options={}, diff_mode=True)
        explicit_options = {
            "services": "nss, pam",
            "config_file_version": "2",
        }
        helper._get_explicit_options = MagicMock(return_value=explicit_options)

        state, options = helper._get_diff_state()

        self.assertEqual(
            state,
            {
                "section_name": "sssd",
                "exists": True,
                "option_names": ["config_file_version", "services"],
            },
        )
        self.assertEqual(options, explicit_options)

    def test_set_diff_reports_added_removed_and_changed_option_names(self):
        helper = make_helper(options={}, diff_mode=True)
        helper._diff_before = {
            "section_name": "sssd",
            "exists": True,
            "option_names": ["domains", "old_option", "services"],
        }
        helper._diff_before_options = {
            "domains": "old.example.com",
            "old_option": "old-value",
            "services": "nss",
        }
        helper._get_diff_state = MagicMock(
            return_value=(
                {
                    "section_name": "sssd",
                    "exists": True,
                    "option_names": [
                        "config_file_version",
                        "domains",
                        "services",
                    ],
                },
                {
                    "config_file_version": "2",
                    "domains": "new.example.com",
                    "services": "nss",
                },
            )
        )
        helper._set_diff()

        self.assertEqual(
            helper._result_diff,
            {
                "before": {
                    "section_name": "sssd",
                    "exists": True,
                    "option_names": [
                        "domains",
                        "old_option",
                        "services",
                    ],
                    "changed_option_names": [],
                },
                "after": {
                    "section_name": "sssd",
                    "exists": True,
                    "option_names": [
                        "config_file_version",
                        "domains",
                        "services",
                    ],
                    "changed_option_names": [
                        "config_file_version",
                        "domains",
                        "old_option",
                    ],
                },
            },
        )

    def test_diff_does_not_expose_option_values(self):
        old_secret = "old-password"
        new_secret = "new-password"
        helper = make_helper(options={}, diff_mode=True)
        helper._diff_before = {
            "section_name": "sssd",
            "exists": True,
            "option_names": ["proxy_password"],
        }
        helper._diff_before_options = {"proxy_password": old_secret}
        helper._get_diff_state = MagicMock(
            return_value=(
                {
                    "section_name": "sssd",
                    "exists": True,
                    "option_names": ["proxy_password"],
                },
                {"proxy_password": new_secret},
            )
        )
        helper._set_diff()

        serialized_diff = json.dumps(helper._result_diff)
        self.assertNotIn(old_secret, serialized_diff)
        self.assertNotIn(new_secret, serialized_diff)

    def test_set_diff_omits_unchanged_state(self):
        helper = make_helper(options={}, diff_mode=True)
        state = {
            "section_name": "sssd",
            "exists": True,
            "option_names": ["services"],
        }
        options = {"services": "nss, pam"}
        helper._diff_before = state
        helper._diff_before_options = options
        helper._get_diff_state = MagicMock(return_value=(dict(state), dict(options)))
        helper._result_diff = {"stale": True}

        helper._set_diff()

        self.assertIsNone(helper._result_diff)

    def test_set_diff_does_nothing_when_diff_mode_is_disabled(self):
        helper = make_helper(options={}, diff_mode=False)
        helper._get_diff_state = MagicMock()
        helper._result_diff = {"stale": True}

        helper._set_diff()

        helper._get_diff_state.assert_not_called()
        self.assertIsNone(helper._result_diff)

    def test_output_merges_custom_diff_without_registering_reserved_name(self):
        helper = make_helper(options={}, diff_mode=True)
        helper.vars = MagicMock()
        helper.vars.output.return_value = {
            "path": "/etc/sssd/sssd.conf",
        }
        helper.vars.diff.return_value = None
        helper._result_diff = {
            "before": {"option_names": ["services"]},
            "after": {"option_names": ["debug_level", "services"]},
        }

        result = helper.output

        self.assertEqual(
            result,
            {
                "path": "/etc/sssd/sssd.conf",
                "diff": helper._result_diff,
            },
        )


class TestQuitModule(unittest.TestCase):
    def test_changed_configuration_is_written(self):
        helper = make_helper(options={})
        helper.changed = True
        helper._set_diff = MagicMock()
        helper._set_return_values = MagicMock()

        helper.__quit_module__()

        helper._set_diff.assert_called_once_with()
        helper.sssd_config.write.assert_called_once_with()
        helper._set_return_values.assert_called_once_with()

    def test_unchanged_configuration_is_not_written(self):
        helper = make_helper(options={})
        helper.changed = False
        helper._set_diff = MagicMock()
        helper._set_return_values = MagicMock()

        helper.__quit_module__()

        helper._set_diff.assert_called_once_with()
        helper.sssd_config.write.assert_not_called()
        helper._set_return_values.assert_called_once_with()

    def test_check_mode_does_not_write_changed_configuration(self):
        helper = make_helper(options={})
        helper.changed = True
        helper.check_mode = True
        helper._set_diff = MagicMock()
        helper._set_return_values = MagicMock()

        helper.__quit_module__()

        helper._set_diff.assert_called_once_with()
        helper.sssd_config.write.assert_not_called()
        helper._set_return_values.assert_called_once_with()


class TestReturnValues(unittest.TestCase):
    def test_output_params_contains_only_path(self):
        self.assertEqual(
            sssd_config.SSSDConfigModule.output_params,
            ("path",),
        )

    def test_return_values_describe_sssd_section(self):
        helper = make_helper(options={})
        helper._get_explicit_options = MagicMock(
            return_value={
                "services": "nss, pam",
                "config_file_version": "2",
            }
        )
        helper.update_output = MagicMock()

        helper._set_return_values()

        helper.update_output.assert_called_once_with(
            section_name="sssd",
            exists=True,
            option_names=["config_file_version", "services"],
        )


class TestMain(unittest.TestCase):
    def test_main_runs_module(self):
        module = MagicMock()

        with patch.object(
            sssd_config,
            "SSSDConfigModule",
            return_value=module,
        ):
            sssd_config.main()

        module.run.assert_called_once_with()

# Copyright (c) 2020, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from contextlib import contextmanager
from unittest.mock import call, patch

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import ipa_otpconfig


@contextmanager
def patch_ipa(**kwargs):
    """Mock context manager for patching the methods in OTPConfigIPAClient that contact the IPA server

    Patches the `login` and `_post_json` methods

    Keyword arguments are passed to the mock object that patches `_post_json`

    No arguments are passed to the mock object that patches `login` because no tests require it

    Example::

        with patch_ipa(return_value={}) as (mock_login, mock_post):
            ...
    """
    obj = ipa_otpconfig.OTPConfigIPAClient
    with patch.object(obj, "login") as mock_login:
        with patch.object(obj, "_post_json", **kwargs) as mock_post:
            yield mock_login, mock_post


class TestIPAOTPConfig(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.module = ipa_otpconfig

    def _test_base(self, module_args, return_value, mock_calls, changed):
        """Base function that's called by all the other test functions

        module_args (dict):
            Arguments passed to the module

        return_value (dict):
            Mocked return value of OTPConfigIPAClient.otpconfig_show, as returned by the IPA API.
            This should be set to the current state. It will be changed to the desired state using the above arguments.
            (Technically, this is the return value of _post_json, but it's only checked by otpconfig_show).

        mock_calls (list/tuple of dicts):
            List of calls made to OTPConfigIPAClient._post_json, in order.
            _post_json is called by all of the otpconfig_* methods of the class.
            Pass an empty list if no calls are expected.

        changed (bool):
            Whether or not the module is supposed to be marked as changed
        """

        # Run the module
        with set_module_args(module_args):
            with patch_ipa(return_value=return_value) as (mock_login, mock_post):
                with self.assertRaises(AnsibleExitJson) as exec_info:
                    self.module.main()

        # Verify that the calls to _post_json match what is expected
        expected_call_count = len(mock_calls)
        if expected_call_count > 1:
            # Convert the call dicts to unittest.mock.call instances because `assert_has_calls` only accepts them
            converted_calls = []
            for call_dict in mock_calls:
                converted_calls.append(call(**call_dict))

            mock_post.assert_has_calls(converted_calls)
            self.assertEqual(len(mock_post.mock_calls), expected_call_count)
        elif expected_call_count == 1:
            mock_post.assert_called_once_with(**mock_calls[0])
        else:  # expected_call_count is 0
            mock_post.assert_not_called()

        # Verify that the module's changed status matches what is expected
        self.assertIs(exec_info.exception.args[0]["changed"], changed)

    def test_set_all_no_adjustment(self):
        """Set values requiring no adjustment"""
        module_args = {
            "ipatokentotpauthwindow": 11,
            "ipatokentotpsyncwindow": 12,
            "ipatokenhotpauthwindow": 13,
            "ipatokenhotpsyncwindow": 14,
        }
        return_value = {
            "ipatokentotpauthwindow": ["11"],
            "ipatokentotpsyncwindow": ["12"],
            "ipatokenhotpauthwindow": ["13"],
            "ipatokenhotpsyncwindow": ["14"],
        }
        mock_calls = ({"method": "otpconfig_show", "name": None}, {"method": "otpconfig_show", "name": None})
        changed = False

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_set_all_aliases_no_adjustment(self):
        """Set values requiring no adjustment on all using aliases values"""
        module_args = {"totpauthwindow": 11, "totpsyncwindow": 12, "hotpauthwindow": 13, "hotpsyncwindow": 14}
        return_value = {
            "ipatokentotpauthwindow": ["11"],
            "ipatokentotpsyncwindow": ["12"],
            "ipatokenhotpauthwindow": ["13"],
            "ipatokenhotpsyncwindow": ["14"],
        }
        mock_calls = ({"method": "otpconfig_show", "name": None}, {"method": "otpconfig_show", "name": None})
        changed = False

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_set_totp_auth_window_no_adjustment(self):
        """Set values requiring no adjustment on totpauthwindow"""
        module_args = {"totpauthwindow": 11}
        return_value = {
            "ipatokentotpauthwindow": ["11"],
            "ipatokentotpsyncwindow": ["12"],
            "ipatokenhotpauthwindow": ["13"],
            "ipatokenhotpsyncwindow": ["14"],
        }
        mock_calls = ({"method": "otpconfig_show", "name": None}, {"method": "otpconfig_show", "name": None})
        changed = False

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_set_totp_sync_window_no_adjustment(self):
        """Set values requiring no adjustment on totpsyncwindow"""
        module_args = {"totpsyncwindow": 12}
        return_value = {
            "ipatokentotpauthwindow": ["11"],
            "ipatokentotpsyncwindow": ["12"],
            "ipatokenhotpauthwindow": ["13"],
            "ipatokenhotpsyncwindow": ["14"],
        }
        mock_calls = ({"method": "otpconfig_show", "name": None}, {"method": "otpconfig_show", "name": None})
        changed = False

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_set_hotp_auth_window_no_adjustment(self):
        """Set values requiring no adjustment on hotpauthwindow"""
        module_args = {"hotpauthwindow": 13}
        return_value = {
            "ipatokentotpauthwindow": ["11"],
            "ipatokentotpsyncwindow": ["12"],
            "ipatokenhotpauthwindow": ["13"],
            "ipatokenhotpsyncwindow": ["14"],
        }
        mock_calls = ({"method": "otpconfig_show", "name": None}, {"method": "otpconfig_show", "name": None})
        changed = False

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_set_hotp_sync_window_no_adjustment(self):
        """Set values requiring no adjustment on hotpsyncwindow"""
        module_args = {"hotpsyncwindow": 14}
        return_value = {
            "ipatokentotpauthwindow": ["11"],
            "ipatokentotpsyncwindow": ["12"],
            "ipatokenhotpauthwindow": ["13"],
            "ipatokenhotpsyncwindow": ["14"],
        }
        mock_calls = ({"method": "otpconfig_show", "name": None}, {"method": "otpconfig_show", "name": None})
        changed = False

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_set_totp_auth_window(self):
        """Set values requiring adjustment on totpauthwindow"""
        module_args = {"totpauthwindow": 10}
        return_value = {
            "ipatokentotpauthwindow": ["11"],
            "ipatokentotpsyncwindow": ["12"],
            "ipatokenhotpauthwindow": ["13"],
            "ipatokenhotpsyncwindow": ["14"],
        }
        mock_calls = (
            {"method": "otpconfig_show", "name": None},
            {"method": "otpconfig_mod", "name": None, "item": {"ipatokentotpauthwindow": "10"}},
            {"method": "otpconfig_show", "name": None},
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_set_totp_sync_window(self):
        """Set values requiring adjustment on totpsyncwindow"""
        module_args = {"totpsyncwindow": 10}
        return_value = {
            "ipatokentotpauthwindow": ["11"],
            "ipatokentotpsyncwindow": ["12"],
            "ipatokenhotpauthwindow": ["13"],
            "ipatokenhotpsyncwindow": ["14"],
        }
        mock_calls = (
            {"method": "otpconfig_show", "name": None},
            {"method": "otpconfig_mod", "name": None, "item": {"ipatokentotpsyncwindow": "10"}},
            {"method": "otpconfig_show", "name": None},
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_set_hotp_auth_window(self):
        """Set values requiring adjustment on hotpauthwindow"""
        module_args = {"hotpauthwindow": 10}
        return_value = {
            "ipatokentotpauthwindow": ["11"],
            "ipatokentotpsyncwindow": ["12"],
            "ipatokenhotpauthwindow": ["13"],
            "ipatokenhotpsyncwindow": ["14"],
        }
        mock_calls = (
            {"method": "otpconfig_show", "name": None},
            {"method": "otpconfig_mod", "name": None, "item": {"ipatokenhotpauthwindow": "10"}},
            {"method": "otpconfig_show", "name": None},
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_set_hotp_sync_window(self):
        """Set values requiring adjustment on hotpsyncwindow"""
        module_args = {"hotpsyncwindow": 10}
        return_value = {
            "ipatokentotpauthwindow": ["11"],
            "ipatokentotpsyncwindow": ["12"],
            "ipatokenhotpauthwindow": ["13"],
            "ipatokenhotpsyncwindow": ["14"],
        }
        mock_calls = (
            {"method": "otpconfig_show", "name": None},
            {"method": "otpconfig_mod", "name": None, "item": {"ipatokenhotpsyncwindow": "10"}},
            {"method": "otpconfig_show", "name": None},
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_set_all(self):
        """Set values requiring adjustment on all"""
        module_args = {
            "ipatokentotpauthwindow": 11,
            "ipatokentotpsyncwindow": 12,
            "ipatokenhotpauthwindow": 13,
            "ipatokenhotpsyncwindow": 14,
        }
        return_value = {
            "ipatokentotpauthwindow": ["1"],
            "ipatokentotpsyncwindow": ["2"],
            "ipatokenhotpauthwindow": ["3"],
            "ipatokenhotpsyncwindow": ["4"],
        }
        mock_calls = (
            {"method": "otpconfig_show", "name": None},
            {
                "method": "otpconfig_mod",
                "name": None,
                "item": {
                    "ipatokentotpauthwindow": "11",
                    "ipatokentotpsyncwindow": "12",
                    "ipatokenhotpauthwindow": "13",
                    "ipatokenhotpsyncwindow": "14",
                },
            },
            {"method": "otpconfig_show", "name": None},
        )
        changed = True

        self._test_base(module_args, return_value, mock_calls, changed)

    def test_fail_post(self):
        """Fail due to an exception raised from _post_json"""
        with set_module_args(
            {
                "ipatokentotpauthwindow": 11,
                "ipatokentotpsyncwindow": 12,
                "ipatokenhotpauthwindow": 13,
                "ipatokenhotpsyncwindow": 14,
            }
        ):
            with patch_ipa(side_effect=Exception("ERROR MESSAGE")) as (mock_login, mock_post):
                with self.assertRaises(AnsibleFailJson) as exec_info:
                    self.module.main()

        self.assertEqual(exec_info.exception.args[0]["msg"], "ERROR MESSAGE")


if __name__ == "__main__":
    unittest.main()

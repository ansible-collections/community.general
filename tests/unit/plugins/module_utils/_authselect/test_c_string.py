# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ctypes
import unittest
from unittest.mock import Mock

from ansible_collections.community.general.plugins.module_utils._authselect.c_string import (
    AllocatedCString,
)


class TestAllocatedCString(unittest.TestCase):
    def setUp(self):
        AllocatedCString._free = None

    def tearDown(self):
        AllocatedCString._free = None

    @staticmethod
    def make_string(value: str, encoding: str = "utf-8"):
        backing_buffer = ctypes.create_string_buffer(value.encode(encoding))
        pointer = ctypes.cast(backing_buffer, AllocatedCString)

        # The test owns this memory, so keep it alive while the pointer is used.
        pointer._test_backing_buffer = backing_buffer

        return pointer

    def test_decode_returns_python_string(self):
        value = self.make_string("authselect")

        self.assertEqual(value.decode(), "authselect")

    def test_decode_uses_utf8_by_default(self):
        value = self.make_string("mkhomedir-ü")

        self.assertEqual(value.decode(), "mkhomedir-ü")

    def test_decode_supports_requested_encoding(self):
        value = self.make_string("authselect", encoding="ascii")

        self.assertEqual(value.decode("ascii"), "authselect")

    def test_null_pointer_cannot_be_decoded(self):
        value = AllocatedCString()

        with self.assertRaisesRegex(
            RuntimeError,
            "AllocatedCString pointer is NULL",
        ):
            value.decode()

    def test_null_pointer_cannot_enter_context_manager(self):
        value = AllocatedCString()

        with self.assertRaisesRegex(
            RuntimeError,
            "AllocatedCString pointer is NULL",
        ):
            with value:
                pass

    def test_close_on_null_pointer_is_noop(self):
        value = AllocatedCString()

        value.close()

    def test_close_without_free_function_fails(self):
        value = self.make_string("authselect")

        with self.assertRaisesRegex(
            RuntimeError,
            "No free function configured for AllocatedCString",
        ):
            value.close()

    def test_close_calls_configured_free_function(self):
        free_function = Mock()
        AllocatedCString.set_free_function(free_function)
        value = self.make_string("authselect")

        value.close()

        free_function.assert_called_once_with(value)
        self.assertTrue(value._closed)

    def test_close_is_idempotent(self):
        free_function = Mock()
        AllocatedCString.set_free_function(free_function)
        value = self.make_string("authselect")

        value.close()
        value.close()

        free_function.assert_called_once_with(value)

    def test_closed_string_cannot_be_decoded(self):
        free_function = Mock()
        AllocatedCString.set_free_function(free_function)
        value = self.make_string("authselect")
        value.close()

        with self.assertRaisesRegex(
            RuntimeError,
            "AllocatedCString has already been freed",
        ):
            value.decode()

    def test_closed_string_cannot_enter_context_manager(self):
        free_function = Mock()
        AllocatedCString.set_free_function(free_function)
        value = self.make_string("authselect")
        value.close()

        with self.assertRaisesRegex(
            RuntimeError,
            "AllocatedCString has already been freed",
        ):
            with value:
                pass

    def test_context_manager_returns_same_string_and_frees_on_exit(self):
        free_function = Mock()
        AllocatedCString.set_free_function(free_function)
        value = self.make_string("authselect")

        with value as entered_value:
            self.assertIs(entered_value, value)
            self.assertEqual(entered_value.decode(), "authselect")
            free_function.assert_not_called()

        free_function.assert_called_once_with(value)
        self.assertTrue(value._closed)

    def test_context_manager_frees_string_when_body_raises(self):
        free_function = Mock()
        AllocatedCString.set_free_function(free_function)
        value = self.make_string("authselect")

        with self.assertRaisesRegex(RuntimeError, "test failure"):
            with value:
                raise RuntimeError("test failure")

        free_function.assert_called_once_with(value)
        self.assertTrue(value._closed)


if __name__ == "__main__":
    unittest.main()

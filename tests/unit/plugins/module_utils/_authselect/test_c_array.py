# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import ctypes
import gc
import unittest
from unittest.mock import Mock

from ansible_collections.community.general.plugins.module_utils._authselect.c_array import (
    CStringArray,
    NullTerminatedStringArray,
)


class TestCStringArray(unittest.TestCase):
    def test_from_strings_converts_strings_to_utf8_bytes(self):
        array = CStringArray.from_strings(
            [
                "with-faillock",
                "mkhomedir-ü",
            ]
        )

        self.assertEqual(array[0], b"with-faillock")
        self.assertEqual(array[1], "mkhomedir-ü".encode("utf-8"))

    def test_from_strings_adds_null_terminator(self):
        values = [
            "with-faillock",
            "with-mkhomedir",
        ]

        array = CStringArray.from_strings(values)

        self.assertIsNone(array[len(values)])

    def test_from_strings_empty_list_creates_null_terminated_empty_array(self):
        array = CStringArray.from_strings([])

        self.assertIsInstance(array, CStringArray)
        self.assertIsNone(array[0])

    def test_from_strings_keeps_backing_memory_alive(self):
        array = CStringArray.from_strings(
            [
                "with-faillock",
                "with-mkhomedir",
            ]
        )

        gc.collect()

        self.assertEqual(array[0], b"with-faillock")
        self.assertEqual(array[1], b"with-mkhomedir")
        self.assertIsNone(array[2])
        self.assertTrue(hasattr(array, "_backing_array"))
        self.assertTrue(hasattr(array, "_encoded_values"))


class TestNullTerminatedStringArray(unittest.TestCase):
    def setUp(self):
        NullTerminatedStringArray._free = None

    def tearDown(self):
        NullTerminatedStringArray._free = None

    @staticmethod
    def make_array(values):
        encoded_values = [value.encode("utf-8") for value in values]
        array_type = ctypes.c_char_p * (len(encoded_values) + 1)
        backing_array = array_type(*encoded_values, None)
        pointer = ctypes.cast(backing_array, NullTerminatedStringArray)

        # The test owns this memory, so keep it alive while the pointer is used.
        pointer._test_backing_array = backing_array

        return pointer

    def test_iter_decodes_strings_and_stops_at_null_terminator(self):
        array = self.make_array(
            [
                "with-faillock",
                "with-mkhomedir",
            ]
        )

        self.assertEqual(
            list(array),
            [
                "with-faillock",
                "with-mkhomedir",
            ],
        )

    def test_iter_decodes_utf8_strings(self):
        array = self.make_array(["mkhomedir-ü"])

        self.assertEqual(list(array), ["mkhomedir-ü"])

    def test_null_pointer_cannot_be_iterated(self):
        array = NullTerminatedStringArray()

        with self.assertRaisesRegex(
            RuntimeError,
            "NullTerminatedStringArray pointer is NULL",
        ):
            list(array)

    def test_null_pointer_cannot_enter_context_manager(self):
        array = NullTerminatedStringArray()

        with self.assertRaisesRegex(
            RuntimeError,
            "NullTerminatedStringArray pointer is NULL",
        ):
            with array:
                pass

    def test_close_on_null_pointer_is_noop(self):
        array = NullTerminatedStringArray()

        array.close()

    def test_close_without_free_function_fails(self):
        array = self.make_array(["with-faillock"])

        with self.assertRaisesRegex(
            RuntimeError,
            "No free function configured for NullTerminatedStringArray",
        ):
            array.close()

    def test_close_calls_configured_free_function(self):
        free_function = Mock()
        NullTerminatedStringArray.set_free_function(free_function)
        array = self.make_array(["with-faillock"])

        array.close()

        free_function.assert_called_once_with(array)
        self.assertTrue(array._closed)

    def test_close_is_idempotent(self):
        free_function = Mock()
        NullTerminatedStringArray.set_free_function(free_function)
        array = self.make_array(["with-faillock"])

        array.close()
        array.close()

        free_function.assert_called_once_with(array)

    def test_closed_array_cannot_be_iterated(self):
        free_function = Mock()
        NullTerminatedStringArray.set_free_function(free_function)
        array = self.make_array(["with-faillock"])
        array.close()

        with self.assertRaisesRegex(
            RuntimeError,
            "NullTerminatedStringArray has already been freed",
        ):
            list(array)

    def test_closed_array_cannot_enter_context_manager(self):
        free_function = Mock()
        NullTerminatedStringArray.set_free_function(free_function)
        array = self.make_array(["with-faillock"])
        array.close()

        with self.assertRaisesRegex(
            RuntimeError,
            "NullTerminatedStringArray has already been freed",
        ):
            with array:
                pass

    def test_context_manager_returns_same_array_and_frees_on_exit(self):
        free_function = Mock()
        NullTerminatedStringArray.set_free_function(free_function)
        array = self.make_array(["with-faillock"])

        with array as entered_array:
            self.assertIs(entered_array, array)
            self.assertEqual(list(entered_array), ["with-faillock"])
            free_function.assert_not_called()

        free_function.assert_called_once_with(array)
        self.assertTrue(array._closed)

    def test_context_manager_frees_array_when_body_raises(self):
        free_function = Mock()
        NullTerminatedStringArray.set_free_function(free_function)
        array = self.make_array(["with-faillock"])

        with self.assertRaisesRegex(RuntimeError, "test failure"):
            with array:
                raise RuntimeError("test failure")

        free_function.assert_called_once_with(array)
        self.assertTrue(array._closed)


if __name__ == "__main__":
    unittest.main()

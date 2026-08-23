from __future__ import annotations

import ctypes
from typing import Callable


class CStringArray(ctypes.POINTER(ctypes.c_char_p)):
    """
    Converts list[str] in Python to 'char **' in C
    """

    _type_ = ctypes.c_char_p

    @classmethod
    def from_strings(cls, values: list[str]) -> CStringArray:
        encoded_values = [value.encode("utf-8") for value in values]
        array_type = ctypes.c_char_p * (len(encoded_values) + 1)
        backing_array = array_type(*encoded_values, None)
        pointer = ctypes.cast(backing_array, cls)

        # Keep the objects that own the memory alive
        # for as long as this pointer exists.
        pointer._backing_array = backing_array
        pointer._encoded_values = encoded_values

        return pointer


class NullTerminatedStringArray(ctypes.POINTER(ctypes.c_char_p)):
    """
    Converts 'char **' from C to list[str] in Python
    """

    _type_ = ctypes.c_char_p

    _free: Callable[[NullTerminatedStringArray], None] | None = None

    @classmethod
    def set_free_function(cls, function: Callable[[NullTerminatedStringArray], None]) -> None:
        cls._free = function

    def __enter__(self):
        self._assert_valid()
        return self

    def __exit__(self, *args) -> None:
        self.close()
        return

    def _assert_valid(self) -> None:
        if not self:
            raise RuntimeError("NullTerminatedStringArray pointer is NULL")

        if getattr(self, "_closed", False):
            raise RuntimeError("NullTerminatedStringArray has already been freed")

    def close(self) -> None:
        if not self:
            return

        # Avoid possible double freeing.
        if getattr(self, "_closed", False):
            return

        if type(self)._free is None:
            raise RuntimeError(
                "No free function configured for NullTerminatedStringArray"
            )

        type(self)._free(self)
        self._closed = True

    def __iter__(self):
        self._assert_valid()
        index = 0
        while True:
            value = self[index]
            if value is None:
                return
            yield value.decode("utf-8")
            index += 1

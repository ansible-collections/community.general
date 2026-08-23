from __future__ import annotations

import ctypes
from typing import Callable


class AllocatedCString(ctypes.POINTER(ctypes.c_char)):
    """
    C-allocated 'char *' that must be manually freed.
    """

    _type_ = ctypes.c_char
    _free: Callable[[AllocatedCString], None] | None = None

    @classmethod
    def set_free_function(cls, function: Callable[[AllocatedCString], None]) -> None:
        cls._free = function

    def __enter__(self):
        self._assert_valid()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def _assert_valid(self) -> None:
        if not self:
            raise RuntimeError("AllocatedCString pointer is NULL")

        if getattr(self, "_closed", False):
            raise RuntimeError("AllocatedCString has already been freed")

    def close(self) -> None:
        if not self:
            return

        if getattr(self, "_closed", False):
            return

        if type(self)._free is None:
            raise RuntimeError("No free function configured for AllocatedCString")

        type(self)._free(self)
        self._closed = True

    def decode(self, encoding: str = "utf-8") -> str:
        self._assert_valid()
        return ctypes.string_at(self).decode(encoding)

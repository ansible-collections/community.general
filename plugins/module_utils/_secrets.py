# Copyright (c) 2026 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t
from collections.abc import Mapping, Sequence

try:
    from ansible.module_utils.secrets import register_secret  # type: ignore[import-not-found]

    HAS_SECRETS_API = True
except ImportError:
    HAS_SECRETS_API = False


def _mark_recursively(value: t.Any, *, int_to_string: bool = False) -> t.Any:
    if isinstance(value, Mapping):
        return {k: _mark_recursively(v, int_to_string=int_to_string) for k, v in value.items()}
    if isinstance(value, str):
        return register_secret(value)
    if isinstance(value, Sequence):
        return [_mark_recursively(v, int_to_string=int_to_string) for v in value]
    if int_to_string and isinstance(value, int):
        register_secret(str(value))
    return value


def mark_values_as_secrets(value: t.Any, *, int_to_string: bool = False) -> t.Any:
    """Register all strings appearing in the (potentially nested) data structure value secrets."""
    if HAS_SECRETS_API:
        value = _mark_recursively(value)
    return value


def mark_as_secret(value: str) -> str:
    """Register a string as a secret."""
    if HAS_SECRETS_API:
        value = register_secret(value)
    return value

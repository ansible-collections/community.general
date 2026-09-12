# Copyright (c) 2026 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t
from collections.abc import Mapping, Sequence

try:
    from ansible.module_utils.secrets import mask_secrets as _mask_secrets  # type: ignore[import-not-found]
    from ansible.module_utils.secrets import register_secret, register_secrets  # type: ignore[import-not-found]

    HAS_SECRETS_API = True
except ImportError:
    HAS_SECRETS_API = False

_T = t.TypeVar("_T")


def _collect_recursively(value: t.Any, collected_values: list[str], *, int_to_string: bool = False) -> None:
    if isinstance(value, Mapping):
        for v in value.items():
            _collect_recursively(v, collected_values, int_to_string=int_to_string)
    elif isinstance(value, str):
        collected_values.append(value)
    elif isinstance(value, Sequence):
        for v in value:
            _collect_recursively(v, collected_values, int_to_string=int_to_string)
    elif int_to_string and isinstance(value, int):
        collected_values.append(str(value))


def mark_values_as_secrets(value: _T, *, int_to_string: bool = False) -> _T:
    """Register all strings appearing in the (potentially nested) data structure ``value`` as secrets."""
    if HAS_SECRETS_API:
        collected_values: list[str] = []
        _collect_recursively(value, collected_values, int_to_string=int_to_string)
        if collected_values:
            register_secrets(collected_values)
    return value


def mark_as_secret(value: str) -> str:
    """Register a string as a secret."""
    if HAS_SECRETS_API:
        value = register_secret(value)
    return value


def mask_secrets(value: str, *, mask_placeholder="$REDACTED$") -> str:
    """Mask secrets in value."""
    if HAS_SECRETS_API:
        return _mask_secrets(value, mask_placeholder=mask_placeholder)
    return value


def _mask_recursively(value: t.Any, *, mask_placeholder: str) -> t.Any:
    if isinstance(value, Mapping):
        return {k: _mask_recursively(v, mask_placeholder=mask_placeholder) for k, v in value.items()}
    if isinstance(value, str):
        return _mask_secrets(value, mask_placeholder=mask_placeholder)
    if isinstance(value, Sequence):
        return [_mask_recursively(v, mask_placeholder=mask_placeholder) for v in value]
    return value


@t.overload
def mask_secret_values(value: dict[str, t.Any], *, mask_placeholder="$REDACTED$") -> dict[str, t.Any]: ...


@t.overload
def mask_secret_values(value: list[t.Any], *, mask_placeholder="$REDACTED$") -> list[t.Any]: ...


@t.overload
def mask_secret_values(value: t.Any, *, mask_placeholder="$REDACTED$") -> t.Any: ...


def mask_secret_values(value: t.Any, *, mask_placeholder="$REDACTED$") -> t.Any:
    """Mask secrets in the (potentially nested) data structure ``value``."""
    if HAS_SECRETS_API:
        return _mask_recursively(value, mask_placeholder=mask_placeholder)
    return value

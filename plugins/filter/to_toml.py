# Copyright (c) Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t
from collections.abc import Mapping, Set

try:
    from tomlkit import dumps
except ImportError as imp_exc:
    TOMLKIT_IMPORT_ERROR = imp_exc
else:
    TOMLKIT_IMPORT_ERROR = None

from ansible.errors import AnsibleRuntimeError, AnsibleError
from ansible.module_utils.common.collections import is_sequence

try:
    # This is ansible-core 2.19+
    from ansible.parsing.vault import VaultHelper, VaultLib
    from ansible.utils.vars import transform_to_native_types

    HAS_TRANSFORM_TO_NATIVE_TYPES = True
except ImportError:
    HAS_TRANSFORM_TO_NATIVE_TYPES = False

from ansible.parsing.yaml.objects import AnsibleVaultEncryptedUnicode
from ansible.utils.unsafe_proxy import AnsibleUnsafe


def _to_native_types_compat(value: t.Any, *, redact_value: str | None) -> t.Any:
    """Compatibility function for ansible-core 2.18 and before."""
    if value is None:
        return value
    if isinstance(value, AnsibleUnsafe):
        # This only works up to ansible-core 2.18:
        return _to_native_types_compat(value._strip_unsafe(), redact_value=redact_value)  # type: ignore
        # But that's fine, since this code path isn't taken on ansible-core 2.19+ anyway.
    if isinstance(value, Mapping):
        return {
            _to_native_types_compat(str(key), redact_value=redact_value): _to_native_types_compat(
                val, redact_value=redact_value
            )
            for key, val in value.items()
        }
    if isinstance(value, Set):
        return {_to_native_types_compat(elt, redact_value=redact_value) for elt in value}
    if is_sequence(value):
        return [_to_native_types_compat(elt, redact_value=redact_value) for elt in value]
    if isinstance(value, AnsibleVaultEncryptedUnicode):
        if redact_value is not None:
            return redact_value
        # This only works up to ansible-core 2.18:
        return value.data
        # But that's fine, since this code path isn't taken on ansible-core 2.19+ anyway.
    if isinstance(value, bytes):
        return bytes(value)
    if isinstance(value, str):
        return str(value)

    return value


def _to_native_types(value: t.Any, *, redact: bool) -> t.Any:
    if isinstance(value, Mapping):
        return {_to_native_types(str(k), redact=redact): _to_native_types(v, redact=redact) for k, v in value.items()}
    if is_sequence(value):
        return [_to_native_types(e, redact=redact) for e in value]
    if redact:
        ciphertext = VaultHelper.get_ciphertext(value, with_tags=False)
        if ciphertext and VaultLib.is_encrypted(ciphertext):
            return "<redacted>"
    return transform_to_native_types(value, redact=redact)


def remove_all_tags(value: t.Any, *, redact_sensitive_values: bool = False) -> t.Any:
    """
    Remove all tags from all values in the input.

    If ``redact_sensitive_values`` is ``True``, all sensitive values will be redacted.
    """
    if HAS_TRANSFORM_TO_NATIVE_TYPES:
        return _to_native_types(value, redact=redact_sensitive_values)

    return _to_native_types_compat(  # type: ignore[unreachable]
        value,
        redact_value="<redacted>"
        if redact_sensitive_values
        else None,  # same string as in ansible-core 2.19 by transform_to_native_types()
    )


def to_toml(value: t.Mapping, *, redact_sensitive_values: bool = False) -> str:
    """Serialize input as terse flow-style TOML."""
    if TOMLKIT_IMPORT_ERROR:
        raise AnsibleRuntimeError('tomlkit must be installed to use this plugin') from TOMLKIT_IMPORT_ERROR
    if not isinstance(value, Mapping):
        raise AnsibleError("to_toml only accepts dictionaries.")
    return dumps(
        remove_all_tags(value, redact_sensitive_values=redact_sensitive_values),
    )


class FilterModule:
    def filters(self):
        return {
            "to_toml": to_toml,
        }

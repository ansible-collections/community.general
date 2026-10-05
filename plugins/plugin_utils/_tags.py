# Copyright (c) Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this plugin util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import typing as t
from collections.abc import Mapping

from ansible.module_utils.common.collections import is_sequence
from ansible.parsing.vault import VaultHelper, VaultLib
from ansible.utils.vars import transform_to_native_types


def _to_native_types(value: t.Any, *, redact: bool) -> t.Any:
    if isinstance(value, Mapping):
        return {_to_native_types(k, redact=redact): _to_native_types(v, redact=redact) for k, v in value.items()}
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
    return _to_native_types(value, redact=redact_sensitive_values)

# Copyright (c) Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t
from collections.abc import Mapping

from ansible.module_utils.common.collections import is_sequence
from ansible.module_utils.common.text.converters import to_text

TOMLKIT_IMPORT_ERROR: ImportError | None
try:
    from tomlkit import dumps
except ImportError as imp_exc:
    TOMLKIT_IMPORT_ERROR = imp_exc
else:
    TOMLKIT_IMPORT_ERROR = None

from ansible.errors import AnsibleError, AnsibleFilterError

from ansible_collections.community.general.plugins.plugin_utils._tags import remove_all_tags


def _stringify_keys(value: t.Any) -> t.Any:
    """Recursively convert all keys to strings."""
    if isinstance(value, Mapping):
        return {to_text(k): _stringify_keys(v) for k, v in value.items()}
    if is_sequence(value):
        return [_stringify_keys(e) for e in value]
    return value


def to_toml(value: t.Mapping, *, redact_sensitive_values: bool = False) -> str:
    """Serialize input as TOML."""
    if TOMLKIT_IMPORT_ERROR:
        raise AnsibleError("tomlkit must be installed to use this plugin") from TOMLKIT_IMPORT_ERROR
    if not isinstance(value, Mapping):
        raise AnsibleFilterError("to_toml only accepts dictionaries.")
    return dumps(
        remove_all_tags(_stringify_keys(value), redact_sensitive_values=redact_sensitive_values),
    )


class FilterModule:
    def filters(self):
        return {
            "to_toml": to_toml,
        }

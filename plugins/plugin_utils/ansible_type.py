# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t
from collections.abc import Mapping

from ansible.errors import AnsibleFilterError

try:
    # Introduced with Data Tagging (https://github.com/ansible/ansible/pull/84621):
    from ansible.module_utils.datatag import native_type_name as _native_type_name

    HAS_NATIVE_TYPE_NAME = True
except ImportError:
    HAS_NATIVE_TYPE_NAME = False


def _atype(data: t.Any, alias: Mapping, *, use_native_type: bool = False) -> str:
    """
    Returns the name of the type class.
    """

    if use_native_type and HAS_NATIVE_TYPE_NAME:
        data_type = _native_type_name(data)
    else:
        data_type = type(data).__name__
    # The following types were introduced with Data Tagging (https://github.com/ansible/ansible/pull/84621):
    if data_type == "_AnsibleLazyTemplateDict":
        data_type = "dict"
    elif data_type == "_AnsibleLazyTemplateList":
        data_type = "list"
    return str(alias.get(data_type, data_type))


def _ansible_type(data: t.Any, alias: t.Any, *, use_native_type: bool = False) -> str:
    """
    Returns the Ansible data type.
    """

    if alias is None:
        alias = {}

    if not isinstance(alias, Mapping):
        raise AnsibleFilterError(f"The argument alias must be a dictionary. {alias!r} is {type(alias)}")

    data_type = _atype(data, alias, use_native_type=use_native_type)

    if data_type == "list" and len(data) > 0:
        items = {_atype(i, alias, use_native_type=use_native_type) for i in data}
        items_type = "|".join(sorted(items))
        return f"{data_type}[{items_type}]"

    if data_type == "dict" and len(data) > 0:
        keys = {_atype(i, alias, use_native_type=use_native_type) for i in data.keys()}
        vals = {_atype(i, alias, use_native_type=use_native_type) for i in data.values()}
        keys_type = "|".join(sorted(keys))
        vals_type = "|".join(sorted(vals))
        return f"{data_type}[{keys_type}, {vals_type}]"

    return data_type

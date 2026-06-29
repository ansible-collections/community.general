# Copyright (c) Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t

from yaml import dump

try:
    from yaml.cyaml import CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeDumper  # type: ignore

from ansible_collections.community.general.plugins.plugin_utils._tags import remove_all_tags


def to_yaml(
    value: t.Any, *, redact_sensitive_values: bool = False, default_flow_style: bool | None = None, **kwargs
) -> str:
    """Serialize input as terse flow-style YAML."""
    return dump(
        remove_all_tags(value, redact_sensitive_values=redact_sensitive_values),
        Dumper=SafeDumper,
        allow_unicode=True,
        default_flow_style=default_flow_style,
        **kwargs,
    )


def to_nice_yaml(
    value: t.Any, *, redact_sensitive_values: bool = False, indent: int = 2, default_flow_style: bool = False, **kwargs
) -> str:
    """Serialize input as verbose multi-line YAML."""
    return to_yaml(
        value,
        redact_sensitive_values=redact_sensitive_values,
        default_flow_style=default_flow_style,
        indent=indent,
        **kwargs,
    )


class FilterModule:
    def filters(self):
        return {
            "to_yaml": to_yaml,
            "to_nice_yaml": to_nice_yaml,
        }

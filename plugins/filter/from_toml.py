# Copyright (c) Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t
from collections.abc import Mapping

import tomllib
from ansible.errors import AnsibleFilterError


def from_toml(value: t.Any) -> Mapping:
    if not isinstance(value, str):
        raise AnsibleFilterError("from_toml only accepts strings.")
    return tomllib.loads(value)


class FilterModule:
    def filters(self):
        return {
            "from_toml": from_toml,
        }

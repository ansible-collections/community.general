# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:  # pragma: no cover
    from ansible_collections.community.general.plugins.module_utils._typing import ArgumentSpecT


def get_default_params(argspec: ArgumentSpecT) -> dict[str, t.Any]:
    result = {}
    for option, data in argspec.items():
        result[option] = data.get("default")
    return result

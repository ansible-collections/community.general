# Copyright (C) 2021 Eric Lavarde <elavarde@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re

from ansible_collections.community.general.plugins.module_utils._version import LooseVersion

_NATURAL_SORT_RE = re.compile(r"(\d+)")


def version_sort(value, reverse=False):
    """Sort a list according to loose versions so that e.g. 2.9 is smaller than 2.10"""
    return sorted(value, key=LooseVersion, reverse=reverse)


def _natural_sort_key(value: str) -> list[int | str]:
    return [int(chunk) if chunk.isdigit() else chunk for chunk in _NATURAL_SORT_RE.split(value)]


def version_sort_natural(value: list[str], reverse: bool = False) -> list[str]:
    """Sort a list of strings by natural version order, tolerating differing numbers of version components."""
    return sorted(value, key=_natural_sort_key, reverse=reverse)


class FilterModule:
    """Version sort filter"""

    def filters(self):
        return {
            "version_sort": version_sort,
            "version_sort_natural": version_sort_natural,
        }

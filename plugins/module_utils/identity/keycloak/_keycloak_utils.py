# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import typing as t


def merge_settings_without_absent_nulls(
    existing_settings: dict[str, t.Any], desired_settings: dict[str, t.Any]
) -> dict[str, t.Any]:
    """
    Merges existing and desired settings into a new dictionary while excluding null values in desired settings that are absent in the existing settings.
    This ensures idempotency by treating absent keys in existing settings and null values in desired settings as equivalent, preventing unnecessary updates.

    Args:
      existing_settings (dict): Dictionary representing the current settings in Keycloak
      desired_settings (dict): Dictionary representing the desired settings

    Returns:
      dict: A new dictionary containing all entries from existing_settings and desired_settings,
      excluding null values in desired_settings whose corresponding keys are not present in existing_settings
    """

    existing = existing_settings or {}
    desired = desired_settings or {}

    return {**existing, **{k: v for k, v in desired.items() if v is not None or k in existing}}

# Copyright (c) 2026, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this doc fragment is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations


class ModuleDocFragment:
    # Common parameters for Kopia modules
    DOCUMENTATION = r"""
options:
  password:
    description:
      - Repository password used to encrypt and decrypt repository contents.
    type: str
  config:
    description:
      - Path to the Kopia config file for this repository connection.
      - Defaults to the Kopia default config path when not set.
    type: path
"""

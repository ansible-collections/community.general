# Copyright: (c) 2025–2026, Eero Aaltonen
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
---
module: pgp_keyring
short_description: Install PGP keyrings in binary format
description: Converts PGP keyrings to binary format on the ansible controller,
    and installs them to the target systems.
version_added: 12.4.0
author: "Eero Aaltonen (@eaaltonen)"
options:
    src:
        description: Source key file (typically ASCII armored)
        required: true
        type: str
    dest:
        description: Destination key file. Can be relative, in which case the target system default is used
        required: true
        type: str
    follow:
        description: This flag indicates that filesystem links in the destination, if they exist, should be followed.
        type: bool
        default: false
"""

EXAMPLES = r"""
- name: Install Microsoft Package signing key
  community.general.pgp_keyring:
    src: microsoft.asc
    dest: microsoft.gpg
  become: true
"""

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Christoph Fiehe <christoph.fiehe@gmail.com>

# Note that this doc fragment is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations


class ModuleDocFragment:
    # Use together with ansible.builtin.url and icinga2_argument_spec from
    # ansible_collections.community.general.plugins.module_utils._icinga2
    DOCUMENTATION = r"""
options:
  url:
    description:
      - URL of the Icinga 2 REST API.
    type: str
    required: true
  ca_path:
    description:
      - CA certificates bundle to use to verify the Icinga 2 server certificate.
    type: path
  timeout:
    description:
      - How long to wait for the server to send data before giving up.
    type: int
    default: 10
"""

# Copyright (c) 2018, Oracle and/or its affiliates.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

#
# DEPRECATED
#
# This fragment is deprecated and will be removed in community.general 13.0.0
#


class ModuleDocFragment:
    DOCUMENTATION = r"""
options:
  force_create:
    description: Whether to attempt non-idempotent creation of a resource. By default, create resource is an idempotent operation,
      and does not create the resource if it already exists. Setting this option to V(true), forcefully creates a copy of
      the resource, even if it already exists. This option is mutually exclusive with O(key_by).
    default: false
    type: bool
  key_by:
    description: The list of comma-separated attributes of this resource which should be used to uniquely identify an instance
      of the resource. By default, all the attributes of a resource except O(freeform_tags) are used to uniquely identify
      a resource.
    type: list
    elements: str
"""

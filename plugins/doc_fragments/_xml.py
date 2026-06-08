# Copyright (c) 2014, Red Hat, Inc.
# Copyright (c) 2014, Tim Bielawa <tbielawa@redhat.com>
# Copyright (c) 2014, Magnus Hedemark <mhedemar@redhat.com>
# Copyright (c) 2017, Dag Wieers <dag@wieers.com>
# Copyright (c) 2026, Shreyash Bhosale <shreyashpb16@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this doc fragment is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations


class ModuleDocFragment:
    DOCUMENTATION = r"""
options:
  path:
    description:
      - Path to the file to operate on.
      - This file must exist ahead of time.
      - This parameter is required, unless O(xmlstring) is given.
    type: path
    aliases: [dest, file]
  xmlstring:
    description:
      - A string containing XML on which to operate.
      - This parameter is required, unless O(path) is given.
    type: str
  xpath:
    description:
      - A valid XPath expression describing the item(s) you want to operate on.
      - Operates on the document root, V(/), by default.
    type: str
  namespaces:
    description:
      - The namespace C(prefix:uri) mapping for the XPath expression.
      - Needs to be a C(dict), not a C(list) of items.
    type: dict
    default: {}
  strip_cdata_tags:
    description:
      - Remove CDATA tags surrounding text values.
      - Note that this might break your XML file if text values contain characters that could be interpreted as XML.
    type: bool
    default: false
  huge_tree:
    description:
      - Disable libxml2 security restrictions on XML node size or document depth, allowing processing of very large XML files.
      - This option should only be activated when needed, as it disables internal safety limits.
    type: bool
    default: false
requirements:
  - lxml >= 2.3.0
notes:
  - This module does not handle complicated xpath expressions, so limit xpath selectors to simple expressions.
  - Beware that in case your XML elements are namespaced, you need to use the O(namespaces) parameter, see the examples.
  - Namespaces prefix should be used for all children of an element where namespace is defined, unless another namespace is
    defined for them.
"""

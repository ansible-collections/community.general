# -*- coding: utf-8 -*-
# Copyright (c) 2018, Oracle and/or its affiliates.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = """
    options:
        name:
            description: Use O(name) along with the other options to return only resources that match the given name
                         exactly.
            type: str
    """

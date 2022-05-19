#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import sys
if sys.version_info.major > 2:
    from typing import Union

from ansible.module_utils.common.validation import (
    check_type_dict,
    check_type_list,
    string_types,
)


def check_type_dict_or_list(value):
    # type: (Union[dict, list, string_types]) -> dict
    """
    Verify that value is a dict or string that can be convertied to a dict or
    a list.
    """
    try:
        if isinstance(value, (list, dict)):
            return value
        elif (isinstance(value, string_types) and
              (value.startswith("{") or '=' in value)):
            return check_type_dict(value)
        else:
            return check_type_list(value)
    except TypeError:
        raise TypeError(
            '%s cannot be converted to dict or a list' % type(value))

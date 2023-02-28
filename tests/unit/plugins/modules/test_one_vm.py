# -*- coding: utf-8 -*-
# Copyright (c) 2023, Michal Opala <mopala@opennebula.io>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.modules.one_vm import parse_updateconf


PARSE_UPDATECONF_VALID = [
    (
        {
            "CPU": 1,
            "OS": {"ARCH": 2},
        },
        {
            "OS": {"ARCH": 2},
        }
    ),
    (
        {
            "OS": {"ARCH": 1, "ASD": 2},  # "ASD" is an invalid attribute, we ignore it
        },
        {
            "OS": {"ARCH": 1},
        }
    ),
    (
        {
            "OS": {"ASD": 1},  # "ASD" is an invalid attribute, we ignore it
        },
        {
        }
    ),
    (
        {
            "MEMORY": 1,
            "CONTEXT": {
                "PASSWORD": 2,
                "SSH_PUBLIC_KEY": 3,
            },
        },
        {
            "CONTEXT": {
                "PASSWORD": 2,
                "SSH_PUBLIC_KEY": 3,
            },
        }
    ),
]


@pytest.mark.parametrize('vm_template,expected_result', PARSE_UPDATECONF_VALID)
def test_parse_updateconf(vm_template, expected_result):
    result = parse_updateconf(vm_template)
    assert result == expected_result, repr(result)

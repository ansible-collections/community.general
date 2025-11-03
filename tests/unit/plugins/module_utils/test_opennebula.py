# Copyright (c) 2023, Michal Opala <mopala@opennebula.io>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import textwrap

import pytest

from ansible_collections.community.general.plugins.module_utils.opennebula import flatten, render


FLATTEN_VALID = [
    ([[[1]], [2], 3], False, [1, 2, 3]),
    ([[[1]], [2], 3], True, [1, 2, 3]),
    ([[1]], False, [1]),
    ([[1]], True, 1),
    (1, False, [1]),
    (1, True, 1),
]

RENDER_VALID = [
    (
        {
            "NIC": {"NAME": "NIC0", "NETWORK_ID": 0},
            "CPU": 1,
            "MEMORY": 1024,
        },
        textwrap.dedent("""
            CPU="1"
            MEMORY="1024"
            NIC=[NAME="NIC0",NETWORK_ID="0"]
        """).strip(),
    ),
    (
        {
            "NIC": [
                {"NAME": "NIC0", "NETWORK_ID": 0},
                {"NAME": "NIC1", "NETWORK_ID": 1},
            ],
            "CPU": 1,
            "MEMORY": 1024,
        },
        textwrap.dedent("""
            CPU="1"
            MEMORY="1024"
            NIC=[NAME="NIC0",NETWORK_ID="0"]
            NIC=[NAME="NIC1",NETWORK_ID="1"]
        """).strip(),
    ),
    (
        {
            "EMPTY_VALUE": None,
            "SCHED_REQUIREMENTS": 'CLUSTER_ID="100"',
            "BACKSLASH_ESCAPED": "this is escaped: \\n; this isn't: \"\nend",
        },
        textwrap.dedent("""
            BACKSLASH_ESCAPED="this is escaped: \\\\n; this isn't: \\"
            end"
            SCHED_REQUIREMENTS="CLUSTER_ID=\\"100\\""
        """).strip(),
    ),
]


@pytest.mark.parametrize("to_flatten,extract,expected_result", FLATTEN_VALID)
def test_flatten(to_flatten, extract, expected_result):
    result = flatten(to_flatten, extract)
    assert result == expected_result, repr(result)


@pytest.mark.parametrize("to_render,expected_result", RENDER_VALID)
def test_render(to_render, expected_result):
    result = render(to_render)
    assert result == expected_result, repr(result)

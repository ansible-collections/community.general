# Copyright (c) 2019, Andrey Tuzhilin <andrei.tuzhilin@gmail.com>
# Copyright (c) 2020, Andrew Klychkov (@Andersson007) <aaklychkov@mail.ru>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest

from ansible_collections.community.general.plugins.module_utils.saslprep import saslprep


VALID = [
    ("", ""),
    ("\u00a0", " "),
    ("a", "a"),
    ("й", "й"),
    ("\u30de\u30c8\u30ea\u30c3\u30af\u30b9", "\u30de\u30c8\u30ea\u30c3\u30af\u30b9"),
    ("The\u00adM\u00aatr\u2168", "TheMatrIX"),
    ("I\u00adX", "IX"),
    ("user", "user"),
    ("USER", "USER"),
    ("\u00aa", "a"),
    ("\u2168", "IX"),
    ("\u05be\u00a0\u05be", "\u05be\u0020\u05be"),
]

INVALID = [
    (None, TypeError),
    (b"", TypeError),
    ("\u0221", ValueError),
    ("\u0007", ValueError),
    ("\u0627\u0031", ValueError),
    ("\ue0001", ValueError),
    ("\ue0020", ValueError),
    ("\ufff9", ValueError),
    ("\ufdd0", ValueError),
    ("\u0000", ValueError),
    ("\u06dd", ValueError),
    ("\uffffD", ValueError),
    ("\ud800", ValueError),
    ("\u200e", ValueError),
    ("\u05be\u00aa\u05be", ValueError),
]


@pytest.mark.parametrize("source,target", VALID)
def test_saslprep_conversions(source, target):
    assert saslprep(source) == target


@pytest.mark.parametrize("source,exception", INVALID)
def test_saslprep_exceptions(source, exception):
    with pytest.raises(exception):
        saslprep(source)

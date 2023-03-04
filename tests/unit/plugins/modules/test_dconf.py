# Copyright (c) 2023 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.modules import dconf

try:
    from gi.repository.GLib import Variant
except ImportError:
    Variant = None

DconfPreference = dconf.DconfPreference


@pytest.mark.parametrize(
    "v1,v2,expected,fallback_expected",
    (("'foo'", "'foo'", True, True),
     ('"foo"', "'foo'", True, False),
     ("'foo'", '"foo"', True, False),
     ("'foo'", '"bar"', False, False),
     ("[1, 2, 3]", "[1, 2, 3]", True, True),
     ("[1, 2, 3]", "[3, 2, 1]", False, False),
     ('1234', '1234', True, True),
     ('1234', '1235', False, False),
     ('1.0', '1.0', True, True),
     ('1.000', '1.0', True, False),
     ('2.0', '4.0', False, False),
     # GVariants with different types aren't equal!
     ('1', '1.0', False, False),
     # Explicit types
     ('@as []', '[]', True, False),
     ))
def test_gvariant_equality(mocker, v1, v2, expected, fallback_expected):
    assert DconfPreference.variants_are_equal(v1, v2) is \
        (expected if Variant else fallback_expected)
    mocker.patch.object(dconf, 'Variant', None)
    mocker.patch.object(dconf, "GError", AttributeError)
    assert DconfPreference.variants_are_equal(v1, v2) is fallback_expected

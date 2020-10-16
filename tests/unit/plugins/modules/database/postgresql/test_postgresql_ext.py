# Copyright 2020, Andrew Klychkov @Andersson007 <aaklychkov@mail.ru>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.modules.database.postgresql.postgresql_ext import (
    parse_ext_versions,
)


@pytest.mark.parametrize(
    'current,test_input,expected',
    [
        (
            '2.0.0',
            [{'version': '3.1.0dev'}, {'version': '3.1.0devnext'}, {'version': 'unpackaged'}],
            ['3.1.0dev', '3.1.0devnext'],
        ),
        (
            '2.0.0',
            [{'version': 'unpackaged'}, {'version': '3.1.0dev'}, {'version': '3.1.0devnext'}],
            ['3.1.0dev', '3.1.0devnext'],
        ),
        (
            '2.0.1',
            [{'version': 'unpackaged'}, {'version': '2.0.0'}, {'version': '2.1.0dev'}],
            ['2.1.0dev'],
        ),
    ]
)
def test_parse_ext_versions(current, test_input, expected):
    assert parse_ext_versions(current, test_input) == expected

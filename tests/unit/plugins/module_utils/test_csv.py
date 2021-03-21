# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils import csv


VALID_CSV = [
    (
        'excel',
        {},
        None,
        "id,name,role\n1,foo,bar\n2,bar,baz",
        [
            {
                "id": "1",
                "name": "foo",
                "role": "bar",
            },
            {
                "id": "2",
                "name": "bar",
                "role": "baz",
            },
        ]
    ),
    (
        'excel',
        {"skipinitialspace": True},
        None,
        "id,name,role\n1, foo, bar\n2, bar, baz",
        [
            {
                "id": "1",
                "name": "foo",
                "role": "bar",
            },
            {
                "id": "2",
                "name": "bar",
                "role": "baz",
            },
        ]
    ),
    (
        'excel',
        {"delimiter": '|'},
        None,
        "id|name|role\n1|foo|bar\n2|bar|baz",
        [
            {
                "id": "1",
                "name": "foo",
                "role": "bar",
            },
            {
                "id": "2",
                "name": "bar",
                "role": "baz",
            },
        ]
    ),
    (
        'unix',
        {},
        None,
        "id,name,role\n1,foo,bar\n2,bar,baz",
        [
            {
                "id": "1",
                "name": "foo",
                "role": "bar",
            },
            {
                "id": "2",
                "name": "bar",
                "role": "baz",
            },
        ]
    ),
    (
        'excel',
        {},
        ['id', 'name', 'role'],
        "1,foo,bar\n2,bar,baz",
        [
            {
                "id": "1",
                "name": "foo",
                "role": "bar",
            },
            {
                "id": "2",
                "name": "bar",
                "role": "baz",
            },
        ]
    ),
]

INVALID_CSV = [
    (
        'excel',
        {'strict': True},
        None,
        'id,name,role\n1,"f"oo",bar\n2,bar,baz',
    ),
]

INVALID_DIALECT = [
    (
        'invalid',
        {},
        None,
        "id,name,role\n1,foo,bar\n2,bar,baz",
    ),
]


@pytest.mark.parametrize("dialect,dialect_params,fieldnames,data,expected", VALID_CSV)
def test_valid_csv(data, dialect, dialect_params, fieldnames, expected):
    dialect = csv.initialize_dialect(dialect, **dialect_params)
    reader = csv.read_csv(data, dialect, fieldnames)
    result = True

    for idx, row in enumerate(reader):
        for k, v in row.items():
            if expected[idx][k] != v:
                result = False
                break

    assert result


@pytest.mark.parametrize("dialect,dialect_params,fieldnames,data", INVALID_CSV)
def test_invalid_csv(data, dialect, dialect_params, fieldnames):
    dialect = csv.initialize_dialect(dialect, **dialect_params)
    reader = csv.read_csv(data, dialect, fieldnames)
    result = False

    try:
        for row in reader:
            continue
    except csv.CSVError:
        result = True

    assert result


@pytest.mark.parametrize("dialect,dialect_params,fieldnames,data", INVALID_DIALECT)
def test_invalid_dialect(data, dialect, dialect_params, fieldnames):
    result = False

    try:
        dialect = csv.initialize_dialect(dialect, **dialect_params)
    except csv.DialectNotAvailableError:
        result = True

    assert result

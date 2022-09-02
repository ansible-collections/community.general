# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import itertools
import json
import pytest

from .conftest import OP_VERSION_FIXTURES


from ansible.errors import AnsibleLookupError
from ansible_collections.community.general.plugins.lookup.onepassword import (
    LookupModule,
    OnePassCLIv1,
    OnePassCLIv2,
)

# Intentionally excludes metadata leaf nodes that would exist in real output if not relevant.
MOCK_ENTRIES = {
    OnePassCLIv1: [
        {
            'vault_name': 'Acme "Quot\'d" Servers',
            'queries': [
                '0123456789',
                'Mock "Quot\'d" Server'
            ],
            'expected': ['t0pS3cret', 't0pS3cret'],
            'output': {
                'uuid': '0123456789',
                'vaultUuid': '2468',
                'overview': {
                    'title': 'Mock "Quot\'d" Server'
                },
                'details': {
                    'sections': [{
                        'title': '',
                        'fields': [
                            {'t': 'username', 'v': 'jamesbond'},
                            {'t': 'password', 'v': 't0pS3cret'},
                            {'t': 'notes', 'v': 'Test note with\nmultiple lines and trailing space.\n\n'},
                            {'t': 'tricksy "quot\'d" field\\', 'v': '"quot\'d" value'}
                        ]
                    }]
                }
            }
        },
        {
            'vault_name': 'Acme Logins',
            'queries': [
                '9876543210',
                'Mock Website',
                'acme.com'
            ],
            'expected': ['t0pS3cret', 't0pS3cret', 't0pS3cret'],
            'output': {
                'uuid': '9876543210',
                'vaultUuid': '1357',
                'overview': {
                    'title': 'Mock Website',
                    'URLs': [
                        {'l': 'website', 'u': 'https://acme.com/login'}
                    ]
                },
                'details': {
                    'sections': [{
                        'title': '',
                        'fields': [
                            {'t': 'password', 'v': 't0pS3cret'}
                        ]
                    }]
                }
            }
        },
        {
            'vault_name': 'Acme Logins',
            'queries': [
                '864201357'
            ],
            'expected': ['vauxhall'],
            'output': {
                'uuid': '864201357',
                'vaultUuid': '1357',
                'overview': {
                    'title': 'Mock Something'
                },
                'details': {
                    'fields': [
                        {
                            'value': 'jbond@mi6.gov.uk',
                            'name': 'emailAddress'
                        },
                        {
                            'name': 'password',
                            'value': 'vauxhall'
                        },
                        {},
                    ]
                }
            }
        },
    ],
    OnePassCLIv2: [
        {
            "vault_name": "Test Vault",
            "queries": [
                "ywvdbojsguzgrgnokmcxtydgdv",
                "Authy Backup",
            ],
            "expected": ["OctoberPoppyNuttyDraperySabbath", "OctoberPoppyNuttyDraperySabbath"],
            "output": {
                "id": "ywvdbojsguzgrgnokmcxtydgdv",
                "title": "Authy Backup",
                "version": 1,
                "vault": {
                    "id": "bcqxysvcnejjrwzoqrwzcqjqxc",
                    "name": "test vault"
                },
                "category": "PASSWORD",
                "last_edited_by": "7FUPZ8ZNE02KSHMAIMKHIVUE17",
                "created_at": "2015-01-18T13:13:38Z",
                "updated_at": "2016-02-20T16:23:54Z",
                "additional_information": "Jan 18, 2015, 08:13:38",
                "fields": [
                    {
                        "id": "password",
                        "type": "CONCEALED",
                        "purpose": "PASSWORD",
                        "label": "password",
                        "value": "OctoberPoppyNuttyDraperySabbath",
                        "reference": "op://Test Vault/Authy Backup/password",
                        "password_details": {
                            "strength": "FANTASTIC"
                        }
                    },
                    {
                        "id": "notesPlain",
                        "type": "STRING",
                        "purpose": "NOTES",
                        "label": "notesPlain",
                        "value": "Backup password to restore Authy",
                        "reference": "op://Test Vault/Authy Backup/notesPlain"
                    }
                ]
            },
        },
    ],
}


@pytest.mark.parametrize(
    ("version", "version_class"),
    (
        ("1.17.2", OnePassCLIv1),
        ("2.27.4", OnePassCLIv2),
    )
)
def test_op_correct_cli_class(fake_op, version, version_class):
    op = fake_op(version)
    assert op._cli.version == version
    assert isinstance(op._cli, version_class)


def test_op_unsupported_cli_version(fake_op):
    with pytest.raises(AnsibleLookupError, match="is unsupported"):
        fake_op("99.77.77")


@pytest.mark.parametrize("op_fixture", OP_VERSION_FIXTURES)
def test_op_set_token_with_config(op_fixture, mocker, request):
    op = request.getfixturevalue(op_fixture)
    token = "F5417F77529B41B595D7F9D6F76EC057"
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch.object(op._cli, "signin", return_value=(0, token + "\n", ""))

    op.set_token()

    assert op.token == token


@pytest.mark.parametrize(
    ("op_fixture", "message"),
    [
        (op, value)
        for op in OP_VERSION_FIXTURES
        for value in
        (
            "Missing required parameters",
            "The operation is unauthorized",
        )
    ]
)
def test_op_set_token_with_config_missing_args(op_fixture, message, request, mocker):
    op = request.getfixturevalue(op_fixture)
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch.object(op._cli, "signin", return_value=(99, "", ""), side_effect=AnsibleLookupError(message))
    mocker.patch.object(op._cli, "full_signin", return_value=(0, "", ""))

    with pytest.raises(AnsibleLookupError, match=message):
        op.set_token()

    op._cli.full_signin.assert_not_called()


@pytest.mark.parametrize("op_fixture", OP_VERSION_FIXTURES)
def test_op_set_token_with_config_full_signin(op_fixture, request, mocker):
    op = request.getfixturevalue(op_fixture)
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch.object(op._cli, "signin", return_value=(99, "", ""), side_effect=AnsibleLookupError("Raised intentionally"))
    mocker.patch.object(op._cli, "full_signin", return_value=(0, "", ""))

    op.set_token()

    op._cli.full_signin.assert_called()


@pytest.mark.parametrize("op_fixture", OP_VERSION_FIXTURES)
def test_op_set_token_without_config(op_fixture, request, mocker):
    op = request.getfixturevalue(op_fixture)
    token = "B988E8A2680A4A348962751A96861FA1"
    mocker.patch("os.path.isfile", return_value=False)
    mocker.patch.object(op._cli, "signin", return_value=(99, "", ""))
    mocker.patch.object(op._cli, "full_signin", return_value=(0, token + "\n", ""))

    op.set_token()

    op._cli.signin.assert_not_called()
    assert op.token == token


@pytest.mark.parametrize(
    ("op_fixture", "login_status"),
    [(op, value) for op in OP_VERSION_FIXTURES for value in [False, True]]
)
def test_op_assert_logged_in(mocker, login_status, op_fixture, request):
    op = request.getfixturevalue(op_fixture)
    mocker.patch.object(op._cli, "assert_logged_in", return_value=login_status)
    mocker.patch.object(op, "set_token")

    op.assert_logged_in()

    op._cli.assert_logged_in.assert_called_once()
    assert op.logged_in == login_status

    if not login_status:
        op.set_token.assert_called_once()


@pytest.mark.parametrize("op_fixture", OP_VERSION_FIXTURES)
def test_op_get_raw_v1(mocker, op_fixture, request):
    op = request.getfixturevalue(op_fixture)
    mocker.patch.object(op._cli, "get_raw", return_value=[99, "RAW OUTPUT", ""])

    result = op.get_raw("some item")

    assert result == "RAW OUTPUT"
    op._cli.get_raw.assert_called_once()


@pytest.mark.parametrize(
    ("op_fixture", "output", "expected"),
    (
        list(itertools.chain([op], d))
        for op in OP_VERSION_FIXTURES
        for d in [
            ("RAW OUTPUT", "RAW OUTPUT"),
            (None, ""),
            ("", ""),
        ]
    )
)
def test_op_get_field(mocker, op_fixture, output, expected, request):
    op = request.getfixturevalue(op_fixture)
    mocker.patch.object(op, "get_raw", return_value=output)
    mocker.patch.object(op._cli, "_parse_field", return_value=output)

    result = op.get_field("some item", "some field")

    assert result == expected


@pytest.mark.parametrize(
    ("cli_class", "vault", "queries", "kwargs", "output", "expected"),
    (
        (_cli_class, item["vault_name"], item["queries"], item.get("kwargs", {}), item["output"], item["expected"])
        for _cli_class in MOCK_ENTRIES
        for item in MOCK_ENTRIES[_cli_class]
    ),
)
def test_op_lookup(mocker, cli_class, vault, queries, kwargs, output, expected):
    mocker.patch("ansible_collections.community.general.plugins.lookup.onepassword.OnePass._get_cli_class", cli_class)
    mocker.patch("ansible_collections.community.general.plugins.lookup.onepassword.OnePass.assert_logged_in", return_value=True)
    mocker.patch("ansible_collections.community.general.plugins.lookup.onepassword.OnePassCLIBase._run", return_value=(0, json.dumps(output), ""))

    result = LookupModule().run(queries, vault=vault, **kwargs)
    assert result == expected


@pytest.mark.parametrize("op_fixture", OP_VERSION_FIXTURES)
def test_signin(op_fixture, request):
    op = request.getfixturevalue(op_fixture)
    op._cli.master_password = "master_pass"
    op._cli.signin()
    print(op._cli.version)
    op._cli._run.assert_called_once_with(['signin', '--raw'], command_input=b"master_pass")

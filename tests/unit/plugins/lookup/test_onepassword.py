# (c) 2020, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest


from ansible.errors import AnsibleLookupError
from ansible_collections.community.general.plugins.lookup.onepassword import (
    OnePass as OnePassLookupModule,
    OnePassCLIv1,
    OnePassCLIv2,
)

from ansible_collections.community.general.plugins.lookup.onepassword_raw import LookupModule as OnePasswordRawLookup


# Intentionally excludes metadata leaf nodes that would exist in real output if not relevant.
MOCK_ENTRIES = [
    {
        'vault_name': 'Acme "Quot\'d" Servers',
        'queries': [
            '0123456789',
            'Mock "Quot\'d" Server'
        ],
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
]


@pytest.fixture
def fake_op(mocker):
    def _fake_op(version):
        mocker.patch("ansible_collections.community.general.plugins.lookup.onepassword.OnePassCLIBase.get_current_version", return_value=version)
        op = OnePassLookupModule(None, None, None, None, None)
        op._config._config_file_path = "/home/jin/.op/config"
        mocker.patch.object(op._cli, "_run")

        return op

    return _fake_op

@pytest.fixture
def opv1(fake_op):
    return fake_op("1.17.2")

@pytest.fixture
def opv2(fake_op):
    return fake_op("2.27.2")


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

def test_op_set_token_with_config(opv2, mocker):
    token = "F5417F77529B41B595D7F9D6F76EC057"
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch.object(opv2._cli, "signin", return_value=(0, token + "\n", ""))

    opv2.set_token()

    assert opv2.token == token

@pytest.mark.parametrize(
    "message",
    (
        "Missing required parameters",
        "The operation is unauthorized",
    )
)
def test_op_set_token_with_config_missing_args(opv2, mocker, message):
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch.object(opv2._cli, "signin", return_value=(99, "", ""), side_effect=AnsibleLookupError(message))
    mocker.patch.object(opv2._cli, "full_signin", return_value=(0, "", ""))

    with pytest.raises(AnsibleLookupError, match=message):
        opv2.set_token()

    opv2._cli.full_signin.assert_not_called()

def test_op_set_token_with_config_full_signin(opv2, mocker):
    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch.object(opv2._cli, "signin", return_value=(99, "", ""), side_effect=AnsibleLookupError("Raised intentionally"))
    mocker.patch.object(opv2._cli, "full_signin", return_value=(0, "", ""))

    opv2.set_token()

    opv2._cli.full_signin.assert_called()

def test_op_set_token_without_config(opv2, mocker):
    token = "B988E8A2680A4A348962751A96861FA1"
    mocker.patch("os.path.isfile", return_value=False)
    mocker.patch.object(opv2._cli, "signin", return_value=(99, "", ""))
    mocker.patch.object(opv2._cli, "full_signin", return_value=(0, token + "\n", ""))

    opv2.set_token()

    opv2._cli.signin.assert_not_called()
    assert opv2.token == token

@pytest.mark.parametrize("login_status",(False, True))
def test_op_assert_logged_in(mocker, login_status, opv2):
    mocker.patch.object(opv2._cli, "assert_logged_in", return_value=login_status)
    mocker.patch.object(opv2, "set_token")

    opv2.assert_logged_in()

    opv2._cli.assert_logged_in.assert_called_once()
    assert opv2.logged_in == login_status

    if not login_status:
        opv2.set_token.assert_called_once()

def test_op_get_raw(mocker, opv2):
    mocker.patch.object(opv2._cli, "get_raw", return_value=[99, "RAW OUTPUT", ""])

    result = opv2.get_raw("some item")

    assert result == "RAW OUTPUT"
    opv2._cli.get_raw.assert_called_once()

@pytest.mark.parametrize(
    ("output", "expected"),
    (
        ("RAW OUTPUT", "RAW OUTPUT"),
        (None, ""),
        ("", ""),
    )
)
def test_op_get_field(mocker, opv2, output, expected):
    mocker.patch.object(opv2, "get_raw", return_value=output)
    mocker.patch.object(opv2._cli, "_parse_field", return_value=output)

    result = opv2.get_field("some item", "some field")

    assert result == expected

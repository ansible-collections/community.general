# Copyright (c) 2022 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import operator
import itertools
import json
import pytest

from .onepassword_common import MOCK_ENTRIES

from ansible.errors import AnsibleLookupError, AnsibleOptionsError
from ansible.plugins.loader import lookup_loader
from ansible_collections.community.general.plugins.lookup.onepassword import (
    OnePassCLIv1,
    OnePassCLIv2,
)


OP_VERSION_FIXTURES = ["opv1", "opv2"]


@pytest.mark.parametrize(
    ("args", "rc", "expected_call_args", "expected_call_kwargs", "expected"),
    (
        (
            [],
            0,
            ["get", "account"],
            {"ignore_errors": True},
            True,
        ),
        (
            [],
            1,
            ["get", "account"],
            {"ignore_errors": True},
            False,
        ),
        (
            ["acme"],
            1,
            ["get", "account", "--account", "acme.1password.com"],
            {"ignore_errors": True},
            False,
        ),
    ),
)
def test_assert_logged_in_v1(mocker, args, rc, expected_call_args, expected_call_kwargs, expected):
    mocker.patch.object(OnePassCLIv1, "_run", return_value=[rc, "", ""])

    op_cli = OnePassCLIv1(*args)
    result = op_cli.assert_logged_in()

    op_cli._run.assert_called_with(expected_call_args, **expected_call_kwargs)
    assert result == expected


def test_full_signin_v1(mocker):
    mocker.patch.object(OnePassCLIv1, "_run", return_value=[0, "", ""])

    op_cli = OnePassCLIv1(
        subdomain="acme",
        username="bob@acme.com",
        secret_key="SECRET",
        master_password="ONEKEYTORULETHEMALL",
    )
    result = op_cli.full_signin()

    op_cli._run.assert_called_with(
        [
            "signin",
            "acme.1password.com",
            b"bob@acme.com",
            b"SECRET",
            "--raw",
        ],
        command_input=b"ONEKEYTORULETHEMALL",
    )
    assert result == [0, "", ""]


@pytest.mark.parametrize(
    ("args", "out", "expected_call_args", "expected_call_kwargs", "expected"),
    (
        (
            [],
            "list of accounts",
            ["account", "get"],
            {"ignore_errors": True},
            True,
        ),
        (
            ["acme"],
            "list of accounts",
            ["account", "get", "--account", "acme.1password.com"],
            {"ignore_errors": True},
            True,
        ),
        (
            [],
            "",
            ["account", "list"],
            {},
            False,
        ),
    ),
)
def test_assert_logged_in_v2(mocker, args, out, expected_call_args, expected_call_kwargs, expected):
    mocker.patch.object(OnePassCLIv2, "_run", return_value=[0, out, ""])
    op_cli = OnePassCLIv2(*args)
    result = op_cli.assert_logged_in()

    op_cli._run.assert_called_with(expected_call_args, **expected_call_kwargs)
    assert result == expected


def test_assert_logged_in_v2_connect():
    op_cli = OnePassCLIv2(connect_host="http://localhost:8080", connect_token="foobar")
    result = op_cli.assert_logged_in()
    assert result


def test_full_signin_v2(mocker):
    mocker.patch.object(OnePassCLIv2, "_run", return_value=[0, "", ""])

    op_cli = OnePassCLIv2(
        subdomain="acme",
        username="bob@acme.com",
        secret_key="SECRET",
        master_password="ONEKEYTORULETHEMALL",
    )
    result = op_cli.full_signin()

    op_cli._run.assert_called_with(
        [
            "account",
            "add",
            "--raw",
            "--address",
            "acme.1password.com",
            "--email",
            b"bob@acme.com",
            "--signin",
        ],
        command_input=b"ONEKEYTORULETHEMALL",
        environment_update={"OP_SECRET_KEY": "SECRET"},
    )
    assert result == [0, "", ""]


@pytest.mark.parametrize(
    ("version", "version_class"),
    (
        ("1.17.2", OnePassCLIv1),
        ("2.27.4", OnePassCLIv2),
    ),
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
    mocker.patch.object(op._cli, "signin", return_value=(0, f"{token}\n", ""))

    op.set_token()

    assert op.token == token


@pytest.mark.parametrize(
    ("op_fixture", "message"),
    [
        (op, value)
        for op in OP_VERSION_FIXTURES
        for value in (
            "Missing required parameters",
            "The operation is unauthorized",
        )
    ],
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
    mocker.patch.object(
        op._cli, "signin", return_value=(99, "", ""), side_effect=AnsibleLookupError("Raised intentionally")
    )
    mocker.patch.object(op._cli, "full_signin", return_value=(0, "", ""))

    op.set_token()

    op._cli.full_signin.assert_called()


@pytest.mark.parametrize("op_fixture", OP_VERSION_FIXTURES)
def test_op_set_token_without_config(op_fixture, request, mocker):
    op = request.getfixturevalue(op_fixture)
    token = "B988E8A2680A4A348962751A96861FA1"
    mocker.patch("os.path.isfile", return_value=False)
    mocker.patch.object(op._cli, "signin", return_value=(99, "", ""))
    mocker.patch.object(op._cli, "full_signin", return_value=(0, f"{token}\n", ""))

    op.set_token()

    op._cli.signin.assert_not_called()
    assert op.token == token


@pytest.mark.parametrize(
    ("op_fixture", "login_status"), [(op, value) for op in OP_VERSION_FIXTURES for value in [False, True]]
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
    ),
)
def test_op_get_field(mocker, op_fixture, output, expected, request):
    op = request.getfixturevalue(op_fixture)
    mocker.patch.object(op, "get_raw", return_value=output)
    mocker.patch.object(op._cli, "_parse_field", return_value=output)

    result = op.get_field("some item", "some field")

    assert result == expected


# This test sometimes fails on older Python versions because the gathered tests mismatch.
# Sort the fixture data to make this reliable
# https://github.com/pytest-dev/pytest-xdist/issues/432
@pytest.mark.parametrize(
    ("cli_class", "vault", "queries", "kwargs", "output", "expected"),
    (
        (_cli_class, item["vault_name"], item["queries"], item.get("kwargs", {}), item["output"], item["expected"])
        for _cli_class in sorted(MOCK_ENTRIES, key=operator.attrgetter("__name__"))
        for item in MOCK_ENTRIES[_cli_class]
    ),
)
def test_op_lookup(mocker, cli_class, vault, queries, kwargs, output, expected):
    mocker.patch("ansible_collections.community.general.plugins.lookup.onepassword.OnePass._get_cli_class", cli_class)
    mocker.patch(
        "ansible_collections.community.general.plugins.lookup.onepassword.OnePass.assert_logged_in", return_value=True
    )
    mocker.patch(
        "ansible_collections.community.general.plugins.lookup.onepassword.OnePassCLIBase._run",
        return_value=(0, json.dumps(output), ""),
    )

    op_lookup = lookup_loader.get("community.general.onepassword")
    result = op_lookup.run(queries, vault=vault, **kwargs)

    assert result == expected


@pytest.mark.parametrize("op_fixture", OP_VERSION_FIXTURES)
def test_signin(op_fixture, request):
    op = request.getfixturevalue(op_fixture)
    op._cli.master_password = "master_pass"
    op._cli.signin()
    op._cli._run.assert_called_once_with(["signin", "--raw"], command_input=b"master_pass")


def test_op_doc(mocker):
    document_contents = "Document Contents\n"

    mocker.patch(
        "ansible_collections.community.general.plugins.lookup.onepassword.OnePass.assert_logged_in", return_value=True
    )
    mocker.patch(
        "ansible_collections.community.general.plugins.lookup.onepassword.OnePassCLIBase._run",
        return_value=(0, document_contents, ""),
    )

    op_lookup = lookup_loader.get("community.general.onepassword_doc")
    result = op_lookup.run(["Private key doc"])

    assert result == [document_contents]


@pytest.mark.parametrize(
    ("plugin", "connect_host", "connect_token"),
    [
        (plugin, connect_host, connect_token)
        for plugin in ("community.general.onepassword", "community.general.onepassword_raw")
        for (connect_host, connect_token) in (
            ("http://localhost", None),
            (None, "foobar"),
        )
    ],
)
def test_op_connect_partial_args(plugin, connect_host, connect_token, mocker):
    op_lookup = lookup_loader.get(plugin)

    mocker.patch(
        "ansible_collections.community.general.plugins.lookup.onepassword.OnePass._get_cli_class", OnePassCLIv2
    )

    with pytest.raises(AnsibleOptionsError):
        op_lookup.run("login", vault_name="test vault", connect_host=connect_host, connect_token=connect_token)


@pytest.mark.parametrize(
    ("kwargs"),
    (
        {"connect_host": "http://localhost", "connect_token": "foobar"},
        {"service_account_token": "foobar"},
    ),
)
def test_opv1_unsupported_features(kwargs):
    op_cli = OnePassCLIv1(**kwargs)
    with pytest.raises(AnsibleLookupError):
        op_cli.full_signin()

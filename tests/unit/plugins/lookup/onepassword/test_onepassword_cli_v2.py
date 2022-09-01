# Copyright (c) 2022 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest


from ansible_collections.community.general.plugins.lookup.onepassword import OnePassCLIv2


@pytest.mark.parametrize(
    ("args", "out", "expected_call_args", "expected"),
    (
        ([], "list of accounts", ["account", "get"], True,),
        (["acme"], "list of accounts", ["account", "get", "--account", "acme.1password.com"], True,),
        ([], "", ["account", "list"], False,),
    )
)
def test_assert_logged_in(mocker, args, out, expected_call_args, expected):
    mocker.patch.object(OnePassCLIv2, "_run", return_value=[0, out, ""])
    op_cli = OnePassCLIv2(*args)
    result = op_cli.assert_logged_in()

    op_cli._run.assert_called_with(expected_call_args)
    assert result == expected


def test_full_signin(mocker):
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
            "account", "add", "--raw",
            "--address", "acme.1password.com",
            "--email", b"bob@acme.com",
            "--signin",
        ],
        command_input=b"ONEKEYTORULETHEMALL",
        environment_update={'OP_SECRET_KEY': 'SECRET'},
    )
    assert result == [0, "", ""]

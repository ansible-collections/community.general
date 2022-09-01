# Copyright (c) 2022 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest


from ansible_collections.community.general.plugins.lookup.onepassword import OnePassCLIv1


@pytest.mark.parametrize(
    ("args", "rc", "expected_call_args", "expected_call_kwargs", "expected"),
    (
        ([], 0, ["get", "account"], {"ignore_errors": True}, True,),
        ([], 1, ["get", "account"], {"ignore_errors": True}, False,),
        (["acme"], 1, ["get", "account", "--account", "acme.1password.com"], {"ignore_errors": True}, False,),
    )
)
def test_assert_logged_in(mocker, args, rc, expected_call_args, expected_call_kwargs, expected):
    mocker.patch.object(OnePassCLIv1, "_run", return_value=[rc, "", ""])

    op_cli = OnePassCLIv1(*args)
    result = op_cli.assert_logged_in()

    op_cli._run.assert_called_with(expected_call_args, **expected_call_kwargs)
    assert result == expected


def test_full_signin(mocker):
    mocker.patch.object(OnePassCLIv1, "_run", return_value=[0, "", ""])

    op_cli = OnePassCLIv1(
        subdomain="acme",
        username="bob@acme.com",
        secret_key="SECRET",
        master_password="ONEKEYTORULETHEMALL",
    )
    result = op_cli.full_signin()

    op_cli._run.assert_called_with([
        "signin",
        "acme.1password.com",
        b"bob@acme.com",
        b"SECRET",
        "--raw",
    ], command_input=b"ONEKEYTORULETHEMALL")
    assert result == [0, "", ""]

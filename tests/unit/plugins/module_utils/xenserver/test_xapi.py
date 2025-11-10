#
# Copyright (c) 2019, Bojan Vitnik <bvitnik@mainstream.rs>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


import pytest
import atexit

from .FakeAnsibleModule import FailJsonException
from ansible.module_utils.ansible_release import __version__ as ANSIBLE_VERSION


testcase_module_local_conn = {
    "params": [
        {
            "hostname": "localhost",
            "username": "someuser",
            "password": "somepwd",
            "validate_certs": True,
        },
    ],
    "ids": [
        "local-conn",
    ],
}

testcase_module_remote_conn = {
    "params": [
        {
            "hostname": "somehost",
            "username": "someuser",
            "password": "somepwd",
            "validate_certs": True,
        },
    ],
    "ids": [
        "remote-conn",
    ],
}

testcase_module_remote_conn_scheme = {
    "params": [
        {
            "hostname": "http://somehost",
            "username": "someuser",
            "password": "somepwd",
            "validate_certs": True,
        },
        {
            "hostname": "https://somehost",
            "username": "someuser",
            "password": "somepwd",
            "validate_certs": True,
        },
    ],
    "ids": [
        "remote-conn-http",
        "remote-conn-https",
    ],
}


@pytest.mark.parametrize(
    "fake_ansible_module",
    testcase_module_local_conn["params"],  # type: ignore
    ids=testcase_module_local_conn["ids"],  # type: ignore
    indirect=True,
)
def test_xapi_connect_local_session(mocker, fake_ansible_module, XenAPI, xenserver):
    """Tests that connection to localhost uses XenAPI.xapi_local() function."""
    mocker.patch("XenAPI.xapi_local")

    xenserver.XAPI.connect(fake_ansible_module)

    XenAPI.xapi_local.assert_called_once()


@pytest.mark.parametrize(
    "fake_ansible_module",
    testcase_module_local_conn["params"],  # type: ignore
    ids=testcase_module_local_conn["ids"],  # type: ignore
    indirect=True,
)
def test_xapi_connect_local_login(mocker, fake_ansible_module, XenAPI, xenserver):
    """Tests that connection to localhost uses empty username and password."""
    mocker.patch.object(XenAPI.Session, "login_with_password", create=True)

    xenserver.XAPI.connect(fake_ansible_module)

    XenAPI.Session.login_with_password.assert_called_once_with("", "", ANSIBLE_VERSION, "Ansible")


def test_xapi_connect_login(mocker, fake_ansible_module, XenAPI, xenserver):
    """
    Tests that username and password are properly propagated to
    XenAPI.Session.login_with_password() function.
    """
    mocker.patch.object(XenAPI.Session, "login_with_password", create=True)

    xenserver.XAPI.connect(fake_ansible_module)

    username = fake_ansible_module.params["username"]
    password = fake_ansible_module.params["password"]

    XenAPI.Session.login_with_password.assert_called_once_with(username, password, ANSIBLE_VERSION, "Ansible")


def test_xapi_connect_login_failure(mocker, fake_ansible_module, XenAPI, xenserver):
    """Tests that login failure is properly handled."""
    fake_error_msg = "Fake XAPI login error!"

    mocked_login = mocker.patch.object(XenAPI.Session, "login_with_password", create=True)
    mocked_login.side_effect = XenAPI.Failure(fake_error_msg)

    hostname = fake_ansible_module.params["hostname"]
    username = fake_ansible_module.params["username"]

    with pytest.raises(FailJsonException) as exc_info:
        xenserver.XAPI.connect(fake_ansible_module)

    assert (
        exc_info.value.kwargs["msg"]
        == f"Unable to log on to XenServer at http://{hostname} as {username}: {fake_error_msg}"
    )


@pytest.mark.parametrize(
    "fake_ansible_module",
    testcase_module_remote_conn_scheme["params"],  # type: ignore
    ids=testcase_module_remote_conn_scheme["ids"],  # type: ignore
    indirect=True,
)
def test_xapi_connect_remote_scheme(mocker, fake_ansible_module, XenAPI, xenserver):
    """Tests that explicit scheme in hostname param is preserved."""
    mocker.patch("XenAPI.Session")

    xenserver.XAPI.connect(fake_ansible_module)

    hostname = fake_ansible_module.params["hostname"]
    ignore_ssl = not fake_ansible_module.params["validate_certs"]

    XenAPI.Session.assert_called_once_with(hostname, ignore_ssl=ignore_ssl)


@pytest.mark.parametrize(
    "fake_ansible_module",
    testcase_module_remote_conn["params"],  # type: ignore
    ids=testcase_module_remote_conn["ids"],  # type: ignore
    indirect=True,
)
def test_xapi_connect_remote_no_scheme(mocker, fake_ansible_module, XenAPI, xenserver):
    """Tests that proper scheme is prepended to hostname without scheme."""
    mocker.patch("XenAPI.Session")

    xenserver.XAPI.connect(fake_ansible_module)

    hostname = fake_ansible_module.params["hostname"]
    ignore_ssl = not fake_ansible_module.params["validate_certs"]

    XenAPI.Session.assert_called_once_with(f"http://{hostname}", ignore_ssl=ignore_ssl)


def test_xapi_connect_support_ignore_ssl(mocker, fake_ansible_module, XenAPI, xenserver):
    """Tests proper handling of ignore_ssl support."""
    mocked_session = mocker.patch("XenAPI.Session")
    mocked_session.side_effect = TypeError()

    with pytest.raises(TypeError):
        xenserver.XAPI.connect(fake_ansible_module)

    hostname = fake_ansible_module.params["hostname"]

    XenAPI.Session.assert_called_with(f"http://{hostname}")


def test_xapi_connect_no_disconnect_atexit(mocker, fake_ansible_module, XenAPI, xenserver):
    """Tests skipping registration of atexit disconnect handler."""
    mocker.patch("atexit.register")

    xenserver.XAPI.connect(fake_ansible_module, disconnect_atexit=False)

    atexit.register.assert_not_called()


def test_xapi_connect_singleton(mocker, fake_ansible_module, XenAPI, xenserver):
    """Tests if XAPI.connect() returns singleton."""
    mocker.patch("XenAPI.Session")

    xapi_session1 = xenserver.XAPI.connect(fake_ansible_module)
    xapi_session2 = xenserver.XAPI.connect(fake_ansible_module)

    XenAPI.Session.assert_called_once()
    assert xapi_session1 == xapi_session2

# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from unittest.mock import Mock, patch
from urllib.error import HTTPError

import pytest
from ansible.plugins.callback import CallbackBase

from ansible_collections.community.general.plugins.callback import logstash as logstash_callback
from ansible_collections.community.general.plugins.callback.logstash import CallbackModule, LogstashHTTPHandler


def _configure_callback(options):
    logger = Mock()
    formatter = Mock()
    logstash = Mock()

    with (
        patch.object(logstash_callback, "HAS_LOGSTASH", True),
        patch.object(logstash_callback, "logstash", logstash, create=True),
        patch.object(logstash_callback, "LogstashFormatterVersion1", return_value=formatter) as formatter_class,
        patch.object(logstash_callback.logging, "getLogger", return_value=logger),
        patch.object(CallbackBase, "set_options"),
    ):
        callback = CallbackModule()
        callback._display = Mock()
        callback.get_option = Mock(side_effect=options.get)
        callback.set_options()

    return callback, logger, logstash, formatter_class


def test_http_handler_posts_formatted_event():
    formatter = Mock()
    formatter.format.return_value = b'{"message": "ansible ok"}'
    response = Mock()
    response.getcode.return_value = 202
    handler = LogstashHTTPHandler(
        url="https://logstash.example.com/",
        formatter=formatter,
        username="logger",
        password="secret",
        validate_certs=True,
        timeout=5,
    )
    record = logging.makeLogRecord({"msg": "ansible ok", "args": ()})

    with patch(
        "ansible_collections.community.general.plugins.callback.logstash.open_url",
        return_value=response,
    ) as open_url:
        handler.emit(record)

    open_url.assert_called_once_with(
        "https://logstash.example.com/",
        data=b'{"message": "ansible ok"}',
        headers={"Content-Type": "application/json"},
        method="POST",
        timeout=5,
        validate_certs=True,
        url_username="logger",
        url_password="secret",
        force_basic_auth=True,
        use_netrc=False,
        follow_redirects="none",
    )
    response.close.assert_called_once_with()


@pytest.mark.parametrize("status", [200, 201, 202, 204])
def test_http_handler_accepts_success_status(status):
    formatter = Mock()
    formatter.format.return_value = b"{}"
    response = Mock()
    response.getcode.return_value = status
    display = Mock()
    handler = LogstashHTTPHandler(url="https://logstash.example.com/", formatter=formatter, display=display)

    with patch(
        "ansible_collections.community.general.plugins.callback.logstash.open_url",
        return_value=response,
    ):
        handler.emit(logging.makeLogRecord({"msg": "ansible ok", "args": ()}))

    display.warning.assert_not_called()
    response.close.assert_called_once_with()


def test_http_handler_sends_client_tls_options():
    formatter = Mock()
    formatter.format.return_value = b"{}"
    response = Mock()
    response.getcode.return_value = 204
    handler = LogstashHTTPHandler(
        url="https://logstash.example.com/events",
        formatter=formatter,
        ca_path="/etc/pki/ca.pem",
        client_cert="/etc/pki/client.pem",
        client_key="/etc/pki/client.key",
    )

    with patch(
        "ansible_collections.community.general.plugins.callback.logstash.open_url",
        return_value=response,
    ) as open_url:
        handler.emit(logging.makeLogRecord({"msg": "ansible ok", "args": ()}))

    assert open_url.call_args.kwargs["ca_path"] == "/etc/pki/ca.pem"
    assert open_url.call_args.kwargs["client_cert"] == "/etc/pki/client.pem"
    assert open_url.call_args.kwargs["client_key"] == "/etc/pki/client.key"


def test_http_handler_omits_auth_for_empty_credentials():
    formatter = Mock()
    formatter.format.return_value = b"{}"
    response = Mock()
    response.getcode.return_value = 204
    handler = LogstashHTTPHandler(
        url="http://logstash.example.com/",
        formatter=formatter,
        username="",
        password="",
    )

    with patch(
        "ansible_collections.community.general.plugins.callback.logstash.open_url",
        return_value=response,
    ) as open_url:
        handler.emit(logging.makeLogRecord({"msg": "ansible ok", "args": ()}))

    assert "url_username" not in open_url.call_args.kwargs
    assert "url_password" not in open_url.call_args.kwargs


def test_http_handler_retries_too_many_requests():
    formatter = Mock()
    formatter.format.return_value = b"{}"
    response = Mock()
    response.getcode.return_value = 202
    error = HTTPError("https://logstash.example.com/", 429, "busy", None, None)
    handler = LogstashHTTPHandler(url="https://logstash.example.com/", formatter=formatter, retries=1)

    with (
        patch(
            "ansible_collections.community.general.plugins.callback.logstash.open_url",
            side_effect=[error, response],
        ) as open_url,
        patch("ansible_collections.community.general.plugins.callback.logstash.time.sleep") as sleep,
        patch("ansible_collections.community.general.plugins.callback.logstash.random.uniform", return_value=0.1),
    ):
        handler.emit(logging.makeLogRecord({"msg": "ansible ok", "args": ()}))

    assert open_url.call_count == 2
    sleep.assert_called_once_with(0.6)


def test_http_handler_does_not_retry_authentication_failures():
    formatter = Mock()
    formatter.format.return_value = b"{}"
    error = HTTPError("https://logstash.example.com/", 401, "unauthorized", None, None)
    display = Mock()
    handler = LogstashHTTPHandler(
        url="https://logstash.example.com/",
        formatter=formatter,
        username="logger",
        password="secret",
        display=display,
    )

    with patch(
        "ansible_collections.community.general.plugins.callback.logstash.open_url",
        side_effect=error,
    ) as open_url:
        handler.emit(logging.makeLogRecord({"msg": "ansible ok", "args": ()}))

    open_url.assert_called_once()
    display.warning.assert_called_once_with("Logstash HTTP request failed with status code 401.")
    assert "secret" not in str(display.warning.call_args)


def test_http_handler_network_error_is_non_fatal():
    formatter = Mock()
    formatter.format.return_value = b"{}"
    display = Mock()
    handler = LogstashHTTPHandler(url="https://logstash.example.com/", formatter=formatter, display=display)

    with patch(
        "ansible_collections.community.general.plugins.callback.logstash.open_url",
        side_effect=OSError("connection failed"),
    ) as open_url:
        handler.emit(logging.makeLogRecord({"msg": "ansible ok", "args": ()}))

    open_url.assert_called_once()
    display.warning.assert_called_once_with("Could not send event to Logstash over HTTP.")


def test_http_protocol_configures_basic_auth_and_tls():
    options = {
        "server": "logstash.example.com",
        "port": 8080,
        "protocol": "https",
        "http_path": "events",
        "username": "logger",
        "password": "secret",
        "validate_certs": True,
        "ca_path": "/etc/pki/ca.pem",
        "client_cert": "/etc/pki/client.pem",
        "client_key": "/etc/pki/client.key",
        "timeout": 4,
        "retries": 10,
        "type": "ansible",
        "pre_command": None,
        "format_version": "v1",
    }

    callback, logger, logstash_mock, formatter_class = _configure_callback(options)

    handler = logger.addHandler.call_args.args[0]
    assert isinstance(handler, LogstashHTTPHandler)
    assert handler.url == "https://logstash.example.com:8080/events"
    assert handler.username == "logger"
    assert handler.password == "secret"
    assert handler.validate_certs is True
    assert handler.ca_path == "/etc/pki/ca.pem"
    assert handler.client_cert == "/etc/pki/client.pem"
    assert handler.client_key == "/etc/pki/client.key"
    assert handler.timeout == 4
    # retries is not restricted to a fixed set of choices, higher values are accepted
    assert handler.retries == 10
    formatter_class.assert_called_once_with(message_type="ansible")
    logstash_mock.TCPLogstashHandler.assert_not_called()
    assert callback.disabled is False


def test_tcp_protocol_keeps_existing_handler():
    options = {
        "server": "logstash.example.com",
        "port": 5000,
        "protocol": "tcp",
        "username": None,
        "password": None,
        "type": "ansible",
        "pre_command": None,
        "format_version": "v1",
    }

    callback, logger, logstash, formatter_class = _configure_callback(options)

    assert callback.disabled is False
    logstash.TCPLogstashHandler.assert_called_once_with("logstash.example.com", 5000, version=1, message_type="ansible")
    logger.addHandler.assert_called_once_with(logstash.TCPLogstashHandler.return_value)
    formatter_class.assert_not_called()


def test_http_protocol_requires_both_credentials():
    options = {
        "server": "logstash.example.com",
        "port": 8080,
        "protocol": "http",
        "http_path": "/",
        "username": "logger",
        "password": None,
        "validate_certs": True,
        "ca_path": None,
        "client_cert": None,
        "client_key": None,
        "timeout": 10,
        "retries": 3,
        "type": "ansible",
        "pre_command": None,
        "format_version": "v1",
    }

    callback, logger, logstash_mock, formatter_class = _configure_callback(options)

    assert callback.disabled is True
    logger.addHandler.assert_not_called()
    logstash_mock.TCPLogstashHandler.assert_not_called()
    formatter_class.assert_not_called()


@pytest.mark.parametrize(
    ("protocol", "ca_path", "client_cert", "client_key"),
    [
        ("http", "/etc/pki/ca.pem", None, None),
        ("https", None, None, "/etc/pki/client.key"),
    ],
)
def test_http_protocol_rejects_invalid_tls_options(protocol, ca_path, client_cert, client_key):
    options = {
        "server": "logstash.example.com",
        "port": 8080,
        "protocol": protocol,
        "http_path": "/",
        "username": None,
        "password": None,
        "validate_certs": True,
        "ca_path": ca_path,
        "client_cert": client_cert,
        "client_key": client_key,
        "timeout": 10,
        "retries": 3,
        "type": "ansible",
        "pre_command": None,
        "format_version": "v1",
    }

    callback, logger, logstash_mock, formatter_class = _configure_callback(options)

    assert callback.disabled is True
    logger.addHandler.assert_not_called()
    logstash_mock.TCPLogstashHandler.assert_not_called()
    formatter_class.assert_not_called()


def test_http_protocol_rejects_non_positive_timeout():
    options = {
        "server": "logstash.example.com",
        "port": 8080,
        "protocol": "https",
        "http_path": "/",
        "username": None,
        "password": None,
        "validate_certs": True,
        "ca_path": None,
        "client_cert": None,
        "client_key": None,
        "timeout": 0,
        "retries": 3,
        "type": "ansible",
        "pre_command": None,
        "format_version": "v1",
    }

    callback, logger, logstash_mock, formatter_class = _configure_callback(options)

    assert callback.disabled is True
    logger.addHandler.assert_not_called()
    logstash_mock.TCPLogstashHandler.assert_not_called()
    formatter_class.assert_not_called()


def test_http_protocol_rejects_negative_retries():
    options = {
        "server": "logstash.example.com",
        "port": 8080,
        "protocol": "https",
        "http_path": "/",
        "username": None,
        "password": None,
        "validate_certs": True,
        "ca_path": None,
        "client_cert": None,
        "client_key": None,
        "timeout": 10,
        "retries": -1,
        "type": "ansible",
        "pre_command": None,
        "format_version": "v1",
    }

    callback, logger, logstash_mock, formatter_class = _configure_callback(options)

    assert callback.disabled is True
    logger.addHandler.assert_not_called()
    logstash_mock.TCPLogstashHandler.assert_not_called()
    formatter_class.assert_not_called()

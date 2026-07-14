# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest
from ansible.module_utils.basic import AnsibleFallbackNotFound

from ansible_collections.community.general.plugins.module_utils import _consul


@pytest.fixture(autouse=True)
def scrub_consul_env(monkeypatch):
    for name in ("CONSUL_HTTP_ADDR", "CONSUL_HTTP_SSL", "CONSUL_HTTP_SSL_VERIFY", "CONSUL_HTTP_TOKEN", "CONSUL_CACERT"):
        monkeypatch.delenv(name, raising=False)


HOST_CASES = [
    ("consul.example.com:8500", "consul.example.com"),
    ("http://consul.example.com:8500", "consul.example.com"),
    ("https://consul.example.com", "consul.example.com"),
    ("consul.example.com", "consul.example.com"),
    ("[2001:db8::1]:8500", "[2001:db8::1]"),
]


@pytest.mark.parametrize("addr, expected", HOST_CASES)
def test_env_consul_host(monkeypatch, addr, expected):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", addr)
    assert _consul.env_consul_host() == expected


PORT_CASES = [
    ("consul.example.com:8501", 8501),
    ("https://consul.example.com:8501", 8501),
    ("[2001:db8::1]:8500", 8500),
]


@pytest.mark.parametrize("addr, expected", PORT_CASES)
def test_env_consul_port(monkeypatch, addr, expected):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", addr)
    assert _consul.env_consul_port() == expected


SCHEME_CASES = [
    # (CONSUL_HTTP_SSL, CONSUL_HTTP_ADDR, expected)
    ("true", None, "https"),
    ("1", None, "https"),
    ("true", "http://consul.example.com:8500", "https"),
    # a false CONSUL_HTTP_SSL must not downgrade an https address
    ("false", "https://consul.example.com:8500", "https"),
    (None, "https://consul.example.com:8500", "https"),
    (None, "http://consul.example.com:8500", "http"),
]


@pytest.mark.parametrize("tls, addr, expected", SCHEME_CASES)
def test_env_consul_scheme(monkeypatch, tls, addr, expected):
    if tls is not None:
        monkeypatch.setenv("CONSUL_HTTP_SSL", tls)
    if addr is not None:
        monkeypatch.setenv("CONSUL_HTTP_ADDR", addr)
    assert _consul.env_consul_scheme() == expected


FALLBACK_NOT_FOUND_CASES = [
    # (env, callable) -> no usable value in the environment
    ({}, _consul.env_consul_host),
    ({}, _consul.env_consul_port),
    ({}, _consul.env_consul_scheme),
    ({"CONSUL_HTTP_ADDR": "consul.example.com"}, _consul.env_consul_port),
    ({"CONSUL_HTTP_ADDR": "consul.example.com:8500"}, _consul.env_consul_scheme),
    ({"CONSUL_HTTP_SSL": "false"}, _consul.env_consul_scheme),
    # set-but-empty variables count as unset, like the consul CLI treats them
    ({"CONSUL_HTTP_ADDR": ""}, _consul.env_consul_host),
    ({"CONSUL_HTTP_SSL": ""}, _consul.env_consul_scheme),
    # addresses the consul CLI accepts but the modules cannot honor faithfully
    # are ignored, so playbooks that never relied on the variable keep working
    ({"CONSUL_HTTP_ADDR": "unix:///var/run/consul.sock"}, _consul.env_consul_host),
    ({"CONSUL_HTTP_ADDR": "https://proxy.example.com:443/consul"}, _consul.env_consul_host),
    ({"CONSUL_HTTP_ADDR": "http://user:pass@consul.example.com:8500"}, _consul.env_consul_host),
    ({"CONSUL_HTTP_ADDR": "http://consul.example.com:8500?dc=dc1"}, _consul.env_consul_host),
    ({"CONSUL_HTTP_ADDR": "   "}, _consul.env_consul_host),
    ({"CONSUL_HTTP_ADDR": "http://:8500"}, _consul.env_consul_host),
]


@pytest.mark.parametrize("env, func", FALLBACK_NOT_FOUND_CASES)
def test_fallback_not_found(monkeypatch, env, func):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(AnsibleFallbackNotFound):
        func()


def test_trailing_slash_is_tolerated(monkeypatch):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", "https://consul.example.com:8501/")
    assert _consul.env_consul_host() == "consul.example.com"
    assert _consul.env_consul_port() == 8501
    assert _consul.env_consul_scheme() == "https"


ERROR_CASES = [
    # (env, callable, message fragment)
    ({"CONSUL_HTTP_ADDR": "consul.example.com:notaport"}, _consul.env_consul_port, "CONSUL_HTTP_ADDR"),
    ({"CONSUL_HTTP_ADDR": "consul.example.com:notaport"}, _consul.env_consul_host, "CONSUL_HTTP_ADDR"),
    ({"CONSUL_HTTP_ADDR": "2001:db8::1"}, _consul.env_consul_host, "CONSUL_HTTP_ADDR"),
    ({"CONSUL_HTTP_SSL": "maybe"}, _consul.env_consul_scheme, "CONSUL_HTTP_SSL"),
]


@pytest.mark.parametrize("env, func, fragment", ERROR_CASES)
def test_invalid_values_fail_loud(monkeypatch, env, func, fragment):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(ValueError, match=fragment):
        func()


NONEMPTY_FALLBACK_CASES = [
    ({"CONSUL_HTTP_TOKEN": "tok"}, ["CONSUL_HTTP_TOKEN"], "tok"),
    ({"CONSUL_CACERT": "/etc/ssl/ca.pem"}, ["CONSUL_CACERT"], "/etc/ssl/ca.pem"),
]


@pytest.mark.parametrize("env, names, expected", NONEMPTY_FALLBACK_CASES)
def test_nonempty_env_fallback(monkeypatch, env, names, expected):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    assert _consul.nonempty_env_fallback(*names) == expected


NONEMPTY_FALLBACK_UNSET_CASES = [
    ({}, ["CONSUL_HTTP_TOKEN"]),
    ({"CONSUL_HTTP_TOKEN": ""}, ["CONSUL_HTTP_TOKEN"]),
]


@pytest.mark.parametrize("env, names", NONEMPTY_FALLBACK_UNSET_CASES)
def test_nonempty_env_fallback_unset(monkeypatch, env, names):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(AnsibleFallbackNotFound):
        _consul.nonempty_env_fallback(*names)

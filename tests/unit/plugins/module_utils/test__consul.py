# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest
from ansible.module_utils import _internal
from ansible.module_utils.basic import AnsibleFallbackNotFound
from ansible.module_utils.common import warnings as _warnings
from ansible.module_utils.common.arg_spec import ModuleArgumentSpecValidator
from ansible.module_utils.common.warnings import get_warning_messages

from ansible_collections.community.general.plugins.module_utils import _consul


@pytest.fixture(autouse=True)
def scrub_consul_env(monkeypatch):
    for name in ("CONSUL_HTTP_ADDR", "CONSUL_HTTP_SSL", "CONSUL_HTTP_SSL_VERIFY", "CONSUL_HTTP_TOKEN", "CONSUL_CACERT"):
        monkeypatch.delenv(name, raising=False)
    # The parse cache and the warning store are process-global; both must be
    # fresh so warning assertions cannot leak between cases. warn() only
    # records to the store when not running as controller code, so pin the
    # flag like ansible-core's own warning tests do (absent on older cores).
    _consul._parse_addr.cache_clear()
    monkeypatch.setattr(_warnings, "_global_warnings", type(_warnings._global_warnings)())
    monkeypatch.setattr(_internal, "is_controller", False, raising=False)


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
    # an address without a host is ignored entirely, no component is half-used
    ({"CONSUL_HTTP_ADDR": "http://:8500"}, _consul.env_consul_host),
    ({"CONSUL_HTTP_ADDR": "http://:8500"}, _consul.env_consul_port),
    ({"CONSUL_HTTP_ADDR": "https://"}, _consul.env_consul_scheme),
    ({"CONSUL_HTTP_ADDR": ":8500"}, _consul.env_consul_port),
]


@pytest.mark.parametrize("env, func", FALLBACK_NOT_FOUND_CASES)
def test_fallback_not_found(monkeypatch, env, func):
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    with pytest.raises(AnsibleFallbackNotFound):
        func()
    assert get_warning_messages() == ()


def test_trailing_slash_is_tolerated(monkeypatch):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", "https://consul.example.com:8501/")
    assert _consul.env_consul_host() == "consul.example.com"
    assert _consul.env_consul_port() == 8501
    assert _consul.env_consul_scheme() == "https"


# Fallback callables may only raise AnsibleFallbackNotFound; ansible-core's
# set_fallbacks catches nothing else, so an unparsable value must warn and
# fall back instead of raising. Only shapes every supported Python rejects
# belong here: newer interpreters reject more bracket forms than older ones.
MALFORMED_ADDR_CASES = [
    "consul.example.com:notaport",
    "consul.example.com:99999",
    "2001:db8::1",
    "[::1",
]


@pytest.mark.parametrize("addr", MALFORMED_ADDR_CASES)
@pytest.mark.parametrize("func", [_consul.env_consul_host, _consul.env_consul_port, _consul.env_consul_scheme])
def test_malformed_addr_warns_and_falls_back(monkeypatch, addr, func):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", addr)
    with pytest.raises(AnsibleFallbackNotFound):
        func()
    warnings = get_warning_messages()
    assert len(warnings) == 1
    assert "CONSUL_HTTP_ADDR" in warnings[0]
    # the value may embed credentials, so the warning must not echo it
    assert addr not in warnings[0]


def test_malformed_addr_warns_once_across_consumers(monkeypatch):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", "[::1")
    for func in (_consul.env_consul_host, _consul.env_consul_port, _consul.env_consul_scheme):
        with pytest.raises(AnsibleFallbackNotFound):
            func()
    assert len(get_warning_messages()) == 1


def test_invalid_ssl_boolean_warns_and_selects_https(monkeypatch):
    # An unparsable CONSUL_HTTP_SSL must not silently pick plaintext: the
    # token fallback would still apply and be sent over http.
    monkeypatch.setenv("CONSUL_HTTP_SSL", "maybe")
    assert _consul.env_consul_scheme() == "https"
    warnings = get_warning_messages()
    assert len(warnings) == 1
    assert "CONSUL_HTTP_SSL" in warnings[0]
    # a value in the wrong variable may be a credential, never echo it
    assert "maybe" not in warnings[0]


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


# The cases below run the spec through ansible-core's own argument handling,
# pinning the fallback contract itself rather than the callables in isolation.


def validate_spec():
    return ModuleArgumentSpecValidator(_consul.AUTH_ARGUMENTS_SPEC).validate({})


def test_spec_resolves_env(monkeypatch):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", "https://consul.example.com:8501")
    monkeypatch.setenv("CONSUL_HTTP_TOKEN", "tok")
    monkeypatch.setenv("CONSUL_HTTP_SSL_VERIFY", "false")
    monkeypatch.setenv("CONSUL_CACERT", "/etc/ssl/ca.pem")
    result = validate_spec()
    assert result.error_messages == []
    parameters = result.validated_parameters
    assert parameters["host"] == "consul.example.com"
    assert parameters["port"] == 8501
    assert parameters["scheme"] == "https"
    assert parameters["token"] == "tok"
    assert parameters["validate_certs"] is False
    assert parameters["ca_path"] == "/etc/ssl/ca.pem"


def test_spec_defaults_without_env():
    result = validate_spec()
    assert result.error_messages == []
    parameters = result.validated_parameters
    assert parameters["host"] == "localhost"
    assert parameters["port"] == 8500
    assert parameters["scheme"] == "http"
    assert parameters["token"] is None


@pytest.mark.parametrize("addr", MALFORMED_ADDR_CASES)
def test_spec_survives_malformed_addr(monkeypatch, addr):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", addr)
    result = validate_spec()
    assert result.error_messages == []
    assert result.validated_parameters["host"] == "localhost"
    assert result.validated_parameters["port"] == 8500
    assert len(get_warning_messages()) == 1


def test_spec_survives_invalid_ssl_boolean(monkeypatch):
    monkeypatch.setenv("CONSUL_HTTP_SSL", "maybe")
    result = validate_spec()
    assert result.error_messages == []
    assert result.validated_parameters["scheme"] == "https"
    assert len(get_warning_messages()) == 1


def test_spec_rejects_invalid_ssl_verify_cleanly(monkeypatch):
    # garbage CONSUL_HTTP_SSL_VERIFY reaches the type='bool' coercion and must
    # surface as a clean validation error, never an exception
    monkeypatch.setenv("CONSUL_HTTP_SSL_VERIFY", "maybe")
    result = validate_spec()
    assert result.error_messages

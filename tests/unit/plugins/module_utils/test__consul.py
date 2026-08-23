# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import pytest
from ansible.module_utils.basic import AnsibleFallbackNotFound
from ansible.module_utils.common.arg_spec import ModuleArgumentSpecValidator

from ansible_collections.community.general.plugins.module_utils import _consul

CONSUL_ENV_VARS = (
    "CONSUL_HTTP_ADDR",
    "CONSUL_HTTP_SSL",
    "CONSUL_HTTP_SSL_VERIFY",
    "CONSUL_HTTP_TOKEN",
    "CONSUL_CACERT",
)


@pytest.fixture(autouse=True)
def scrub_consul_env(monkeypatch):
    for name in CONSUL_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


class FailJson(Exception):
    pass


class ModuleStub:
    """Just enough AnsibleModule for resolve_connection_params."""

    def __init__(self, params):
        self.params = params
        self.fail_msg = None
        self.no_log_values = set()

    def fail_json(self, msg, **kwargs):
        self.fail_msg = msg
        raise FailJson(msg)


def resolve(explicit=None):
    """Run the real argument spec, then the resolution, like a module does."""
    result = ModuleArgumentSpecValidator(_consul.AUTH_ARGUMENTS_SPEC).validate(explicit or {})
    assert result.error_messages == []
    module = ModuleStub(dict(result.validated_parameters))
    _consul.resolve_connection_params(module)
    return module.params


URL_CASES = [
    # (url, host, port, scheme)
    ("consul.example.com:8501", "consul.example.com", 8501, "http"),
    ("http://consul.example.com:8501", "consul.example.com", 8501, "http"),
    ("https://consul.example.com:8501", "consul.example.com", 8501, "https"),
    # each component is optional and falls back on its own
    ("consul.example.com", "consul.example.com", 8500, "http"),
    ("https://consul.example.com", "consul.example.com", 8500, "https"),
    ("https://consul.example.com/", "consul.example.com", 8500, "https"),
    # IPv6 addresses stay bracketed so the composed URL is valid
    ("[2001:db8::1]:8501", "[2001:db8::1]", 8501, "http"),
    ("https://[2001:db8::1]", "[2001:db8::1]", 8500, "https"),
]


@pytest.mark.parametrize("url, host, port, scheme", URL_CASES)
def test_url_option_components(url, host, port, scheme):
    params = resolve({"url": url})
    assert (params["host"], params["port"], params["scheme"]) == (host, port, scheme)


@pytest.mark.parametrize("url, host, port, scheme", URL_CASES)
def test_url_environment_components(monkeypatch, url, host, port, scheme):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", url)
    params = resolve()
    assert (params["host"], params["port"], params["scheme"]) == (host, port, scheme)


def test_defaults_without_url():
    params = resolve()
    assert (params["host"], params["port"], params["scheme"]) == ("localhost", 8500, "http")


EXPLICIT_WINS_CASES = [
    ({"host": "explicit.example.com"}, "explicit.example.com", 8501, "https"),
    ({"port": 9999}, "env.example.com", 9999, "https"),
    ({"scheme": "http"}, "env.example.com", 8501, "http"),
    (
        {"host": "explicit.example.com", "port": 9999, "scheme": "http"},
        "explicit.example.com",
        9999,
        "http",
    ),
]


@pytest.mark.parametrize("explicit, host, port, scheme", EXPLICIT_WINS_CASES)
def test_explicit_options_win_over_url(monkeypatch, explicit, host, port, scheme):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", "https://env.example.com:8501")
    params = resolve(explicit)
    assert (params["host"], params["port"], params["scheme"]) == (host, port, scheme)


def test_url_option_wins_over_environment(monkeypatch):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", "http://environment.example.com:8500")
    params = resolve({"url": "https://option.example.com:8501"})
    assert (params["host"], params["port"], params["scheme"]) == ("option.example.com", 8501, "https")


SSL_CASES = [
    # (CONSUL_HTTP_SSL, url, expected scheme)
    ("true", None, "https"),
    ("1", None, "https"),
    ("yes", None, "https"),
    # a true value selects https even when the address says http
    ("true", "http://consul.example.com:8500", "https"),
    # a false value does not downgrade an https address
    ("false", "https://consul.example.com:8500", "https"),
    ("false", "http://consul.example.com:8500", "http"),
    ("false", None, "http"),
    # an empty variable counts as unset, like the consul CLI treats it
    ("", "https://consul.example.com:8500", "https"),
]


@pytest.mark.parametrize("tls, url, scheme", SSL_CASES)
def test_consul_http_ssl(monkeypatch, tls, url, scheme):
    monkeypatch.setenv("CONSUL_HTTP_SSL", tls)
    if url is not None:
        monkeypatch.setenv("CONSUL_HTTP_ADDR", url)
    assert resolve()["scheme"] == scheme


def test_explicit_scheme_wins_over_consul_http_ssl(monkeypatch):
    monkeypatch.setenv("CONSUL_HTTP_SSL", "true")
    assert resolve({"scheme": "http"})["scheme"] == "http"


# Addresses these modules cannot use fail instead of silently connecting
# somewhere else. Only shapes every supported Python rejects belong in the
# parse-failure cases: newer interpreters reject more bracket forms.
UNUSABLE_URL_CASES = [
    ("unix:///var/run/consul.sock", "unsupported scheme"),
    ("ftp://consul.example.com:8500", "unsupported scheme"),
    ("https://consul.example.com:8500/prefix", "must not contain a path"),
    ("https://consul.example.com:8500?dc=dc1", "must not contain a query"),
    ("https://user:pass@consul.example.com:8500", "must not contain credentials"),
    ("https://", "does not contain a host"),
    ("http://:8500", "does not contain a host"),
    ("consul.example.com:notaport", "cannot be parsed"),
    ("consul.example.com:99999", "cannot be parsed"),
    ("2001:db8::1", "cannot be parsed"),
    ("[::1", "cannot be parsed"),
]


@pytest.mark.parametrize("url, reason", UNUSABLE_URL_CASES)
def test_unusable_url_option_fails(url, reason):
    with pytest.raises(FailJson) as exc:
        resolve({"url": url})
    assert reason in str(exc.value)
    # the address may embed credentials, so the failure must not repeat it
    assert url not in str(exc.value)


@pytest.mark.parametrize("url, reason", UNUSABLE_URL_CASES)
def test_unusable_url_environment_fails(monkeypatch, url, reason):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", url)
    with pytest.raises(FailJson) as exc:
        resolve()
    assert reason in str(exc.value)
    assert url not in str(exc.value)


def test_parse_failure_does_not_reuse_the_underlying_message(monkeypatch):
    # The message for a netloc that fails NFKC normalization quotes the whole
    # netloc, credentials included, so it must not be passed on.
    monkeypatch.setenv("CONSUL_HTTP_ADDR", "http://user:s3cr3t@consul℀.example.com:8500")
    with pytest.raises(FailJson) as exc:
        resolve()
    assert "cannot be parsed" in str(exc.value)
    assert "s3cr3t" not in str(exc.value)


@pytest.mark.parametrize("url, reason", UNUSABLE_URL_CASES)
def test_unusable_url_is_ignored_when_nothing_is_needed(monkeypatch, url, reason):
    # A task that spells out its connection must not be broken by an address
    # exported for the consul CLI that these modules happen not to support.
    monkeypatch.setenv("CONSUL_HTTP_ADDR", url)
    params = resolve({"host": "consul.example.com", "port": 8501, "scheme": "https"})
    assert (params["host"], params["port"], params["scheme"]) == ("consul.example.com", 8501, "https")


def test_invalid_consul_http_ssl_is_ignored_when_scheme_is_set(monkeypatch):
    monkeypatch.setenv("CONSUL_HTTP_SSL", "maybe")
    params = resolve({"host": "consul.example.com", "port": 8501, "scheme": "https"})
    assert params["scheme"] == "https"


MASKING_CASES = [
    # a url given as an option is echoed back with the result, so a password in
    # it has to be registered for masking whatever else happens to the value
    "https://user:s3cr3t@consul.example.com:8501",
    "http://user:s3cr3t@consul\u2100.example.com:8500",
    "http://user:s3cr3t@[::1",
    "http://user:s3cr3t@consul.example.com:notaport",
]


@pytest.mark.parametrize("url", MASKING_CASES)
def test_password_in_the_url_option_is_registered_for_masking(url):
    result = ModuleArgumentSpecValidator(_consul.AUTH_ARGUMENTS_SPEC).validate({"url": url})
    module = ModuleStub(dict(result.validated_parameters))
    with pytest.raises(FailJson):
        _consul.resolve_connection_params(module)
    assert "s3cr3t" in module.no_log_values


@pytest.mark.parametrize("url", MASKING_CASES)
def test_password_in_the_url_option_is_registered_even_when_unused(url):
    # host, port and scheme are all set, so the url is never parsed, but it is
    # still echoed back with the result
    result = ModuleArgumentSpecValidator(_consul.AUTH_ARGUMENTS_SPEC).validate(
        {"url": url, "host": "consul.example.com", "port": 8501, "scheme": "https"}
    )
    module = ModuleStub(dict(result.validated_parameters))
    _consul.resolve_connection_params(module)
    assert "s3cr3t" in module.no_log_values


@pytest.mark.parametrize("url", MASKING_CASES)
def test_environment_address_never_reaches_the_module_arguments(monkeypatch, url):
    # CONSUL_HTTP_ADDR is read in code rather than through a fallback, so a
    # password exported for the consul CLI is never copied where ansible-core
    # echoes it back
    monkeypatch.setenv("CONSUL_HTTP_ADDR", url)
    result = ModuleArgumentSpecValidator(_consul.AUTH_ARGUMENTS_SPEC).validate({})
    assert result.validated_parameters["url"] is None


URL_PASSWORD_CASES = [
    ("https://user:s3cr3t@consul.example.com:8501", "s3cr3t"),
    ("user:s3cr3t@consul.example.com:8501", "s3cr3t"),
    ("http://user:s3cr3t@[::1", "s3cr3t"),
    # the last @ separates the userinfo, and the first colon in it separates
    # the password, so the password is everything between, as urlparse reads it
    ("http://user:p@ss:w0rd@consul.example.com:8501", "p@ss:w0rd"),
    ("https://consul.example.com:8501", None),
    ("https://user@consul.example.com:8501", None),
    ("https://user:@consul.example.com:8501", None),
    ("consul.example.com:8501", None),
    ("[::1", None),
]


@pytest.mark.parametrize("url, password", URL_PASSWORD_CASES)
def test_url_password(url, password):
    assert _consul.url_password(url) == password


@pytest.mark.parametrize("tls", ["maybe", "2", "tru", "null"])
def test_invalid_consul_http_ssl_fails(monkeypatch, tls):
    monkeypatch.setenv("CONSUL_HTTP_SSL", tls)
    with pytest.raises(FailJson) as exc:
        resolve()
    assert "CONSUL_HTTP_SSL" in str(exc.value)


@pytest.mark.parametrize("url", ["", "   "])
def test_blank_url_is_unset(monkeypatch, url):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", url)
    params = resolve()
    assert (params["host"], params["port"], params["scheme"]) == ("localhost", 8500, "http")


def test_surrounding_whitespace_is_tolerated(monkeypatch):
    monkeypatch.setenv("CONSUL_HTTP_ADDR", "  https://consul.example.com:8501  ")
    params = resolve()
    assert (params["host"], params["port"], params["scheme"]) == ("consul.example.com", 8501, "https")


NONEMPTY_FALLBACK_CASES = [
    ("token", "CONSUL_HTTP_TOKEN", "s3cr3t"),
    ("ca_path", "CONSUL_CACERT", "/etc/ssl/ca.pem"),
]


@pytest.mark.parametrize("option, name, value", NONEMPTY_FALLBACK_CASES)
def test_environment_fills_option(monkeypatch, option, name, value):
    monkeypatch.setenv(name, value)
    assert resolve()[option] == value


@pytest.mark.parametrize("option, name, value", NONEMPTY_FALLBACK_CASES)
def test_empty_environment_variable_counts_as_unset(monkeypatch, option, name, value):
    monkeypatch.setenv(name, "")
    assert resolve()[option] is None


def test_validate_certs_from_environment(monkeypatch):
    monkeypatch.setenv("CONSUL_HTTP_SSL_VERIFY", "false")
    assert resolve()["validate_certs"] is False


def test_validate_certs_defaults_to_true():
    assert resolve()["validate_certs"] is True


def test_invalid_validate_certs_fails_cleanly(monkeypatch):
    # garbage reaches the type='bool' coercion and must surface as a clean
    # validation error rather than an exception
    monkeypatch.setenv("CONSUL_HTTP_SSL_VERIFY", "maybe")
    result = ModuleArgumentSpecValidator(_consul.AUTH_ARGUMENTS_SPEC).validate({})
    assert result.error_messages


def test_nonempty_env_fallback(monkeypatch):
    monkeypatch.setenv("CONSUL_HTTP_TOKEN", "s3cr3t")
    assert _consul.nonempty_env_fallback("CONSUL_HTTP_TOKEN") == "s3cr3t"


@pytest.mark.parametrize("value", [None, ""])
def test_nonempty_env_fallback_unset(monkeypatch, value):
    if value is not None:
        monkeypatch.setenv("CONSUL_HTTP_TOKEN", value)
    with pytest.raises(AnsibleFallbackNotFound):
        _consul.nonempty_env_fallback("CONSUL_HTTP_TOKEN")

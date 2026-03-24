# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json

import pytest
from pytest_mock import MockerFixture

dns = pytest.importorskip("dns")

import dns.exception
import dns.message
import dns.name
import dns.rcode
import dns.rdata
import dns.rdataclass
import dns.rdatatype
import dns.resolver
import dns.update
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

import ansible_collections.community.general.plugins.modules.nsupdate as nsupdate_module
from ansible_collections.community.general.plugins.module_utils import deps

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def register_deps():
    """Re-register the dnspython dep after deps_cleanup clears _deps before each test."""
    with deps.declare("dnspython"):
        pass


@pytest.fixture
def run_module(capfd):
    def _run(args):
        with set_module_args(args):
            with pytest.raises(SystemExit):
                nsupdate_module.main()
        out, dummy = capfd.readouterr()
        return json.loads(out)

    return _run


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE_PARAMS = dict(
    server="10.1.1.1",
    record="ansible",
    zone="example.org",
    key_name="testkey",
    key_secret="dGVzdA==",
    key_algorithm="hmac-md5",
    type="A",
    value=["192.168.1.1"],
    ttl=3600,
    state="present",
    protocol="tcp",
    port=53,
)

# Used for zone auto-detection tests — no zone, absolute record
PARAMS_NO_ZONE = {**BASE_PARAMS, "record": "ansible.example.org.", "zone": None}


def make_update_response(query, rcode_val=dns.rcode.NOERROR):
    """Build a DNS response for an UPDATE or prerequisite check."""
    response = dns.message.make_response(query)
    response.set_rcode(rcode_val)
    return response


def make_soa_response(query, zone_name_text):
    """Build a DNS response with an SOA in the authority section (zone lookup)."""
    response = dns.message.make_response(query)
    rrset = response.find_rrset(
        dns.message.AUTHORITY,
        dns.name.from_text(zone_name_text),
        dns.rdataclass.IN,
        dns.rdatatype.SOA,
        create=True,
    )
    soa = dns.rdata.from_text(
        dns.rdataclass.IN,
        dns.rdatatype.SOA,
        "ns1.example.org. admin.example.org. 2024010101 3600 900 604800 300",
    )
    rrset.add(soa, ttl=3600)
    return response


def make_a_response(query, addresses, ttl=3600):
    """Build a DNS response with A records in the answer section (TTL lookup)."""
    response = dns.message.make_response(query)
    name = query.question[0].name
    rrset = response.find_rrset(dns.message.ANSWER, name, dns.rdataclass.IN, dns.rdatatype.A, create=True)
    for addr in addresses:
        rrset.add(dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, addr), ttl=ttl)
    return response


def route_query(query, update_rcodes):
    """Dispatch a dns.query.tcp call to the right response builder.

    UPDATE queries consume the next rcode from update_rcodes.
    SOA queries (zone lookup) get a fixed example.org. SOA response.
    Other queries (A record / TTL lookup) get an A response with the base value.
    """
    if isinstance(query, dns.update.Update):
        return make_update_response(query, update_rcodes.pop(0))
    if query.question and query.question[0].rdtype == dns.rdatatype.SOA:
        return make_soa_response(query, "example.org.")
    return make_a_response(query, ["192.168.1.1"], ttl=3600)


# ---------------------------------------------------------------------------
# resolve_server()
# ---------------------------------------------------------------------------


def test_resolve_server_ipv4(mocker: MockerFixture, run_module) -> None:
    """IPv4 server is used directly without any DNS resolution."""
    rcodes = [dns.rcode.NXDOMAIN, dns.rcode.NOERROR]
    mocker.patch("dns.query.tcp", side_effect=lambda q, *a, **kw: route_query(q, rcodes))
    result = run_module(BASE_PARAMS)
    assert result["changed"] is True


def test_resolve_server_ipv6(mocker: MockerFixture, run_module) -> None:
    """IPv6 server is used directly without any DNS resolution."""
    rcodes = [dns.rcode.NXDOMAIN, dns.rcode.NOERROR]
    mocker.patch("dns.query.tcp", side_effect=lambda q, *a, **kw: route_query(q, rcodes))
    result = run_module({**BASE_PARAMS, "server": "2001:db8::1"})
    assert result["changed"] is True


def test_resolve_server_fqdn(mocker: MockerFixture, run_module) -> None:
    """FQDN server is resolved to an IP address before making DNS queries."""
    MockResolver = mocker.patch("dns.resolver.Resolver")
    MockResolver.return_value.resolve.side_effect = (
        lambda name, rdatatype: ["192.168.1.1"]
        if rdatatype == dns.rdatatype.A
        else (_ for _ in ()).throw(dns.resolver.NoAnswer())
    )
    rcodes = [dns.rcode.NXDOMAIN, dns.rcode.NOERROR]
    mocker.patch("dns.query.tcp", side_effect=lambda q, *a, **kw: route_query(q, rcodes))
    result = run_module({**BASE_PARAMS, "server": "ns1.example.org"})
    assert result["changed"] is True


def test_resolve_server_fqdn_unresolvable_fails(mocker: MockerFixture, run_module) -> None:
    """Module fails with a clear message when the FQDN server cannot be resolved."""
    MockResolver = mocker.patch("dns.resolver.Resolver")
    MockResolver.return_value.resolve.side_effect = dns.resolver.NXDOMAIN
    result = run_module({**BASE_PARAMS, "server": "nonexistent.example.org"})
    assert result["failed"] is True
    assert "Failed to resolve" in result["msg"]


# ---------------------------------------------------------------------------
# lookup_zone()
# ---------------------------------------------------------------------------


def test_lookup_zone_auto_detects_zone(mocker: MockerFixture, run_module) -> None:
    """Zone is correctly auto-detected from the SOA in the authority section."""
    rcodes = [dns.rcode.NXDOMAIN, dns.rcode.NOERROR]
    mocker.patch("dns.query.tcp", side_effect=lambda q, *a, **kw: route_query(q, rcodes))
    result = run_module(PARAMS_NO_ZONE)
    assert result["record"]["zone"] == "example.org."


def test_lookup_zone_tsig_key_attached_when_keyring_set(mocker: MockerFixture, run_module) -> None:
    """Zone lookup attaches the TSIG key so split-view DNS servers pick the right view.

    Regression test for issue #749.
    """
    soa_queries = []
    rcodes = [dns.rcode.NXDOMAIN, dns.rcode.NOERROR]

    def mock_tcp(query, *args, **kwargs):
        if not isinstance(query, dns.update.Update):
            soa_queries.append(query)
        return route_query(query, rcodes)

    mocker.patch("dns.query.tcp", side_effect=mock_tcp)
    run_module(PARAMS_NO_ZONE)

    assert soa_queries, "expected at least one SOA query for zone lookup"
    assert soa_queries[0].keyring is not None, "SOA query must carry the TSIG key"


def test_lookup_zone_no_tsig_without_key(mocker: MockerFixture, run_module) -> None:
    """Zone lookup sends no TSIG key when no key_name is configured."""
    soa_queries = []
    rcodes = [dns.rcode.NXDOMAIN, dns.rcode.NOERROR]

    def mock_tcp(query, *args, **kwargs):
        if not isinstance(query, dns.update.Update):
            soa_queries.append(query)
        return route_query(query, rcodes)

    mocker.patch("dns.query.tcp", side_effect=mock_tcp)
    run_module({**PARAMS_NO_ZONE, "key_name": None, "key_secret": None})

    assert soa_queries, "expected at least one SOA query for zone lookup"
    assert soa_queries[0].keyring is None, "SOA query must not carry a TSIG key"


# ---------------------------------------------------------------------------
# state=present
# ---------------------------------------------------------------------------


def test_creates_record_when_absent(mocker: MockerFixture, run_module) -> None:
    """Record is created and changed=True when it does not exist."""
    rcodes = [dns.rcode.NXDOMAIN, dns.rcode.NOERROR]
    mocker.patch("dns.query.tcp", side_effect=lambda q, *a, **kw: route_query(q, rcodes))
    result = run_module(BASE_PARAMS)
    assert result["changed"] is True


def test_no_change_when_record_matches(mocker: MockerFixture, run_module) -> None:
    """No change when the record already exists with the correct value and TTL."""
    mocker.patch(
        "dns.query.tcp", side_effect=lambda q, *a, **kw: route_query(q, [dns.rcode.NOERROR, dns.rcode.NOERROR])
    )
    result = run_module(BASE_PARAMS)
    assert result["changed"] is False


# ---------------------------------------------------------------------------
# state=absent
# ---------------------------------------------------------------------------


def test_deletes_record_when_present(mocker: MockerFixture, run_module) -> None:
    """Record is deleted and changed=True when it exists."""
    rcodes = [dns.rcode.NOERROR, dns.rcode.NOERROR]
    mocker.patch("dns.query.tcp", side_effect=lambda q, *a, **kw: route_query(q, rcodes))
    result = run_module({**BASE_PARAMS, "state": "absent"})
    assert result["changed"] is True


def test_no_change_when_record_already_absent(mocker: MockerFixture, run_module) -> None:
    """No change when the record does not exist and state=absent."""
    rcodes = [dns.rcode.NXDOMAIN]
    mocker.patch("dns.query.tcp", side_effect=lambda q, *a, **kw: route_query(q, rcodes))
    result = run_module({**BASE_PARAMS, "state": "absent"})
    assert result["changed"] is False


# ---------------------------------------------------------------------------
# check_mode
# ---------------------------------------------------------------------------


def test_check_mode_reports_changed_without_updating(mocker: MockerFixture, run_module) -> None:
    """Check mode returns changed=True but does not send the actual DNS update."""
    tcp_mock = mocker.patch(
        "dns.query.tcp",
        return_value=make_update_response(dns.update.Update("example.org."), dns.rcode.NXDOMAIN),
    )
    result = run_module({**BASE_PARAMS, "_ansible_check_mode": True})
    assert result["changed"] is True
    assert tcp_mock.call_count == 1, "check mode must not send the update"

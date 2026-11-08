# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.modules import ipa_dnsrecord

BASE_ARGS = dict(ipa_host="ipa.example.com", ipa_pass="secret")


@pytest.fixture
def ipa_post(mocker):
    """Patch the IPA client; the returned function sets the current record and gives back the _post_json mock."""
    mocker.patch.object(ipa_dnsrecord.DNSRecordIPAClient, "login")

    def setup(current):
        def post_json(method, name, item):
            if method in ("dnsrecord_find", "dnsrecord_show"):
                return dict(current)
            return {}

        return mocker.patch.object(ipa_dnsrecord.DNSRecordIPAClient, "_post_json", side_effect=post_json)

    return setup


def run_module(args, capsys):
    with set_module_args(dict(BASE_ARGS, **args)):
        with pytest.raises(SystemExit):
            ipa_dnsrecord.main()
    return json.loads(capsys.readouterr().out)


def change_calls(mock_post):
    return [
        c.kwargs for c in mock_post.call_args_list if c.kwargs["method"] not in ("dnsrecord_find", "dnsrecord_show")
    ]


def test_fqdn_values_appends_dot(ipa_post, capsys):
    mock_post = ipa_post({})
    result = run_module(
        dict(
            zone_name="2.168.192.in-addr.arpa",
            record_name="5",
            record_type="PTR",
            record_value="host.example.com",
            fqdn_values=True,
        ),
        capsys,
    )

    assert result["changed"] is True
    assert change_calls(mock_post) == [
        dict(
            method="dnsrecord_add",
            name="2.168.192.in-addr.arpa",
            item=dict(idnsname="5", ptr_part_hostname="host.example.com."),
        )
    ]


def test_fqdn_values_default_keeps_value(ipa_post, capsys):
    mock_post = ipa_post({})
    result = run_module(
        dict(zone_name="example.com", record_name="www", record_type="CNAME", record_value="web"),
        capsys,
    )

    assert result["changed"] is True
    assert change_calls(mock_post) == [
        dict(method="dnsrecord_add", name="example.com", item=dict(idnsname="www", cname_part_hostname="web"))
    ]


def test_fqdn_values_mx_adds_only_missing(ipa_post, capsys):
    mock_post = ipa_post({"idnsname": ["@"], "mxrecord": ["1 mx1.example.com."]})
    result = run_module(
        dict(
            zone_name="example.com",
            record_name="@",
            record_type="MX",
            record_values=["1 mx1.example.com", "2 mx2.example.com."],
            exclusive=False,
            fqdn_values=True,
        ),
        capsys,
    )

    assert result["changed"] is True
    assert change_calls(mock_post) == [
        dict(method="dnsrecord_add", name="example.com", item=dict(idnsname="@", mxrecord="2 mx2.example.com."))
    ]


def test_fqdn_values_no_change(ipa_post, capsys):
    mock_post = ipa_post({"idnsname": ["www"], "cnamerecord": ["web01.example.org."]})
    result = run_module(
        dict(
            zone_name="example.com",
            record_name="www",
            record_type="CNAME",
            record_value="web01.example.org",
            fqdn_values=True,
        ),
        capsys,
    )

    assert result["changed"] is False
    assert change_calls(mock_post) == []


def test_fqdn_values_removes_matching(ipa_post, capsys):
    mock_post = ipa_post({"idnsname": ["5"], "ptrrecord": ["host.example.com.", "other.example.com."]})
    result = run_module(
        dict(
            zone_name="2.168.192.in-addr.arpa",
            record_name="5",
            record_type="PTR",
            record_value="host.example.com",
            state="absent",
            exclusive=False,
            fqdn_values=True,
        ),
        capsys,
    )

    assert result["changed"] is True
    assert change_calls(mock_post) == [
        dict(
            method="dnsrecord_del",
            name="2.168.192.in-addr.arpa",
            item=dict(idnsname="5", ptrrecord=["host.example.com."]),
        )
    ]


def test_fqdn_values_other_record_type_unchanged(ipa_post, capsys):
    mock_post = ipa_post({})
    result = run_module(
        dict(zone_name="example.com", record_name="txt", record_type="TXT", record_value="some text", fqdn_values=True),
        capsys,
    )

    assert result["changed"] is True
    assert change_calls(mock_post) == [
        dict(method="dnsrecord_add", name="example.com", item=dict(idnsname="txt", txtrecord="some text"))
    ]

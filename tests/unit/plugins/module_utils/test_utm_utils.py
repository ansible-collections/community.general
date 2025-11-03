# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c) 2018, Johannes Brunswicker <johannes.brunswicker@gmail.com>
#
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

from ansible_collections.community.general.plugins.module_utils.utm_utils import UTM


class FakeModule:
    def __init__(self, params):
        self.params = params


def test_combine_headers_returns_only_default():
    expected = {"Accept": "application/json", "Content-type": "application/json"}
    module = FakeModule(
        params={
            "utm_protocol": "utm_protocol",
            "utm_host": "utm_host",
            "utm_port": 1234,
            "utm_token": "utm_token",
            "name": "FakeName",
            "headers": {},
        }
    )
    result = UTM(module, "endpoint", [])._combine_headers()
    assert result == expected


def test_combine_headers_returns_only_default2():
    expected = {"Accept": "application/json", "Content-type": "application/json"}
    module = FakeModule(
        params={
            "utm_protocol": "utm_protocol",
            "utm_host": "utm_host",
            "utm_port": 1234,
            "utm_token": "utm_token",
            "name": "FakeName",
        }
    )
    result = UTM(module, "endpoint", [])._combine_headers()
    assert result == expected


def test_combine_headers_returns_combined():
    expected = {"Accept": "application/json", "Content-type": "application/json", "extraHeader": "extraHeaderValue"}
    module = FakeModule(
        params={
            "utm_protocol": "utm_protocol",
            "utm_host": "utm_host",
            "utm_port": 1234,
            "utm_token": "utm_token",
            "name": "FakeName",
            "headers": {"extraHeader": "extraHeaderValue"},
        }
    )
    result = UTM(module, "endpoint", [])._combine_headers()
    assert result == expected

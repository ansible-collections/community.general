# Copyright (c) 2022 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import os

from ansible_collections.community.general.plugins.lookup.onepassword import (
    OnePassCLIv2,
)


def load_file(file):
    with open(os.path.join(os.path.dirname(__file__), "onepassword_fixtures", file)) as f:
        return json.loads(f.read())


# Intentionally excludes metadata leaf nodes that would exist in real output if not relevant.
MOCK_ENTRIES = {
    OnePassCLIv2: [
        {
            "vault_name": "Test Vault",
            "queries": [
                "ywvdbojsguzgrgnokmcxtydgdv",
                "Authy Backup",
            ],
            "expected": ["OctoberPoppyNuttyDraperySabbath", "OctoberPoppyNuttyDraperySabbath"],
            "output": load_file("v2_out_01.json"),
        },
        {
            # Request a custom field where ID and label are different
            "vault_name": "Test Vault",
            "queries": ["Dummy Login"],
            "kwargs": {
                "field": "password1",
            },
            "expected": ["data in custom field"],
            "output": load_file("v2_out_02.json"),
        },
        {
            # Request data from a custom section
            "vault_name": "Test Vault",
            "queries": ["Duplicate Sections"],
            "kwargs": {
                "field": "s2 text",
                "section": "Section 2",
            },
            "expected": ["first value"],
            "output": load_file("v2_out_03.json"),
        },
        {
            # Request data from an omitted value (label lookup, no section)
            "vault_name": "Test Vault",
            "queries": ["Omitted values"],
            "kwargs": {
                "field": "label-without-value",
            },
            "expected": [""],
            "output": load_file("v2_out_04.json"),
        },
        {
            # Request data from an omitted value (id lookup, no section)
            "vault_name": "Test Vault",
            "queries": ["Omitted values"],
            "kwargs": {
                "field": "67890q7mspf4x6zrlw3qejn7m",
            },
            "expected": [""],
            "output": load_file("v2_out_04.json"),
        },
        {
            # Request data from an omitted value (label lookup, with section)
            "vault_name": "Test Vault",
            "queries": ["Omitted values"],
            "kwargs": {"field": "section-label-without-value", "section": "Section-Without-Values"},
            "expected": [""],
            "output": load_file("v2_out_04.json"),
        },
        {
            # Request data from an omitted value (id lookup, with section)
            "vault_name": "Test Vault",
            "queries": ["Omitted values"],
            "kwargs": {
                "field": "123345q7mspf4x6zrlw3qejn7m",
                "section": "section-without-values",
            },
            "expected": [""],
            "output": load_file("v2_out_04.json"),
        },
        {
            # Query item without section by lowercase id (case matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "lowercaseid",
            },
            "expected": ["lowercaseid"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item without section by lowercase id (case not matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "LOWERCASEID",
            },
            "expected": ["lowercaseid"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item without section by lowercase label (case matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "lowercaselabel",
            },
            "expected": ["lowercaselabel"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item without section by lowercase label (case not matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "LOWERCASELABEL",
            },
            "expected": ["lowercaselabel"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item without section by mixed case id (case matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "MiXeDcAsEiD",
            },
            "expected": ["mixedcaseid"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item without section by mixed case id (case not matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "mixedcaseid",
            },
            "expected": ["mixedcaseid"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item without section by mixed case label (case matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "MiXeDcAsElAbEl",
            },
            "expected": ["mixedcaselabel"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item without section by mixed case label (case not matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "mixedcaselabel",
            },
            "expected": ["mixedcaselabel"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item with section by lowercase id (case matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "sectionlowercaseid",
                "section": "section-with-values",
            },
            "expected": ["sectionlowercaseid"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item with section by lowercase id (case not matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "SECTIONLOWERCASEID",
                "section": "section-with-values",
            },
            "expected": ["sectionlowercaseid"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item with section by lowercase label (case matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "sectionlowercaselabel",
                "section": "section-with-values",
            },
            "expected": ["sectionlowercaselabel"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item with section by lowercase label (case not matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "SECTIONLOWERCASELABEL",
                "section": "section-with-values",
            },
            "expected": ["sectionlowercaselabel"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item with section by lowercase id (case matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "SeCtIoNmIxEdCaSeId",
                "section": "section-with-values",
            },
            "expected": ["sectionmixedcaseid"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item with section by lowercase id (case not matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "sectionmixedcaseid",
                "section": "section-with-values",
            },
            "expected": ["sectionmixedcaseid"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item with section by lowercase label (case matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "SeCtIoNmIxEdCaSeLaBeL",
                "section": "section-with-values",
            },
            "expected": ["sectionmixedcaselabel"],
            "output": load_file("v2_out_05.json"),
        },
        {
            # Query item with section by lowercase label (case not matching)
            "vault_name": "Test Vault",
            "queries": ["LabelCasing"],
            "kwargs": {
                "field": "sectionmixedcaselabel",
                "section": "section-with-values",
            },
            "expected": ["sectionmixedcaselabel"],
            "output": load_file("v2_out_05.json"),
        },
    ],
}

SSH_KEY_MOCK_ENTRIES = [
    # loads private key in PKCS#8 format by default
    {
        "vault_name": "Personal",
        "queries": ["ssh key"],
        "expected": ["-----BEGIN PRIVATE KEY-----\n..........=\n-----END PRIVATE KEY-----\n"],
        "output": load_file("ssh_key_output.json"),
    },
    # loads private key in PKCS#8 format becasue ssh_format=false
    {
        "vault_name": "Personal",
        "queries": ["ssh key"],
        "kwargs": {
            "ssh_format": False,
        },
        "expected": ["-----BEGIN PRIVATE KEY-----\n..........=\n-----END PRIVATE KEY-----\n"],
        "output": load_file("ssh_key_output.json"),
    },
    # loads private key in ssh format
    {
        "vault_name": "Personal",
        "queries": ["ssh key"],
        "kwargs": {
            "ssh_format": True,
        },
        "expected": ["-----BEGIN OPENSSH PRIVATE KEY-----\r\n.....\r\n-----END OPENSSH PRIVATE KEY-----\r\n"],
        "output": load_file("ssh_key_output.json"),
    },
]

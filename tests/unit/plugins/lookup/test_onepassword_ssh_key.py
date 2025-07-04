# Copyright (c) 2025 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest

from .onepassword_common import SSH_KEY_MOCK_ENTRIES

from ansible.plugins.loader import lookup_loader


@pytest.mark.parametrize(
    ("vault", "queries", "kwargs", "output", "expected"),
    (
        (item["vault_name"], item["queries"], item.get("kwargs", {}), item["output"], item["expected"])
        for item in SSH_KEY_MOCK_ENTRIES
    )
)
def test_ssh_key(mocker, vault, queries, kwargs, output, expected):
    mocker.patch("ansible_collections.community.general.plugins.lookup.onepassword.OnePass.assert_logged_in", return_value=True)
    mocker.patch("ansible_collections.community.general.plugins.lookup.onepassword.OnePassCLIBase._run", return_value=(0, json.dumps(output), ""))

    op_lookup = lookup_loader.get("community.general.onepassword_ssh_key")
    result = op_lookup.run(queries, vault=vault, **kwargs)

    assert result == expected

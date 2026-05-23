# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
from unittest.mock import PropertyMock

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.module_utils._onepassword import OnePasswordConfig
from ansible_collections.community.general.plugins.modules import onepassword_info

from .uthelper import RunCommandMock, TestCaseMock, UTHelper


ITEM_JSON = json.dumps(
    {
        "fields": [
            {"id": "password", "label": "password", "value": "secret123"},
        ]
    }
)


class OnePasswordConfigMock(TestCaseMock):
    name = "onepassword_config"

    def setup(self, mocker):
        mocker.patch.object(
            OnePasswordConfig,
            "config_file_path",
            new_callable=PropertyMock,
            return_value=self.mock_specs.get("config_file_path"),
        )

    def check(self, test_case, results):
        pass


UTHelper.from_module(onepassword_info, __name__, mocks=[RunCommandMock, OnePasswordConfigMock])


def _patch_bin_path(mocker):
    mocker.patch(
        "ansible.module_utils.basic.AnsibleModule.get_bin_path",
        lambda self_, path, *args, **kwargs: f"/testbin/{path}",
    )


def _patch_run_command(mocker, responses):
    mocker.patch(
        "ansible.module_utils.basic.AnsibleModule.run_command",
        side_effect=lambda cmd, **kwargs: next(responses),
    )


def test_get_token_signin(mocker, capfd):
    master_password = "masterpass"
    with set_module_args(
        {
            "search_terms": [{"name": "My Item"}],
            "auto_login": {"subdomain": "mycompany", "master_password": master_password},
        }
    ):
        _patch_bin_path(mocker)
        mocker.patch.object(
            OnePasswordConfig,
            "config_file_path",
            new_callable=PropertyMock,
            return_value="/home/user/.op/config",
        )
        mocker.patch(
            "ansible_collections.community.general.plugins.modules.onepassword_info.os.path.isfile",
            return_value=True,
        )
        _patch_run_command(
            mocker,
            iter(
                [
                    (0, "", ""),  # account list → out empty, not logged in
                    (0, "mytoken\n", ""),  # signin --raw --account mycompany
                    (0, ITEM_JSON, ""),  # item get --format json My Item --session=mytoken
                ]
            ),
        )

        with pytest.raises(SystemExit):
            onepassword_info.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert not result.get("failed"), result.get("msg")
    assert result["onepassword"]["My Item"]["password"] == "secret123"


def test_full_login(mocker, capfd):
    master_password = "masterpass"
    with set_module_args(
        {
            "search_terms": [{"name": "My Item"}],
            "auto_login": {
                "subdomain": "mycompany",
                "username": "user@example.com",
                "secret_key": "mysecretkey",
                "master_password": master_password,
            },
        }
    ):
        _patch_bin_path(mocker)
        mocker.patch.object(
            OnePasswordConfig,
            "config_file_path",
            new_callable=PropertyMock,
            return_value=None,
        )
        _patch_run_command(
            mocker,
            iter(
                [
                    (0, "", ""),  # account list → not logged in
                    (0, "mytoken\n", ""),  # account add --raw --signin → token
                    (0, ITEM_JSON, ""),  # item get --format json My Item --session=mytoken
                ]
            ),
        )

        with pytest.raises(SystemExit):
            onepassword_info.main()

    out, dummy = capfd.readouterr()
    result = json.loads(out)
    assert not result.get("failed"), result.get("msg")
    assert result["onepassword"]["My Item"]["password"] == "secret123"

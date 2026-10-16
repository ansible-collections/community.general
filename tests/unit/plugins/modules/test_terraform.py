# Copyright (c) 2019, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import json
import os

import pytest
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.general.plugins.modules import terraform


def test_terraform_without_argument(capfd):
    with set_module_args({}):
        with pytest.raises(SystemExit):
            terraform.main()

    out, err = capfd.readouterr()
    assert not err
    assert json.loads(out)["failed"]
    assert "project_path" in json.loads(out)["msg"]


class FailJson(Exception):
    pass


class FakeModule:
    def __init__(self):
        self.commands = []

    def fail_json(self, msg, **kwargs):
        raise FailJson(msg)

    def run_command(self, cmd, check_rc=False, cwd=None):
        self.commands.append((cmd, cwd))
        return 0, "", ""


@pytest.mark.parametrize("project_path", ["project", "./project", "/abs/project"])
def test_preflight_validation_accepts_relative_and_absolute_paths(tmp_path, monkeypatch, project_path):
    bin_path = tmp_path / "terraform"
    bin_path.write_text("")
    monkeypatch.chdir(tmp_path)
    if project_path.startswith("/"):
        project_path = str(tmp_path / "abs" / "project")
        (tmp_path / "abs" / "project").mkdir(parents=True)
    else:
        (tmp_path / "project").mkdir(exist_ok=True)

    module = FakeModule()
    terraform.preflight_validation(module, str(bin_path), project_path, "1.5.0")

    assert module.commands == [([str(bin_path), "validate", "-no-color"], project_path)]


@pytest.mark.parametrize("project_path", [None, ""])
def test_preflight_validation_rejects_missing_path(tmp_path, project_path):
    bin_path = tmp_path / "terraform"
    bin_path.write_text("")

    with pytest.raises(FailJson, match="can not be None or ''"):
        terraform.preflight_validation(FakeModule(), str(bin_path), project_path, "1.5.0")


def test_main_resolves_relative_project_path(tmp_path, monkeypatch):
    bin_path = tmp_path / "terraform"
    bin_path.write_text("")
    (tmp_path / "project").mkdir()
    monkeypatch.chdir(tmp_path)
    seen = {}

    def fake_preflight(module, bin_path, project_path, *args, **kwargs):
        seen["project_path"] = project_path
        module.fail_json(msg="stop after preflight")

    monkeypatch.setattr(terraform, "get_version", lambda module, bin_path: "1.5.0")
    monkeypatch.setattr(
        terraform, "get_workspace_context", lambda *args, **kwargs: {"current": "default", "all": ["default"]}
    )
    monkeypatch.setattr(terraform, "preflight_validation", fake_preflight)

    with set_module_args({"project_path": "project", "binary_path": str(bin_path)}):
        with pytest.raises(SystemExit):
            terraform.main()

    assert seen["project_path"] == os.path.join(os.getcwd(), "project")

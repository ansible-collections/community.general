# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest import mock

from ansible_collections.community.general.plugins.modules import pipx


def _helper(application, *, check_mode=False, force=False, inject_packages=None, name="cowsay"):
    helper = mock.Mock()
    helper.module = mock.Mock()
    helper.module.check_mode = check_mode
    helper.vars.application = application
    helper.vars.name = name
    helper.vars.suffix = None
    helper.vars.force = force
    helper.vars.inject_packages = inject_packages
    helper.vars.source = None
    helper.changed = False
    ctx = mock.MagicMock()
    runner_cm = mock.MagicMock()
    runner_cm.__enter__.return_value = ctx
    runner_cm.__exit__.return_value = False
    helper.runner.return_value = runner_cm
    return helper, ctx


def test_uninstall_sets_changed_when_installed():
    helper, _ctx = _helper({"cowsay": {"version": "1.0"}})
    pipx.PipX.state_uninstall(helper)
    assert helper.changed is True


def test_uninstall_unchanged_when_missing():
    helper, _ctx = _helper({})
    pipx.PipX.state_uninstall(helper)
    assert helper.changed is False


def test_inject_sets_changed_when_package_missing():
    helper, _ctx = _helper(
        {"cowsay": {"version": "1.0", "injected": {}}},
        inject_packages=["art"],
    )
    pipx.PipX.state_inject(helper)
    assert helper.changed is True


def test_inject_unchanged_when_package_already_present():
    helper, _ctx = _helper(
        {"cowsay": {"version": "1.0", "injected": {"art": "6.0"}}},
        inject_packages=["art"],
    )
    pipx.PipX.state_inject(helper)
    assert helper.changed is False


def test_uninject_sets_changed_when_package_present():
    helper, _ctx = _helper(
        {"cowsay": {"version": "1.0", "injected": {"art": "6.0"}}},
        inject_packages=["art"],
    )
    pipx.PipX.state_uninject(helper)
    assert helper.changed is True


def test_latest_check_mode_sets_changed_when_installed():
    helper, _ctx = _helper({"cowsay": {"version": "1.0"}}, check_mode=True)
    pipx.PipX.state_latest(helper)
    assert helper.changed is True


def test_upgrade_check_mode_sets_changed_when_installed():
    helper, _ctx = _helper({"cowsay": {"version": "1.0"}}, check_mode=True)
    pipx.PipX.state_upgrade(helper)
    assert helper.changed is True

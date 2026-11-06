# Author: Dexter Le (dextersydney2001@gmail.com)
# Largely adapted from test_redhat_subscription by
# Jiri Hnidek (jhnidek@redhat.com)
#
# Copyright (c) Dexter Le (dextersydney2001@gmail.com)
# Copyright (c) Jiri Hnidek (jhnidek@redhat.com)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json

import pytest

from ansible_collections.community.general.plugins.modules import pacemaker_resource

from .uthelper import RunCommandMock, UTHelper

UTHelper.from_module(pacemaker_resource, __name__, mocks=[RunCommandMock])


# ---------------------------------------------------------------------------
# Runtime-state assertion tests: state=enabled/disabled own the wait/poll loop.
# state=present is a configuration state and must NOT poll status after create.
# ---------------------------------------------------------------------------

NO_MAINTENANCE_OUT = (
    "Cluster Properties: cib-bootstrap-options\n"
    "cluster-infrastructure=corosync\n"
    "cluster-name=hacluster\n"
    "dc-version=2.1.9-1.fc41-7188dbf\n"
    "have-watchdog=false\n"
)


@pytest.fixture
def patch_bin(mocker):
    def mockie(self_, path, *args, **kwargs):
        return f"/testbin/{path}"

    mocker.patch("ansible.module_utils.basic.AnsibleModule.get_bin_path", mockie)


def _run_module(mp, args):
    mp.setattr(
        "ansible.module_utils.basic._ANSIBLE_ARGS",
        json.dumps({"ANSIBLE_MODULE_ARGS": args}).encode(),
    )
    mp.setattr("ansible.module_utils.basic._ANSIBLE_PROFILE", "legacy", raising=False)
    pacemaker_resource.main()


def _warning_msg(w):
    """Return the message text of an Ansible warning.

    New Ansible wraps warnings as dicts with the text at ``event.msg``;
    old Ansible returns the plain string.
    """
    if isinstance(w, dict):
        return w.get("event", {}).get("msg", "")
    return w


@pytest.mark.usefixtures("patch_bin")
def test_present_does_not_poll_runtime_state(mocker, capfd):
    """state=present must be a configuration-only change: no status polling after create.

    Previously state=present blocked until the resource reported Started, conflating a
    CIB mutation with a runtime assertion. This test locks in the corrected semantics.
    """
    mocker.patch("ansible_collections.community.general.plugins.module_utils._pacemaker.time.sleep")

    # Expected call sequence with the fix:
    # 1. initial _get(): pcs resource status → not found (rc=1)
    # 2. state_present: pcs property config → no maintenance (guards the create idempotency check)
    # 3. state_present: pcs resource create → rc=0
    # 4. __quit_module__ _get(): pcs resource status → whatever the current state is (may still be Stopped)
    run_command_calls = [
        (1, "", "Error: resource or tag id 'virtual-ip' not found"),
        (1, NO_MAINTENANCE_OUT, ""),
        (0, "Assumed agent name 'ocf:heartbeat:IPaddr2'", ""),
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Stopped", ""),
    ]

    def side_effect(self_, **kwargs):
        return run_command_calls.pop(0)

    mocker.patch("ansible.module_utils.basic.AnsibleModule.run_command", side_effect=side_effect)

    with pytest.raises(SystemExit):
        with pytest.MonkeyPatch().context() as mp:
            _run_module(
                mp,
                {
                    "state": "present",
                    "name": "virtual-ip",
                    "resource_type": {"resource_name": "IPaddr2"},
                    "resource_option": ["ip=192.168.2.1"],
                },
            )

    out, _err = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is True
    assert result.get("failed") is not True
    # The whole point of the fix: state=present returns without waiting for Started.
    # Every mock call was consumed; no leftover status polls were needed.
    assert run_command_calls == []


@pytest.mark.usefixtures("patch_bin")
def test_present_with_wait_emits_deprecation_warning(mocker, capfd):
    """Setting wait on state=present must trigger a warning; wait is only meaningful for enabled/disabled."""
    mocker.patch("ansible_collections.community.general.plugins.module_utils._pacemaker.time.sleep")

    run_command_calls = [
        (1, "", "Error: resource or tag id 'virtual-ip' not found"),
        (1, NO_MAINTENANCE_OUT, ""),
        (0, "Assumed agent name 'ocf:heartbeat:IPaddr2'", ""),
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Stopped", ""),
    ]

    def side_effect(self_, **kwargs):
        return run_command_calls.pop(0)

    mocker.patch("ansible.module_utils.basic.AnsibleModule.run_command", side_effect=side_effect)

    with pytest.raises(SystemExit):
        with pytest.MonkeyPatch().context() as mp:
            _run_module(
                mp,
                {
                    "state": "present",
                    "name": "virtual-ip",
                    "resource_type": {"resource_name": "IPaddr2"},
                    "resource_option": ["ip=192.168.2.1"],
                    "wait": 30,
                },
            )

    out, _err = capfd.readouterr()
    result = json.loads(out)
    warnings = result.get("warnings") or []
    assert any("'wait' parameter has no effect on state='present'" in _warning_msg(w) for w in warnings), warnings


@pytest.mark.usefixtures("patch_bin")
def test_enabled_race_condition_stopped_then_started(mocker, capfd):
    """state=enabled must poll pcs resource status until Started/Promoted/Unpromoted is seen."""
    mocker.patch("ansible_collections.community.general.plugins.module_utils._pacemaker.time.sleep")

    # Sequence:
    # 1. initial _get(): status → Stopped (already exists, currently disabled)
    # 2. state_enabled: pcs resource enable → rc=0
    # 3. _wait_for_runtime_state maintenance check: property config → no maintenance
    # 4. poll 1: status → Stopped (not yet running)
    # 5. poll 2: status → Started
    # 6. __quit_module__ _get(): status → Started
    run_command_calls = [
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Stopped (disabled)", ""),
        (0, "", ""),
        (1, NO_MAINTENANCE_OUT, ""),
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Stopped", ""),
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Started", ""),
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Started", ""),
    ]

    def side_effect(self_, **kwargs):
        return run_command_calls.pop(0)

    mocker.patch("ansible.module_utils.basic.AnsibleModule.run_command", side_effect=side_effect)

    with pytest.raises(SystemExit):
        with pytest.MonkeyPatch().context() as mp:
            _run_module(mp, {"state": "enabled", "name": "virtual-ip", "wait": 30})

    out, _err = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is True
    assert result.get("failed") is not True
    assert "Started" in result["value"]


@pytest.mark.usefixtures("patch_bin")
def test_enabled_wait_timeout_raises(mocker, capfd):
    """state=enabled must fail with a timeout message when the resource never reaches a running state."""
    mocker.patch("ansible_collections.community.general.plugins.module_utils._pacemaker.time.sleep")

    monotonic_values = iter([0.0, 999.0])
    mocker.patch(
        "ansible_collections.community.general.plugins.module_utils._pacemaker.time.monotonic",
        side_effect=lambda: next(monotonic_values),
    )

    run_command_calls = [
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Stopped (disabled)", ""),
        (0, "", ""),
        (1, NO_MAINTENANCE_OUT, ""),
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Stopped", ""),
    ]

    def side_effect(self_, **kwargs):
        return run_command_calls.pop(0)

    mocker.patch("ansible.module_utils.basic.AnsibleModule.run_command", side_effect=side_effect)

    with pytest.raises(SystemExit):
        with pytest.MonkeyPatch().context() as mp:
            _run_module(mp, {"state": "enabled", "name": "virtual-ip", "wait": 10})

    out, _err = capfd.readouterr()
    result = json.loads(out)
    assert result.get("failed") is True
    assert "Timed out" in result["msg"]
    assert "virtual-ip" in result["msg"]


@pytest.mark.usefixtures("patch_bin")
def test_disabled_polls_for_stopped(mocker, capfd):
    """state=disabled must poll pcs resource status until Stopped is seen."""
    mocker.patch("ansible_collections.community.general.plugins.module_utils._pacemaker.time.sleep")

    # Sequence:
    # 1. initial _get(): status → Started (currently running)
    # 2. state_disabled: pcs resource disable → rc=0
    # 3. _wait_for_runtime_state maintenance check: property config → no maintenance
    # 4. poll 1: status → Started (not yet stopped)
    # 5. poll 2: status → Stopped
    # 6. __quit_module__ _get(): status → Stopped
    run_command_calls = [
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Started", ""),
        (0, "", ""),
        (1, NO_MAINTENANCE_OUT, ""),
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Started", ""),
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Stopped (disabled)", ""),
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Stopped (disabled)", ""),
    ]

    def side_effect(self_, **kwargs):
        return run_command_calls.pop(0)

    mocker.patch("ansible.module_utils.basic.AnsibleModule.run_command", side_effect=side_effect)

    with pytest.raises(SystemExit):
        with pytest.MonkeyPatch().context() as mp:
            _run_module(mp, {"state": "disabled", "name": "virtual-ip", "wait": 30})

    out, _err = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is True
    assert result.get("failed") is not True
    assert "Stopped" in result["value"]

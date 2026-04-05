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
# Race condition tests: resource starts after one or more Stopped polls
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


@pytest.mark.usefixtures("patch_bin")
def test_present_race_condition_stopped_then_started(mocker, capfd):
    """Resource reports Stopped on the first poll then Started on the second — must succeed."""
    mocker.patch(
        "ansible_collections.community.general.plugins.module_utils.pacemaker.time.sleep"
    )

    # Sequence of run_command calls:
    # 1. initial _get(): resource status → not found (rc=1)
    # 2. state_present: property config → no maintenance
    # 3. state_present: resource create → rc=0
    # 4. post-create maintenance check → no maintenance
    # 5. wait_for_resource poll 1: status → Stopped (not yet running)
    # 6. wait_for_resource poll 2: status → Started
    # 7. __quit_module__ _get(): status → Started
    run_command_calls = [
        (1, "", "Error: resource or tag id 'virtual-ip' not found"),
        (1, NO_MAINTENANCE_OUT, ""),
        (0, "Assumed agent name 'ocf:heartbeat:IPaddr2'", ""),
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
            mp.setattr(
                "ansible.module_utils.basic._ANSIBLE_ARGS",
                json.dumps({"ANSIBLE_MODULE_ARGS": {
                    "state": "present",
                    "name": "virtual-ip",
                    "resource_type": {"resource_name": "IPaddr2"},
                    "resource_option": ["ip=192.168.2.1"],
                    "wait": 30,
                }}).encode(),
            )
            pacemaker_resource.main()

    out, _err = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is True
    assert result.get("failed") is not True
    assert "Started" in result["value"]


@pytest.mark.usefixtures("patch_bin")
def test_present_wait_timeout_raises(mocker, capfd):
    """Resource never starts within the wait window — must fail with a timeout message."""
    mocker.patch(
        "ansible_collections.community.general.plugins.module_utils.pacemaker.time.sleep"
    )

    # Simulate time advancing past the deadline immediately on the first poll
    monotonic_values = iter([0.0, 0.0, 999.0])
    mocker.patch(
        "ansible_collections.community.general.plugins.module_utils.pacemaker.time.monotonic",
        side_effect=lambda: next(monotonic_values),
    )

    run_command_calls = [
        (1, "", "Error: resource or tag id 'virtual-ip' not found"),
        (1, NO_MAINTENANCE_OUT, ""),
        (0, "Assumed agent name 'ocf:heartbeat:IPaddr2'", ""),
        (1, NO_MAINTENANCE_OUT, ""),
        (0, "  * virtual-ip\t(ocf:heartbeat:IPAddr2):\t Stopped", ""),
    ]

    def side_effect(self_, **kwargs):
        return run_command_calls.pop(0)

    mocker.patch("ansible.module_utils.basic.AnsibleModule.run_command", side_effect=side_effect)

    with pytest.raises(SystemExit):
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "ansible.module_utils.basic._ANSIBLE_ARGS",
                json.dumps({"ANSIBLE_MODULE_ARGS": {
                    "state": "present",
                    "name": "virtual-ip",
                    "resource_type": {"resource_name": "IPaddr2"},
                    "resource_option": ["ip=192.168.2.1"],
                    "wait": 10,
                }}).encode(),
            )
            pacemaker_resource.main()

    out, _err = capfd.readouterr()
    result = json.loads(out)
    assert result.get("failed") is True
    assert "Timed out" in result["msg"]
    assert "virtual-ip" in result["msg"]

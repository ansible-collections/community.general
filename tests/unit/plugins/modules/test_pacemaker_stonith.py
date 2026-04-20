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

from ansible_collections.community.general.plugins.modules import pacemaker_stonith

from .uthelper import RunCommandMock, UTHelper

UTHelper.from_module(pacemaker_stonith, __name__, mocks=[RunCommandMock])


# ---------------------------------------------------------------------------
# Race condition tests: resource starts after one or more Stopped polls
# ---------------------------------------------------------------------------


@pytest.fixture
def patch_bin(mocker):
    def mockie(self_, path, *args, **kwargs):
        return f"/testbin/{path}"

    mocker.patch("ansible.module_utils.basic.AnsibleModule.get_bin_path", mockie)


@pytest.mark.usefixtures("patch_bin")
def test_present_race_condition_stopped_then_started(mocker, capfd):
    """Resource reports Stopped on the first poll then Started on the second — must succeed."""
    mocker.patch("ansible_collections.community.general.plugins.module_utils._pacemaker.time.sleep")

    # Sequence of run_command calls:
    # 1. initial _get(): stonith status → not found (rc=1)
    # 2. state_present create → rc=0
    # 3. wait_for_resource poll 1: status → Stopped (not yet running)
    # 4. wait_for_resource poll 2: status → Started
    # 5. __quit_module__ _get(): status → Started
    run_command_calls = [
        (1, "", ""),
        (0, "", ""),
        (0, "  * virtual-stonith\t(stonith:fence_virt):\t Stopped", ""),
        (0, "  * virtual-stonith\t(stonith:fence_virt):\t Started", ""),
        (0, "  * virtual-stonith\t(stonith:fence_virt):\t Started", ""),
    ]

    def side_effect(self_, **kwargs):
        return run_command_calls.pop(0)

    mocker.patch("ansible.module_utils.basic.AnsibleModule.run_command", side_effect=side_effect)

    with pytest.raises(SystemExit):
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "ansible.module_utils.basic._ANSIBLE_ARGS",
                json.dumps(
                    {
                        "ANSIBLE_MODULE_ARGS": {
                            "state": "present",
                            "name": "virtual-stonith",
                            "stonith_type": "fence_virt",
                            "stonith_options": ["pcmk_host_list=f1"],
                            "wait": 30,
                        }
                    }
                ).encode(),
            )
            mp.setattr("ansible.module_utils.basic._ANSIBLE_PROFILE", "legacy", raising=False)
            pacemaker_stonith.main()

    out, _err = capfd.readouterr()
    result = json.loads(out)
    assert result["changed"] is True
    assert result.get("failed") is not True
    assert "Started" in result["value"]


@pytest.mark.usefixtures("patch_bin")
def test_present_wait_timeout_raises(mocker, capfd):
    """Resource never starts within the wait window — must fail with a timeout message."""
    mocker.patch("ansible_collections.community.general.plugins.module_utils._pacemaker.time.sleep")

    # Simulate time advancing past the deadline immediately on the first poll
    monotonic_values = iter([0.0, 999.0])
    mocker.patch(
        "ansible_collections.community.general.plugins.module_utils._pacemaker.time.monotonic",
        side_effect=lambda: next(monotonic_values),
    )

    # Sequence: initial _get() → not found, create → rc=0, poll → Stopped (deadline exceeded)
    run_command_calls = [
        (1, "", ""),
        (0, "", ""),
        (0, "  * virtual-stonith\t(stonith:fence_virt):\t Stopped", ""),
    ]

    def side_effect(self_, **kwargs):
        return run_command_calls.pop(0)

    mocker.patch("ansible.module_utils.basic.AnsibleModule.run_command", side_effect=side_effect)

    with pytest.raises(SystemExit):
        with pytest.MonkeyPatch().context() as mp:
            mp.setattr(
                "ansible.module_utils.basic._ANSIBLE_ARGS",
                json.dumps(
                    {
                        "ANSIBLE_MODULE_ARGS": {
                            "state": "present",
                            "name": "virtual-stonith",
                            "stonith_type": "fence_virt",
                            "stonith_options": ["pcmk_host_list=f1"],
                            "wait": 10,
                        }
                    }
                ).encode(),
            )
            mp.setattr("ansible.module_utils.basic._ANSIBLE_PROFILE", "legacy", raising=False)
            pacemaker_stonith.main()

    out, _err = capfd.readouterr()
    result = json.loads(out)
    assert result.get("failed") is True
    assert "Timed out" in result["msg"]
    assert "virtual-stonith" in result["msg"]

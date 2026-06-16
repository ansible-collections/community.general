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

from ansible_collections.community.general.plugins.module_utils import _pacemaker
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
    mocker.patch("ansible_collections.community.general.plugins.module_utils._pacemaker.time.sleep")

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
                json.dumps(
                    {
                        "ANSIBLE_MODULE_ARGS": {
                            "state": "present",
                            "name": "virtual-ip",
                            "resource_type": {"resource_name": "IPaddr2"},
                            "resource_option": ["ip=192.168.2.1"],
                            "wait": 30,
                        }
                    }
                ).encode(),
            )
            mp.setattr("ansible.module_utils.basic._ANSIBLE_PROFILE", "legacy", raising=False)
            pacemaker_resource.main()

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
                json.dumps(
                    {
                        "ANSIBLE_MODULE_ARGS": {
                            "state": "present",
                            "name": "virtual-ip",
                            "resource_type": {"resource_name": "IPaddr2"},
                            "resource_option": ["ip=192.168.2.1"],
                            "wait": 10,
                        }
                    }
                ).encode(),
            )
            mp.setattr("ansible.module_utils.basic._ANSIBLE_PROFILE", "legacy", raising=False)
            pacemaker_resource.main()

    out, _err = capfd.readouterr()
    result = json.loads(out)
    assert result.get("failed") is True
    assert "Timed out" in result["msg"]
    assert "virtual-ip" in result["msg"]


# ---------------------------------------------------------------------------
# is_resource_cloned: pure-function tests over the parsed pcs JSON DTO
# ---------------------------------------------------------------------------


PRIMITIVE_VIRTUAL_IP: dict = {
    "id": "virtual-ip",
    "agent_name": {"standard": "ocf", "provider": "heartbeat", "type": "IPaddr2"},
    "description": None,
    "operations": [],
    "meta_attributes": [],
    "instance_attributes": [],
    "utilization": [],
}


def _config(*, primitives=(), clones=(), groups=(), bundles=()):
    return {
        "primitives": list(primitives),
        "clones": list(clones),
        "groups": list(groups),
        "bundles": list(bundles),
    }


def test_is_resource_cloned_true_for_primitive():
    config = _config(
        primitives=[PRIMITIVE_VIRTUAL_IP],
        clones=[
            {
                "id": "virtual-ip-clone",
                "description": None,
                "member_id": "virtual-ip",
                "meta_attributes": [],
                "instance_attributes": [],
            }
        ],
    )
    assert _pacemaker.is_resource_cloned(config, "virtual-ip") is True


def test_is_resource_cloned_true_for_group():
    """Cloned-group case from the upstream bug report (locking-clone [locking])."""
    config = _config(
        clones=[
            {
                "id": "locking-clone",
                "description": None,
                "member_id": "locking",
                "meta_attributes": [],
                "instance_attributes": [],
            }
        ],
        groups=[
            {
                "id": "locking",
                "description": None,
                "member_ids": ["dlm", "clvmd"],
                "meta_attributes": [],
                "instance_attributes": [],
            }
        ],
    )
    assert _pacemaker.is_resource_cloned(config, "locking") is True


def test_is_resource_cloned_true_for_promotable_clone():
    """A promotable clone is still a clone — detection is purely on member_id."""
    config = _config(
        primitives=[PRIMITIVE_VIRTUAL_IP],
        clones=[
            {
                "id": "virtual-ip-clone",
                "description": None,
                "member_id": "virtual-ip",
                "meta_attributes": [
                    {
                        "id": "virtual-ip-clone-meta_attributes",
                        "options": {},
                        "rule": None,
                        "nvpairs": [
                            {
                                "id": "virtual-ip-clone-meta_attributes-promotable",
                                "name": "promotable",
                                "value": "true",
                            }
                        ],
                    }
                ],
                "instance_attributes": [],
            }
        ],
    )
    assert _pacemaker.is_resource_cloned(config, "virtual-ip") is True


def test_is_resource_cloned_false_when_no_clones():
    config = _config(primitives=[PRIMITIVE_VIRTUAL_IP])
    assert _pacemaker.is_resource_cloned(config, "virtual-ip") is False


def test_is_resource_cloned_false_when_clone_targets_other_resource():
    """A clone exists in the cluster but not for the requested resource."""
    config = _config(
        primitives=[
            PRIMITIVE_VIRTUAL_IP,
            {"id": "other", **{k: v for k, v in PRIMITIVE_VIRTUAL_IP.items() if k != "id"}},
        ],
        clones=[
            {
                "id": "other-clone",
                "description": None,
                "member_id": "other",
                "meta_attributes": [],
                "instance_attributes": [],
            }
        ],
    )
    assert _pacemaker.is_resource_cloned(config, "virtual-ip") is False


def test_is_resource_cloned_false_for_empty_name():
    config = _config(
        clones=[
            {
                "id": "virtual-ip-clone",
                "description": None,
                "member_id": "virtual-ip",
                "meta_attributes": [],
                "instance_attributes": [],
            }
        ]
    )
    assert _pacemaker.is_resource_cloned(config, "") is False
    assert _pacemaker.is_resource_cloned(config, None) is False


def test_is_resource_cloned_false_when_clones_key_missing():
    """Defensive: pcs schema mandates the key but tolerate its absence."""
    assert _pacemaker.is_resource_cloned({}, "virtual-ip") is False
    assert _pacemaker.is_resource_cloned({"clones": None}, "virtual-ip") is False


# ---------------------------------------------------------------------------
# get_pacemaker_maintenance_mode: tolerant JSON parsing
# ---------------------------------------------------------------------------


class _StubCtx:
    def __init__(self, rc, out, err):
        self._result = (rc, out, err)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def run(self, **_kwargs):
        return self._result


class _StubRunner:
    def __init__(self, rc, out, err):
        self.rc = rc
        self.out = out
        self.err = err

    def __call__(self, *_args, **_kwargs):
        return _StubCtx(self.rc, self.out, self.err)


@pytest.mark.parametrize(
    "out,expected",
    [
        # maintenance-mode true via nvpair
        (
            '{"nvsets": [{"id": "cib-bootstrap-options", "options": {}, "rule": null,'
            ' "nvpairs": [{"id": "x", "name": "maintenance-mode", "value": "true"}]}]}',
            True,
        ),
        # maintenance-mode explicitly false
        (
            '{"nvsets": [{"id": "cib-bootstrap-options", "options": {}, "rule": null,'
            ' "nvpairs": [{"id": "x", "name": "maintenance-mode", "value": "false"}]}]}',
            False,
        ),
        # maintenance-mode absent (only other properties present)
        (
            '{"nvsets": [{"id": "cib-bootstrap-options", "options": {}, "rule": null,'
            ' "nvpairs": [{"id": "x", "name": "cluster-name", "value": "hacluster"}]}]}',
            False,
        ),
        # empty nvsets
        ('{"nvsets": []}', False),
        # nvset with empty nvpairs
        (
            '{"nvsets": [{"id": "cib-bootstrap-options", "options": {}, "rule": null, "nvpairs": []}]}',
            False,
        ),
        # malformed JSON — must not raise, must return False
        ("not-valid-json", False),
        # empty stdout — must not raise, must return False
        ("", False),
        # value present but not "true" (stricter than the old regex which would have matched substrings)
        (
            '{"nvsets": [{"id": "cib-bootstrap-options", "options": {}, "rule": null,'
            ' "nvpairs": [{"id": "x", "name": "maintenance-mode", "value": "TRUE"}]}]}',
            False,
        ),
    ],
)
def test_get_pacemaker_maintenance_mode(out, expected):
    runner = _StubRunner(rc=0, out=out, err="")
    assert _pacemaker.get_pacemaker_maintenance_mode(runner) is expected


# ---------------------------------------------------------------------------
# get_pacemaker_resource_config: tolerant JSON parsing and rc handling
# ---------------------------------------------------------------------------


def test_get_pacemaker_resource_config_returns_none_on_nonzero_rc():
    runner = _StubRunner(rc=1, out="", err="Error: unable to find resource: virtual-ip")
    assert _pacemaker.get_pacemaker_resource_config(runner) is None


def test_get_pacemaker_resource_config_returns_none_on_invalid_json():
    runner = _StubRunner(rc=0, out="not-valid-json", err="")
    assert _pacemaker.get_pacemaker_resource_config(runner) is None


def test_get_pacemaker_resource_config_returns_parsed_dto():
    out = (
        '{"primitives": [], "clones": [{"id": "virtual-ip-clone", "description": null,'
        ' "member_id": "virtual-ip", "meta_attributes": [], "instance_attributes": []}],'
        ' "groups": [], "bundles": []}'
    )
    runner = _StubRunner(rc=0, out=out, err="")
    config = _pacemaker.get_pacemaker_resource_config(runner)
    assert config is not None
    assert _pacemaker.is_resource_cloned(config, "virtual-ip") is True

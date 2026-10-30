# Copyright (c) 2026, community.general contributors
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ansible_collections.community.general.plugins.module_utils import _pacemaker
from ansible_collections.community.general.plugins.module_utils._pacemaker import (
    _DEFAULT_RESOURCE_READY_STATES,
    get_pacemaker_maintenance_mode,
    get_pacemaker_resource_config,
    is_resource_cloned,
    wait_for_resource,
)

_PROMOTABLE_READY_STATES = ("Started", "Promoted", "Unpromoted")


def _make_runner(outputs):
    """Build a fake CmdRunner that yields the given ``(rc, out, err)`` tuples in order.

    The fake mirrors the runner usage in :func:`wait_for_resource`::

        with runner("cli_action state name") as ctx:
            rc, out, err = ctx.run(cli_action=..., state="status")
    """
    outputs_iter = iter(outputs)

    def runner_call(*args, **kwargs):
        ctx = MagicMock()
        ctx.run.return_value = next(outputs_iter)
        cm = MagicMock()
        cm.__enter__.return_value = ctx
        cm.__exit__.return_value = False
        return cm

    runner = MagicMock(side_effect=runner_call)
    return runner


@pytest.fixture(autouse=True)
def _no_sleep(mocker):
    """Avoid real sleeps in any test in this module."""
    mocker.patch.object(_pacemaker.time, "sleep")


def test_default_ready_states_is_started_only():
    """The default must preserve pre-fix behaviour for stonith and non-promotable callers."""
    assert _DEFAULT_RESOURCE_READY_STATES == ("Started",)


@pytest.mark.parametrize(
    "status_line",
    [
        "  * virtual-ip\t(ocf:heartbeat:IPaddr2):\t Started node-a",
        "  * drbd_data\t(ocf:linbit:drbd):\t Promoted node-a",
        "  * drbd_data\t(ocf:linbit:drbd):\t Unpromoted node-b",
    ],
    ids=["started", "promoted", "unpromoted"],
)
def test_wait_for_resource_promotable_ready_states(status_line):
    """Each ready state in the promotable set must cause an immediate successful return."""
    runner = _make_runner([(0, status_line, "")])

    wait_for_resource(runner, "resource", "any-resource", wait=30, ready_states=_PROMOTABLE_READY_STATES)

    # One poll, one success — no further runner calls.
    assert runner.call_count == 1


def test_wait_for_resource_default_matches_started(mocker):
    """Calling without ready_states must match Started — the stonith and non-promotable default."""
    runner = _make_runner(
        [
            (0, "  * fence-node-a\t(stonith:fence_ipmilan):\t Started node-a", ""),
        ]
    )

    wait_for_resource(runner, "stonith", "fence-node-a", wait=30)

    assert runner.call_count == 1


def test_wait_for_resource_default_rejects_promoted(mocker):
    """With the default ready_states, Promoted output must NOT short-circuit (stonith never promotes)."""
    mocker.patch.object(_pacemaker.time, "monotonic", side_effect=[0.0, 999.0])

    runner = _make_runner(
        [
            (0, "  * drbd_data\t(ocf:linbit:drbd):\t Promoted node-a", ""),
        ]
    )

    with pytest.raises(Exception) as excinfo:
        wait_for_resource(runner, "stonith", "drbd_data", wait=10)

    assert "Timed out waiting 10s" in str(excinfo.value)


def test_wait_for_resource_returns_when_promotable_replicas_present():
    """A promotable resource output listing both replicas must be detected as ready."""
    out = "  * drbd_data\t(ocf:linbit:drbd):\t Promoted node-a\n  * drbd_data\t(ocf:linbit:drbd):\t Unpromoted node-b"
    runner = _make_runner([(0, out, "")])

    wait_for_resource(runner, "resource", "drbd_data", wait=30, ready_states=_PROMOTABLE_READY_STATES)

    assert runner.call_count == 1


def test_wait_for_resource_polls_until_ready(mocker):
    """The wait loop must keep polling while the resource is not in a ready state."""
    # Monotonic must not advance past the deadline before the ready output is seen.
    mocker.patch.object(_pacemaker.time, "monotonic", side_effect=[0.0, 1.0, 2.0, 3.0])

    runner = _make_runner(
        [
            (0, "  * drbd_data\t(ocf:linbit:drbd):\t Stopped", ""),
            (0, "  * drbd_data\t(ocf:linbit:drbd):\t Starting node-a", ""),
            (0, "  * drbd_data\t(ocf:linbit:drbd):\t Promoted node-a", ""),
        ]
    )

    wait_for_resource(runner, "resource", "drbd_data", wait=300, ready_states=_PROMOTABLE_READY_STATES)

    assert runner.call_count == 3


def test_wait_for_resource_transitional_states_do_not_short_circuit(mocker):
    """Transitional states (``Starting``/``Promoting``/``Demoting``) must not be treated as ready."""
    # Force the deadline to expire after the first poll so the timeout exception fires.
    mocker.patch.object(_pacemaker.time, "monotonic", side_effect=[0.0, 999.0])

    runner = _make_runner(
        [
            (0, "  * drbd_data\t(ocf:linbit:drbd):\t Promoting node-a", ""),
        ]
    )

    with pytest.raises(Exception) as excinfo:
        wait_for_resource(runner, "resource", "drbd_data", wait=10, ready_states=_PROMOTABLE_READY_STATES)

    assert "Timed out waiting 10s" in str(excinfo.value)
    assert "drbd_data" in str(excinfo.value)


def test_wait_for_resource_times_out_when_never_ready(mocker):
    """The wait loop must raise a timeout error when the ready state is never observed."""
    mocker.patch.object(_pacemaker.time, "monotonic", side_effect=[0.0, 999.0])

    runner = _make_runner(
        [
            (0, "  * virtual-ip\t(ocf:heartbeat:IPaddr2):\t Stopped", ""),
        ]
    )

    with pytest.raises(Exception) as excinfo:
        wait_for_resource(runner, "resource", "virtual-ip", wait=10)

    assert "Timed out waiting 10s" in str(excinfo.value)
    assert "virtual-ip" in str(excinfo.value)


def test_wait_for_resource_empty_output_does_not_match(mocker):
    """An empty status output must not be treated as ready even though ``in`` of empty matches."""
    mocker.patch.object(_pacemaker.time, "monotonic", side_effect=[0.0, 999.0])

    runner = _make_runner(
        [
            (0, "", ""),
        ]
    )

    with pytest.raises(Exception) as excinfo:
        wait_for_resource(runner, "resource", "any-resource", wait=5)

    assert "Timed out waiting 5s" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Maintenance-mode detection (JSON with plaintext fallback)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("out", "expected"),
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
        ('{"nvsets": [{"id": "cib-bootstrap-options", "options": {}, "rule": null, "nvpairs": []}]}', False),
        # value present but not the literal "true" (stricter than the old regex)
        (
            '{"nvsets": [{"id": "cib-bootstrap-options", "options": {}, "rule": null,'
            ' "nvpairs": [{"id": "x", "name": "maintenance-mode", "value": "TRUE"}]}]}',
            False,
        ),
    ],
    ids=[
        "true",
        "explicit-false",
        "absent",
        "empty-nvsets",
        "empty-nvpairs",
        "uppercase-not-matched",
    ],
)
def test_get_pacemaker_maintenance_mode_json(out, expected):
    """On pcs >= 0.11.6 the JSON path is used and no deprecation is emitted."""
    runner = _make_runner([(0, out, "")])
    assert get_pacemaker_maintenance_mode(runner) is expected
    runner.module.deprecate.assert_not_called()


@pytest.mark.parametrize(
    ("plaintext", "expected"),
    [
        ("maintenance-mode=true", True),
        ("maintenance-mode: true", True),
        ("maintenance-mode=false (default)", False),
        ("", False),
    ],
    ids=["flat-true", "colon-true", "false-default", "empty"],
)
def test_get_pacemaker_maintenance_mode_plaintext_fallback(plaintext, expected):
    """On pcs < 0.11.6 the JSON attempt fails to parse; the plaintext fallback runs and deprecates."""
    # 1st call: `pcs property config --output-format=json` rejected by old pcs (non-JSON output).
    # 2nd call: `pcs property config` returns plaintext.
    runner = _make_runner([(1, "", "Error: unknown option '--output-format'"), (0, plaintext, "")])
    assert get_pacemaker_maintenance_mode(runner) is expected
    runner.module.deprecate.assert_called_once()


# ---------------------------------------------------------------------------
# Clone-detection helpers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("config", "name", "expected"),
    [
        ({"clones": [{"id": "virtual-ip-clone", "member_id": "virtual-ip"}]}, "virtual-ip", True),
        ({"clones": [{"id": "locking-clone", "member_id": "locking"}]}, "locking", True),
        ({"clones": [{"id": "other-clone", "member_id": "other"}]}, "virtual-ip", False),
        ({"clones": []}, "virtual-ip", False),
        ({}, "virtual-ip", False),
    ],
    ids=["cloned-primitive", "cloned-group", "other-resource-cloned", "empty-clones", "clones-absent"],
)
def test_is_resource_cloned(config, name, expected):
    assert is_resource_cloned(config, name) is expected


def test_get_pacemaker_resource_config_parses_json():
    payload = '{"primitives": [], "clones": [{"member_id": "virtual-ip"}], "groups": [], "bundles": []}'
    runner = _make_runner([(0, payload, "")])
    assert is_resource_cloned(get_pacemaker_resource_config(runner, "virtual-ip"), "virtual-ip") is True


def test_get_pacemaker_resource_config_returns_none_on_old_pcs():
    """Unparseable/old-pcs output yields None so the caller can fall back to the stderr path."""
    runner = _make_runner([(1, "", "Error: unknown option '--output-format'")])
    assert get_pacemaker_resource_config(runner, "virtual-ip") is None

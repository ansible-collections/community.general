# Copyright (c) 2026, community.general contributors
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ansible_collections.community.general.plugins.module_utils import _pacemaker
from ansible_collections.community.general.plugins.module_utils._pacemaker import (
    _DEFAULT_RESOURCE_READY_STATES,
    _PCS_JSON_MIN,
    PacemakerRunner,
    _maintenance_mode_json,
    _maintenance_mode_plaintext,
    get_pacemaker_maintenance_mode,
    is_resource_cloned_any,
    is_resource_cloned_plaintext,
    pacemaker_runner,
    parse_pcs_version,
    wait_for_resource,
)

_PROMOTABLE_READY_STATES = ("Started", "Promoted", "Unpromoted")


def _make_runner(outputs, params=None, pcs_version="0.11.7"):
    """Build a real :class:`PacemakerRunner`, backed by a mocked ``AnsibleModule``.

    Mirrors the pattern used by ``test__cmd_runner.py`` and
    ``test__python_runner.py``: instantiate the real runner and mock only the
    ``AnsibleModule`` dependencies it consumes.

    ``outputs`` is a list of ``(rc, out, err)`` tuples fed sequentially to
    ``module.run_command`` via ``side_effect`` **after** the version probe. The
    probe itself is prepended automatically from ``pcs_version``:

    * ``pcs_version="0.11.7"`` (default) — a JSON-capable version, probe rc=0.
    * ``pcs_version="0.10.18"`` — a plaintext-only version.
    * ``pcs_version=None`` — probe fails (rc=1), forcing the plaintext fallback.

    ``params`` supplies ``module.params`` for the real ``CmdRunner`` argument
    resolver. Helpers that reference ``name`` in their args-order spec but do
    not forward it via ``ctx.run(...)`` (such as :func:`wait_for_resource` and
    :func:`is_resource_cloned_plaintext`) rely on the module params to supply
    it — matching the way real modules invoke these helpers in production.

    Returns the runner; the mocked module is accessible as ``runner.module``
    for call-count assertions. Note that ``run_command.call_count`` includes
    the version probe (one extra call beyond ``outputs``).
    """
    module = MagicMock()
    module.check_mode = False
    module.get_bin_path.return_value = "/testbin/pcs"
    module.params = dict(params) if params else {}
    probe = (1, "", "pcs missing") if pcs_version is None else (0, pcs_version, "")
    module.run_command.side_effect = [probe] + list(outputs)
    return pacemaker_runner(module)


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
    runner = _make_runner([(0, status_line, "")], params={"name": "any-resource"})

    wait_for_resource(runner, "resource", "any-resource", wait=30, ready_states=_PROMOTABLE_READY_STATES)

    # One version probe + one status poll = 2 calls.
    assert runner.module.run_command.call_count == 2


def test_wait_for_resource_default_matches_started(mocker):
    """Calling without ready_states must match Started — the stonith and non-promotable default."""
    runner = _make_runner(
        [
            (0, "  * fence-node-a\t(stonith:fence_ipmilan):\t Started node-a", ""),
        ],
        params={"name": "fence-node-a"},
    )

    wait_for_resource(runner, "stonith", "fence-node-a", wait=30)

    assert runner.module.run_command.call_count == 2


def test_wait_for_resource_default_rejects_promoted(mocker):
    """With the default ready_states, Promoted output must NOT short-circuit (stonith never promotes)."""
    mocker.patch.object(_pacemaker.time, "monotonic", side_effect=[0.0, 999.0])

    runner = _make_runner(
        [
            (0, "  * drbd_data\t(ocf:linbit:drbd):\t Promoted node-a", ""),
        ],
        params={"name": "drbd_data"},
    )

    with pytest.raises(Exception) as excinfo:
        wait_for_resource(runner, "stonith", "drbd_data", wait=10)

    assert "Timed out waiting 10s" in str(excinfo.value)


def test_wait_for_resource_returns_when_promotable_replicas_present():
    """A promotable resource output listing both replicas must be detected as ready."""
    out = "  * drbd_data\t(ocf:linbit:drbd):\t Promoted node-a\n  * drbd_data\t(ocf:linbit:drbd):\t Unpromoted node-b"
    runner = _make_runner([(0, out, "")], params={"name": "drbd_data"})

    wait_for_resource(runner, "resource", "drbd_data", wait=30, ready_states=_PROMOTABLE_READY_STATES)

    assert runner.module.run_command.call_count == 2


def test_wait_for_resource_polls_until_ready(mocker):
    """The wait loop must keep polling while the resource is not in a ready state."""
    # Monotonic must not advance past the deadline before the ready output is seen.
    mocker.patch.object(_pacemaker.time, "monotonic", side_effect=[0.0, 1.0, 2.0, 3.0])

    runner = _make_runner(
        [
            (0, "  * drbd_data\t(ocf:linbit:drbd):\t Stopped", ""),
            (0, "  * drbd_data\t(ocf:linbit:drbd):\t Starting node-a", ""),
            (0, "  * drbd_data\t(ocf:linbit:drbd):\t Promoted node-a", ""),
        ],
        params={"name": "drbd_data"},
    )

    wait_for_resource(runner, "resource", "drbd_data", wait=300, ready_states=_PROMOTABLE_READY_STATES)

    # One version probe + three status polls = 4 calls.
    assert runner.module.run_command.call_count == 4


def test_wait_for_resource_transitional_states_do_not_short_circuit(mocker):
    """Transitional states (``Starting``/``Promoting``/``Demoting``) must not be treated as ready."""
    # Force the deadline to expire after the first poll so the timeout exception fires.
    mocker.patch.object(_pacemaker.time, "monotonic", side_effect=[0.0, 999.0])

    runner = _make_runner(
        [
            (0, "  * drbd_data\t(ocf:linbit:drbd):\t Promoting node-a", ""),
        ],
        params={"name": "drbd_data"},
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
        ],
        params={"name": "virtual-ip"},
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
        ],
        params={"name": "any-resource"},
    )

    with pytest.raises(Exception) as excinfo:
        wait_for_resource(runner, "resource", "any-resource", wait=5)

    assert "Timed out waiting 5s" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Version probe / dispatch
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0.11.7", (0, 11, 7)),
        ("0.11.7\n", (0, 11, 7)),
        ("  0.11.7  ", (0, 11, 7)),
        ("0.10.18-2.el8", (0, 10, 18)),
        ("0.11.7.dev.1234", (0, 11, 7)),
        ("1.2.3-rc4+build.5", (1, 2, 3)),
        ("0.9.169", (0, 9, 169)),
        ("", None),
        (None, None),
        ("garbage", None),
        ("0.11", None),
    ],
    ids=[
        "clean",
        "trailing-newline",
        "leading-and-trailing-whitespace",
        "distro-suffix",
        "dev-suffix",
        "semver-metadata",
        "old-rhel7",
        "empty",
        "none",
        "non-numeric",
        "truncated",
    ],
)
def test_parse_pcs_version(raw, expected):
    assert parse_pcs_version(raw) == expected


def test_pacemaker_runner_populates_version_attributes():
    """Construction probes ``pcs --version`` exactly once and stashes parsed state."""
    runner = _make_runner([], pcs_version="0.11.7-2.el9")

    assert runner.raw_version == "0.11.7-2.el9"
    assert runner.version == (0, 11, 7)
    assert runner.supports_json is True
    # Exactly one shell-out — the version probe — at construction.
    assert runner.module.run_command.call_count == 1


def test_pacemaker_runner_falls_open_when_probe_fails():
    """A failing probe leaves ``version`` as ``None`` and ``supports_json`` as False."""
    runner = _make_runner([], pcs_version=None)

    assert runner.raw_version == ""
    assert runner.version is None
    assert runner.supports_json is False


def test_pacemaker_runner_falls_open_when_probe_output_is_unparseable():
    """Unparseable ``pcs --version`` output must not raise; supports_json must be False."""
    runner = _make_runner([], pcs_version="not-a-version")

    assert runner.raw_version == "not-a-version"
    assert runner.version is None
    assert runner.supports_json is False


@pytest.mark.parametrize(
    ("version_str", "expected"),
    [
        ("0.11.7", True),
        ("0.11.6", True),  # equals the minimum
        ("0.11.5", False),
        ("0.10.18", False),
        ("0.9.169", False),
        ("1.0.0", True),
    ],
    ids=["above", "equal", "just-below", "rhel8", "rhel7", "far-above"],
)
def test_pacemaker_runner_supports_json_boundary_conditions(version_str, expected):
    runner = _make_runner([], pcs_version=version_str)
    assert runner.supports_json is expected


def test_pcs_json_min_is_frozen():
    """The minimum-supported JSON version is a documented invariant."""
    assert _PCS_JSON_MIN == (0, 11, 6)


def test_pacemaker_runner_is_a_cmdrunner():
    """The subclass contract: PacemakerRunner instances must be usable anywhere a CmdRunner is expected."""
    from ansible_collections.community.general.plugins.module_utils._cmd_runner import CmdRunner

    runner = _make_runner([])
    assert isinstance(runner, CmdRunner)
    assert isinstance(runner, PacemakerRunner)


# ---------------------------------------------------------------------------
# Maintenance-mode helpers
# ---------------------------------------------------------------------------


def test_maintenance_mode_json_true():
    payload = '{"nvsets": [{"nvpairs": [{"name": "maintenance-mode", "value": "true"}]}]}'
    runner = _make_runner([(0, payload, "")])
    assert _maintenance_mode_json(runner) is True


def test_maintenance_mode_json_false_when_absent():
    payload = '{"nvsets": [{"nvpairs": []}]}'
    runner = _make_runner([(0, payload, "")])
    assert _maintenance_mode_json(runner) is False


def test_maintenance_mode_json_false_on_unparseable_output():
    runner = _make_runner([(0, "not-json", "")])
    assert _maintenance_mode_json(runner) is False


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("maintenance-mode=true", True),
        ("maintenance-mode: true", True),
        ("maintenance-mode = TRUE", True),
        ("maintenance-mode=false (default)", False),
        ("maintenance-mode=false", False),
        ("maintenance-mode: false", False),
        ("", False),
        ("  ", False),
    ],
    ids=[
        "flat-true",
        "colon-true",
        "case-insensitive",
        "with-default-annotation",
        "flat-false",
        "colon-false",
        "empty",
        "whitespace-only",
    ],
)
def test_maintenance_mode_plaintext_shapes(text, expected):
    runner = _make_runner([(0, text, "")])
    assert _maintenance_mode_plaintext(runner) is expected


def test_maintenance_mode_plaintext_returns_false_on_rc_nonzero():
    """A ``pcs`` failure must map to False rather than crashing the caller."""
    runner = _make_runner([(1, "", "Error: unable to get cib")])
    assert _maintenance_mode_plaintext(runner) is False


def test_get_pacemaker_maintenance_mode_dispatches_to_json_on_new_pcs():
    """On new pcs, dispatch must exercise the JSON path (and only the JSON path)."""
    payload = '{"nvsets": [{"nvpairs": [{"name": "maintenance-mode", "value": "true"}]}]}'
    runner = _make_runner(
        [
            (0, payload, ""),  # pcs property config --output-format=json
        ],
        pcs_version="0.11.7",
    )

    assert get_pacemaker_maintenance_mode(runner) is True
    # One version probe at construction + one dispatched call = 2.
    assert runner.module.run_command.call_count == 2


def test_get_pacemaker_maintenance_mode_dispatches_to_plaintext_on_old_pcs():
    """On old pcs, dispatch must exercise the plaintext single-property path."""
    runner = _make_runner(
        [
            (0, "maintenance-mode=true", ""),  # pcs property config maintenance-mode
        ],
        pcs_version="0.10.18",
    )

    assert get_pacemaker_maintenance_mode(runner) is True
    assert runner.module.run_command.call_count == 2


def test_get_pacemaker_maintenance_mode_plaintext_false_when_default():
    runner = _make_runner(
        [
            (0, "maintenance-mode=false (default)", ""),
        ],
        pcs_version="0.10.18",
    )
    assert get_pacemaker_maintenance_mode(runner) is False


# ---------------------------------------------------------------------------
# Clone-detection helpers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Clone: virtual-ip-clone\n Resource: virtual-ip ...", True),
        ("  Clone: virtual-ip-clone\n", True),
        # ``Clone Set:`` is the wording used by older pcs releases.
        ("Clone Set: virtual-ip-clone [virtual-ip]\n", True),
        # Bare primitive: no clone header must yield False.
        ("Resource: virtual-ip (class=ocf provider=heartbeat type=IPaddr2)", False),
        # Text mentioning "clone" outside a header line must not match.
        ('Attributes: description="clone-related"', False),
        ("", False),
    ],
    ids=[
        "clone-header",
        "indented-clone-header",
        "clone-set-header-old-pcs",
        "bare-primitive",
        "false-positive-guard",
        "empty",
    ],
)
def test_is_resource_cloned_plaintext_shapes(text, expected):
    runner = _make_runner([(0, text, "")], params={"name": "virtual-ip"})
    assert is_resource_cloned_plaintext(runner) is expected


def test_is_resource_cloned_plaintext_returns_false_on_rc_nonzero():
    runner = _make_runner([(1, "", "Error: unable to find resource")], params={"name": "virtual-ip"})
    assert is_resource_cloned_plaintext(runner) is False


def test_is_resource_cloned_any_dispatches_to_json_on_new_pcs():
    """New-pcs path: resource config JSON matched against clones[]."""
    payload = '{"primitives": [], "clones": [{"member_id": "virtual-ip"}], "groups": [], "bundles": []}'
    runner = _make_runner(
        [
            (0, payload, ""),  # pcs resource config <name> --output-format=json
        ],
        params={"name": "virtual-ip"},
        pcs_version="0.11.7",
    )

    assert is_resource_cloned_any(runner, "virtual-ip") is True


def test_is_resource_cloned_any_dispatches_to_plaintext_on_old_pcs():
    """Old-pcs path: plaintext resource config regex-matched for Clone header."""
    plaintext = "Clone: virtual-ip-clone\n Resource: virtual-ip\n"
    runner = _make_runner(
        [
            (0, plaintext, ""),
        ],
        params={"name": "virtual-ip"},
        pcs_version="0.10.18",
    )

    assert is_resource_cloned_any(runner, "virtual-ip") is True


def test_is_resource_cloned_any_false_when_target_not_in_clones_json():
    """New-pcs guard: another resource is cloned but our target is not — must return False."""
    payload = '{"primitives": [], "clones": [{"member_id": "other"}], "groups": [], "bundles": []}'
    runner = _make_runner(
        [
            (0, payload, ""),
        ],
        params={"name": "virtual-ip"},
        pcs_version="0.11.7",
    )

    assert is_resource_cloned_any(runner, "virtual-ip") is False


def test_is_resource_cloned_any_false_when_resource_config_returns_invalid_json():
    """New-pcs defensive: unparseable JSON must not crash, must return False."""
    runner = _make_runner(
        [
            (0, "not-valid-json", ""),
        ],
        params={"name": "virtual-ip"},
        pcs_version="0.11.7",
    )

    assert is_resource_cloned_any(runner, "virtual-ip") is False

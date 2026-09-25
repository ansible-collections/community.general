# Copyright (c) 2025, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

"""Private helpers for the ``community.general.pacemaker_*`` modules.

Version-dispatch model
----------------------
``pcs`` versions ``0.11.6`` and newer support ``--output-format=json`` on
``property config`` and ``resource config``, which is the parse-friendly form
this collection prefers. Older ``pcs`` releases (RHEL 7/8 era, and any distro
still shipping ``pcs`` < 0.11.6) only emit plaintext.

To support both, :class:`PacemakerRunner` probes ``pcs --version`` once at
construction and exposes the parsed tuple plus a ``supports_json`` bit. The
helpers below then dispatch to a JSON path or a plaintext path based on that
bit. On probe failure (``pcs`` missing, non-zero rc, unparseable output)
callers fall open to the plaintext path so a transient ``pcs --version``
glitch cannot break otherwise-functional automation.

The plaintext path preserves the behavioural contract of each helper:

* ``get_pacemaker_maintenance_mode`` still returns ``True``/``False``.
* ``is_resource_cloned_any`` still returns ``True``/``False`` for clone
  idempotency gating.

``pacemaker_info`` is the one exception: its return value is user-facing and on
older ``pcs`` it hands back raw plaintext strings under the ``*_info`` keys
instead of parsed dicts.
"""

from __future__ import annotations

import json
import re
import time
import typing as t

from ansible_collections.community.general.plugins.module_utils._cmd_runner import CmdRunner, cmd_runner_fmt

if t.TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from ansible.module_utils.basic import AnsibleModule


_state_map = {
    "present": "create",
    "absent": "remove",
    "cloned": "clone",
    "status": "status",
    "enabled": "enable",
    "disabled": "disable",
    "online": "start",
    "offline": "stop",
    "maintenance": "set",
    "config": "config",
    "cleanup": "cleanup",
}


# ``pcs`` versions supporting ``--output-format=json`` on the subcommands this
# collection needs. Bump if a new subcommand requires a newer floor.
_PCS_JSON_MIN = (0, 11, 6)

_PCS_VERSION_RE = re.compile(r"^\s*(\d+)\.(\d+)\.(\d+)")
_MAINTENANCE_MODE_RE = re.compile(r"maintenance-mode\s*[:=]\s*(true|false)\b", re.IGNORECASE)
# Accept both ``Clone:`` (modern pcs) and ``Clone Set:`` (older pcs) headers.
_CLONE_HEADER_RE = re.compile(r"^\s*Clone(?:\s+Set)?:\s+\S+", re.MULTILINE)


def fmt_resource_type(value):
    return [
        ":".join(
            value[k] for k in ["resource_standard", "resource_provider", "resource_name"] if value.get(k) is not None
        )
    ]


def fmt_resource_operation(value):
    cmd = []
    for op in value:
        cmd.append("op")
        cmd.append(op.get("operation_action"))
        for operation_option in op.get("operation_option"):
            cmd.append(operation_option)

    return cmd


def fmt_resource_argument(value):
    return ["--group" if value["argument_action"] == "group" else value["argument_action"]] + value["argument_option"]


def parse_pcs_version(raw: str) -> tuple[int, int, int] | None:
    """Parse the leading ``MAJOR.MINOR.PATCH`` from a ``pcs --version`` output line.

    Returns ``None`` if the output is empty or does not begin with a
    dotted-triple integer version. Trailing build/dev suffixes are ignored.
    """
    if not raw:
        return None
    match = _PCS_VERSION_RE.match(raw)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def _maintenance_mode_json(runner: PacemakerRunner) -> bool:
    """JSON path: parse ``pcs property config --output-format=json``."""
    with runner("cli_action config output_format") as ctx:
        rc, out, err = ctx.run(cli_action="property")
    try:
        data = json.loads(out)
    except (TypeError, ValueError):
        return False
    for nvset in data.get("nvsets", []):
        for nvpair in nvset.get("nvpairs", []):
            if nvpair.get("name") == "maintenance-mode" and nvpair.get("value") == "true":
                return True
    return False


def _maintenance_mode_plaintext(runner: PacemakerRunner) -> bool:
    """Plaintext path: query the single property directly and regex-match.

    Uses ``pcs property config maintenance-mode`` which returns output shaped
    like ``maintenance-mode=true``, ``maintenance-mode: true``, or
    ``maintenance-mode=false (default)`` depending on ``pcs`` version.
    """
    with runner("cli_action config name") as ctx:
        rc, out, err = ctx.run(cli_action="property", name="maintenance-mode")
    if rc != 0 or not out:
        return False
    match = _MAINTENANCE_MODE_RE.search(out)
    return bool(match and match.group(1).lower() == "true")


def get_pacemaker_maintenance_mode(runner: PacemakerRunner) -> bool:
    """Return ``True`` if cluster property ``maintenance-mode`` is set to ``true``.

    Dispatches to a JSON parser on ``pcs`` >= 0.11.6 and to a plaintext parser
    on older versions.
    """
    if runner.supports_json:
        return _maintenance_mode_json(runner)
    return _maintenance_mode_plaintext(runner)


def get_pacemaker_resource_config(runner: PacemakerRunner) -> dict | None:
    """Return parsed ``pcs resource config <name> --output-format=json`` for the
    runner-bound ``name``, or ``None`` if the output cannot be parsed or the
    installed ``pcs`` does not support JSON output.

    Callers requiring clone-idempotency on both new and old ``pcs`` should use
    :func:`is_resource_cloned_any` instead of consuming this DTO directly.
    """
    if not runner.supports_json:
        return None
    with runner("cli_action state name output_format") as ctx:
        rc, out, err = ctx.run(cli_action="resource", state="config")
    try:
        return json.loads(out)
    except (TypeError, ValueError):
        return None


def is_resource_cloned(config: Mapping, name: str) -> bool:
    """Return True if *name* appears as a clone ``member_id`` in the given resource
    config DTO. Matches both directly-cloned primitives and cloned groups, since pcs
    represents cloned-group membership the same way (``clones[].member_id == <group_id>``).
    """
    return any(clone.get("member_id") == name for clone in config.get("clones", []))


def is_resource_cloned_plaintext(runner: PacemakerRunner) -> bool:
    """Plaintext path: run ``pcs resource config <name>`` (no JSON) and check
    for a ``Clone:`` / ``Clone Set:`` header line in the output.

    The runner must already be bound to a resource ``name``.
    """
    with runner("cli_action state name") as ctx:
        rc, out, err = ctx.run(cli_action="resource", state="config")
    if rc != 0 or not out:
        return False
    return bool(_CLONE_HEADER_RE.search(out))


def is_resource_cloned_any(runner: PacemakerRunner, name: str) -> bool:
    """Version-dispatched idempotency check: is *name* already part of a clone?

    Uses structured JSON on ``pcs`` >= 0.11.6 and falls back to plaintext
    header matching on older versions. Both paths preserve idempotency of
    clone creation.
    """
    if runner.supports_json:
        config = get_pacemaker_resource_config(runner)
        return config is not None and is_resource_cloned(config, name)
    return is_resource_cloned_plaintext(runner)


_DEFAULT_RESOURCE_READY_STATES = ("Started",)


def wait_for_resource(
    runner: PacemakerRunner,
    cli_noun: str,
    name: str,
    wait: int,
    sleep_interval: int = 5,
    ready_states: Iterable[str] = _DEFAULT_RESOURCE_READY_STATES,
) -> None:
    """Poll ``pcs <cli_noun> status <name>`` until the resource reports a ready state or the wait budget expires.

    A resource is considered ready when its status output contains any of the states in
    *ready_states*. The default ``("Started",)`` matches non-promotable resources and stonith
    fencing devices. Callers managing promotable resources should pass
    ``("Started", "Promoted", "Unpromoted")`` because promotable resources never reach
    ``Started``.

    Raises an exception if the resource does not reach a ready state within *wait* seconds.
    """
    deadline = time.monotonic() + wait
    while True:
        with runner("cli_action state name") as ctx:
            rc, out, err = ctx.run(cli_action=cli_noun, state="status")
        if out and any(state in out for state in ready_states):
            return
        if time.monotonic() >= deadline:
            raise Exception(f"Timed out waiting {wait}s for {cli_noun} resource '{name}' to start")
        time.sleep(sleep_interval)


class PacemakerRunner(CmdRunner):
    """CmdRunner subclass for the ``pcs`` CLI.

    Probes ``pcs --version`` once at construction and exposes:

    * :attr:`raw_version` — the trimmed raw output of ``pcs --version`` (with
      any distro build suffix retained, for user-facing display).
    * :attr:`version` — the parsed ``(major, minor, patch)`` tuple, or ``None``
      when the probe fails or the output is unparseable.
    * :attr:`supports_json` — ``True`` when :attr:`version` is at least
      :data:`_PCS_JSON_MIN`. Version-dispatch helpers read this attribute to
      choose between the JSON and plaintext code paths; fails open (plaintext)
      on probe failure so a transient ``pcs --version`` glitch cannot break
      otherwise-functional automation.
    """

    def __init__(self, module: AnsibleModule, **kwargs) -> None:
        super().__init__(
            module,
            command=["pcs"],
            arg_formats=dict(
                cli_action=cmd_runner_fmt.as_list(),
                state=cmd_runner_fmt.as_map(_state_map),
                name=cmd_runner_fmt.as_list(),
                resource_type=cmd_runner_fmt.as_func(fmt_resource_type),
                resource_option=cmd_runner_fmt.as_list(),
                resource_operation=cmd_runner_fmt.as_func(fmt_resource_operation),
                resource_meta=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("meta"),
                resource_argument=cmd_runner_fmt.as_func(fmt_resource_argument),
                resource_clone_ids=cmd_runner_fmt.as_list(),
                resource_clone_meta=cmd_runner_fmt.as_list(),
                apply_all=cmd_runner_fmt.as_bool("--all"),
                agent_validation=cmd_runner_fmt.as_bool("--agent-validation"),
                wait=cmd_runner_fmt.as_opt_eq_val("--wait"),
                config=cmd_runner_fmt.as_fixed("config"),
                force=cmd_runner_fmt.as_bool("--force"),
                version=cmd_runner_fmt.as_fixed("--version"),
                output_format=cmd_runner_fmt.as_fixed("--output-format=json"),
            ),
            **kwargs,
        )
        self.raw_version = self._probe_version()
        self.version = parse_pcs_version(self.raw_version)
        self.supports_json = self.version is not None and self.version >= _PCS_JSON_MIN

    def _probe_version(self) -> str:
        """Shell out ``pcs --version`` and return the trimmed raw output.

        Returns an empty string on any probe failure so the parsers downstream
        gracefully treat the result as "unknown" (fails open to the plaintext
        path). Extracted as a method so tests can patch it via
        ``mocker.patch.object(PacemakerRunner, "_probe_version", ...)``.
        """
        with self("version") as ctx:
            rc, out, err = ctx.run()
        return out.strip() if rc == 0 and out else ""


def pacemaker_runner(module: AnsibleModule, **kwargs) -> PacemakerRunner:
    return PacemakerRunner(module, **kwargs)

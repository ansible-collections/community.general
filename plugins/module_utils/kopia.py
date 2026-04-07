# Copyright (c) 2026, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt

if t.TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule

# Maps kopia_repository module state values to kopia CLI subcommands.
# Used with cmd_runner_fmt.as_map() for the 'state' arg format.
REPOSITORY_STATE_MAP = {
    "created": "create",
    "connected": "connect",
    "disconnected": "disconnect",
    "synced": "sync-to",
    "throttled": "throttle",
}

# Maps backend provider names to their CLI flag names.
# Each provider emits its name as a positional sub-subcommand, followed by
# --flag value pairs for each non-None param.
# The "server" provider is intentionally absent: `kopia repository connect server`
# uses top-level flags (--url, --server-cert-fingerprint) rather than backend flags,
# so fmt_backend() returns [] for it and those flags are passed separately.
_PROVIDER_BACKEND_MAP = {
    "azure": {
        "container": "--container",
        "storage_account": "--storage-account",
        "storage_key": "--storage-key",
        "sas_token": "--sas-token",
        "storage_domain": "--storage-domain",
        "prefix": "--prefix",
    },
    "b2": {
        "bucket": "--bucket",
        "access_key": "--key-id",
        "secret_access_key": "--key",
        "prefix": "--prefix",
    },
    "filesystem": {
        "path": "--path",
    },
    "gcs": {
        "bucket": "--bucket",
        "credentials_file": "--credentials-file",
        "prefix": "--prefix",
    },
    "gdrive": {
        "folder_id": "--folder-id",
        "credentials_file": "--credentials-file",
    },
    "rclone": {
        "path": "--remote-path",
    },
    "s3": {
        "bucket": "--bucket",
        "access_key": "--access-key",
        "secret_access_key": "--secret-access-key",
        "endpoint": "--endpoint",
        "region": "--region",
        "prefix": "--prefix",
        "session_token": "--session-token",
    },
    "sftp": {
        "path": "--path",
        "host": "--host",
        "username": "--username",
        "port": "--port",
        "keyfile": "--keyfile",
        "known_hosts": "--known-hosts",
    },
    "webdav": {
        "url": "--url",
        "webdav_username": "--webdav-username",
        "webdav_password": "--webdav-password",
    },
}

# Argument spec entries shared by all kopia modules.
# Include this in each module's argument_spec via dict unpacking.
KOPIA_COMMON_ARGUMENT_SPEC = dict(
    password=dict(type="str", no_log=True),
    config=dict(type="path"),
)


def fmt_backend(value):
    """Format the backend dict into positional + flag arguments for kopia CLI.

    For most providers the output is:
        [provider_name, --flag1, value1, --flag2, value2, ...]

    For the "server" provider, returns [] because server connect uses top-level
    flags (--url, --server-cert-fingerprint) passed separately.
    """
    provider = value["provider"]
    if provider == "server":
        return []
    result = [provider]
    for param_name, flag in _PROVIDER_BACKEND_MAP[provider].items():
        param_value = value.get(param_name)
        if param_value is not None:
            result.append(f"{flag}={param_value}")
    return result


def kopia_runner(module: AnsibleModule, extra_formats: dict | None = None, **kwargs) -> CmdRunner:
    """Create a CmdRunner for the kopia CLI.

    Provides arg formats for all params shared across kopia modules.
    Pass extra_formats to add module-specific arg formats on top of the shared ones.
    """
    formats = dict(
        cli_action=cmd_runner_fmt.as_list(),
        state=cmd_runner_fmt.as_map(REPOSITORY_STATE_MAP),
        backend=cmd_runner_fmt.as_func(fmt_backend),
        password=cmd_runner_fmt.as_opt_eq_val("--password"),
        fingerprint_ssl=cmd_runner_fmt.as_opt_eq_val("--server-cert-fingerprint"),
        url=cmd_runner_fmt.as_opt_eq_val("--url"),
        config=cmd_runner_fmt.as_opt_eq_val("--config-file"),
        throttle_operation=cmd_runner_fmt.as_list(),
    )
    if extra_formats:
        formats.update(extra_formats)
    return CmdRunner(
        module,
        command=["kopia"],
        arg_formats=formats,
        **kwargs,
    )

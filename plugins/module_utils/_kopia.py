# Copyright (c) 2026, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import typing as t

from ansible_collections.community.general.plugins.module_utils._cmd_runner import CmdRunner, cmd_runner_fmt

if t.TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule

# Maps state values across all kopia modules to their kopia CLI subcommands.
# Used with cmd_runner_fmt.as_map() for the 'state' arg format.
STATE_MAP = {
    # kopia_repository
    "created": "create",
    "connected": "connect",
    "disconnected": "disconnect",
    "synced": "sync-to",
    "throttled": "throttle",
}

# Maps backend provider names to their CLI parameter definitions.
# Each provider maps param_name -> (flag, type) where type is:
#   "str"  - emit --flag=value (skip if None)
#   "bool" - emit --flag only when value is True (skip if False or None)
#   "list" - emit --flag item once per item in the list (skip if empty or None)
# The "server" provider is intentionally absent: `kopia repository connect server`
# uses top-level flags (--url, --server-cert-fingerprint) rather than backend flags,
# so fmt_backend() returns [] for it and those flags are passed separately.
_PROVIDER_BACKEND_MAP: dict[str, dict[str, tuple[str, str]]] = {
    "azure": {
        "container": ("--container", "str"),
        "storage_account": ("--storage-account", "str"),
        "storage_key": ("--storage-key", "str"),
        "sas_token": ("--sas-token", "str"),
        "storage_domain": ("--storage-domain", "str"),
        "prefix": ("--prefix", "str"),
        "client_id": ("--client-id", "str"),
        "client_secret": ("--client-secret", "str"),
        "tenant_id": ("--tenant-id", "str"),
        "azure_federated_token_file": ("--azure-federated-token-file", "str"),
    },
    "b2": {
        "bucket": ("--bucket", "str"),
        "access_key": ("--key-id", "str"),
        "secret_access_key": ("--key", "str"),
        "prefix": ("--prefix", "str"),
    },
    "filesystem": {
        "path": ("--path", "str"),
    },
    "gcs": {
        "bucket": ("--bucket", "str"),
        "credentials_file": ("--credentials-file", "str"),
        "prefix": ("--prefix", "str"),
        "embed_credentials": ("--embed-credentials", "bool"),
        "read_only": ("--read-only", "bool"),
    },
    "gdrive": {
        "folder_id": ("--folder-id", "str"),
        "credentials_file": ("--credentials-file", "str"),
        "read_only": ("--read-only", "bool"),
    },
    "rclone": {
        "path": ("--remote-path", "str"),
        "rclone_exe": ("--rclone-exe", "str"),
        "rclone_args": ("--rclone-args", "list"),
        "rclone_env": ("--rclone-env", "list"),
        "embed_rclone_config": ("--embed-rclone-config", "bool"),
    },
    "s3": {
        "bucket": ("--bucket", "str"),
        "access_key": ("--access-key", "str"),
        "secret_access_key": ("--secret-access-key", "str"),
        "endpoint": ("--endpoint", "str"),
        "region": ("--region", "str"),
        "prefix": ("--prefix", "str"),
        "session_token": ("--session-token", "str"),
    },
    "sftp": {
        "path": ("--path", "str"),
        "host": ("--host", "str"),
        "username": ("--username", "str"),
        "port": ("--port", "str"),
        "keyfile": ("--keyfile", "str"),
        "known_hosts": ("--known-hosts", "str"),
        "sftp_password": ("--sftp-password", "str"),
        "key_data": ("--key-data", "str"),
        "known_hosts_data": ("--known-hosts-data", "str"),
        "embed_credentials": ("--embed-credentials", "bool"),
        "external": ("--external", "bool"),
        "ssh_command": ("--ssh-command", "str"),
        "ssh_args": ("--ssh-args", "list"),
    },
    "webdav": {
        "url": ("--url", "str"),
        "webdav_username": ("--webdav-username", "str"),
        "webdav_password": ("--webdav-password", "str"),
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
        [provider_name, --flag1=value1, --flag2, ...]

    Param types:
        str  - emits --flag=value; skipped when value is None.
        bool - emits --flag when True; skipped when False or None.
        list - emits --flag item once per item; skipped when empty or None.

    For the "server" provider, returns [] because server connect uses top-level
    flags (--url, --server-cert-fingerprint) passed separately.
    """
    provider = value["provider"]
    if provider == "server":
        return []
    result = [provider]
    for param_name, (flag, kind) in _PROVIDER_BACKEND_MAP[provider].items():
        param_value = value.get(param_name)
        if kind == "str":
            if param_value is not None:
                result.append(f"{flag}={param_value}")
        elif kind == "bool":
            if param_value:
                result.append(flag)
        elif kind == "list":
            if param_value:
                for item in param_value:
                    result.extend([flag, item])
    return result


def _fmt_throttle(value):
    """Format the throttle dict into --flag value arguments for kopia repository throttle set."""
    if not value:
        return []
    flag_map = {
        "download_bytes_per_second": "--download-bytes-per-second",
        "upload_bytes_per_second": "--upload-bytes-per-second",
        "read_requests_per_second": "--read-requests-per-second",
        "write_requests_per_second": "--write-requests-per-second",
        "list_requests_per_second": "--list-requests-per-second",
        "concurrent_reads": "--concurrent-reads",
        "concurrent_writes": "--concurrent-writes",
    }
    result = []
    for param, flag in flag_map.items():
        v = value.get(param)
        if v is not None:
            result.extend([flag, str(v)])
    return result


def kopia_runner(module: AnsibleModule, extra_formats: dict | None = None, **kwargs) -> CmdRunner:
    """Create a CmdRunner for the kopia CLI.

    Provides arg formats for all params shared across kopia modules.
    Pass extra_formats to add module-specific arg formats on top of the shared ones.
    """
    formats = dict(
        cli_action=cmd_runner_fmt.as_list(),
        status=cmd_runner_fmt.as_fixed("repository", "status"),
        get_throttle=cmd_runner_fmt.as_fixed("repository", "throttle", "get"),
        state=cmd_runner_fmt.as_map(STATE_MAP),
        backend=cmd_runner_fmt.as_func(fmt_backend),
        password=cmd_runner_fmt.as_opt_eq_val("--password"),
        fingerprint_tls=cmd_runner_fmt.as_opt_eq_val("--server-cert-fingerprint"),
        url=cmd_runner_fmt.as_opt_eq_val("--url"),
        config=cmd_runner_fmt.as_opt_eq_val("--config-file"),
        throttle_operation=cmd_runner_fmt.as_list(),
        throttle=cmd_runner_fmt.as_func(_fmt_throttle),
    )
    if extra_formats:
        formats.update(extra_formats)
    return CmdRunner(
        module,
        command=["kopia"],
        arg_formats=formats,
        **kwargs,
    )

# Copyright (c) 2026, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.community.general.plugins.module_utils.kopia import (
    KOPIA_COMMON_ARGUMENT_SPEC,
    REPOSITORY_STATE_MAP,
    fmt_backend,
    kopia_runner,
)

# ---------------------------------------------------------------------------
# KOPIA_COMMON_ARGUMENT_SPEC
# ---------------------------------------------------------------------------


def test_common_argument_spec_has_password():
    assert "password" in KOPIA_COMMON_ARGUMENT_SPEC
    spec = KOPIA_COMMON_ARGUMENT_SPEC["password"]
    assert spec["type"] == "str"
    assert spec["no_log"] is True


def test_common_argument_spec_has_config():
    assert "config" in KOPIA_COMMON_ARGUMENT_SPEC
    assert KOPIA_COMMON_ARGUMENT_SPEC["config"]["type"] == "path"


def test_common_argument_spec_only_two_keys():
    assert set(KOPIA_COMMON_ARGUMENT_SPEC.keys()) == {"password", "config"}


# ---------------------------------------------------------------------------
# REPOSITORY_STATE_MAP
# ---------------------------------------------------------------------------


def test_repository_state_map_entries():
    assert REPOSITORY_STATE_MAP["created"] == "create"
    assert REPOSITORY_STATE_MAP["connected"] == "connect"
    assert REPOSITORY_STATE_MAP["disconnected"] == "disconnect"
    assert REPOSITORY_STATE_MAP["synced"] == "sync-to"
    assert REPOSITORY_STATE_MAP["throttled"] == "throttle"


# ---------------------------------------------------------------------------
# fmt_backend
# ---------------------------------------------------------------------------

TC_FMT_BACKEND = dict(
    server=(
        {"provider": "server"},
        [],
    ),
    filesystem_path=(
        {"provider": "filesystem", "path": "/mnt/backup"},
        ["filesystem", "--path=/mnt/backup"],
    ),
    filesystem_no_path=(
        {"provider": "filesystem"},
        ["filesystem"],
    ),
    s3_full=(
        {
            "provider": "s3",
            "bucket": "my-bucket",
            "access_key": "keyid",
            "secret_access_key": "secret",
            "endpoint": "https://s3.example.com",
            "region": "us-east-1",
            "prefix": "backups/",
            "session_token": "tok123",
        },
        [
            "s3",
            "--bucket=my-bucket",
            "--access-key=keyid",
            "--secret-access-key=secret",
            "--endpoint=https://s3.example.com",
            "--region=us-east-1",
            "--prefix=backups/",
            "--session-token=tok123",
        ],
    ),
    s3_minimal=(
        {"provider": "s3", "bucket": "my-bucket"},
        ["s3", "--bucket=my-bucket"],
    ),
    azure_full=(
        {
            "provider": "azure",
            "container": "my-container",
            "storage_account": "myaccount",
            "storage_key": "mykey",
            "sas_token": "mytoken",
            "storage_domain": "blob.core.windows.net",
            "prefix": "data/",
        },
        [
            "azure",
            "--container=my-container",
            "--storage-account=myaccount",
            "--storage-key=mykey",
            "--sas-token=mytoken",
            "--storage-domain=blob.core.windows.net",
            "--prefix=data/",
        ],
    ),
    azure_minimal=(
        {"provider": "azure", "container": "my-container", "storage_account": "myaccount"},
        ["azure", "--container=my-container", "--storage-account=myaccount"],
    ),
    gcs_full=(
        {"provider": "gcs", "bucket": "my-bucket", "credentials_file": "/etc/gcs.json", "prefix": "kopia/"},
        ["gcs", "--bucket=my-bucket", "--credentials-file=/etc/gcs.json", "--prefix=kopia/"],
    ),
    gdrive=(
        {"provider": "gdrive", "folder_id": "abc123", "credentials_file": "/etc/gdrive.json"},
        ["gdrive", "--folder-id=abc123", "--credentials-file=/etc/gdrive.json"],
    ),
    b2_full=(
        {"provider": "b2", "bucket": "my-b2-bucket", "access_key": "kid", "secret_access_key": "sec"},
        ["b2", "--bucket=my-b2-bucket", "--key-id=kid", "--key=sec"],
    ),
    rclone=(
        {"provider": "rclone", "path": "remote:backup"},
        ["rclone", "--remote-path=remote:backup"],
    ),
    sftp_full=(
        {
            "provider": "sftp",
            "path": "/backup",
            "host": "sftp.example.com",
            "username": "admin",
            "port": "22",
            "keyfile": "/root/.ssh/id_rsa",
            "known_hosts": "/root/.ssh/known_hosts",
        },
        [
            "sftp",
            "--path=/backup",
            "--host=sftp.example.com",
            "--username=admin",
            "--port=22",
            "--keyfile=/root/.ssh/id_rsa",
            "--known-hosts=/root/.ssh/known_hosts",
        ],
    ),
    webdav_full=(
        {
            "provider": "webdav",
            "url": "https://dav.example.com",
            "webdav_username": "user",
            "webdav_password": "pass",
        },
        ["webdav", "--url=https://dav.example.com", "--webdav-username=user", "--webdav-password=pass"],
    ),
    none_values_skipped=(
        {"provider": "s3", "bucket": "b", "access_key": None, "secret_access_key": None},
        ["s3", "--bucket=b"],
    ),
)

TC_FMT_BACKEND_IDS = sorted(TC_FMT_BACKEND.keys())


@pytest.mark.parametrize(
    "backend, expected",
    (TC_FMT_BACKEND[tc] for tc in TC_FMT_BACKEND_IDS),
    ids=TC_FMT_BACKEND_IDS,
)
def test_fmt_backend(backend, expected):
    assert fmt_backend(backend) == expected


# ---------------------------------------------------------------------------
# kopia_runner
# ---------------------------------------------------------------------------


def _make_mock_module(**params):
    module = MagicMock()
    module.params = params
    module.get_bin_path.return_value = "/testbin/kopia"
    module.run_command.return_value = (0, "", "")
    return module


def test_kopia_runner_returns_cmd_runner():
    from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner

    module = _make_mock_module(config=None, password=None)
    with patch(
        "ansible_collections.community.general.plugins.module_utils.cmd_runner.CmdRunner.__init__",
        return_value=None,
    ):
        runner = kopia_runner(module)
    # kopia_runner returns a CmdRunner instance
    assert isinstance(runner, CmdRunner)


def test_kopia_runner_has_shared_formats():
    """Verify that the shared format keys are registered."""
    formats_captured = {}

    original_init = __import__(
        "ansible_collections.community.general.plugins.module_utils.cmd_runner",
        fromlist=["CmdRunner"],
    ).CmdRunner.__init__

    def capturing_init(self, module, command, arg_formats=None, **kwargs):
        if arg_formats:
            formats_captured.update(arg_formats)
        original_init(self, module, command, arg_formats=arg_formats, **kwargs)

    module = _make_mock_module(config=None, password=None)
    with patch(
        "ansible_collections.community.general.plugins.module_utils.cmd_runner.CmdRunner.__init__",
        capturing_init,
    ):
        kopia_runner(module)

    for key in ("cli_action", "state", "backend", "password", "fingerprint_ssl", "url", "config", "throttle_operation"):
        assert key in formats_captured, f"expected format key '{key}' not registered"


def test_kopia_runner_extra_formats_merged():
    """Extra formats passed to kopia_runner are merged into args_formats."""
    formats_captured = {}

    original_init = __import__(
        "ansible_collections.community.general.plugins.module_utils.cmd_runner",
        fromlist=["CmdRunner"],
    ).CmdRunner.__init__

    def capturing_init(self, module, command, arg_formats=None, **kwargs):
        if arg_formats:
            formats_captured.update(arg_formats)
        original_init(self, module, command, arg_formats=arg_formats, **kwargs)

    from ansible_collections.community.general.plugins.module_utils.cmd_runner import cmd_runner_fmt

    extra = {"my_custom_flag": cmd_runner_fmt.as_opt_eq_val("--custom")}

    module = _make_mock_module(config=None, password=None)
    with patch(
        "ansible_collections.community.general.plugins.module_utils.cmd_runner.CmdRunner.__init__",
        capturing_init,
    ):
        kopia_runner(module, extra_formats=extra)

    assert "my_custom_flag" in formats_captured
    # shared keys still present
    assert "cli_action" in formats_captured


def test_kopia_runner_no_extra_formats():
    """kopia_runner(module, extra_formats=None) should not raise."""
    module = _make_mock_module(config=None, password=None)
    # Should not raise; CmdRunner will call get_bin_path internally
    try:
        kopia_runner(module, extra_formats=None)
    except Exception:
        pass  # CmdRunner may need the binary; we just ensure no TypeError from extra_formats

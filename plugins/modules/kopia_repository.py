#!/usr/bin/python

# Copyright (c) 2026, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: kopia_repository
short_description: Manage Kopia repository
author:
  - Dexter Le (@munchtoast)
version_added: "13.1.0"
description:
  - Manage a Kopia repository using the Kopia CLI.
  - Supports creating, connecting, disconnecting, syncing, and throttling repositories.
extends_documentation_fragment:
  - community.general._attributes
  - community.general._kopia
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  state:
    description:
      - Desired state of the Kopia repository.
    type: str
    choices:
      created: Creates a new repository at the given backend.
      connected: Connects to an existing repository or Kopia server.
      disconnected: Disconnects from the current repository.
      synced: Synchronizes the current repository to another backend location.
      throttled: Sets throttle limits on the current repository.
    default: created
  fingerprint_tls:
    description:
      - TLS certificate fingerprint of the Kopia server.
      - Required if O(state=connected) and O(backend.provider=server).
    type: str
  url:
    description:
      - URL of the Kopia server to connect to.
      - Required if O(state=connected) and O(backend.provider=server).
    type: str
  throttle:
    description:
      - Throttle limits for the repository connection.
      - Only used when O(state=throttled).
    type: dict
    suboptions:
      download_bytes_per_second:
        description:
          - Maximum download speed in bytes per second. Set to V(0) to disable the limit.
        type: int
      upload_bytes_per_second:
        description:
          - Maximum upload speed in bytes per second. Set to V(0) to disable the limit.
        type: int
      read_requests_per_second:
        description:
          - Maximum number of read requests per second.
        type: float
      write_requests_per_second:
        description:
          - Maximum number of write requests per second.
        type: float
      list_requests_per_second:
        description:
          - Maximum number of list requests per second.
        type: float
      concurrent_reads:
        description:
          - Maximum number of concurrent read operations.
        type: int
      concurrent_writes:
        description:
          - Maximum number of concurrent write operations.
        type: int
  backend:
    description:
      - Backend storage configuration for the repository.
      - Required if O(state=created), O(state=connected), or O(state=synced).
    type: dict
    suboptions:
      provider:
        description:
          - Backend storage provider.
          - Use V(server) to connect to a Kopia repository server instead of directly to storage.
        type: str
        required: true
        choices: [azure, b2, filesystem, gcs, gdrive, rclone, s3, sftp, webdav, server]
      bucket:
        description:
          - Bucket name for the backend.
          - Required if O(backend.provider=b2), O(backend.provider=gcs), or O(backend.provider=s3).
        type: str
      container:
        description:
          - Azure Blob Storage container name.
          - Required if O(backend.provider=azure).
        type: str
      storage_account:
        description:
          - Azure storage account name.
          - Required if O(backend.provider=azure).
        type: str
      storage_key:
        description:
          - Azure storage account key used to authenticate.
          - Optional if O(backend.provider=azure); omit when using managed identity or SAS tokens.
        type: str
      sas_token:
        description:
          - Azure Shared Access Signature token for authentication.
          - Optional alternative to O(backend.storage_key) when O(backend.provider=azure).
        type: str
      storage_domain:
        description:
          - Azure storage domain override.
          - Optional if O(backend.provider=azure).
        type: str
      access_key:
        description:
          - Access key ID for the backend.
          - Required if O(backend.provider=b2) or O(backend.provider=s3).
        type: str
      secret_access_key:
        description:
          - Secret access key for the backend.
          - Required if O(backend.provider=b2) or O(backend.provider=s3).
        type: str
      session_token:
        description:
          - Session token for temporary AWS credentials.
          - Optional if O(backend.provider=s3).
        type: str
      endpoint:
        description:
          - S3-compatible endpoint URL.
          - Optional if O(backend.provider=s3); defaults to C(s3.amazonaws.com).
        type: str
      region:
        description:
          - S3 bucket region.
          - Optional if O(backend.provider=s3).
        type: str
      folder_id:
        description:
          - Google Drive folder ID to use as the backend root.
          - Required if O(backend.provider=gdrive).
        type: str
      credentials_file:
        description:
          - Path to a JSON credentials file for authentication.
          - Optional if O(backend.provider=gcs) or O(backend.provider=gdrive).
        type: path
      path:
        description:
          - Local file system path or remote path for the backend.
          - Required if O(backend.provider=filesystem), O(backend.provider=rclone), or O(backend.provider=sftp).
        type: path
      host:
        description:
          - SFTP server hostname.
          - Required if O(backend.provider=sftp).
        type: str
      username:
        description:
          - SFTP username for authentication.
          - Required if O(backend.provider=sftp).
        type: str
      port:
        description:
          - SFTP server port.
          - Optional if O(backend.provider=sftp); defaults to V(22).
        type: int
      keyfile:
        description:
          - Path to the SSH private key file for SFTP authentication.
          - Optional if O(backend.provider=sftp).
        type: path
      known_hosts:
        description:
          - Path to a known_hosts file for SFTP host key verification.
          - Optional if O(backend.provider=sftp).
        type: path
      url:
        description:
          - WebDAV server URL.
          - Required if O(backend.provider=webdav).
        type: str
      webdav_username:
        description:
          - Username for WebDAV authentication.
          - Optional if O(backend.provider=webdav).
        type: str
      webdav_password:
        description:
          - Password for WebDAV authentication.
          - Optional if O(backend.provider=webdav).
        type: str
      prefix:
        description:
          - Object key prefix within the backend storage.
          - Optional if O(backend.provider=azure), O(backend.provider=b2),
            O(backend.provider=gcs), or O(backend.provider=s3).
        type: str
"""

EXAMPLES = r"""
- name: Create a Kopia repository with S3 backend
  community.general.kopia_repository:
    state: created
    password: secret
    config: /etc/kopia/root.config
    backend:
      provider: s3
      bucket: my-bucket
      access_key: myaccesskey
      secret_access_key: mysecretaccesskey

- name: Create a Kopia repository on the local filesystem
  community.general.kopia_repository:
    state: created
    password: secret
    backend:
      provider: filesystem
      path: /mnt/backup/kopia

- name: Connect to a Kopia repository server
  community.general.kopia_repository:
    state: connected
    password: secret
    config: /etc/kopia/root.config
    url: https://kopia.example.com:51515
    fingerprint_tls: AA:BB:CC:DD:EE:FF
    backend:
      provider: server

- name: Connect directly to an Azure backend
  community.general.kopia_repository:
    state: connected
    password: secret
    backend:
      provider: azure
      container: my-container
      storage_account: mystorageaccount
      storage_key: mystoragekey

- name: Disconnect the Kopia repository
  community.general.kopia_repository:
    state: disconnected
    config: /etc/kopia/root.config

- name: Sync Kopia repository to an S3 location
  community.general.kopia_repository:
    state: synced
    password: secret
    config: /etc/kopia/root.config
    backend:
      provider: s3
      bucket: my-synced-bucket
      access_key: myaccesskey
      secret_access_key: mysecretaccesskey
"""

RETURN = r"""
kopia_repository:
  description: Output from the Kopia repository command.
  type: str
  sample: |-
    Connected to repository: s3:/my-bucket/
    Config file: /etc/kopia/root.config
    ...
  returned: always
"""

from ansible_collections.community.general.plugins.module_utils._kopia import (
    KOPIA_COMMON_ARGUMENT_SPEC,
    kopia_runner,
)
from ansible_collections.community.general.plugins.module_utils._module_helper import StateModuleHelper


class KopiaRepository(StateModuleHelper):
    module = dict(
        supports_check_mode=True,
        argument_spec=dict(
            **KOPIA_COMMON_ARGUMENT_SPEC,
            state=dict(
                type="str",
                default="created",
                choices=["created", "connected", "disconnected", "synced", "throttled"],
            ),
            fingerprint_tls=dict(type="str"),
            url=dict(type="str"),
            throttle=dict(
                type="dict",
                options=dict(
                    download_bytes_per_second=dict(type="int"),
                    upload_bytes_per_second=dict(type="int"),
                    read_requests_per_second=dict(type="float"),
                    write_requests_per_second=dict(type="float"),
                    list_requests_per_second=dict(type="float"),
                    concurrent_reads=dict(type="int"),
                    concurrent_writes=dict(type="int"),
                ),
            ),
            backend=dict(
                type="dict",
                options=dict(
                    provider=dict(
                        type="str",
                        required=True,
                        choices=[
                            "azure",
                            "b2",
                            "filesystem",
                            "gcs",
                            "gdrive",
                            "rclone",
                            "s3",
                            "sftp",
                            "webdav",
                            "server",
                        ],
                    ),
                    bucket=dict(type="str"),
                    container=dict(type="str"),
                    storage_account=dict(type="str"),
                    storage_key=dict(type="str", no_log=True),
                    sas_token=dict(type="str", no_log=True),
                    storage_domain=dict(type="str"),
                    access_key=dict(type="str", no_log=True),
                    secret_access_key=dict(type="str", no_log=True),
                    session_token=dict(type="str", no_log=True),
                    endpoint=dict(type="str"),
                    region=dict(type="str"),
                    folder_id=dict(type="str"),
                    credentials_file=dict(type="path"),
                    path=dict(type="path"),
                    host=dict(type="str"),
                    username=dict(type="str"),
                    port=dict(type="int"),
                    keyfile=dict(type="path"),
                    known_hosts=dict(type="path"),
                    url=dict(type="str"),
                    webdav_username=dict(type="str"),
                    webdav_password=dict(type="str", no_log=True),
                    prefix=dict(type="str"),
                ),
                required_if=[
                    ("provider", "azure", ["container", "storage_account"]),
                    ("provider", "b2", ["bucket", "access_key", "secret_access_key"]),
                    ("provider", "filesystem", ["path"]),
                    ("provider", "gcs", ["bucket"]),
                    ("provider", "gdrive", ["folder_id"]),
                    ("provider", "rclone", ["path"]),
                    ("provider", "s3", ["bucket", "access_key", "secret_access_key"]),
                    ("provider", "sftp", ["path", "host", "username"]),
                    ("provider", "webdav", ["url"]),
                ],
            ),
        ),
        required_if=[
            ("state", "created", ["backend"]),
            ("state", "connected", ["backend"]),
            ("state", "synced", ["backend"]),
        ],
    )

    def __init_module__(self):
        self.runner = kopia_runner(self.module)
        self.vars.set("previous_value", self._get()["out"])
        self.vars.set("value", self.vars.previous_value, change=True, diff=True)

    def __quit_module__(self):
        if self.module.check_mode:
            self.vars.set("value", self._predict_value())
        else:
            self.vars.set("value", self._get()["out"])

    def _predict_value(self):
        """Predict the post-operation repository status for check mode change detection."""
        state = self.module.params["state"]
        previous = self.vars.previous_value
        if state in ("created", "connected"):
            return previous if previous is not None else "Connected to repository."
        if state == "disconnected":
            return None if previous is not None else previous
        return previous

    def _get(self):
        with self.runner("status config") as ctx:
            result = ctx.run()
            return dict(
                rc=result[0],
                out=(result[1].rstrip() if result[1] else None),
                err=result[2],
            )

    def _process_command_output(self, fail_on_err, ignore_err_msg=""):
        def process(rc, out, err):
            if fail_on_err and rc != 0 and err and ignore_err_msg not in err:
                self.do_raise(f"kopia failed with error (rc={rc}): {err}")
            out = out.rstrip()
            return None if out == "" else out

        return process

    def state_created(self):
        with self.runner(
            "cli_action state backend password config",
            output_process=self._process_command_output(True, "already exists"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="repository")

    def state_connected(self):
        with self.runner(
            "cli_action state backend password fingerprint_tls url config",
            output_process=self._process_command_output(True, "already connected"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="repository")

    def state_disconnected(self):
        with self.runner(
            "cli_action state password config",
            output_process=self._process_command_output(True, "does not exist"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="repository")

    def state_synced(self):
        with self.runner(
            "cli_action state backend password config",
            output_process=self._process_command_output(True, "already synced"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="repository")

    def state_throttled(self):
        with self.runner(
            "cli_action state throttle_operation throttle config",
            output_process=self._process_command_output(True),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="repository", throttle_operation="set")


def main():
    KopiaRepository.execute()


if __name__ == "__main__":
    main()

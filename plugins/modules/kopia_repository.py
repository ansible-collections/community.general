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
version_added: "12.6.0"
description:
  - Manage a Kopia repository using the Kopia CLI.
  - Supports creating, connecting, disconnecting, syncing, and throttling repositories.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  state:
    description:
      - Desired state of the Kopia repository.
      - V(created) creates a new repository at the given backend.
      - V(connected) connects to an existing repository or Kopia server.
      - V(disconnected) disconnects from the current repository.
      - V(synced) synchronises the current repository to another backend location.
      - V(throttled) sets or gets throttle limits on the current repository.
    type: str
    choices: [created, connected, disconnected, synced, throttled]
    default: created
  password:
    description:
      - Repository password used to encrypt and decrypt repository contents.
      - Required if O(state=created) or O(state=connected).
    type: str
  fingerprint_ssl:
    description:
      - TLS certificate fingerprint of the Kopia server.
      - Required if O(state=connected) and O(backend.provider=server).
    type: str
  url:
    description:
      - URL of the Kopia server to connect to.
      - Required if O(state=connected) and O(backend.provider=server).
    type: str
  config:
    description:
      - Path to the Kopia config file for this repository connection.
      - Defaults to the Kopia default config path when not set.
    type: path
  throttle_operation:
    description:
      - Whether to V(set) or V(get) throttle limits on the repository.
      - Required if O(state=throttled).
    type: str
    choices: [set, get]
    default: get
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
          - Optional if O(backend.provider=azure); can be omitted when using managed identity or SAS tokens.
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
          - Local filesystem path or remote path for the backend.
          - Required if O(backend.provider=filesystem), O(backend.provider=rclone), or O(backend.provider=sftp).
        type: str
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
          - Optional if O(backend.provider=sftp); defaults to C(22).
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
    fingerprint_ssl: AA:BB:CC:DD:EE:FF
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

- name: Get throttle settings for the Kopia repository
  community.general.kopia_repository:
    state: throttled
    throttle_operation: get
    config: /etc/kopia/root.config
"""

RETURN = r"""
kopia_repository:
  description: Output from the Kopia repository command.
  type: str
  sample: ""
  returned: always
"""

from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper
from ansible_collections.community.general.plugins.module_utils.kopia import (
    KOPIA_COMMON_ARGUMENT_SPEC,
    kopia_runner,
)


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
            fingerprint_ssl=dict(type="str"),
            url=dict(type="str"),
            throttle_operation=dict(type="str", default="get", choices=["set", "get"]),
            backend=dict(
                type="dict",
                options=dict(
                    provider=dict(
                        type="str",
                        required=True,
                        choices=["azure", "b2", "filesystem", "gcs", "gdrive", "rclone", "s3", "sftp", "webdav", "server"],
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
                    path=dict(type="str"),
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
        self.vars.set("value", self._get()["out"])

    def _get(self):
        with self.runner("cli_action config") as ctx:
            result = ctx.run(cli_action=["repository", "status"])
            return dict(
                rc=result[0],
                out=(result[1].rstrip() if result[1] else None),
                err=result[2],
            )

    def _process_command_output(self, fail_on_err, ignore_err_msg=""):
        def process(rc, out, err):
            if fail_on_err and rc != 0 and err and ignore_err_msg not in err:
                self.do_raise(f"kopia failed with error (rc={rc}): {err}")
            out = out.rstrip() if out else ""
            return None if out == "" else out

        return process

    def state_created(self):
        with self.runner(
            "cli_action state backend password config",
            output_process=self._process_command_output(True, "already exists"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="repository", state=self.vars.state)

    def state_connected(self):
        with self.runner(
            "cli_action state backend password fingerprint_ssl url config",
            output_process=self._process_command_output(True, "already connected"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="repository", state=self.vars.state)

    def state_disconnected(self):
        with self.runner(
            "cli_action state password config",
            output_process=self._process_command_output(True, "does not exist"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="repository", state=self.vars.state)

    def state_synced(self):
        with self.runner(
            "cli_action state backend password config",
            output_process=self._process_command_output(True, "already synced"),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="repository", state=self.vars.state)

    def state_throttled(self):
        with self.runner(
            "cli_action state throttle_operation config",
            output_process=self._process_command_output(True),
            check_mode_skip=True,
        ) as ctx:
            ctx.run(cli_action="repository", state=self.vars.state)


def main():
    KopiaRepository.execute()


if __name__ == "__main__":
    main()

# Copyright (c) 2025, Sean McAvoy (@smcavoy) <seanmcavoy@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = """
---
module: lxd_storage_pool_info
short_description: Retrieve information about LXD storage pools
version_added: 12.1.0
description:
  - Retrieve information about LXD storage pools.
  - This module returns details about all storage pools or a specific storage pool.
author: "Sean McAvoy (@smcavoy)"
extends_documentation_fragment:
  - community.general.attributes
  - community.general.attributes.info_module
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  name:
    description:
      - Name of a specific storage pool to retrieve information about.
      - If not specified, information about all storage pools are returned.
    type: str
  type:
    description:
      - Filter storage pools by driver/type (for example V(dir), V(zfs), V(btrfs), V(lvm), or V(ceph)).
      - If not specified, all storage pool types are returned.
      - Can be a single type or a list of types.
    type: list
    elements: str
    default: []
  project:
    description:
      - 'Project of the storage pool.
        See U(https://documentation.ubuntu.com/lxd/en/latest/projects/).'
    type: str
  url:
    description:
      - The Unix domain socket path or the https URL for the LXD server.
    default: unix:/var/lib/lxd/unix.socket
    type: str
  snap_url:
    description:
      - The Unix domain socket path when LXD is installed by snap package manager.
    default: unix:/var/snap/lxd/common/lxd/unix.socket
    type: str
  client_key:
    description:
      - The client certificate key file path.
      - If not specified, it defaults to C($HOME/.config/lxc/client.key).
    aliases: [key_file]
    type: path
  client_cert:
    description:
      - The client certificate file path.
      - If not specified, it defaults to C($HOME/.config/lxc/client.crt).
    aliases: [cert_file]
    type: path
  trust_password:
    description:
      - The client trusted password.
      - 'You need to set this password on the LXD server before
        running this module using the following command:
        C(lxc config set core.trust_password <some random password>)
        See U(https://www.stgraber.org/2016/04/18/lxd-api-direct-interaction/).'
      - If O(trust_password) is set, this module sends a request for
        authentication before sending any requests.
    type: str
"""

EXAMPLES = """
- name: Get information about all storage pools
  community.general.lxd_storage_pool_info:
  register: result

- name: Get information about a specific storage pool
  community.general.lxd_storage_pool_info:
    name: default
  register: result

- name: Get information about all ZFS storage pools
  community.general.lxd_storage_pool_info:
    type:
      - zfs
      - ceph
  register: result

- name: Get information about ZFS and BTRFS storage pools
  community.general.lxd_storage_pool_info:
    type:
      - zfs
      - btrfs
  register: result

- name: Get storage pool information via HTTPS connection
  community.general.lxd_storage_pool_info:
    url: https://127.0.0.1:8443
    trust_password: mypassword
    name: default
  register: result

- name: Get storage pool information for a specific project
  community.general.lxd_storage_pool_info:
    project: myproject
  register: result
"""

RETURN = """
storage_pools:
  description: List of LXD storage pools.
  returned: success
  type: list
  elements: dict
  sample: [
    {
      "name": "default",
      "driver": "dir",
      "used_by": ["/1.0/instances/container1"],
      "config": {
        "source": "/var/lib/lxd/storage-pools/default"
      },
      "description": "Default storage pool",
      "status": "Created",
      "locations": ["none"]
    }
  ]
  contains:
    name:
      description: The name of the storage pool.
      type: str
      returned: success
    driver:
      description: The storage pool driver/type.
      type: str
      returned: success
    used_by:
      description: List of resources using this storage pool.
      type: list
      elements: str
      returned: success
    config:
      description: Configuration of the storage pool.
      type: dict
      returned: success
    description:
      description: Description of the storage pool.
      type: str
      returned: success
    status:
      description: Current status of the storage pool.
      type: str
      returned: success
    locations:
      description: Cluster member locations for the pool.
      type: list
      elements: str
      returned: success
logs:
  description: The logs of requests and responses.
  returned: when ansible-playbook is invoked with -vvvv.
  type: list
  elements: dict
  sample: [
    {
      "type": "sent request",
      "request": {
        "method": "GET",
        "url": "/1.0/storage-pools",
        "json": null,
        "timeout": null
      },
      "response": {
        "json": {"type": "sync", "status": "Success"}
      }
    }
  ]
"""

import os
import typing as t
from urllib.parse import urlencode

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils.lxd import (
    LXDClient,
    LXDClientException,
    default_cert_file,
    default_key_file,
)

# ANSIBLE_LXD_DEFAULT_URL is a default value of the lxd endpoint
ANSIBLE_LXD_DEFAULT_URL = "unix:/var/lib/lxd/unix.socket"
ANSIBLE_LXD_DEFAULT_SNAP_URL = "unix:/var/snap/lxd/common/lxd/unix.socket"

# API endpoints
LXD_API_VERSION = "1.0"
LXD_API_STORAGE_POOLS_ENDPOINT = f"/{LXD_API_VERSION}/storage-pools"


class LXDStoragePoolInfo:
    def __init__(self, module: AnsibleModule) -> None:
        """Gather information about LXD storage pools.

        :param module: Processed Ansible Module.
        :type module: AnsibleModule
        """
        self.module = module
        self.name = self.module.params["name"]
        # pool_type is guaranteed to be a list (may be empty) due to default=[]
        self.pool_type = self.module.params["type"]
        self.project = self.module.params["project"]

        self.key_file = self.module.params["client_key"]
        if self.key_file is None:
            self.key_file = default_key_file()
        self.cert_file = self.module.params["client_cert"]
        if self.cert_file is None:
            self.cert_file = default_cert_file()
        self.debug = self.module._verbosity >= 4

        snap_socket_path = self.module.params["snap_url"]
        if snap_socket_path.startswith("unix:"):
            snap_socket_path = snap_socket_path[5:]

        if self.module.params["url"] != ANSIBLE_LXD_DEFAULT_URL:
            self.url = self.module.params["url"]
        elif os.path.exists(snap_socket_path):
            self.url = self.module.params["snap_url"]
        else:
            self.url = self.module.params["url"]

        try:
            self.client = LXDClient(
                self.url,
                key_file=self.key_file,
                cert_file=self.cert_file,
                debug=self.debug,
            )
        except LXDClientException as e:
            self._fail_from_lxd_exception(e)

        self.trust_password = self.module.params["trust_password"]

    def _fail_from_lxd_exception(self, exception: LXDClientException) -> t.NoReturn:
        """Build failure parameters from LXDClientException and fail.

        :param exception: The LXDClientException instance
        :type exception: LXDClientException
        """
        fail_params = {}
        if self.client.debug and "logs" in exception.kwargs:
            fail_params["logs"] = exception.kwargs["logs"]
        self.module.fail_json(msg=exception.msg, changed=False, **fail_params)

    def _build_url(self, endpoint: str) -> str:
        """Build URL with project parameter if specified."""
        if self.project:
            return f"{endpoint}?{urlencode({'project': self.project})}"
        return endpoint

    def _get_storage_pool_list(self, recursion: int = 0) -> list:
        """Get list of all storage pools.

        :param recursion: API recursion level (0 for URLs only, 1 for full objects)
        :type recursion: int
        :return: List of pool names (recursion=0) or pool objects (recursion=1)
        :rtype: list
        """
        endpoint = LXD_API_STORAGE_POOLS_ENDPOINT
        if recursion > 0:
            endpoint = f"{endpoint}?recursion={recursion}"
        url = self._build_url(endpoint)
        resp_json = self.client.do("GET", url, ok_error_codes=[])

        if resp_json["type"] == "error":
            self.module.fail_json(
                msg=f"Failed to retrieve storage pools: {resp_json.get('error', 'Unknown error')}",
                error_code=resp_json.get("error_code"),
            )

        metadata = resp_json.get("metadata", [])

        if recursion == 0:
            # With recursion=0: list of pool URLs like ['/1.0/storage-pools/default']
            # Extract the pool names from URLs
            return [url.split("/")[-1] for url in metadata]
        else:
            # With recursion=1: list of pool objects with full metadata
            return metadata

    def _get_storage_pool_info(self, pool_name: str) -> dict:
        """Get detailed information about a specific storage pool."""
        url = self._build_url(f"{LXD_API_STORAGE_POOLS_ENDPOINT}/{pool_name}")
        resp_json = self.client.do("GET", url, ok_error_codes=[404])

        if resp_json["type"] == "error":
            if resp_json.get("error_code") == 404:
                self.module.fail_json(msg=f'Storage pool "{pool_name}" not found')
            else:
                self.module.fail_json(
                    msg=f'Failed to retrieve storage pool "{pool_name}": {resp_json.get("error", "Unknown error")}',
                    error_code=resp_json.get("error_code"),
                )

        return resp_json.get("metadata", {})

    def get_storage_pools(self) -> list[dict]:
        """Retrieve storage pool information based on module parameters."""
        storage_pools = []

        if self.name:
            # Get information about a specific storage pool
            pool_info = self._get_storage_pool_info(self.name)
            storage_pools.append(pool_info)
        else:
            # Get information about all storage pools using recursion
            # This retrieves all pool details in a single API call instead of one call per pool
            storage_pools = self._get_storage_pool_list(recursion=1)

        # Filter by type if specified
        if self.pool_type:
            storage_pools = [pool for pool in storage_pools if pool.get("driver") in self.pool_type]

        return storage_pools

    def run(self) -> None:
        """Run the main method."""
        try:
            if self.trust_password is not None:
                self.client.authenticate(self.trust_password)

            storage_pools = self.get_storage_pools()

            result_json = {"storage_pools": storage_pools}
            if self.client.debug:
                result_json["logs"] = self.client.logs
            self.module.exit_json(**result_json)
        except LXDClientException as e:
            self._fail_from_lxd_exception(e)


def main() -> None:
    """Ansible Main module."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str"),
            type=dict(type="list", elements="str", default=[]),
            project=dict(type="str"),
            url=dict(type="str", default=ANSIBLE_LXD_DEFAULT_URL),
            snap_url=dict(type="str", default=ANSIBLE_LXD_DEFAULT_SNAP_URL),
            client_key=dict(type="path", aliases=["key_file"]),
            client_cert=dict(type="path", aliases=["cert_file"]),
            trust_password=dict(type="str", no_log=True),
        ),
        supports_check_mode=True,
    )

    lxd_info = LXDStoragePoolInfo(module=module)
    lxd_info.run()


if __name__ == "__main__":
    main()

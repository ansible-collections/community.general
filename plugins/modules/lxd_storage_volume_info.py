# Copyright (c) 2025, Sean McAvoy (@smcavoy) <seanmcavoy@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = """
---
module: lxd_storage_volume_info
short_description: Retrieve information about LXD storage volumes
version_added: 12.1.0
description:
  - Retrieve information about LXD storage volumes in a specific storage pool.
  - This module returns details about all volumes or a specific volume in a pool.
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
  pool:
    description:
      - Name of the storage pool to query for volumes.
      - This parameter is required.
    required: true
    type: str
  name:
    description:
      - Name of a specific storage volume to retrieve information about.
      - If not specified, information about all volumes in the pool are returned.
    type: str
  type:
    description:
      - Filter volumes by type.
      - Common types include V(container), V(virtual-machine), V(image), and V(custom).
      - If not specified, all volume types are returned.
    type: str
  project:
    description:
      - 'Project of the storage volume.
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
- name: Get information about all volumes in the default storage pool
  community.general.lxd_storage_volume_info:
    pool: default
  register: result

- name: Get information about a specific volume
  community.general.lxd_storage_volume_info:
    pool: default
    name: my-volume
  register: result

- name: Get information about all custom volumes in a pool
  community.general.lxd_storage_volume_info:
    pool: default
    type: custom
  register: result

- name: Get volume information via HTTPS connection
  community.general.lxd_storage_volume_info:
    url: https://127.0.0.1:8443
    trust_password: mypassword
    pool: default
    name: my-volume
  register: result

- name: Get volume information for a specific project
  community.general.lxd_storage_volume_info:
    project: myproject
    pool: default
  register: result

- name: Get container volumes only
  community.general.lxd_storage_volume_info:
    pool: default
    type: container
  register: result
"""

RETURN = """
storage_volumes:
  description: List of LXD storage volumes.
  returned: success
  type: list
  elements: dict
  sample: [
    {
      "name": "my-volume",
      "type": "custom",
      "used_by": [],
      "config": {
        "size": "10GiB"
      },
      "description": "My custom volume",
      "content_type": "filesystem",
      "location": "none"
    }
  ]
  contains:
    name:
      description: The name of the storage volume.
      type: str
      returned: success
    type:
      description: The type of the storage volume.
      type: str
      returned: success
    used_by:
      description: List of resources using this storage volume.
      type: list
      elements: str
      returned: success
    config:
      description: Configuration of the storage volume.
      type: dict
      returned: success
    description:
      description: Description of the storage volume.
      type: str
      returned: success
    content_type:
      description: Content type of the volume (filesystem or block).
      type: str
      returned: success
    location:
      description: Cluster member location for the volume.
      type: str
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
        "url": "/1.0/storage-pools/default/volumes",
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
from urllib.parse import quote, urlencode

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


class LXDStorageVolumeInfo:
    def __init__(self, module: AnsibleModule) -> None:
        """Gather information about LXD storage volumes.

        :param module: Processed Ansible Module.
        :type module: AnsibleModule
        """
        self.module = module
        self.pool = self.module.params["pool"]
        self.name = self.module.params["name"]
        self.volume_type = self.module.params["type"]
        self.project = self.module.params["project"]

        self.key_file = self.module.params["client_key"]
        if self.key_file is None:
            self.key_file = default_key_file()
        self.cert_file = self.module.params["client_cert"]
        if self.cert_file is None:
            self.cert_file = default_cert_file()
        self.debug = self.module._verbosity >= 4

        # check if domain socket to be used
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

    def _check_pool_exists(self) -> None:
        """Verify that the storage pool exists."""
        url = self._build_url(f"{LXD_API_STORAGE_POOLS_ENDPOINT}/{quote(self.pool, safe='')}")
        resp_json = self.client.do("GET", url, ok_error_codes=[404])

        if resp_json["type"] == "error":
            if resp_json.get("error_code") == 404:
                self.module.fail_json(msg=f'Storage pool "{self.pool}" not found')
            else:
                self.module.fail_json(
                    msg=f'Failed to retrieve storage pool "{self.pool}": {resp_json.get("error", "Unknown error")}'
                )

    def _get_volume_list(self, recursion: int = 0) -> list:
        """Get list of all volumes in the storage pool.

        :param recursion: API recursion level (0 for URLs only, 1 for full objects)
        :type recursion: int
        :return: List of volume URLs (recursion=0) or volume objects (recursion=1)
        :rtype: list
        """
        endpoint = f"{LXD_API_STORAGE_POOLS_ENDPOINT}/{quote(self.pool, safe='')}/volumes"
        if recursion > 0:
            endpoint = f"{endpoint}?recursion={recursion}"
        url = self._build_url(endpoint)
        resp_json = self.client.do("GET", url, ok_error_codes=[])

        if resp_json["type"] == "error":
            self.module.fail_json(
                msg=f'Failed to retrieve volumes from pool "{self.pool}": {resp_json.get("error", "Unknown error")}',
                error_code=resp_json.get("error_code"),
            )

        # With recursion=0: list of volume URLs like ['/1.0/storage-pools/default/volumes/custom/my-volume']
        # With recursion=1: list of volume objects with full metadata
        return resp_json.get("metadata", [])

    def _get_volume_info(self, volume_type: str, volume_name: str) -> dict:
        """Get detailed information about a specific storage volume."""
        url = self._build_url(
            f"{LXD_API_STORAGE_POOLS_ENDPOINT}/{quote(self.pool, safe='')}/volumes/{quote(volume_type, safe='')}/{quote(volume_name, safe='')}"
        )
        resp_json = self.client.do("GET", url, ok_error_codes=[404])

        if resp_json["type"] == "error":
            if resp_json.get("error_code") == 404:
                self.module.fail_json(
                    msg=f'Storage volume "{volume_name}" of type "{volume_type}" not found in pool "{self.pool}"'
                )
            else:
                self.module.fail_json(
                    msg=f'Failed to retrieve volume "{volume_name}" of type "{volume_type}": {resp_json.get("error", "Unknown error")}'
                )

        return resp_json.get("metadata", {})

    def get_storage_volumes(self) -> list[dict]:
        """Retrieve storage volume information based on module parameters."""
        # First check if the pool exists
        self._check_pool_exists()

        storage_volumes = []

        if self.name:
            # Get information about a specific volume
            # We need to determine the type if not specified
            if self.volume_type:
                volume_info = self._get_volume_info(self.volume_type, self.name)
                storage_volumes.append(volume_info)
            else:
                # Try to find the volume by name using recursion for efficiency
                # This gets all volume objects in a single API call
                volumes = self._get_volume_list(recursion=1)
                found = False
                for volume in volumes:
                    if volume.get("name") == self.name:
                        storage_volumes.append(volume)
                        found = True
                        break

                if not found:
                    self.module.fail_json(msg=f'Storage volume "{self.name}" not found in pool "{self.pool}"')
        else:
            # Get information about all volumes in the pool using recursion
            # This retrieves all volume details in a single API call instead of one call per volume
            volumes = self._get_volume_list(recursion=1)
            for volume in volumes:
                # Apply type filter if specified
                if self.volume_type and volume.get("type") != self.volume_type:
                    continue
                storage_volumes.append(volume)

        return storage_volumes

    def run(self) -> None:
        """Run the main method."""
        try:
            if self.trust_password is not None:
                self.client.authenticate(self.trust_password)

            storage_volumes = self.get_storage_volumes()

            result_json = {"storage_volumes": storage_volumes}
            if self.client.debug:
                result_json["logs"] = self.client.logs
            self.module.exit_json(**result_json)
        except LXDClientException as e:
            self._fail_from_lxd_exception(e)


def main() -> None:
    """Ansible Main module."""
    module = AnsibleModule(
        argument_spec=dict(
            pool=dict(type="str", required=True),
            name=dict(type="str"),
            type=dict(type="str"),
            project=dict(type="str"),
            url=dict(type="str", default=ANSIBLE_LXD_DEFAULT_URL),
            snap_url=dict(type="str", default=ANSIBLE_LXD_DEFAULT_SNAP_URL),
            client_key=dict(type="path", aliases=["key_file"]),
            client_cert=dict(type="path", aliases=["cert_file"]),
            trust_password=dict(type="str", no_log=True),
        ),
        supports_check_mode=True,
    )

    lxd_info = LXDStorageVolumeInfo(module=module)
    lxd_info.run()


if __name__ == "__main__":
    main()

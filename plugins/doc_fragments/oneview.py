#
# Copyright (c) 2016-2017, Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


class ModuleDocFragment:
    # OneView doc fragment
    DOCUMENTATION = r"""
options:
  config:
    description:
      - Path to a JSON configuration file containing the OneView client configuration. The configuration file is optional
        and when used should be present in the host running the ansible commands. If the file path is not provided, the configuration
        is loaded from environment variables. For links to example configuration files or how to use the environment variables
        verify the notes section.
    type: path
  api_version:
    description:
      - OneView API Version.
    type: int
  image_streamer_hostname:
    description:
      - IP address or hostname for the HPE Image Streamer REST API.
    type: str
  hostname:
    description:
      - IP address or hostname for the appliance.
    type: str
  username:
    description:
      - Username for API authentication.
    type: str
  password:
    description:
      - Password for API authentication.
    type: str

requirements:
  - Python >= 2.7.9

notes:
  - 'A sample configuration file for the config parameter can be found at:
    U(https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/oneview_config-rename.json).'
  - 'Check how to use environment variables for configuration at: U(https://github.com/HewlettPackard/oneview-ansible#environment-variables).'
  - 'Additional Playbooks for the HPE OneView Ansible modules can be found at: U(https://github.com/HewlettPackard/oneview-ansible/tree/master/examples).'
  - 'The OneView API version used directly affects returned and expected fields in resources. Information on setting the desired
    API version and can be found at: U(https://github.com/HewlettPackard/oneview-ansible#setting-your-oneview-version).'
"""

    VALIDATEETAG = r"""
options:
  validate_etag:
    description:
      - When the ETag Validation is enabled, the request is conditionally processed only if the current ETag for the resource
        matches the ETag provided in the data.
    type: bool
    default: true
"""

    FACTSPARAMS = r"""
options:
  params:
    description:
      - List of parameters to delimit, filter and sort the list of resources.
      - 'Parameter keys allowed are:'
      - 'V(start): The first item to return, using 0-based indexing.'
      - 'V(count): The number of resources to return.'
      - 'V(filter): A general filter/query string to narrow the list of items returned.'
      - 'V(sort): The sort order of the returned data set.'
    type: dict
"""

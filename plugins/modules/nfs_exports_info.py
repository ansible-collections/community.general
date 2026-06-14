#!/usr/bin/python

# SPDX-FileCopyrightText: (c) 2025, Samaneh Yousefnezhad <s-yousefenzhad@um.ac.ir>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import hashlib
import os
import re

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = r"""
---
module: nfs_exports_info

short_description: Extract folders, IPs, and options from C(/etc/exports)

description:
  - This module retrieves and processes the contents of the C(/etc/exports) file from a remote server,
    mapping folders to their corresponding IP addresses and access options.

author:
  - Samaneh Yousefnezhad (@yousefenzhad)
version_added: "12.2.0"

extends_documentation_fragment:
  - community.general._attributes
  - community.general._attributes.info_module

options:
  output_format:
    description:
      - The format of the returned mapping.
      - If set to C(ips_per_share), output maps shared folders to IPs and options.
      - If set to C(shares_per_ip), output maps IPs to shared folders and options.
    required: true
    type: str
    choices: ['ips_per_share', 'shares_per_ip']
  file_path:
    description:
      - The path to the NFS exports configurations file.
    type: path
    default: /etc/exports
"""

EXAMPLES = r"""
- name: Get IPs and options per shared folder
  community.general.nfs_exports_info:
    output_format: 'ips_per_share'
  register: result

- name: Get shared folders and options per IP
  community.general.nfs_exports_info:
    output_format: 'shares_per_ip'
  register: result
"""

RETURN = r"""
exports_info:
  description:
    - A mapping of shared folders to IPs and their options, or the reverse.
    - What it is depends on O(output_format).
  type: dict
  returned: always
file_digest:
  description:
    - A dictionary containing various hash values of the C(/etc/exports) file for integrity verification.
    - Keys are the hash algorithm names (for example C(sha256), C(sha1), C(md5)), and values are their corresponding hexadecimal digests.
    - At least one hash value is guaranteed to be present if the file exists and is readable.
  type: dict
  returned: always
"""


def get_exports(module: AnsibleModule) -> tuple[dict, dict]:
    output_format = module.params["output_format"]
    file_path = module.params["file_path"]

    shares_per_ip = {}
    ips_per_share = {}
    file_digest = {}

    try:
        if not os.path.exists(file_path):
            module.fail_json(msg=f"{file_path} file not found")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        for algo in ["md5", "sha1", "sha256"]:
            try:
                hasher = hashlib.new(algo)
                hasher.update(content.encode("utf-8"))
                file_digest[algo] = hasher.hexdigest()
            except ValueError:
                continue

        # پردازش خطوط فایل exports
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = re.split(r"\s+", line)
            if len(parts) < 2:
                continue

            folder = parts[0]
            for client_part in parts[1:]:
                match = re.match(r"^([^\(]+)\(([^\)]+)\)$", client_part)
                if match:
                    ip = match.group(1)
                    options = [opt.strip() for opt in match.group(2).split(",")]
                else:
                    ip = client_part
                    options = []

                if ip not in shares_per_ip:
                    shares_per_ip[ip] = []
                shares_per_ip[ip].append({"folder": folder, "options": options})

                if folder not in ips_per_share:
                    ips_per_share[folder] = []
                ips_per_share[folder].append({"ip": ip, "options": options})

    except Exception as e:
        module.fail_json(msg=f"Failed to process {file_path}: {str(e)}")

    if output_format == "ips_per_share":
        return ips_per_share, file_digest
    return shares_per_ip, file_digest


def main() -> None:
    module_args = {
        "output_format": {"type": "str", "required": True, "choices": ["ips_per_share", "shares_per_ip"]},
        "file_path": {"type": "path", "default": "/etc/exports"}
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    exports_info, file_digest = get_exports(module)

    module.exit_json(
        changed=False,
        exports_info=exports_info,
        file_digest=file_digest
    )


if __name__ == "__main__":
    main()

#!/usr/bin/python

# SPDX-FileCopyrightText: (c) 2025, Samaneh Yousefnezhad <s-yousefenzhad@um.ac.ir>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: nfs_exports_info

short_description: Extract folders, IPs, and options from C(/etc/exports)

description:
  - This module retrieves and processes the contents of the /etc/exports file from a remote server,
    mapping folders to their corresponding IP addresses and access options.

author:
  - Samaneh Yousefnezhad (@yousefenzhad)
version_added: "11.1.0"

options:
  output_format:
    description:
      - The format of the returned mapping.
      - If set to C(ips_per_share), output maps shared folders to IPs and options.
      - If set to C(shares_per_ip), output maps IPs to shared folders and options.
    required: true
    type: str
    choices: ['ips_per_share', 'shares_per_ip']
"""

EXAMPLES = r"""
- name: Get IPs and options per shared folder
  community.general.nfs_exports_info:
    output_format: 'ips_per_share'
  register: result

- name: Get shared folders and options per IP
  community.general.nfs_exports_info:
    output_format: 'shares_per_ip'
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
    - A dictionary containing various hash values of the /etc/exports file for integrity verification.
    - Keys are the hash algorithm names (e.g., 'sha256', 'sha1', 'md5'), and values are their corresponding hexadecimal digests.
    - At least one hash value is guaranteed to be present if the file exists and is readable.
  type: dict
  returned: always
  sample:
    sha256: "a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
    sha1: "f7e8d9c0b1a23c4d5e6f7a8b9c0d1e2f3a4b5c6d"
    md5: "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d"
"""

from ansible.module_utils.basic import AnsibleModule
import re
import hashlib


def get_exports(module, output_format, file_path="/etc/exports"):
    IP_ENTRY_PATTERN = re.compile(r'(\d+\.\d+\.\d+\.\d+)\(([^)]+)\)')
    MAIN_LINE_PATTERN = re.compile(r'\s*(\S+)\s+(.+)')

    file_digests = {}
    hash_algorithms = ['sha256', 'sha1', 'md5']

    try:

        if not module.file_exists(file_path):
            module.fail_json(msg="{} file not found".format(file_path))

        file_content_bytes = None
        try:
            with open(file_path, 'rb') as f:
                file_content_bytes = f.read()
        except IOError:
            module.fail_json(msg="Could not read {}".format(file_path))

        if file_content_bytes:
            for algo in hash_algorithms:
                try:
                    hasher = hashlib.new(algo)
                    hasher.update(file_content_bytes)
                    file_digests[algo] = hasher.hexdigest()
                except ValueError:
                    module.warn("Hash algorithm '{}' not available on this system. Skipping.".format(algo))
                except Exception as ex:
                    module.warn("Error calculating '{}' hash: {}".format(algo, ex))
        exports = {}

        output_lines = []
        if file_content_bytes:
            output_lines = file_content_bytes.decode('utf-8', errors='ignore').splitlines()
        for line in output_lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            match = MAIN_LINE_PATTERN.match(line)
            if not match:
                continue

            folder = match.group(1)
            rest = match.group(2)

            entries = IP_ENTRY_PATTERN.findall(rest)
            for ip, options_str in entries:
                options = options_str.split(',')

                if output_format == "ips_per_share":
                    entry = {"ip": ip, "options": options}
                    if folder not in exports:
                        exports[folder] = []
                    exports[folder].append(entry)

                elif output_format == "shares_per_ip":
                    entry = {"folder": folder, "options": options}
                    if ip not in exports:
                        exports[ip] = []
                    exports[ip].append(entry)

        return {
            'exports_info': exports,
            'file_digest': file_digests
        }

    except Exception as e:
        module.fail_json(msg="Error while processing exports: {}".format(e))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            output_format=dict(type='str', required=True, choices=['ips_per_share', 'shares_per_ip'])
        ),
        supports_check_mode=True
    )

    output_format = module.params['output_format']
    result = get_exports(module, output_format)

    module.exit_json(
        changed=False,
        exports_info=result['exports_info'],
        file_digest=result['file_digest']
    )


if __name__ == '__main__':
    main()

__all__ = ['get_exports']

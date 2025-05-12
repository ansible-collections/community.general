# Copyright: (c) 2025, Samaneh Yousefnezhad <s-yousefenzhad@um.ac.ir>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: nfs_exports_info

short_description: Extract folders, IPs, and options from /etc/exports

description: >
  This module retrieves and processes the contents of the /etc/exports file from a remote server,
  mapping folders to their corresponding IP addresses and access options.

author:
  - Samaneh Yousefnezhad (@yousefenzhad)

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
  fava.infra.nfs_exports_info:
    output_format: 'ips_per_share'

- name: Get shared folders and options per IP
  fava.infra.nfs_exports_info:
    output_format: 'shares_per_ip'
"""

RETURN = r"""
exports_info:
  description: A mapping of shared folders to IPs and their options, or the reverse.
  type: dict
  returned: always

file_digest:
  description: SHA1 hash of /etc/exports file for integrity verification.
  type: str
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
import re


def get_exports(module, output_format, file_path="/etc/exports"):
    try:
        exports_file_digest = module.digest_from_file(file_path, 'sha1')
        if exports_file_digest is None:
            module.fail_json(msg=f"{file_path} file not found")

        with open(file_path, 'r') as f:
            output_lines = f.readlines()

        exports = {}
        pattern = r'\s*(\S+)\s+(.+)'

        for line in output_lines:
            if line.strip() and not line.strip().startswith('#'):
                match = re.match(pattern, line)
                if not match:
                    continue

                folder = match.group(1)
                rest = match.group(2)

                entries = re.findall(r'(\d+\.\d+\.\d+\.\d+)\(([^)]+)\)', rest)
                for ip, options_str in entries:
                    options = options_str.split(',')

                    if output_format == "ips_per_share":
                        entry = {"ip": ip, "options": options}
                        exports.setdefault(folder, []).append(entry)

                    elif output_format == "shares_per_ip":
                        entry = {"folder": folder, "options": options}
                        exports.setdefault(ip, []).append(entry)

        return {
            'exports_info': exports,
            'file_digest': exports_file_digest
        }

    except FileNotFoundError:
        module.fail_json(msg=f"{file_path} file not found")
    except Exception as e:
        module.fail_json(msg=str(e))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            output_format=dict(type='str', required=True, choices=['ips_per_share', 'shares_per_ip'])
        ),
        supports_check_mode=True
    )

    output_format = module.params['output_format']
    exports_info = get_exports(module, output_format)

    module.exit_json(
        changed=False,
        exports_info=exports_info['exports_info'],
        file_digest=exports_info['file_digest']
    )


if __name__ == '__main__':
    main()

__all__ = ['get_exports']

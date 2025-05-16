#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Tobias Zeuch <tobias.zeuch@sap.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: zypper_repository_info
author: "Tobias Zeuch (@TobiasZeuch181)"
version_added: 10.0.0
short_description: List Zypper repositories
description:
    - List Zypper repositories on SUSE and openSUSE.
extends_documentation_fragment:
    - community.general.attributes
    - community.general.attributes.info_module

requirements:
    - "zypper >= 1.0  (included in openSUSE >= 11.1 or SUSE Linux Enterprise Server/Desktop >= 11.0)"
    - python-xml
notes:
    - "For info about packages, use the module M(ansible.builtin.package_facts)."
'''

EXAMPLES = '''
- name: List registered repositories and store in variable repositories
  community.general.zypper_repository_info: {}
  register: repodatalist
'''

RETURN = '''
repodatalist:
    description:
        - A list of repository descriptions like it is returned by the command C(zypper repos).
    type: list
    returned: always
    elements: dict
    contains:
        alias:
            description: The alias of the repository.
            type: str
        autorefresh:
            description: Indicates, if autorefresh is enabled on the repository.
            type: int
        enabled:
            description: indicates, if the repository is enabled
            type: int
        gpgcheck:
            description: indicates, if the GPG signature of the repository meta data is checked
            type: int
        name:
            description: the name of the repository
            type: str
        priority:
            description: the priority of the repository
            type: int
        url:
            description: The URL of the repository on the internet.
            type: str
    sample: [
                {
                    "alias": "SLE-Product-SLES",
                    "autorefresh": "1",
                    "enabled": "1",
                    "gpgcheck": "1",
                    "name": "SLE-Product-SLES",
                    "priority": "99",
                    "url": "http://repo:50000/repo/SUSE/Products/SLE-Product-SLES/15-SP2/x86_64/product"
                }
            ]
'''


from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare("parseXML"):
    from xml.dom.minidom import parseString as parseXML

from ansible.module_utils.basic import AnsibleModule

REPO_OPTS = ['alias', 'name', 'priority', 'enabled', 'autorefresh', 'gpgcheck']


def _get_cmd(module, *args):
    """Combines the non-interactive zypper command with arguments/subcommands"""
    cmd = [module.get_bin_path('zypper', required=True), '--quiet', '--non-interactive']
    cmd.extend(args)

    return cmd


def _parse_repos(module):
    """parses the output of zypper --xmlout repos and return a parse repo dictionary"""
    cmd = _get_cmd(module, '--xmlout', 'repos')

    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    if rc == 0:
        repos = []
        dom = parseXML(stdout)
        repo_list = dom.getElementsByTagName('repo')
        for repo in repo_list:
            opts = {}
            for o in REPO_OPTS:
                opts[o] = repo.getAttribute(o)
            opts['url'] = repo.getElementsByTagName('url')[0].firstChild.data
            # A repo can be uniquely identified by an alias + url
            repos.append(opts)
        return repos
    # exit code 6 is ZYPPER_EXIT_NO_REPOS (no repositories defined)
    elif rc == 6:
        return []
    else:
        module.fail_json(msg='Failed to execute "%s"' % " ".join(cmd), rc=rc, stdout=stdout, stderr=stderr)


def main():
    module = AnsibleModule(
        argument_spec=dict(
        ),
        supports_check_mode=True
    )

    deps.validate(parseXML)

    repodatalist = _parse_repos(module)
    module.exit_json(changed=False, repodatalist=repodatalist)


if __name__ == '__main__':
    main()

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
author: "Tobias Zeuch"
short_description: List Zypper repositories
description:
    - List Zypper repositories on SUSE and openSUSE.
    - Note: for info about packages, use the packages ansible.builtin.package_facts
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none

requirements:
    - "zypper >= 1.0  # included in openSUSE >= 11.1 or SUSE Linux Enterprise Server/Desktop >= 11.0"
    - python-xml
'''

EXAMPLES = '''
- name: List registered repositories and store in fact repositories
  community.general.zypper_repository_info:
  register: repositories

'''

import traceback

XML_IMP_ERR = None
try:
    from xml.dom.minidom import parseString as parseXML
    HAS_XML = True
except ImportError:
    XML_IMP_ERR = traceback.format_exc()
    HAS_XML = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib

from ansible_collections.community.general.plugins.module_utils.version import LooseVersion

REPO_OPTS = ['alias', 'name', 'priority', 'enabled', 'autorefresh', 'gpgcheck']


def _get_cmd(module, *args):
    """Combines the non-interactive zypper command with arguments/subcommands"""
    cmd = [module.get_bin_path('zypper', required=True), '--quiet', '--non-interactive']
    cmd.extend(args)

    return cmd


def _parse_repos(module):
    """parses the output of zypper --xmlout repos and return a parse repo dictionary"""
    cmd = _get_cmd(module, '--xmlout', 'repos')

    if not HAS_XML:
        module.fail_json(msg=missing_required_lib("python-xml"), exception=XML_IMP_ERR)
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


def get_zypper_version(module):
    rc, stdout, stderr = module.run_command([module.get_bin_path('zypper', required=True), '--version'])
    if rc != 0 or not stdout.startswith('zypper '):
        return LooseVersion('1.0')
    return LooseVersion(stdout.split()[1])


def main():
    module = AnsibleModule(
        argument_spec=dict(
        ),
        supports_check_mode=False,
    )

    zypper_version = get_zypper_version(module)
    warnings = []  # collect warning messages for final output

    repodatalist = _parse_repos(module)
    module.exit_json(changed=False, repodatalist=repodatalist)


if __name__ == '__main__':
    main()

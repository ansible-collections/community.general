#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
module: python_requirements_info
short_description: Show python path and assert dependency versions
description:
  - Get info about available Python requirements on the target host, including listing required libraries and gathering versions.
  - This module was called C(python_requirements_facts) before Ansible 2.9. The usage did not change.
options:
  dependencies:
    type: list
    elements: str
    description: >
      A list of version-likes or module names to check for installation.
      Supported operators: <, >, <=, >=, or ==. The bare module name like
      I(ansible), the module with a specific version like I(boto3==1.6.1), or a
      partial version like I(requests>2) are all valid specifications.
    default: []
author:
  - Will Thames (@willthames)
  - Ryan Scott Brown (@ryansb)
'''

EXAMPLES = '''
- name: Show python lib/site paths
  community.general.python_requirements_info:

- name: Check for modern boto3 and botocore versions
  community.general.python_requirements_info:
    dependencies:
      - boto3>1.6
      - botocore<2
'''

RETURN = '''
python:
  description: path to python version used
  returned: always
  type: str
  sample: /usr/local/opt/python@2/bin/python2.7
python_version:
  description: version of python
  returned: always
  type: str
  sample: "2.7.15 (default, May  1 2018, 16:44:08)\n[GCC 4.2.1 Compatible Apple LLVM 9.1.0 (clang-902.0.39.1)]"
python_version_info:
  description: breakdown version of python
  returned: always
  type: dict
  contains:
    major:
      description: The C(major) component of the python interpreter version.
      returned: always
      type: int
      sample: 3
    minor:
      description: The C(minor) component of the python interpreter version.
      returned: always
      type: int
      sample: 8
    micro:
      description: The C(micro) component of the python interpreter version.
      returned: always
      type: int
      sample: 10
    releaselevel:
      description: The C(releaselevel) component of the python interpreter version.
      returned: always
      type: str
      sample: final
    serial:
      description: The C(serial) component of the python interpreter version.
      returned: always
      type: int
      sample: 0
  version_added: 4.2.0
python_system_path:
  description: List of paths python is looking for modules in
  returned: always
  type: list
  sample:
    - /usr/local/opt/python@2/site-packages/
    - /usr/lib/python/site-packages/
valid:
  description: A dictionary of dependencies that matched their desired versions. If no version was specified, then I(desired) will be null
  returned: always
  type: dict
  sample:
    boto3:
      desired: null
      installed: 1.7.60
    botocore:
      desired: botocore<2
      installed: 1.10.60
mismatched:
  description: A dictionary of dependencies that did not satisfy the desired version
  returned: always
  type: dict
  sample:
    botocore:
      desired: botocore>2
      installed: 1.10.60
not_found:
  description: A list of packages that could not be imported at all, and are not installed
  returned: always
  type: list
  sample:
    - boto4
    - requests
'''

import re
import sys
import operator

HAS_DISTUTILS = False
try:
    import pkg_resources
    from ansible_collections.community.general.plugins.module_utils.version import LooseVersion
    HAS_DISTUTILS = True
except ImportError:
    pass

from ansible.module_utils.basic import AnsibleModule

operations = {
    '<=': operator.le,
    '>=': operator.ge,
    '<': operator.lt,
    '>': operator.gt,
    '==': operator.eq,
}

python_version_info = dict(
    major=sys.version_info[0],
    minor=sys.version_info[1],
    micro=sys.version_info[2],
    releaselevel=sys.version_info[3],
    serial=sys.version_info[4],
)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            dependencies=dict(type='list', elements='str', default=[])
        ),
        supports_check_mode=True,
    )
    if not HAS_DISTUTILS:
        module.fail_json(
            msg='Could not import "distutils" and "pkg_resources" libraries to introspect python environment.',
            python=sys.executable,
            python_version=sys.version,
            python_version_info=python_version_info,
            python_system_path=sys.path,
        )
    pkg_dep_re = re.compile(r'(^[a-zA-Z][a-zA-Z0-9_-]+)(?:(==|[><]=?)([0-9.]+))?$')

    results = dict(
        not_found=[],
        mismatched={},
        valid={},
    )

    for dep in module.params['dependencies']:
        match = pkg_dep_re.match(dep)
        if not match:
            module.fail_json(msg="Failed to parse version requirement '{0}'. Must be formatted like 'ansible>2.6'".format(dep))
        pkg, op, version = match.groups()
        if op is not None and op not in operations:
            module.fail_json(msg="Failed to parse version requirement '{0}'. Operator must be one of >, <, <=, >=, or ==".format(dep))
        try:
            existing = pkg_resources.get_distribution(pkg).version
        except pkg_resources.DistributionNotFound:
            # not there
            results['not_found'].append(pkg)
            continue
        if op is None and version is None:
            results['valid'][pkg] = {
                'installed': existing,
                'desired': None,
            }
        elif operations[op](LooseVersion(existing), LooseVersion(version)):
            results['valid'][pkg] = {
                'installed': existing,
                'desired': dep,
            }
        else:
            results['mismatched'][pkg] = {
                'installed': existing,
                'desired': dep,
            }

    module.exit_json(
        python=sys.executable,
        python_version=sys.version,
        python_version_info=python_version_info,
        python_system_path=sys.path,
        **results
    )


if __name__ == '__main__':
    main()

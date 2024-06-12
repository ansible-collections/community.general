#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: django_check
author:
  - Alexei Znamensky (@russoz)
short_description: Wrapper for C(django-admin check)
version_added: 9.1.0
description:
  - This module is a wrapper for the execution of C(django-admin check).
extends_documentation_fragment:
  - community.general.attributes
  - community.general.django
options:
  database:
    description:
      - Specify databases to run checks against.
      - If not specified, Django will not run database tests.
    type: list
    elements: str
  deploy:
    description:
      - Include additional checks relevant in a deployment setting.
    type: bool
    default: false
  fail_level:
    description:
      - Message level that will trigger failure.
      - Default is the Django default value. Check the documentation for the version being used.
    type: str
    choices: [CRITICAL, ERROR, WARNING, INFO, DEBUG]
  tags:
    description:
      - Restrict checks to specific tags.
    type: list
    elements: str
  apps:
    description:
      - Restrict checks to specific applications.
      - Default is to check all applications.
    type: list
    elements: str
notes:
  - The outcome of the module is found in the common return values RV(ignore:stdout), RV(ignore:stderr), RV(ignore:rc).
  - The module will fail if RV(ignore:rc) is not zero.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
"""

EXAMPLES = """
- name: Check the entire project
  community.general.django_check:
    settings: myproject.settings

- name: Create the project using specific databases
  community.general.django_check:
    database:
      - somedb
      - myotherdb
    settings: fancysite.settings
    pythonpath: /home/joedoe/project/fancysite
    venv: /home/joedoe/project/fancysite/venv
"""

RETURN = """
run_info:
  description: Command-line execution information.
  type: dict
  returned: success and C(verbosity) >= 3
"""

from ansible_collections.community.general.plugins.module_utils.django import DjangoModuleHelper
from ansible_collections.community.general.plugins.module_utils.cmd_runner import cmd_runner_fmt


class DjangoCheck(DjangoModuleHelper):
    module = dict(
        argument_spec=dict(
            database=dict(type="list", elements="str"),
            deploy=dict(type="bool", default=False),
            fail_level=dict(type="str", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]),
            tags=dict(type="list", elements="str"),
            apps=dict(type="list", elements="str"),
        ),
        supports_check_mode=True,
    )
    arg_formats = dict(
        database=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("--database"),
        deploy=cmd_runner_fmt.as_bool("--deploy"),
        fail_level=cmd_runner_fmt.as_opt_val("--fail-level"),
        tags=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("--tag"),
        apps=cmd_runner_fmt.as_list(),
    )
    django_admin_cmd = "check"
    django_admin_arg_order = "database deploy fail_level tags apps"


def main():
    DjangoCheck.execute()


if __name__ == '__main__':
    main()

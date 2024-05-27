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
  - community.general.django.database
options:
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
  tags:
    description:
      - Restrict checks to specific tags.
    type: str
  apps:
    description:
      - Restrict checks to specific applications.
      - Default is to check all applications.
    type: str
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
"""

EXAMPLES = """    **************************************
- name: Create cache table in the default database
  community.general.check:
    settings: myproject.settings

- name: Create cache table in the other database
  community.general.check:
    database: myotherdb
    settings: fancysite.settings
    pythonpath: /home/joedoe/project/fancysite
    venv: /home/joedoe/project/fancysite/venv
"""

RETURN = """
run_info:
  description: Command-line execution information.
  type: dict
  returned: success and O(verbosity) >= 3
"""

from itertools import zip_longest

from ansible_collections.community.general.plugins.module_utils.django import DjangoModuleHelper
from ansible_collections.community.general.plugins.module_utils.cmd_runner import cmd_runner_fmt


def stack_format(param):
    def tags_format(tags):
        zippit = zip_longest([], tags, fillvalue=param)
        return [item for pair in zippit for item in pair]
    return tags_format


class DjangoCheck(DjangoModuleHelper):
    module = dict(
        arguments_spec=dict(
            deploy=dict(type="bool", default=False),
            fail_level=dict(type="str", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]),
            tags=dict(type="list", elements="str"),
            apps=dict(type="list", elements="str"),
        ),
        supports_check_mode=True,
    )
    arg_formats = dict(
        deploy=cmd_runner_fmt.as_bool("--deploy"),
        fail_level=cmd_runner_fmt.as_opt_val("--fail-level"),
        tags=cmd_runner_fmt.as_func(stack_format("--tag")),
        tags=cmd_runner_fmt.as_func(stack_format("--database")),
        apps=cmd_runner_fmt.as_list(),
    )
    django_admin_cmd = "check"
    django_admin_arg_order = "database deploy fail_level tags apps"
    _django_args = ["database"]


def main():
    DjangoCheck.execute()


if __name__ == '__main__':
    main()

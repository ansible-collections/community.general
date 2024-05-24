#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: django_createcachetable
author:
  - Alexei Znamensky (@russoz)
short_description: Wrapper for C(django-admin createcachetable)
version_added: 9.0.0
description:
  - This module is a wrapper for the execution of C(django-admin createcachetable).
extends_documentation_fragment:
  - community.general.attributes
  - community.general.django
  - community.general.django.database
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
"""

EXAMPLES = """
- name: Check the project
  community.general.django_command:
    command: check
    settings: myproject.settings

- name: Check the project in specified python path, using virtual environment
  community.general.django_command:
    command: check
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

from ansible_collections.community.general.plugins.module_utils.django import DjangoModuleHelper
from ansible_collections.community.general.plugins.module_utils.cmd_runner import cmd_runner_fmt


class DjangoCreateCacheTable(DjangoModuleHelper):
    module = dict(
        supports_check_mode=True,
    )
    arg_formats = dict(
        extra_args=cmd_runner_fmt.as_list(),
    )
    django_admin_cmd = "createcachetable"
    django_admin_arg_order = "noinput database dry_run"
    _django_args = ["noinput", "database", "dry_run"]
    _check_mode_arg = "dry_run"


def main():
    DjangoCreateCacheTable.execute()


if __name__ == '__main__':
    main()

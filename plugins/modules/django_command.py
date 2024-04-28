#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
module: django_command
author:
  - Alexei Znamensky (@russoz)
short_description: Run Django admin commands
description:
  - This module allows the execution of arbitrary Django admin commands.
extends_documentation_fragment:
  - community.general.django
options:
  command:
    description:
      - Django admin command. It must be a valid command accepted by C(python -m django) at the target system.
    type: str
    required: true
  extra_args:
    type: list
    elements: str
    description:
      - List of extra arguments passed to the django admin command.
"""

EXAMPLES = """
"""

RETURN = """
"""

from ansible_collections.community.general.plugins.module_utils.django import DjangoBase
from ansible_collections.community.general.plugins.module_utils.cmd_runner import cmd_runner_fmt


class DjangoCommand(DjangoBase):
    module = dict(
        argument_spec=dict(
            command=dict(type="str", required=True),
            extra_args=dict(type="list", elements="str"),
        ),
        supports_check_mode=False,
    )
    arg_formats = dict(
        extra_args=cmd_runner_fmt.as_list(),
    )
    django_admin_arg_order = "extra_args"


def main():
    DjangoCommand.execute()


if __name__ == '__main__':
    main()

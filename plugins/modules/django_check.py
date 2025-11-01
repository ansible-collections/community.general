#!/usr/bin/python
# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
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
  databases:
    description:
      - Specify databases to run checks against.
      - If not specified, Django does not run database tests.
      - The parameter has been renamed to O(databases) in community.general 11.3.0. The old name is still available as an alias.
    type: list
    elements: str
    aliases: ["database"]
  deploy:
    description:
      - Include additional checks relevant in a deployment setting.
    type: bool
    default: false
  fail_level:
    description:
      - Message level that triggers failure.
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
  - The module fails if RV(ignore:rc) is not zero.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
"""

EXAMPLES = r"""
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

RETURN = r"""
run_info:
  description: Command-line execution information.
  type: dict
  returned: success and C(verbosity) >= 3
version:
  description: Version of Django.
  type: str
  returned: always
  sample: 5.1.2
  version_added: 10.0.0
"""

from ansible_collections.community.general.plugins.module_utils.django import DjangoModuleHelper


class DjangoCheck(DjangoModuleHelper):
    module = dict(
        argument_spec=dict(
            databases=dict(type="list", elements="str", aliases=["database"]),
            deploy=dict(type="bool", default=False),
            fail_level=dict(type="str", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]),
            tags=dict(type="list", elements="str"),
            apps=dict(type="list", elements="str"),
        ),
        supports_check_mode=True,
    )
    django_admin_cmd = "check"
    django_admin_arg_order = "database_stacked_dash deploy fail_level tags apps"

    def __init_module__(self):
        self.vars.set("database_stacked_dash", self.vars.databases, output=False)


def main():
    DjangoCheck.execute()


if __name__ == "__main__":
    main()

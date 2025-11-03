#!/usr/bin/python
# Copyright (c) 2025, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: django_loaddata
author:
  - Alexei Znamensky (@russoz)
short_description: Wrapper for C(django-admin loaddata)
version_added: 11.3.0
description:
  - This module is a wrapper for the execution of C(django-admin loaddata).
extends_documentation_fragment:
  - community.general.attributes
  - community.general.django
  - community.general.django.database
  - community.general.django.data
attributes:
  check_mode:
    support: none
  diff_mode:
    support: none
options:
  app:
    description: Specifies a single app to look for fixtures in rather than looking in all apps.
    type: str
  ignore_non_existent:
    description: Ignores fields and models that may have been removed since the fixture was originally generated.
    type: bool
  fixtures:
    description:
      - List of paths to the fixture files.
    type: list
    elements: path
"""

EXAMPLES = r"""
- name: Dump all data
  community.general.django_dumpdata:
    settings: myproject.settings

- name: Create cache table in the other database
  community.general.django_createcachetable:
    database: myotherdb
    settings: fancysite.settings
    pythonpath: /home/joedoe/project/fancysite
    venv: /home/joedoe/project/fancysite/venv
"""

RETURN = r"""
run_info:
  description: Command-line execution information.
  type: dict
  returned: success and O(verbosity) >= 3
version:
  description: Version of Django.
  type: str
  returned: always
  sample: 5.1.2
"""

from ansible_collections.community.general.plugins.module_utils.django import DjangoModuleHelper


class DjangoLoadData(DjangoModuleHelper):
    module = dict(
        argument_spec=dict(
            app=dict(type="str"),
            ignore_non_existent=dict(type="bool"),
            fixtures=dict(type="list", elements="path"),
        ),
        supports_check_mode=False,
    )
    django_admin_cmd = "loaddata"
    django_admin_arg_order = "database_dash ignore_non_existent app format excludes fixtures"
    _django_args = ["data", "database_dash"]

    def __init_module__(self):
        self.vars.set("database_dash", self.vars.database, output=False)


def main():
    DjangoLoadData.execute()


if __name__ == "__main__":
    main()

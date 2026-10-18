#!/usr/bin/python
# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: django_makemigrations
author:
  - Alexei Znamensky (@russoz)
short_description: Wrapper for C(django-admin makemigrations)
version_added: 14.0.0
description:
  - This module is a wrapper for the execution of C(django-admin makemigrations).
  - It creates new migration files in the source code of the applications, based on the changes detected in their models.
extends_documentation_fragment:
  - community.general._attributes
  - community.general._django
  - community.general._django.skip_checks
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  apps:
    description:
      - Applications for which to create migrations.
      - If not specified, migrations are created for all applications.
    type: list
    elements: str
  empty:
    description:
      - Create an empty migration for each one of the applications in O(apps).
      - When V(true), the module is not idempotent, because a new migration is created in every run.
    type: bool
  name:
    description:
      - Name of the migration files.
      - It must be a valid Python identifier.
    type: str
  no_header:
    description:
      - Do not add the header comments to the migration files.
    type: bool
  update:
    description:
      - Merge the model changes into the latest migration of each application, instead of creating a new one.
      - This option requires Django 4.2 or newer.
    type: bool
  verbosity:
    description:
      - Specifies the amount of notification and debug information in the output of C(django-admin).
      - The value V(0) is not supported, because the module relies on the output of C(django-admin) to determine
        which migration files are created.
    choices: [1, 2, 3]
requirements:
  - django >= 4.1
notes:
  - Renamed model fields are not detected as renames. They are treated as a field being removed and another one being added,
    so the data in that field is lost when the migration is applied.
  - Adding a non-nullable field without a default value to a model makes the module fail.
"""

EXAMPLES = r"""
- name: Create migrations for all applications
  community.general.django_makemigrations:
    settings: myproject.settings

- name: Create a named migration for some applications
  community.general.django_makemigrations:
    settings: fancysite.settings
    pythonpath: /home/joedoe/project/fancysite
    venv: /home/joedoe/project/fancysite/venv
    apps:
      - blog
      - shop
    name: add_discount_fields

- name: Fail if any model change is missing a migration
  community.general.django_makemigrations:
    settings: myproject.settings
  check_mode: true
  register: missing_migrations
  failed_when: missing_migrations is changed
"""

RETURN = r"""
migrations:
  description:
    - Paths of the migration files created, or that would be created in check mode.
    - Paths are relative to the current working directory when the files are located below it, and absolute otherwise.
  type: list
  elements: str
  returned: success
  sample:
    - /home/joedoe/project/fancysite/blog/migrations/0002_add_discount_fields.py
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

from ansible_collections.community.general.plugins.module_utils._django import DjangoModuleHelper


class DjangoMakeMigrations(DjangoModuleHelper):
    module = dict(
        argument_spec=dict(
            apps=dict(type="list", elements="str"),
            empty=dict(type="bool"),
            name=dict(type="str"),
            no_header=dict(type="bool"),
            update=dict(type="bool"),
            verbosity=dict(type="int", choices=[1, 2, 3]),
        ),
        mutually_exclusive=[("empty", "update")],
        supports_check_mode=True,
    )
    django_admin_cmd = "makemigrations"
    django_admin_arg_order = "skip_checks noinput scriptable dry_run empty update no_header name apps"
    _django_args = ["skip_checks"]
    _check_mode_arg = "dry_run"

    def __quit_module__(self):
        self.vars.migrations = self.vars.stdout.splitlines()
        self.changed = bool(self.vars.migrations)


def main():
    DjangoMakeMigrations.execute()


if __name__ == "__main__":
    main()

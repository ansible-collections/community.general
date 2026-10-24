#!/usr/bin/python
# Copyright (c) 2026, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: django_flush
author:
  - Alexei Znamensky (@russoz)
short_description: Wrapper for C(django-admin flush)
version_added: 14.0.0
description:
  - This module is a wrapper for the execution of C(django-admin flush).
  - It removes B(all data) from the database, including data added during migrations.
extends_documentation_fragment:
  - community.general._attributes
  - community.general._django
  - community.general._django.skip_checks
  - community.general._django.database
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
notes:
  - The option C(--noinput) is always passed, so C(django-admin) does not prompt for confirmation.
  - The module always reports a change, because it cannot tell whether the database had any data to remove.
    Even right after a flush, some applications (for example C(django.contrib.auth) and C(django.contrib.contenttypes))
    populate their tables again.
"""

EXAMPLES = r"""
- name: Remove all data from the default database
  community.general.django_flush:
    settings: myproject.settings

- name: Remove all data from another database
  community.general.django_flush:
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

from ansible_collections.community.general.plugins.module_utils._django import DjangoModuleHelper


class DjangoFlush(DjangoModuleHelper):
    module = dict(
        supports_check_mode=True,
    )
    django_admin_cmd = "flush"
    django_admin_arg_order = "skip_checks noinput database_dash"
    _django_args = ["database_dash", "skip_checks"]
    _check_mode_skip = True

    def __init_module__(self):
        self.vars.set("database_dash", self.vars.database, output=False)

    def __quit_module__(self):
        self.changed = True


def main():
    DjangoFlush.execute()


if __name__ == "__main__":
    main()

#!/usr/bin/python
# Copyright (c) 2025, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: django_dumpdata
author:
  - Alexei Znamensky (@russoz)
short_description: Wrapper for C(django-admin dumpdata)
version_added: 11.3.0
description:
  - This module is a wrapper for the execution of C(django-admin dumpdata).
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
  all:
    description: Dump all records, including those which might otherwise be filtered or modified by a custom manager.
    type: bool
  indent:
    description:
      - Indentation size for the output.
      - Default is not to indent, so the output is generated in one single line.
    type: int
  natural_foreign:
    description: Use natural keys when serializing for foreign keys.
    type: bool
  natural_primary:
    description: Omit primary keys when serializing.
    type: bool
  primary_keys:
    description:
      - List of primary keys to include in the dump.
      - Only available when dumping one single model.
    type: list
    elements: str
    aliases: ["pks"]
  fixture:
    description:
      - Path to the output file.
      - The fixture filename may end with V(.bz2), V(.gz), V(.lzma) or V(.xz), in which case the corresponding
        compression format is used.
      - This corresponds to the C(--output) parameter for the C(django-admin dumpdata) command.
    type: path
    aliases: [output]
    required: true
  apps_models:
    description:
      - Dump only the applications and models listed in the dump.
      - Format must be either V(app_label) or V(app_label.ModelName).
      - If not passed, all applications and models are to be dumped.
    type: list
    elements: str
"""

EXAMPLES = r"""
- name: Dump all data
  community.general.django_dumpdata:
    settings: myproject.settings
    fixture: /tmp/mydata.json

- name: Dump data excluding certain apps, into a compressed JSON file
  community.general.django_dumpdata:
    settings: myproject.settings
    database: myotherdb
    excludes:
      - auth
      - contenttypes
    fixture: /tmp/mydata.json.gz
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


class DjangoDumpData(DjangoModuleHelper):
    module = dict(
        argument_spec=dict(
            all=dict(type="bool"),
            indent=dict(type="int"),
            natural_foreign=dict(type="bool"),
            natural_primary=dict(type="bool"),
            primary_keys=dict(type="list", elements="str", aliases=["pks"], no_log=False),
            # the underlying vardict does not allow the name "output"
            fixture=dict(type="path", required=True, aliases=["output"]),
            apps_models=dict(type="list", elements="str"),
        ),
        supports_check_mode=False,
    )
    django_admin_cmd = "dumpdata"
    django_admin_arg_order = (
        "all format indent excludes database_dash natural_foreign natural_primary primary_keys fixture apps_models"
    )
    _django_args = ["data", "database_dash"]

    def __init_module__(self):
        self.vars.set("database_dash", self.vars.database, output=False)


def main():
    DjangoDumpData.execute()


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
options:
  venv:
    description:
      - Use the the Python interpreter from this virtual environment.
      - Pass the path to the root of the virtualenv, not the C(bin/) directory nor the C(python) executable.
    type: path
  settings:
    description:
      - Specifies the settings module to use.
      - The value will be passed as is to the C(--settings) argument in C(django-admin).
    type: str
  pythonpath:
    description:
      - Adds the given filesystem path to the Python import search path.
      - The value will be passed as is to the C(--pythonpath) argument in C(django-admin).
    type: path
  traceback:
    description:
      - Provides a full stack trace in the output when a C(CommandError) is raised.
    type: bool
  verbosity:
    description:
      - Specifies the amount of notification and debug information in the output of C(django-admin).
    type: int
    choices: [0, 1, 2, 3]
  skip_checks:
    description:
      - Skips running system checks prior to running the command.
    type: bool


notes:
  - Please refer to U(https://docs.djangoproject.com/en/5.0/ref/django-admin/) for the builtin commands and options of C(django-admin).
'''

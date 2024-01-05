# Author: Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or
# https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2023, Ansible Project

"""
TOML handling.
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

try:
    import tomllib

    HAS_TOMLLIB = True
except ImportError:
    HAS_TOMLLIB = False

try:
    import toml

    HAS_TOML = True
except ImportError:
    HAS_TOML = False

try:
    import tomli

    HAS_TOMLI = True
except ImportError:
    HAS_TOMLI = False


def has_toml_loader_available():
    """
    Return whether a supported TOML loader is available.
    """
    return HAS_TOMLLIB or HAS_TOML or HAS_TOMLI


def load_toml(path):
    """
    Load and parse TOML file ``path``.
    """
    if HAS_TOMLLIB:
        with open(path, "rb") as f:
            return tomllib.load(f)
    if HAS_TOMLI:
        with open(path, "r", encoding="utf-8") as f:
            return tomli.loads(f.read())
    if HAS_TOML:
        with open(path, "r", encoding="utf-8") as f:
            return toml.loads(f.read())
    raise RuntimeError("Need tomllib/tomli/toml library to read TOML file")

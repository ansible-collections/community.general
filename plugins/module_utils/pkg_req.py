# -*- coding: utf-8 -*-
# Copyright (c) 2025, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.six import raise_from

from ansible_collections.community.general.plugins.module_utils import deps


with deps.declare("packaging"):
    from packaging.requirements import Requirement
    from packaging.version import parse as parse_version, InvalidVersion


class PackageRequirement:
    def __init__(self, module, name):
        self.module = module
        self.parsed_name, self.requirement = self._parse_spec(name)

    def _parse_spec(self, name):
        """
        Parse a package name that may include version specifiers using PEP 508.
        Returns a tuple of (name, requirement) where requirement is of type packaging.requirements.Requirement and it may be None.

        Example inputs:
            "package"
            "package>=1.0"
            "package>=1.0,<2.0"
            "package[extra]>=1.0"
            "package[foo,bar]>=1.0,!=1.5"

        :param name: Package name with optional version specifiers and extras
        :return: Tuple of (name, requirement)
        :raises ValueError: If the package specification is invalid
        """
        if not name:
            return name, None

        # Quick check for simple package names
        if not any(c in name for c in '>=<!~[]'):
            return name.strip(), None

        deps.validate(self.module, "packaging")

        try:
            req = Requirement(name)
            return req.name, req

        except Exception as e:
            raise_from(ValueError("Invalid package specification for '{0}': {1}".format(name, e)), e)

    def matches_version(self, version):
        """
        Check if a version string fulfills a version specifier.

        :param version: Version string to check
        :return: True if version fulfills the requirement, False otherwise
        :raises ValueError: If version is invalid
        """
        # If no spec provided, any version is valid
        if not self.requirement:
            return True

        try:
            # Parse version string
            ver = parse_version(version)

            return ver in self.requirement.specifier

        except InvalidVersion as e:
            raise_from(ValueError("Invalid version '{0}': {1}".format(version, e)))

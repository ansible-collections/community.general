# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from ansible_collections.community.general.plugins.module_utils.homebrew import HomebrewValidate


class TestHomebrewModule(unittest.TestCase):
    def setUp(self):
        self.brew_app_names = ["git-ssh", "awscli@1", "bash"]

        self.invalid_names = [
            "git ssh",
            "git*",
        ]

    def test_valid_package_names(self):
        for name in self.brew_app_names:
            self.assertTrue(HomebrewValidate.valid_package(name))

    def test_invalid_package_names(self):
        for name in self.invalid_names:
            self.assertFalse(HomebrewValidate.valid_package(name))

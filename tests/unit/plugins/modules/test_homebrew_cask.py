# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.modules.packaging.os.homebrew_cask import HomebrewCask


class TestHomebrewCaskModule(unittest.TestCase):

    def setUp(self):
        self.brew_cask_names = [
            'visual-studio-code',
            'firefox'
        ]

    def test_valid_cask_names(self):
        for name in self.brew_cask_names:
            self.assertTrue(HomebrewCask.valid_cask(name))

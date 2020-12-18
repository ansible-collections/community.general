# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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

    def test_version_comparison(self):
        mock_brew_version_1 = '2.4.0'
        mock_brew_version_2 = '2.8.0'

        comparison_result_1 = HomebrewCask._compare_version(mock_brew_version_1, mock_brew_version_2)

        mock_brew_version_3 = '2.8.0'
        mock_brew_version_4 = '2.4.0'

        comparison_result_2 = HomebrewCask._compare_version(mock_brew_version_3, mock_brew_version_4)

        mock_brew_version_5 = '2.4.0'
        mock_brew_version_6 = '2.4.0'

        comparison_result_3 = HomebrewCask._compare_version(mock_brew_version_5, mock_brew_version_6)

        self.assertEqual(comparison_result_1, -1)
        self.assertEqual(comparison_result_1, 1)
        self.assertEqual(comparison_result_1, 0)

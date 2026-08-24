# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import unittest
import warnings

from ansible_collections.community.general.plugins.filter.unicode_normalize import unicode_normalize


class TestUnicodeNormalize(unittest.TestCase):
    def test_normalize_no_warnings(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.assertEqual(unicode_normalize("é"), "é")


if __name__ == "__main__":
    unittest.main()

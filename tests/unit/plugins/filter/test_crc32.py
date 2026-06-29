# Copyright (c) 2022, Julien Riou <julien@riou.xyz>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest

from ansible_collections.community.general.plugins.filter.crc32 import crc32s


class TestFilterCrc32(unittest.TestCase):
    def test_checksum(self):
        self.assertEqual(crc32s("test"), "d87f7e0c")

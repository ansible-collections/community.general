# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import unittest
import warnings

from ansible_collections.community.general.plugins.filter.hashids import hashids_encode, hashids_decode


class TestHashids(unittest.TestCase):
    def test_encode_decode_no_warnings(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            hashed = hashids_encode([1, 2, 3], salt="salt")
            self.assertEqual(hashids_decode(hashed, salt="salt"), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()

# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import errno
import unittest

from ansible_collections.community.general.plugins.module_utils._authselect.authselect_enums import (
    AuthselectValidationStatus,
)


class TestAuthselectValidationStatus(unittest.TestCase):
    def test_validation_complete_value(self):
        self.assertEqual(
            AuthselectValidationStatus.VALIDATION_COMPLETE,
            0,
        )

    def test_no_configuration_uses_enoent(self):
        self.assertEqual(
            AuthselectValidationStatus.NO_CONFIGURATION,
            errno.ENOENT,
        )

    def test_not_managed_uses_eexist(self):
        self.assertEqual(
            AuthselectValidationStatus.NOT_MANAGED,
            errno.EEXIST,
        )


if __name__ == "__main__":
    unittest.main()

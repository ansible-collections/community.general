# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.general.plugins.module_utils.scaleway import SecretVariables, argon2


class SecretVariablesTestCase(unittest.TestCase):
    def test_dict_to_list(self):
        source = dict(
            attribute1="value1",
            attribute2="value2"
        )
        expect = [
            dict(key="attribute1", value="value1"),
            dict(key="attribute2", value="value2")
        ]

        result = SecretVariables.dict_to_list(source)
        result = sorted(result, key=lambda el: el['key'])
        self.assertEqual(result, expect)

    def test_list_to_dict(self):
        source = [
            dict(key="secret1", hashed_value="$argon2id$v=19$m=65536,t=1,p=2$NuZk+6UATHNFV78nFRXFvA$3kivcXfzNHI1c/4ZBpP8BeBSGhhI82NfOh4Dd48JJgc"),
            dict(key="secret2", hashed_value="$argon2id$v=19$m=65536,t=1,p=2$etGO/Z8ImYDeKr6uFsyPAQ$FbL5+hG/duDEpa8UCYqXpEUQ5EacKg6i2iAs+Dq4dAI")
        ]
        expect = dict(
            secret1="$argon2id$v=19$m=65536,t=1,p=2$NuZk+6UATHNFV78nFRXFvA$3kivcXfzNHI1c/4ZBpP8BeBSGhhI82NfOh4Dd48JJgc",
            secret2="$argon2id$v=19$m=65536,t=1,p=2$etGO/Z8ImYDeKr6uFsyPAQ$FbL5+hG/duDEpa8UCYqXpEUQ5EacKg6i2iAs+Dq4dAI"
        )

        self.assertEqual(SecretVariables.list_to_dict(source, hashed=True), expect)

    def test_list_to_dict(self):
        source = [
            dict(key="secret1", value="value1"),
            dict(key="secret2", value="value2")
        ]
        expect = dict(
            secret1="value1",
            secret2="value2"
        )

        self.assertEqual(SecretVariables.list_to_dict(source, hashed=False), expect)

    @unittest.skipIf(argon2 is None, "Missing required 'argon2' library")
    def test_decode_full(self):
        source_secret = [
            dict(key="secret1", hashed_value="$argon2id$v=19$m=65536,t=1,p=2$NuZk+6UATHNFV78nFRXFvA$3kivcXfzNHI1c/4ZBpP8BeBSGhhI82NfOh4Dd48JJgc"),
            dict(key="secret2", hashed_value="$argon2id$v=19$m=65536,t=1,p=2$etGO/Z8ImYDeKr6uFsyPAQ$FbL5+hG/duDEpa8UCYqXpEUQ5EacKg6i2iAs+Dq4dAI"),
        ]
        source_value = [
            dict(key="secret1", value="value1"),
            dict(key="secret2", value="value2"),
        ]

        expect = [
            dict(key="secret1", value="value1"),
            dict(key="secret2", value="value2"),
        ]

        result = SecretVariables.decode(source_secret, source_value)
        result = sorted(result, key=lambda el: el['key'])
        self.assertEqual(result, expect)

    @unittest.skipIf(argon2 is None, "Missing required 'argon2' library")
    def test_decode_dict_divergent_values(self):
        source_secret = [
            dict(key="secret1", hashed_value="$argon2id$v=19$m=65536,t=1,p=2$NuZk+6UATHNFV78nFRXFvA$3kivcXfzNHI1c/4ZBpP8BeBSGhhI82NfOh4Dd48JJgc"),
            dict(key="secret2", hashed_value="$argon2id$v=19$m=65536,t=1,p=2$etGO/Z8ImYDeKr6uFsyPAQ$FbL5+hG/duDEpa8UCYqXpEUQ5EacKg6i2iAs+Dq4dAI"),
        ]
        source_value = [
            dict(key="secret1", value="value1"),
            dict(key="secret2", value="diverged_value2"),
        ]

        expect = [
            dict(key="secret1", value="value1"),
            dict(key="secret2", value="$argon2id$v=19$m=65536,t=1,p=2$etGO/Z8ImYDeKr6uFsyPAQ$FbL5+hG/duDEpa8UCYqXpEUQ5EacKg6i2iAs+Dq4dAI"),
        ]

        result = SecretVariables.decode(source_secret, source_value)
        result = sorted(result, key=lambda el: el['key'])
        self.assertEqual(result, expect)

    @unittest.skipIf(argon2 is None, "Missing required 'argon2' library")
    def test_decode_dict_missing_values_left(self):
        source_secret = [
            dict(key="secret1", hashed_value="$argon2id$v=19$m=65536,t=1,p=2$NuZk+6UATHNFV78nFRXFvA$3kivcXfzNHI1c/4ZBpP8BeBSGhhI82NfOh4Dd48JJgc"),
        ]
        source_value = [
            dict(key="secret1", value="value1"),
            dict(key="secret2", value="value2"),
        ]

        expect = [
            dict(key="secret1", value="value1"),
        ]

        result = SecretVariables.decode(source_secret, source_value)
        result = sorted(result, key=lambda el: el['key'])
        self.assertEqual(result, expect)

    @unittest.skipIf(argon2 is None, "Missing required 'argon2' library")
    def test_decode_dict_missing_values_right(self):
        source_secret = [
            dict(key="secret1", hashed_value="$argon2id$v=19$m=65536,t=1,p=2$NuZk+6UATHNFV78nFRXFvA$3kivcXfzNHI1c/4ZBpP8BeBSGhhI82NfOh4Dd48JJgc"),
            dict(key="secret2", hashed_value="$argon2id$v=19$m=65536,t=1,p=2$etGO/Z8ImYDeKr6uFsyPAQ$FbL5+hG/duDEpa8UCYqXpEUQ5EacKg6i2iAs+Dq4dAI"),
        ]
        source_value = [
            dict(key="secret1", value="value1"),
        ]

        expect = [
            dict(key="secret1", value="value1"),
            dict(key="secret2", value="$argon2id$v=19$m=65536,t=1,p=2$etGO/Z8ImYDeKr6uFsyPAQ$FbL5+hG/duDEpa8UCYqXpEUQ5EacKg6i2iAs+Dq4dAI"),
        ]

        result = SecretVariables.decode(source_secret, source_value)
        result = sorted(result, key=lambda el: el['key'])
        self.assertEqual(result, expect)

# -*- coding: utf-8 -*-
# (c) 2020, Adam Migus <adam@migus.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat.unittest import TestCase
from ansible_collections.community.general.tests.unit.compat.mock import (
    patch,
    DEFAULT,
    MagicMock,
)
from ansible_collections.community.general.plugins.lookup import tss
from ansible.plugins.loader import lookup_loader


TSS_IMPORT_PATH = 'ansible_collections.community.general.plugins.lookup.tss'


def make_absolute(name):
    return '.'.join([TSS_IMPORT_PATH, name])


class MockSecretServer(MagicMock):
    RESPONSE = '{"foo": "bar"}'

    def get_secret_json(self, path):
        return self.RESPONSE


class SecretServerError(Exception):
    pass


@patch(make_absolute('SecretServer'), MockSecretServer())
class TestTSSClient(TestCase):
    def setUp(self):
        self.server_params = {
            'base_url': '',
            'username': '',
            'domain': '',
            'password': '',
            'api_path_uri': '',
            'token_path_uri': '',
        }

    def test_from_params(self):
        with patch(make_absolute('HAS_TSS_AUTHORIZER'), False):
            client = tss.TSSClient.from_params(**self.server_params)
            self.assertIsInstance(client, tss.TSSClientV0)

            with patch.dict(self.server_params, {'domain': 'foo'}):
                with self.assertRaises(tss.AnsibleError):
                    tss.TSSClient.from_params(**self.server_params)

        with patch.multiple(TSS_IMPORT_PATH,
                            HAS_TSS_AUTHORIZER=True,
                            PasswordGrantAuthorizer=DEFAULT,
                            DomainPasswordGrantAuthorizer=DEFAULT):

            client = tss.TSSClient.from_params(**self.server_params)
            self.assertIsInstance(client, tss.TSSClientV1)

            with patch.dict(self.server_params, {'domain': 'foo'}):
                client = tss.TSSClient.from_params(**self.server_params)
                self.assertIsInstance(client, tss.TSSClientV1)


@patch(make_absolute('SecretServer'), MockSecretServer())
class TestLookupModule(TestCase):
    def setUp(self):
        tss.HAS_TSS_SDK = True
        self.lookup = lookup_loader.get("community.general.tss")

    def test_get_secret_json(self):
        self.assertListEqual(
            [MockSecretServer.RESPONSE],
            self.lookup.run(
                [1],
                [],
                **{"base_url": "dummy", "username": "dummy", "password": "dummy", }
            ),
        )

    @patch(make_absolute('SecretServerError'), SecretServerError)
    def test_get_secret_json_invalid_term(self):
        with self.assertRaises(tss.AnsibleOptionsError):
            self.lookup.run(
                ['foo'],
                [],
                **{"base_url": "dummy", "username": "dummy", "password": "dummy"}
            )

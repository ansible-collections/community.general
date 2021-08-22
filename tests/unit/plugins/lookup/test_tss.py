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


class SecretServerError(Exception):
    def __init__(self):
        self.message = ''


TSS_IMPORT_PATH = 'ansible_collections.community.general.plugins.lookup.tss'


def make_absolute(name):
    return '.'.join([TSS_IMPORT_PATH, name])


class MockSecretServer(MagicMock):
    RESPONSE = '{"foo": "bar"}'

    def get_secret_json(self, path):
        return self.RESPONSE


class MockFaultySecretServer(MagicMock):
    RESPONSE = '{"foo": "bar"}'

    def get_secret_json(self, path):
        raise SecretServerError


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


class TestLookupModule(TestCase):
    def setUp(self):
        self.lookup = lookup_loader.get("community.general.tss")

    @patch.multiple(TSS_IMPORT_PATH,
                    HAS_TSS_SDK=False,
                    SecretServer=MockSecretServer)
    def test_missing_sdk(self):
        with self.assertRaises(tss.AnsibleError):
            self.lookup.run([], [], **{})

    @patch.multiple(TSS_IMPORT_PATH,
                    HAS_TSS_SDK=True,
                    SecretServer=MockSecretServer)
    def test_get_secret_json(self):
        self.assertListEqual(
            [MockSecretServer.RESPONSE],
            self.lookup.run(
                [1],
                [],
                **{"base_url": "dummy", "username": "dummy", "password": "dummy", }
            ),
        )

    @patch.multiple(TSS_IMPORT_PATH,
                    HAS_TSS_SDK=True,
                    SecretServer=MockFaultySecretServer,
                    SecretServerError=SecretServerError)
    def test_get_secret_json_server_error(self):
        with self.assertRaises(tss.AnsibleError):
            self.lookup.run(
                [1],
                [],
                **{"base_url": "dummy", "username": "dummy", "password": "dummy"}
            )

    @patch.multiple(TSS_IMPORT_PATH,
                    HAS_TSS_SDK=True,
                    SecretServer=MockSecretServer,
                    SecretServerError=SecretServerError)
    def test_get_secret_json_invalid_term(self):
        with self.assertRaises(tss.AnsibleOptionsError):
            self.lookup.run(
                ['foo'],
                [],
                **{"base_url": "dummy", "username": "dummy", "password": "dummy"}
            )

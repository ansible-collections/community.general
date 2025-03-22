# Copyright (c) 2016 Andrew Zenk <azenk@umn.edu>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from argparse import ArgumentParser

from ansible_collections.community.internal_test_tools.tests.unit.compat import unittest
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch

from ansible.errors import AnsibleError
from ansible.module_utils import six
from ansible.plugins.loader import lookup_loader
from ansible_collections.community.general.plugins.lookup.lastpass import LPass, LPassException


MOCK_ENTRIES = [{'username': 'user',
                 'name': 'Mock Entry',
                 'password': 't0pS3cret passphrase entry!',
                 'url': 'https://localhost/login',
                 'notes': 'Test\nnote with multiple lines.\n',
                 'id': '0123456789'}]


class MockLPass(LPass):

    _mock_logged_out = False
    _mock_disconnected = False

    def _lookup_mock_entry(self, key):
        for entry in MOCK_ENTRIES:
            if key == entry['id'] or key == entry['name']:
                return entry

    def _run(self, args, stdin=None, expected_rc=0):
        # Mock behavior of lpass executable
        base_options = ArgumentParser(add_help=False)
        base_options.add_argument('--color', default="auto", choices=['auto', 'always', 'never'])

        p = ArgumentParser()
        sp = p.add_subparsers(help='command', dest='subparser_name')

        logout_p = sp.add_parser('logout', parents=[base_options], help='logout')
        show_p = sp.add_parser('show', parents=[base_options], help='show entry details')

        field_group = show_p.add_mutually_exclusive_group(required=True)
        for field in MOCK_ENTRIES[0].keys():
            field_group.add_argument("--{0}".format(field), default=False, action='store_true')
        field_group.add_argument('--field', default=None)
        show_p.add_argument('selector', help='Unique Name or ID')

        args = p.parse_args(args)

        def mock_exit(output='', error='', rc=0):
            if rc != expected_rc:
                raise LPassException(error)
            return output, error

        if args.color != 'never':
            return mock_exit(error='Error: Mock only supports --color=never', rc=1)

        if args.subparser_name == 'logout':
            if self._mock_logged_out:
                return mock_exit(error='Error: Not currently logged in', rc=1)

            logged_in_error = 'Are you sure you would like to log out? [Y/n]'
            if stdin and stdin.lower() == 'n\n':
                return mock_exit(output='Log out: aborted.', error=logged_in_error, rc=1)
            elif stdin and stdin.lower() == 'y\n':
                return mock_exit(output='Log out: complete.', error=logged_in_error, rc=0)
            else:
                return mock_exit(error='Error: aborted response', rc=1)

        if args.subparser_name == 'show':
            if self._mock_logged_out:
                return mock_exit(error='Error: Could not find decryption key.' +
                                 ' Perhaps you need to login with `lpass login`.', rc=1)

            if self._mock_disconnected:
                return mock_exit(error='Error: Couldn\'t resolve host name.', rc=1)

            mock_entry = self._lookup_mock_entry(args.selector)

            if args.field:
                return mock_exit(output=mock_entry.get(args.field, ''))
            elif args.password:
                return mock_exit(output=mock_entry.get('password', ''))
            elif args.username:
                return mock_exit(output=mock_entry.get('username', ''))
            elif args.url:
                return mock_exit(output=mock_entry.get('url', ''))
            elif args.name:
                return mock_exit(output=mock_entry.get('name', ''))
            elif args.id:
                return mock_exit(output=mock_entry.get('id', ''))
            elif args.notes:
                return mock_exit(output=mock_entry.get('notes', ''))

        raise LPassException('We should never get here')


class DisconnectedMockLPass(MockLPass):

    _mock_disconnected = True


class LoggedOutMockLPass(MockLPass):

    _mock_logged_out = True


class TestLPass(unittest.TestCase):

    def setUp(self):
        self.lookup = lookup_loader.get('community.general.lastpass')

    def test_lastpass_cli_path(self):
        lp = MockLPass(path='/dev/null')
        self.assertEqual('/dev/null', lp.cli_path)

    def test_lastpass_build_args_logout(self):
        lp = MockLPass()
        self.assertEqual(['logout', '--color=never'], lp._build_args("logout"))

    def test_lastpass_logged_in_true(self):
        lp = MockLPass()
        self.assertTrue(lp.logged_in)

    def test_lastpass_logged_in_false(self):
        lp = LoggedOutMockLPass()
        self.assertFalse(lp.logged_in)

    def test_lastpass_show_disconnected(self):
        lp = DisconnectedMockLPass()

        with self.assertRaises(LPassException):
            lp.get_field('0123456789', 'username')

    def test_lastpass_show(self):
        lp = MockLPass()
        for entry in MOCK_ENTRIES:
            entry_id = entry.get('id')
            for k, v in six.iteritems(entry):
                self.assertEqual(v.strip(), lp.get_field(entry_id, k))


class TestLastpassPlugin(unittest.TestCase):

    def setUp(self):
        self.lookup = lookup_loader.get('community.general.lastpass')

    @patch('ansible_collections.community.general.plugins.lookup.lastpass.LPass', new=MockLPass)
    def test_lastpass_plugin_normal(self):
        for entry in MOCK_ENTRIES:
            entry_id = entry.get('id')
            for k, v in six.iteritems(entry):
                self.assertEqual(v.strip(),
                                 self.lookup.run([entry_id], field=k)[0])

    @patch('ansible_collections.community.general.plugins.lookup.lastpass.LPass', LoggedOutMockLPass)
    def test_lastpass_plugin_logged_out(self):
        entry = MOCK_ENTRIES[0]
        entry_id = entry.get('id')
        with self.assertRaises(AnsibleError):
            self.lookup.run([entry_id], field='password')

    @patch('ansible_collections.community.general.plugins.lookup.lastpass.LPass', DisconnectedMockLPass)
    def test_lastpass_plugin_disconnected(self):
        entry = MOCK_ENTRIES[0]
        entry_id = entry.get('id')
        with self.assertRaises(AnsibleError):
            self.lookup.run([entry_id], field='password')

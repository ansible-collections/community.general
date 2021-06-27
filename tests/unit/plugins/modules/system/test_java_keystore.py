# -*- coding: utf-8 -*-

# Copyright (c) 2018, Ansible Project
# Copyright (c) 2018, Abhijeet Kasurde <akasurde@redhat.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

from ansible_collections.community.general.tests.unit.plugins.modules.utils import ModuleTestCase, set_module_args
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.compat.mock import Mock
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.modules.system.java_keystore import JavaKeystore


module_argument_spec = dict(
    name=dict(type='str', required=True),
    dest=dict(type='path', required=True),
    certificate=dict(type='str', no_log=True),
    certificate_path=dict(type='path'),
    private_key=dict(type='str', no_log=True),
    private_key_path=dict(type='path', no_log=False),
    private_key_passphrase=dict(type='str', no_log=True),
    password=dict(type='str', required=True, no_log=True),
    ssl_backend=dict(type='str', default='openssl', choices=['openssl', 'cryptography']),
    keystore_type=dict(type='str', choices=['jks', 'pkcs12']),
    force=dict(type='bool', default=False),
)
module_supports_check_mode = True
module_choose_between = (['certificate', 'certificate_path'],
                         ['private_key', 'private_key_path'])


class TestCreateJavaKeystore(ModuleTestCase):
    """Test the creation of a Java keystore."""

    def setUp(self):
        """Setup."""
        super(TestCreateJavaKeystore, self).setUp()

        orig_exists = os.path.exists
        self.mock_create_file = patch('ansible_collections.community.general.plugins.modules.system.java_keystore.create_file')
        self.mock_create_path = patch('ansible_collections.community.general.plugins.modules.system.java_keystore.create_path')
        self.mock_current_type = patch('ansible_collections.community.general.plugins.modules.system.java_keystore.JavaKeystore.current_type')
        self.mock_run_command = patch('ansible.module_utils.basic.AnsibleModule.run_command')
        self.mock_get_bin_path = patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')
        self.mock_preserved_copy = patch('ansible.module_utils.basic.AnsibleModule.preserved_copy')
        self.mock_atomic_move = patch('ansible.module_utils.basic.AnsibleModule.atomic_move')
        self.mock_os_path_exists = patch('os.path.exists',
                                         side_effect=lambda path: True if path == '/path/to/keystore.jks' else orig_exists(path))
        self.mock_selinux_context = patch('ansible.module_utils.basic.AnsibleModule.selinux_context',
                                          side_effect=lambda path: ['unconfined_u', 'object_r', 'user_home_t', 's0'])
        self.mock_is_special_selinux_path = patch('ansible.module_utils.basic.AnsibleModule.is_special_selinux_path',
                                                  side_effect=lambda path: (False, None))
        self.run_command = self.mock_run_command.start()
        self.get_bin_path = self.mock_get_bin_path.start()
        self.preserved_copy = self.mock_preserved_copy.start()
        self.atomic_move = self.mock_atomic_move.start()
        self.create_file = self.mock_create_file.start()
        self.create_path = self.mock_create_path.start()
        self.current_type = self.mock_current_type.start()
        self.selinux_context = self.mock_selinux_context.start()
        self.is_special_selinux_path = self.mock_is_special_selinux_path.start()
        self.os_path_exists = self.mock_os_path_exists.start()

    def tearDown(self):
        """Teardown."""
        super(TestCreateJavaKeystore, self).tearDown()
        self.mock_create_file.stop()
        self.mock_create_path.stop()
        self.mock_current_type.stop()
        self.mock_run_command.stop()
        self.mock_get_bin_path.stop()
        self.mock_preserved_copy.stop()
        self.mock_atomic_move.stop()
        self.mock_selinux_context.stop()
        self.mock_is_special_selinux_path.stop()
        self.mock_os_path_exists.stop()

    def test_create_jks_success(self):
        set_module_args(dict(
            certificate='cert-foo',
            private_key='private-foo',
            dest='/path/to/keystore.jks',
            name='test',
            password='changeit'
        ))

        module = AnsibleModule(
            argument_spec=module_argument_spec,
            supports_check_mode=module_supports_check_mode,
            mutually_exclusive=module_choose_between,
            required_one_of=module_choose_between
        )

        with patch('os.remove', return_value=True):
            self.create_path.side_effect = ['/tmp/tmpgrzm2ah7']
            self.create_file.side_effect = ['/tmp/etacifitrec', '/tmp/yek_etavirp', '']
            self.run_command.side_effect = [(0, '', ''), (0, '', '')]
            self.get_bin_path.side_effect = ['keytool', 'openssl', '']
            jks = JavaKeystore(module)
            assert jks.create() == {
                'changed': True,
                'cmd': ["keytool", "-importkeystore",
                        "-destkeystore", "/path/to/keystore.jks",
                        "-srckeystore", "/tmp/tmpgrzm2ah7", "-srcstoretype", "pkcs12", "-alias", "test",
                        "-noprompt"],
                'msg': '',
                'rc': 0
            }

    def test_create_jks_keypass_fail_export_pkcs12(self):
        set_module_args(dict(
            certificate='cert-foo',
            private_key='private-foo',
            private_key_passphrase='passphrase-foo',
            dest='/path/to/keystore.jks',
            name='test',
            password='changeit'
        ))

        module = AnsibleModule(
            argument_spec=module_argument_spec,
            supports_check_mode=module_supports_check_mode,
            mutually_exclusive=module_choose_between,
            required_one_of=module_choose_between
        )

        module.exit_json = Mock()
        module.fail_json = Mock()

        with patch('os.remove', return_value=True):
            self.create_path.side_effect = ['/tmp/tmp1cyp12xa']
            self.create_file.side_effect = ['/tmp/tmpvalcrt32', '/tmp/tmpwh4key0c', '']
            self.run_command.side_effect = [(1, '', 'Oops'), (0, '', '')]
            self.get_bin_path.side_effect = ['keytool', 'openssl', '']
            jks = JavaKeystore(module)
            jks.create()
            module.fail_json.assert_called_once_with(
                cmd=["openssl", "pkcs12", "-export", "-name", "test",
                     "-in", "/tmp/tmpvalcrt32",
                     "-inkey", "/tmp/tmpwh4key0c",
                     "-out", "/tmp/tmp1cyp12xa",
                     "-passout", "stdin",
                     "-passin", "stdin"],
                msg='',
                err='Oops',
                rc=1
            )

    def test_create_jks_fail_export_pkcs12(self):
        set_module_args(dict(
            certificate='cert-foo',
            private_key='private-foo',
            dest='/path/to/keystore.jks',
            name='test',
            password='changeit'
        ))

        module = AnsibleModule(
            argument_spec=module_argument_spec,
            supports_check_mode=module_supports_check_mode,
            mutually_exclusive=module_choose_between,
            required_one_of=module_choose_between
        )

        module.exit_json = Mock()
        module.fail_json = Mock()

        with patch('os.remove', return_value=True):
            self.create_path.side_effect = ['/tmp/tmp1cyp12xa']
            self.create_file.side_effect = ['/tmp/tmpvalcrt32', '/tmp/tmpwh4key0c', '']
            self.run_command.side_effect = [(1, '', 'Oops'), (0, '', '')]
            self.get_bin_path.side_effect = ['keytool', 'openssl', '']
            jks = JavaKeystore(module)
            jks.create()
            module.fail_json.assert_called_once_with(
                cmd=["openssl", "pkcs12", "-export", "-name", "test",
                     "-in", "/tmp/tmpvalcrt32",
                     "-inkey", "/tmp/tmpwh4key0c",
                     "-out", "/tmp/tmp1cyp12xa",
                     "-passout", "stdin"],
                msg='',
                err='Oops',
                rc=1
            )

    def test_create_jks_fail_import_key(self):
        set_module_args(dict(
            certificate='cert-foo',
            private_key='private-foo',
            dest='/path/to/keystore.jks',
            name='test',
            password='changeit'
        ))

        module = AnsibleModule(
            argument_spec=module_argument_spec,
            supports_check_mode=module_supports_check_mode,
            mutually_exclusive=module_choose_between,
            required_one_of=module_choose_between
        )

        module.exit_json = Mock()
        module.fail_json = Mock()

        with patch('os.remove', return_value=True):
            self.create_path.side_effect = ['/tmp/tmpgrzm2ah7']
            self.create_file.side_effect = ['/tmp/etacifitrec', '/tmp/yek_etavirp', '']
            self.run_command.side_effect = [(0, '', ''), (1, '', 'Oops')]
            self.get_bin_path.side_effect = ['keytool', 'openssl', '']
            jks = JavaKeystore(module)
            jks.create()
            module.fail_json.assert_called_once_with(
                cmd=["keytool", "-importkeystore",
                     "-destkeystore", "/path/to/keystore.jks",
                     "-srckeystore", "/tmp/tmpgrzm2ah7", "-srcstoretype", "pkcs12", "-alias", "test",
                     "-noprompt"],
                msg='',
                err='Oops',
                rc=1
            )


class TestCertChanged(ModuleTestCase):
    """Test if the cert has changed."""

    def setUp(self):
        """Setup."""
        super(TestCertChanged, self).setUp()
        self.mock_create_file = patch('ansible_collections.community.general.plugins.modules.system.java_keystore.create_file')
        self.mock_current_type = patch('ansible_collections.community.general.plugins.modules.system.java_keystore.JavaKeystore.current_type')
        self.mock_run_command = patch('ansible.module_utils.basic.AnsibleModule.run_command')
        self.mock_get_bin_path = patch('ansible.module_utils.basic.AnsibleModule.get_bin_path')
        self.mock_preserved_copy = patch('ansible.module_utils.basic.AnsibleModule.preserved_copy')
        self.mock_atomic_move = patch('ansible.module_utils.basic.AnsibleModule.atomic_move')
        self.run_command = self.mock_run_command.start()
        self.create_file = self.mock_create_file.start()
        self.get_bin_path = self.mock_get_bin_path.start()
        self.current_type = self.mock_current_type.start()
        self.preserved_copy = self.mock_preserved_copy.start()
        self.atomic_move = self.mock_atomic_move.start()

    def tearDown(self):
        """Teardown."""
        super(TestCertChanged, self).tearDown()
        self.mock_create_file.stop()
        self.mock_current_type.stop()
        self.mock_run_command.stop()
        self.mock_get_bin_path.stop()
        self.mock_preserved_copy.stop()
        self.mock_atomic_move.stop()

    def test_cert_unchanged_same_fingerprint(self):
        set_module_args(dict(
            certificate='cert-foo',
            private_key='private-foo',
            dest='/path/to/keystore.jks',
            name='foo',
            password='changeit'
        ))

        module = AnsibleModule(
            argument_spec=module_argument_spec,
            supports_check_mode=module_supports_check_mode,
            mutually_exclusive=module_choose_between,
            required_one_of=module_choose_between
        )

        with patch('os.remove', return_value=True):
            self.create_file.side_effect = ['/tmp/placeholder', '']
            self.run_command.side_effect = [(0, 'foo=abcd:1234:efgh', ''), (0, 'SHA256: abcd:1234:efgh', '')]
            self.get_bin_path.side_effect = ['keytool', 'openssl', '']
            self.current_type.side_effect = ['jks']
            jks = JavaKeystore(module)
            result = jks.cert_changed()
            self.assertFalse(result, 'Fingerprint is identical')

    def test_cert_changed_fingerprint_mismatch(self):
        set_module_args(dict(
            certificate='cert-foo',
            private_key='private-foo',
            dest='/path/to/keystore.jks',
            name='foo',
            password='changeit'
        ))

        module = AnsibleModule(
            argument_spec=module_argument_spec,
            supports_check_mode=module_supports_check_mode,
            mutually_exclusive=module_choose_between,
            required_one_of=module_choose_between
        )

        with patch('os.remove', return_value=True):
            self.create_file.side_effect = ['/tmp/placeholder', '']
            self.run_command.side_effect = [(0, 'foo=abcd:1234:efgh', ''), (0, 'SHA256: wxyz:9876:stuv', '')]
            self.get_bin_path.side_effect = ['keytool', 'openssl', '']
            self.current_type.side_effect = ['jks']
            jks = JavaKeystore(module)
            result = jks.cert_changed()
            self.assertTrue(result, 'Fingerprint mismatch')

    def test_cert_changed_alias_does_not_exist(self):
        set_module_args(dict(
            certificate='cert-foo',
            private_key='private-foo',
            dest='/path/to/keystore.jks',
            name='foo',
            password='changeit'
        ))

        module = AnsibleModule(
            argument_spec=module_argument_spec,
            supports_check_mode=module_supports_check_mode,
            mutually_exclusive=module_choose_between,
            required_one_of=module_choose_between
        )

        with patch('os.remove', return_value=True):
            self.create_file.side_effect = ['/tmp/placeholder', '']
            self.run_command.side_effect = [(0, 'foo=abcd:1234:efgh', ''),
                                            (1, 'keytool error: java.lang.Exception: Alias <foo> does not exist', '')]
            self.get_bin_path.side_effect = ['keytool', 'openssl', '']
            jks = JavaKeystore(module)
            result = jks.cert_changed()
            self.assertTrue(result, 'Alias mismatch detected')

    def test_cert_changed_password_mismatch(self):
        set_module_args(dict(
            certificate='cert-foo',
            private_key='private-foo',
            dest='/path/to/keystore.jks',
            name='foo',
            password='changeit'
        ))

        module = AnsibleModule(
            argument_spec=module_argument_spec,
            supports_check_mode=module_supports_check_mode,
            mutually_exclusive=module_choose_between,
            required_one_of=module_choose_between
        )

        with patch('os.remove', return_value=True):
            self.create_file.side_effect = ['/tmp/placeholder', '']
            self.run_command.side_effect = [(0, 'foo=abcd:1234:efgh', ''),
                                            (1, 'keytool error: java.io.IOException: Keystore password was incorrect', '')]
            self.get_bin_path.side_effect = ['keytool', 'openssl', '']
            jks = JavaKeystore(module)
            result = jks.cert_changed()
            self.assertTrue(result, 'Password mismatch detected')

    def test_cert_changed_fail_read_cert(self):
        set_module_args(dict(
            certificate='cert-foo',
            private_key='private-foo',
            dest='/path/to/keystore.jks',
            name='foo',
            password='changeit'
        ))

        module = AnsibleModule(
            argument_spec=module_argument_spec,
            supports_check_mode=module_supports_check_mode,
            mutually_exclusive=module_choose_between,
            required_one_of=module_choose_between
        )

        module.exit_json = Mock()
        module.fail_json = Mock()

        with patch('os.remove', return_value=True):
            self.create_file.side_effect = ['/tmp/tmpdj6bvvme', '']
            self.run_command.side_effect = [(1, '', 'Oops'), (0, 'SHA256: wxyz:9876:stuv', '')]
            self.get_bin_path.side_effect = ['keytool', 'openssl', '']
            self.current_type.side_effect = ['jks']
            jks = JavaKeystore(module)
            jks.cert_changed()
            module.fail_json.assert_called_once_with(
                cmd=["openssl", "x509", "-noout", "-in", "/tmp/tmpdj6bvvme", "-fingerprint", "-sha256"],
                msg='',
                err='Oops',
                rc=1
            )

    def test_cert_changed_fail_read_keystore(self):
        set_module_args(dict(
            certificate='cert-foo',
            private_key='private-foo',
            dest='/path/to/keystore.jks',
            name='foo',
            password='changeit'
        ))

        module = AnsibleModule(
            argument_spec=module_argument_spec,
            supports_check_mode=module_supports_check_mode,
            mutually_exclusive=module_choose_between,
            required_one_of=module_choose_between
        )

        module.exit_json = Mock()
        module.fail_json = Mock(return_value=True)

        with patch('os.remove', return_value=True):
            self.create_file.side_effect = ['/tmp/placeholder', '']
            self.run_command.side_effect = [(0, 'foo: wxyz:9876:stuv', ''), (1, '', 'Oops')]
            self.get_bin_path.side_effect = ['keytool', 'openssl', '']
            jks = JavaKeystore(module)
            jks.cert_changed()
            module.fail_json.assert_called_with(
                cmd=["keytool", "-list", "-alias", "foo", "-keystore", "/path/to/keystore.jks", "-v"],
                msg='',
                err='Oops',
                rc=1
            )

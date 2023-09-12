# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch, Mock
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
from ansible_collections.community.general.plugins.modules import jenkins_node

import json


def set_module_args(args):
    """Prepare arguments so that they will be picked up during module creation."""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case."""
    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case."""
    pass


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class TestJenkinsNode(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    def test_name_missing(self, test_deps):
        test_deps.return_value = None
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            jenkins_node.main()

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.configure_node')
    def test_present_not_exists(self, configure_node, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.node_exists = Mock(return_value=False)
        server.assert_node_exists = Mock(
            side_effect=lambda _: server.create_node.assert_called_with(name)
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.create_node.assert_called_with(name)
        configure_node.assert_called()

        self.assertTrue(result['created'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.configure_node')
    def test_present_not_exists_check_mode(
        self, configure_node, get_server, test_dependencies
    ):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.node_exists = Mock(return_value=False)

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.create_node.assert_not_called()
        configure_node.assert_not_called()

        self.assertTrue(result['created'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.configure_node')
    def test_present_exists(
        self, configure_node, get_server, test_dependencies
    ):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock(
            side_effect=lambda _: server.node_exists.assert_called_with(name)
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.create_node.assert_not_called()
        configure_node.assert_called()

        self.assertFalse(result['created'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.configure_node')
    def test_present_exists_check_mode(
        self, configure_node, get_server, test_dependencies
    ):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.node_exists = Mock(return_value=True)

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.create_node.assert_not_called()
        configure_node.assert_called()

        self.assertFalse(result['created'])
        self.assertFalse(result['changed'])


    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_absent_exists(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.node_exists = Mock(return_value=True)
        server.delete_node = Mock(
            side_effect=lambda _: server.node_exists.assert_called_with(name)
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'absent',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.delete_node.assert_called_with(name)

        self.assertTrue(result['deleted'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_absent_exists_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.node_exists = Mock(return_value=True)

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'absent',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.delete_node.assert_not_called()

        self.assertTrue(result['deleted'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_absent_not_exists(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.node_exists = Mock(return_value=False)

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'absent',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.delete_node.assert_not_called()

        self.assertFalse(result['deleted'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_absent_not_exists_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.node_exists = Mock(return_value=False)

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'absent',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.delete_node.assert_not_called()

        self.assertFalse(result['deleted'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.present_node')
    def test_enable_enabled(self, present_node, get_server, test_dependencies):
        test_dependencies.return_value = None

        present_node.return_value = True

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.get_node_info = Mock(
            return_value={'offline': False}
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'enabled',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.enable_node.assert_not_called()

        self.assertFalse(result['enabled'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.present_node')
    def test_enable_enabled_check_mode(self, present_node, get_server, test_dependencies):
        test_dependencies.return_value = None

        present_node.return_value = True

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.get_node_info = Mock(
            return_value={'offline': False}
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'enabled',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.enable_node.assert_not_called()

        self.assertFalse(result['enabled'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.present_node')
    def test_enable_disabled(self, present_node, get_server, test_dependencies):
        test_dependencies.return_value = None

        present_node.return_value = True

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.get_node_info = Mock(
            return_value={'offline': True}
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'enabled',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.enable_node.assert_called_with(name)

        self.assertTrue(result['enabled'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.present_node')
    def test_enable_disabled_check_mode(self, present_node, get_server, test_dependencies):
        test_dependencies.return_value = None

        present_node.return_value = True

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.get_node_info = Mock(
            return_value={'offline': True}
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'enabled',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.enable_node.assert_not_called()

        self.assertTrue(result['enabled'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.present_node')
    def test_disable_disabled_same_offline_message(
        self, present_node, get_server, test_dependencies
    ):
        test_dependencies.return_value = None

        present_node.return_value = True

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.get_node_info = Mock(
            return_value={
                'offline': True,
                'offlineCauseReason': 'oh no!',
            }
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'disabled',
                'offline_message': 'oh no!',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.disable_node.assert_not_called()

        self.assertFalse(result['disabled'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.present_node')
    def test_disable_disabled_same_offline_message_check_mode(
        self, present_node, get_server, test_dependencies
    ):
        test_dependencies.return_value = None

        present_node.return_value = True

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.get_node_info = Mock(
            return_value={
                'offline': True,
                'offlineCauseReason': '',
            }
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'disabled',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.disable_node.assert_not_called()

        self.assertFalse(result['disabled'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.present_node')
    def test_disable_disabled_changed_offline_message(
        self, present_node, get_server, test_dependencies
    ):
        test_dependencies.return_value = None

        present_node.return_value = True

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.get_node_info = Mock(
            return_value={
                'offline': True,
                'offlineCauseReason': 'oh no!',
            }
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'disabled',
                'offline_message': 'oh nooo!!',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.disable_node.assert_called_with(name, 'oh nooo!!')

        self.assertTrue(result['disabled'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.present_node')
    def test_disable_disabled_changed_offline_message_check_mode(
        self, present_node, get_server, test_dependencies
    ):
        test_dependencies.return_value = None

        present_node.return_value = True

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.get_node_info = Mock(
            return_value={
                'offline': True,
                'offlineCauseReason': 'oh no!',
            }
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'disabled',
                'offline_message': 'oh nooo!!',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.disable_node.assert_not_called()

        self.assertTrue(result['disabled'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.present_node')
    def test_disable_enabled(self, present_node, get_server, test_dependencies):
        test_dependencies.return_value = None

        present_node.return_value = True

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.get_node_info = Mock(
            return_value={'offline': False}
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'disabled',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.disable_node.assert_called_with(name, '')

        self.assertTrue(result['disabled'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.present_node')
    def test_disable_enabled_check_mode(
        self, present_node, get_server, test_dependencies
    ):
        test_dependencies.return_value = None

        present_node.return_value = True

        server = Mock()
        get_server.return_value = server

        name = 'test-node'

        server.get_node_info = Mock(
            return_value={'offline': False}
        )

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'disabled',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.disable_node.assert_not_called()

        self.assertTrue(result['disabled'])
        self.assertTrue(result['changed'])

    # TODO: launch_ssh tests
    # TODO: launch_jnlp tests

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_description_added(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <description/>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'description': 'Test node.',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_description_added_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <description/>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'description': 'Test node.',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_description_changed(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <description>Before text.</description>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'description': 'After text.',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_description_changed_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <description>Before text.</description>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'description': 'After text.',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_description_not_changed(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <description>Before text.</description>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'description': 'Before text.',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_description_not_changed_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <description>Before text.</description>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'description': 'Before text.',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_num_executors_changed(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <numExecutors>1</numExecutors>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'num_executors': 2,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_num_executors_changed_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <numExecutors>1</numExecutors>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'num_executors': 2,
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_num_executors_not_changed(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <numExecutors>1</numExecutors>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'num_executors': 1,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_num_executors_not_changed_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <numExecutors>1</numExecutors>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'num_executors': 1,
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_labels_added(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <label/>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'labels': ['a', 'b'],
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_labels_added_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <label/>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'labels': ['a', 'b'],
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_labels_changed(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <label>a b</label>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'labels': ['a', 'c'],
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_labels_changed_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <label>a b</label>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'labels': ['a', 'c'],
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_labels_not_changed(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <label>a b</label>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'labels': ['a', 'b'],
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_labels_not_changed_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <label>a b</label>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'labels': ['a', 'b'],
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_remote_fs_added(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <remoteFS/>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'remote_fs': '/path/to/fs',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_remote_fs_added_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <remoteFS/>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'remote_fs': '/path/to/fs',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_remote_fs_changed(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <remoteFS>/the/path/before</remoteFS>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'remote_fs': '/the/path/after',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_remote_fs_changed_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <remoteFS>/the/path/before</remoteFS>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'remote_fs': '/the/path/after',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_remote_fs_not_changed(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <remoteFS>/the/path/before</remoteFS>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'remote_fs': '/the/path/before',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_remote_fs_not_changed_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <remoteFS>/the/path/before</remoteFS>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'remote_fs': '/the/path/before',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_mode_changed(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <mode>NORMAL</mode>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'mode': 'exclusive',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_mode_changed_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <mode>NORMAL</mode>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'mode': 'exclusive',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_mode_not_changed(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <mode>NORMAL</mode>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'mode': 'normal',
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_mode_not_changed_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <mode>NORMAL</mode>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'mode': 'normal',
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_defer_wipeout_disabled(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <nodeProperties/>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'defer_wipeout': False,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_defer_wipeout_disabled_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <nodeProperties/>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'defer_wipeout': False,
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_defer_wipeout_not_disabled(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <nodeProperties/>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'defer_wipeout': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_defer_wipeout_not_disabled_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <nodeProperties/>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'defer_wipeout': True,
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_defer_wipeout_enabled(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <nodeProperties>
        <hudson.plugins.ws__cleanup.DisableDeferredWipeoutNodeProperty plugin="ws-cleanup@0.45"/>
    </nodeProperties>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'defer_wipeout': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_defer_wipeout_enabled_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <nodeProperties>
        <hudson.plugins.ws__cleanup.DisableDeferredWipeoutNodeProperty plugin="ws-cleanup@0.45"/>
    </nodeProperties>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'defer_wipeout': True,
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertTrue(result['configured'])
        self.assertTrue(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_defer_wipeout_not_enabled(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <nodeProperties>
        <hudson.plugins.ws__cleanup.DisableDeferredWipeoutNodeProperty plugin="ws-cleanup@0.45"/>
    </nodeProperties>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'defer_wipeout': False,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_node.JenkinsNode.get_server')
    def test_defer_wipeout_not_enabled_check_mode(self, get_server, test_dependencies):
        test_dependencies.return_value = None

        server = Mock()
        get_server.return_value = server

        server.node_exists = Mock(return_value=True)
        server.assert_node_exists = Mock()
        server.get_node_config = Mock(return_value="""
<slave>
    <nodeProperties>
        <hudson.plugins.ws__cleanup.DisableDeferredWipeoutNodeProperty plugin="ws-cleanup@0.45"/>
    </nodeProperties>
</slave>
""".lstrip())

        name = 'test-node'

        with self.assertRaises(AnsibleExitJson) as exc:
            set_module_args({
                'name': name,
                'state': 'present',
                'defer_wipeout': False,
                '_ansible_check_mode': True,
            })
            jenkins_node.main()

        result = exc.exception.args[0]

        server.assert_node_exists.assert_called_with(name)
        server.reconfig_node.assert_not_called()

        self.assertFalse(result['configured'])
        self.assertFalse(result['changed'])

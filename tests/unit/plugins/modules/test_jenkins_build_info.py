# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
from ansible_collections.community.general.plugins.modules import jenkins_build_info

import jenkins
import json


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class JenkinsMock():

    def get_build_info(self, name, build_number):
        if name == "job-absent":
            raise jenkins.JenkinsException()
        elif name == "job-exception":
            raise Exception()

        return {
            "result": "SUCCESS",
            "build_info": {}
        }

    def get_job_info(self, name):
        if name == "job-absent":
            raise jenkins.JenkinsException()
        elif name == "job-exception":
            raise Exception()

        return {
            "lastBuild": {
                "number": 123
            }
        }


class TestJenkinsBuildInfo(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule,
                                                 exit_json=exit_json,
                                                 fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies')
    def test_module_fail_when_required_args_missing(self, test_deps):
        test_deps.return_value = None
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            jenkins_build_info.main()

    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_jenkins_connection')
    def test_module_get_build_info(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson) as return_json:
            set_module_args({
                "name": "job-present",
                "user": "abc",
                "token": "xyz",
                "build_number": 30
            })
            jenkins_build_info.main()

        self.assertFalse(return_json.exception.args[0]["changed"])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_jenkins_connection')
    def test_module_get_build_info_if_build_does_not_exist(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson) as return_json:
            set_module_args({
                "name": "job-absent",
                "user": "abc",
                "token": "xyz",
                "build_number": 30
            })
            jenkins_build_info.main()

        self.assertFalse(return_json.exception.args[0]['changed'])
        self.assertTrue(return_json.exception.args[0]['failed'])
        self.assertEquals("ABSENT", return_json.exception.args[0]['build_info']['result'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_jenkins_connection')
    def test_module_get_build_info_get_last_build(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson) as return_json:
            set_module_args({
                "name": "job-present",
                "user": "abc",
                "token": "xyz"
            })
            jenkins_build_info.main()

        self.assertFalse(return_json.exception.args[0]['changed'])
        self.assertEquals("SUCCESS", return_json.exception.args[0]['build_info']['result'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_jenkins_connection')
    def test_module_get_build_info_if_exception_trying_to_get_build(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                "name": "job-exception",
                "user": "abc",
                "token": "xyz",
                "build_number": 30
            })
            jenkins_build_info.main()

    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_jenkins_connection')
    def test_module_get_build_info_if_job_does_not_exist(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson) as return_json:
            set_module_args({
                "name": "job-absent",
                "user": "abc",
                "token": "xyz"
            })
            jenkins_build_info.main()

        self.assertFalse(return_json.exception.args[0]['changed'])
        self.assertTrue(return_json.exception.args[0]['failed'])
        self.assertEquals("ABSENT", return_json.exception.args[0]['build_info']['result'])

    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies')
    @patch('ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_jenkins_connection')
    def test_module_get_build_info_if_exception_trying_to_get_job(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleFailJson):
            set_module_args({
                "name": "job-exception",
                "user": "abc",
                "token": "xyz"
            })
            jenkins_build_info.main()

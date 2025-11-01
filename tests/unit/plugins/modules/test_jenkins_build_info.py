# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import patch

from ansible.module_utils import basic
from ansible_collections.community.general.plugins.modules import jenkins_build_info
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    set_module_args,
    exit_json,
    fail_json,
)


class jenkins:
    class JenkinsException(Exception):
        pass


class JenkinsBuildMock:
    def __init__(self, name, build_number=None):
        self.name = name
        self.build_number = build_number

    def get_build_status(self):
        try:
            instance = JenkinsMock()
            response = JenkinsMock.get_build_info(instance, self.name, self.build_number)
            return response
        except jenkins.JenkinsException:
            response = {}
            response["result"] = "ABSENT"
            return response
        except Exception as e:
            fail_json(msg=f"Unable to fetch build information, {e}")


class JenkinsMock:
    def get_build_info(self, name, build_number):
        if name == "job-absent":
            raise jenkins.JenkinsException()

        return {"result": "SUCCESS", "build_info": {}}

    def get_job_info(self, name):
        if name == "job-absent":
            raise jenkins.JenkinsException()

        return {"lastBuild": {"number": 123}}


class TestJenkinsBuildInfo(unittest.TestCase):
    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies")
    def test_module_fail_when_required_args_missing(self, test_deps):
        test_deps.return_value = None
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                jenkins_build_info.main()

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies")
    @patch(
        "ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_jenkins_connection"
    )
    def test_module_get_build_info(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson) as return_json:
            with set_module_args({"name": "job-present", "user": "abc", "token": "xyz", "build_number": 30}):
                jenkins_build_info.main()

        self.assertFalse(return_json.exception.args[0]["changed"])

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies")
    @patch(
        "ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_jenkins_connection"
    )
    @patch("ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_build_status")
    def test_module_get_build_info_if_build_does_not_exist(self, build_status, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()
        build_status.return_value = JenkinsBuildMock("job-absent", 30).get_build_status()

        with self.assertRaises(AnsibleExitJson) as return_json:
            with set_module_args({"name": "job-absent", "user": "abc", "token": "xyz", "build_number": 30}):
                jenkins_build_info.main()

        self.assertFalse(return_json.exception.args[0]["changed"])
        self.assertTrue(return_json.exception.args[0]["failed"])
        self.assertEqual("ABSENT", return_json.exception.args[0]["build_info"]["result"])

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies")
    @patch(
        "ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_jenkins_connection"
    )
    def test_module_get_build_info_get_last_build(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson) as return_json:
            with set_module_args({"name": "job-present", "user": "abc", "token": "xyz"}):
                jenkins_build_info.main()

        self.assertFalse(return_json.exception.args[0]["changed"])
        self.assertEqual("SUCCESS", return_json.exception.args[0]["build_info"]["result"])

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build_info.test_dependencies")
    @patch(
        "ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_jenkins_connection"
    )
    @patch("ansible_collections.community.general.plugins.modules.jenkins_build_info.JenkinsBuildInfo.get_build_status")
    def test_module_get_build_info_if_job_does_not_exist(self, build_status, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()
        build_status.return_value = JenkinsBuildMock("job-absent").get_build_status()

        with self.assertRaises(AnsibleExitJson) as return_json:
            with set_module_args({"name": "job-absent", "user": "abc", "token": "xyz"}):
                jenkins_build_info.main()

        self.assertFalse(return_json.exception.args[0]["changed"])
        self.assertTrue(return_json.exception.args[0]["failed"])
        self.assertEqual("ABSENT", return_json.exception.args[0]["build_info"]["result"])

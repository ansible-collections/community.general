# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import patch

from ansible.module_utils import basic
from ansible_collections.community.general.plugins.modules import jenkins_build
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

    class NotFoundException(JenkinsException):
        pass


class JenkinsBuildMock:
    def get_build_status(self):
        try:
            instance = JenkinsMock()
            response = JenkinsMock.get_build_info(instance, "host-delete", 1234)
            return response
        except jenkins.JenkinsException:
            response = {}
            response["result"] = "ABSENT"
            return response
        except Exception as e:
            fail_json(msg=f"Unable to fetch build information, {e}")


class JenkinsMock:
    def get_job_info(self, name):
        return {"nextBuildNumber": 1234}

    def get_build_info(self, name, build_number):
        if name == "host-delete":
            raise jenkins.JenkinsException(f"job {name} number {build_number} does not exist")
        elif name == "create-detached":
            return {"building": True, "result": None}
        return {"building": True, "result": "SUCCESS"}

    def build_job(self, *args):
        return None

    def delete_build(self, name, build_number):
        return None

    def stop_build(self, name, build_number):
        return None


class JenkinsMockIdempotent:
    def get_job_info(self, name):
        return {"nextBuildNumber": 1235}

    def get_build_info(self, name, build_number):
        return {"building": False, "result": "ABORTED"}

    def build_job(self, *args):
        return None

    def delete_build(self, name, build_number):
        raise jenkins.NotFoundException(f"job {name} number {build_number} does not exist")

    def stop_build(self, name, build_number):
        return None


class TestJenkinsBuild(unittest.TestCase):
    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.test_dependencies")
    def test_module_fail_when_required_args_missing(self, test_deps):
        test_deps.return_value = None
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({}):
                jenkins_build.main()

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.test_dependencies")
    def test_module_fail_when_missing_build_number(self, test_deps):
        test_deps.return_value = None
        with self.assertRaises(AnsibleFailJson):
            with set_module_args({"name": "required-if", "state": "stopped"}):
                jenkins_build.main()

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.test_dependencies")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.JenkinsBuild.get_jenkins_connection")
    def test_module_create_build(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson):
            with set_module_args({"name": "host-check", "user": "abc", "token": "xyz"}):
                jenkins_build.main()

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.test_dependencies")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.JenkinsBuild.get_jenkins_connection")
    def test_module_stop_build(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson) as return_json:
            with set_module_args(
                {"name": "host-check", "build_number": "1234", "state": "stopped", "user": "abc", "token": "xyz"}
            ):
                jenkins_build.main()

        self.assertTrue(return_json.exception.args[0]["changed"])

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.test_dependencies")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.JenkinsBuild.get_jenkins_connection")
    def test_module_stop_build_again(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMockIdempotent()

        with self.assertRaises(AnsibleExitJson) as return_json:
            with set_module_args(
                {"name": "host-check", "build_number": "1234", "state": "stopped", "user": "abc", "password": "xyz"}
            ):
                jenkins_build.main()

        self.assertFalse(return_json.exception.args[0]["changed"])

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.test_dependencies")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.JenkinsBuild.get_jenkins_connection")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.JenkinsBuild.get_build_status")
    def test_module_delete_build(self, build_status, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()
        build_status.return_value = JenkinsBuildMock().get_build_status()

        with self.assertRaises(AnsibleExitJson):
            with set_module_args(
                {"name": "host-delete", "build_number": "1234", "state": "absent", "user": "abc", "token": "xyz"}
            ):
                jenkins_build.main()

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.test_dependencies")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.JenkinsBuild.get_jenkins_connection")
    def test_module_delete_build_again(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMockIdempotent()

        with self.assertRaises(AnsibleFailJson):
            with set_module_args(
                {"name": "host-delete", "build_number": "1234", "state": "absent", "user": "abc", "token": "xyz"}
            ):
                jenkins_build.main()

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.test_dependencies")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.JenkinsBuild.get_jenkins_connection")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.JenkinsBuild.get_build_status")
    def test_module_create_build_without_detach(self, build_status, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()
        build_status.return_value = JenkinsBuildMock().get_build_status()

        with self.assertRaises(AnsibleExitJson) as return_json:
            with set_module_args({"name": "create-detached", "user": "abc", "token": "xyz"}):
                jenkins_build.main()

        self.assertFalse(return_json.exception.args[0]["changed"])

    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.test_dependencies")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_build.JenkinsBuild.get_jenkins_connection")
    def test_module_create_build_detached(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson) as return_json:
            with set_module_args({"name": "create-detached", "user": "abc", "token": "xyz", "detach": True}):
                jenkins_build.main()

        self.assertTrue(return_json.exception.args[0]["changed"])

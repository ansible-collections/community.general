# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest
from unittest.mock import patch

from ansible.module_utils import basic
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    exit_json,
    fail_json,
    set_module_args,
)

from ansible_collections.community.general.plugins.modules import jenkins_job_info

FOLDER_JOB = {
    "name": "jobs_name_one",
    "fullname": "jobs_name_one",
    "url": "https://jenkins.example.com/job/jobs_name_one",
    "jobs": [
        {
            "name": "master",
            "fullname": "jobs_name_one/master",
            "url": "https://jenkins.example.com/job/jobs_name_one/job/master/",
            "color": "blue",
        },
    ],
}

FLAT_JOB = {
    "name": "flat-job",
    "fullname": "flat-job",
    "url": "https://jenkins.example.com/job/flat-job/",
    "color": "blue",
}


class JenkinsMock:
    def get_all_jobs(self):
        return [FOLDER_JOB, FLAT_JOB]


class TestJenkinsJobInfo(unittest.TestCase):
    def setUp(self):
        self.mock_module_helper = patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    @patch("ansible_collections.community.general.plugins.modules.jenkins_job_info.test_dependencies")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_job_info.get_jenkins_connection")
    def test_glob_with_color_on_folder_job(self, jenkins_connection, test_deps):
        """Folder jobs without a top-level color must not raise KeyError."""
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson) as return_json:
            with set_module_args(
                {
                    "glob": "jobs_name_one",
                    "color": "blue",
                    "user": "user",
                    "token": "token",
                }
            ):
                jenkins_job_info.main()

        result = return_json.exception.args[0]
        self.assertFalse(result["changed"])
        self.assertEqual(len(result["jobs"]), 1)
        self.assertEqual(result["jobs"][0]["name"], "jobs_name_one")
        self.assertEqual(result["jobs"][0]["jobs"][0]["color"], "blue")

    @patch("ansible_collections.community.general.plugins.modules.jenkins_job_info.test_dependencies")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_job_info.get_jenkins_connection")
    def test_glob_with_color_on_flat_job(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson) as return_json:
            with set_module_args(
                {
                    "glob": "flat-job",
                    "color": "blue",
                    "user": "user",
                    "token": "token",
                }
            ):
                jenkins_job_info.main()

        result = return_json.exception.args[0]
        self.assertEqual(len(result["jobs"]), 1)
        self.assertEqual(result["jobs"][0]["fullname"], "flat-job")

    @patch("ansible_collections.community.general.plugins.modules.jenkins_job_info.test_dependencies")
    @patch("ansible_collections.community.general.plugins.modules.jenkins_job_info.get_jenkins_connection")
    def test_glob_with_color_no_match(self, jenkins_connection, test_deps):
        test_deps.return_value = None
        jenkins_connection.return_value = JenkinsMock()

        with self.assertRaises(AnsibleExitJson) as return_json:
            with set_module_args(
                {
                    "glob": "jobs_name_one",
                    "color": "red",
                    "user": "user",
                    "token": "token",
                }
            ):
                jenkins_job_info.main()

        self.assertEqual(return_json.exception.args[0]["jobs"], [])

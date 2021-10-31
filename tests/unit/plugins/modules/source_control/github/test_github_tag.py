from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.general.plugins.modules.source_control.github import github_tag
from ansible_collections.community.general.tests.unit.compat import unittest
from ansible_collections.community.general.tests.unit.compat.mock import patch
from ansible_collections.community.general.tests.unit.plugins.modules.utils import AnsibleExitJson, AnsibleFailJson, ModuleTestCase, set_module_args


class TestGithubTag(ModuleTestCase):
    def test_mutually_exclusive(self):
        with self.assertRaises(AnsibleFailJson) as exec_info:
            set_module_args({
                "username": "testusername",
                "password": "testpassword",
                "token": "abcde12345",
                "organization": "MyOrganization",
                "repo": "myrepo",
                "branch": "main",
                "tag": "1.0.0",
                "tagger": {
                    "name": "Test User",
                    "email": "test.user@test.com"
                },
                "message": "Test tag",
            })
            github_tag.main()

        self.assertEqual(
            exec_info.exception.args[0]['msg'],
            'parameters are mutually exclusive: password|token',
        )

    def test_missing_dependency(self):
        with self.assertRaises(AnsibleFailJson) as exec_info:
            github_tag.HAS_GITHUB3_PACKAGE = False
            set_module_args({
                "token": "mytoken",
                "organization": "MyOrganization",
                "repo": "myrepo",
                "branch": "main",
                "tag": "1.0.0",
                "tagger": {
                    "name": "Test User",
                    "email": "test.user@test.com"
                },
                "message": "Test tag",
                "url": "https://api.github.com"
            })
            github_tag.main()

        self.assertIn("Failed to import the required Python library (github3.py >= 1.0.0)", exec_info.exception.args[0]['msg'])

    @patch.object(github_tag, 'create_tag')
    @patch.object(github_tag, 'get_repo')
    @patch.object(github_tag, 'authenticate')
    def test_create_tag(self, mock_authenticate, mock_get_repo, mock_create_tag):
        mock_get_repo.return_value.commit = "15a694d58f849a99f14b1cd9f62a92d8fbb85b6e"
        mock_create_tag.return_value.tag = "1.0.0"
        with self.assertRaises(AnsibleExitJson) as exec_info:
            set_module_args({
                "token": "mytoken",
                "organization": "MyOrganization",
                "repo": "myrepo",
                "branch": "main",
                "tag": "1.0.0",
                "tagger": {
                    "name": "Test User",
                    "email": "test.user@test.com"
                },
                "message": "Test tag",
                "url": "https://api.github.com"
            })
            github_tag.main()

        self.assertEqual(exec_info.exception.args[0]['changed'], True)
        self.assertEqual(exec_info.exception.args[0]['tag'], "1.0.0")
        self.assertEqual(exec_info.exception.args[0]['branch'], "main")

    @patch.object(github_tag, 'create_tag')
    @patch.object(github_tag, 'get_repo')
    @patch.object(github_tag, 'authenticate')
    def test_create_tag_already_exists(self, mock_authenticate, mock_get_repo, mock_create_tag):
        mock_get_repo.return_value = False
        mock_create_tag.return_value.tag = "1.0.0"
        with self.assertRaises(AnsibleExitJson) as exec_info:
            set_module_args({
                "token": "mytoken",
                "organization": "MyOrganization",
                "repo": "myrepo",
                "branch": "main",
                "tag": "1.0.0",
                "tagger": {
                    "name": "Test User",
                    "email": "test.user@test.com"
                },
                "message": "Test tag",
                "url": "https://api.github.com"
            })
            github_tag.main()

        self.assertEqual(exec_info.exception.args[0]['changed'], False)


if __name__ == "__main__":
    unittest.main()

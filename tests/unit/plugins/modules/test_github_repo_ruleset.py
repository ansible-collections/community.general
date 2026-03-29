# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import unittest

from ansible_collections.community.general.plugins.modules import github_repo_ruleset

# These tests validate the helper functions directly since the module uses
# fetch_url which requires an AnsibleModule instance for HTTP calls.


class TestGithubRepoRuleset(unittest.TestCase):
    def test_build_ruleset_body_minimal(self):
        params = {
            "name": "my-ruleset",
            "target": "branch",
            "enforcement": "active",
            "conditions": None,
            "bypass_actors": [],
            "rules": [],
        }
        body = github_repo_ruleset.build_ruleset_body(params)
        self.assertEqual(body["name"], "my-ruleset")
        self.assertEqual(body["target"], "branch")
        self.assertEqual(body["enforcement"], "active")
        self.assertEqual(body["conditions"], {"ref_name": {"include": ["~ALL"], "exclude": []}})
        self.assertEqual(body["bypass_actors"], [])
        self.assertEqual(body["rules"], [])

    def test_build_ruleset_body_with_conditions(self):
        params = {
            "name": "main-protection",
            "target": "branch",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
            "bypass_actors": [{"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}],
            "rules": [{"type": "pull_request", "parameters": {"required_approving_review_count": 2}}],
        }
        body = github_repo_ruleset.build_ruleset_body(params)
        self.assertEqual(body["conditions"]["ref_name"]["include"], ["~DEFAULT_BRANCH"])
        self.assertEqual(len(body["bypass_actors"]), 1)
        self.assertEqual(body["bypass_actors"][0]["actor_id"], 5)
        self.assertEqual(len(body["rules"]), 1)
        self.assertEqual(body["rules"][0]["type"], "pull_request")

    def test_normalize_for_comparison_sorting(self):
        data1 = {
            "name": "test",
            "target": "branch",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["~ALL"], "exclude": []}},
            "bypass_actors": [
                {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"},
                {"actor_id": 1, "actor_type": "Team", "bypass_mode": "pull_request"},
            ],
            "rules": [
                {"type": "required_linear_history"},
                {"type": "deletion"},
            ],
        }
        data2 = {
            "name": "test",
            "target": "branch",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["~ALL"], "exclude": []}},
            "bypass_actors": [
                {"actor_id": 1, "actor_type": "Team", "bypass_mode": "pull_request"},
                {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"},
            ],
            "rules": [
                {"type": "deletion"},
                {"type": "required_linear_history"},
            ],
        }
        norm1 = github_repo_ruleset.normalize_for_comparison(data1)
        norm2 = github_repo_ruleset.normalize_for_comparison(data2)
        self.assertEqual(norm1, norm2)

    def test_normalize_for_comparison_different(self):
        data1 = {
            "name": "test",
            "target": "branch",
            "enforcement": "active",
            "conditions": {"ref_name": {"include": ["~ALL"], "exclude": []}},
            "bypass_actors": [],
            "rules": [{"type": "deletion"}],
        }
        data2 = {
            "name": "test",
            "target": "branch",
            "enforcement": "disabled",
            "conditions": {"ref_name": {"include": ["~ALL"], "exclude": []}},
            "bypass_actors": [],
            "rules": [{"type": "deletion"}],
        }
        norm1 = github_repo_ruleset.normalize_for_comparison(data1)
        norm2 = github_repo_ruleset.normalize_for_comparison(data2)
        self.assertNotEqual(norm1, norm2)

    def test_build_ruleset_body_tag_target(self):
        params = {
            "name": "tag-ruleset",
            "target": "tag",
            "enforcement": "evaluate",
            "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
            "bypass_actors": [],
            "rules": [{"type": "creation"}, {"type": "deletion"}],
        }
        body = github_repo_ruleset.build_ruleset_body(params)
        self.assertEqual(body["target"], "tag")
        self.assertEqual(body["enforcement"], "evaluate")
        self.assertEqual(len(body["rules"]), 2)

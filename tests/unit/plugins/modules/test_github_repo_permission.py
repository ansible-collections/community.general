# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import unittest
import sys
try:  # Python 3
    from unittest.mock import patch
except Exception:  # Python 2 fallback
    try:
        from mock import patch  # type: ignore
    except Exception:
        patch = None  # type: ignore
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (  # type: ignore
    ModuleTestCase,
    set_module_args,
    AnsibleExitJson,
)

from ansible_collections.community.general.plugins.modules import github_repo_permission as mod

# Skip the entire module on Python 2.7 if 'mock' isn't available
if sys.version_info[0] < 3 and patch is None:  # type: ignore
    import pytest  # type: ignore
    pytest.skip("mock not available on Python 2.7 test env", allow_module_level=True)


def _resp(status=200, body=None, extra_info=None):
    class Dummy:
        def __init__(self, data):
            self._data = data

        def read(self):
            return self._data

    data = b""
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    info = {"status": status}
    if extra_info:
        info.update(extra_info)
    return Dummy(data), info


class TestGithubRepoPermission(ModuleTestCase):
    def setUp(self):
        super(TestGithubRepoPermission, self).setUp()

    def test_team_present_idempotent_builtin(self):
        # Team already has push -> desired push => changed False
        def side_effect(module, url, **kwargs):
            method = kwargs.get('method', 'GET').upper()
            if method == 'GET' and url.endswith('/orgs/myorg/teams/backend/repos/myorg/myrepo'):
                return _resp(200, {"permission": "push"})
            # Should not PUT when idempotent
            raise AssertionError("Unexpected HTTP call: %s %s" % (method, url))

        with set_module_args({
            'access_token': 't',
            'repository': 'myorg/myrepo',
            'team_slug': 'backend',
            'permission': 'push',
            'state': 'present',
            'api_url': 'https://api.github.com',
        }):
            with patch.object(mod, 'fetch_url', side_effect=side_effect):
                with self.assertRaises(AnsibleExitJson) as ctx:
                    mod.main()

        result = ctx.exception.args[0]
        assert result['changed'] is False
        assert result['result']['permission'] == 'push'

    def test_team_present_update_builtin(self):
        calls = []

        def side_effect(module, url, **kwargs):
            method = kwargs.get('method', 'GET').upper()
            calls.append((method, url))
            # First GET shows current pull
            if method == 'GET' and url.endswith('/orgs/myorg/teams/backend/repos/myorg/myrepo'):
                # Return pull first, then push after PUT
                if any(m == 'PUT' for m, url_value in calls):
                    return _resp(200, {"permission": "push"})
                return _resp(200, {"permission": "pull"})
            if method == 'PUT' and url.endswith('/orgs/myorg/teams/backend/repos/myorg/myrepo'):
                body = json.loads(kwargs.get('data'))
                assert body == {'permission': 'push'}
                return _resp(204, {})
            raise AssertionError("Unexpected HTTP call: %s %s" % (method, url))

        with set_module_args({
            'access_token': 't',
            'repository': 'myorg/myrepo',
            'team_slug': 'backend',
            'permission': 'push',
            'state': 'present',
            'api_url': 'https://api.github.com',
        }):
            with patch.object(mod, 'fetch_url', side_effect=side_effect):
                with self.assertRaises(AnsibleExitJson) as ctx:
                    mod.main()

        result = ctx.exception.args[0]
        assert result['changed'] is True
        assert result['result']['permission'] == 'push'

    def test_team_absent_deletes(self):
        def side_effect(module, url, **kwargs):
            method = kwargs.get('method', 'GET').upper()
            if method == 'GET' and url.endswith('/orgs/myorg/teams/backend/repos/myorg/myrepo'):
                return _resp(200, {"permission": "triage"})
            if method == 'DELETE' and url.endswith('/orgs/myorg/teams/backend/repos/myorg/myrepo'):
                return _resp(204, {})
            raise AssertionError("Unexpected HTTP call: %s %s" % (method, url))

        with set_module_args({
            'access_token': 't',
            'repository': 'myorg/myrepo',
            'team_slug': 'backend',
            'state': 'absent',
            'api_url': 'https://api.github.com',
        }):
            with patch.object(mod, 'fetch_url', side_effect=side_effect):
                with self.assertRaises(AnsibleExitJson) as ctx:
                    mod.main()

        result = ctx.exception.args[0]
        assert result['changed'] is True
        assert result['result']['permission'] is None

    def test_team_present_custom_role_first_grant(self):
        # Custom role 'Maintainer' exists; no prior access; after PUT, presence is used for verification
        calls = {"teams_list_called": 0}

        def side_effect(module, url, **kwargs):
            method = kwargs.get('method', 'GET').upper()
            # roles endpoint
            if method == 'GET' and url.endswith('/orgs/myorg/custom-repository-roles'):
                return _resp(200, {"roles": [{"name": "Maintainer"}]})
            # team-repo endpoint: before PUT 404 (no access yet)
            if method == 'GET' and url.endswith('/orgs/myorg/teams/backend/repos/myorg/myrepo'):
                return _resp(404, {"message": "Not Found"})
            # repo teams list: empty before PUT, then contains team
            if method == 'GET' and url.endswith('/repos/myorg/myrepo/teams'):
                calls["teams_list_called"] += 1
                if calls["teams_list_called"] <= 1:
                    return _resp(200, [])
                return _resp(200, [{"slug": "backend", "permission": "push"}])
            if method == 'PUT' and url.endswith('/orgs/myorg/teams/backend/repos/myorg/myrepo'):
                body = json.loads(kwargs.get('data'))
                assert body == {'permission': 'Maintainer'}
                return _resp(204, {})
            raise AssertionError("Unexpected HTTP call: %s %s" % (method, url))

        with set_module_args({
            'access_token': 't',
            'repository': 'myorg/myrepo',
            'team_slug': 'backend',
            'permission': 'Maintainer',
            'state': 'present',
            'api_url': 'https://api.github.com',
        }):
            with patch.object(mod, 'fetch_url', side_effect=side_effect):
                with self.assertRaises(AnsibleExitJson) as ctx:
                    mod.main()
        result = ctx.exception.args[0]
        assert result['changed'] is True
        assert result['result']['permission'] == 'Maintainer'

    def test_user_present_idempotent_read_synonym(self):
        # User has permission 'read' -> normalized to 'pull'; desired 'pull' => idempotent
        def side_effect(module, url, **kwargs):
            method = kwargs.get('method', 'GET').upper()
            if method == 'GET' and url.endswith('/repos/myorg/myrepo/collaborators/alice/permission'):
                return _resp(200, {"permission": "read"})
            raise AssertionError("Unexpected HTTP call: %s %s" % (method, url))

        with set_module_args({
            'access_token': 't',
            'repository': 'myorg/myrepo',
            'username': 'alice',
            'permission': 'pull',
            'state': 'present',
            'api_url': 'https://api.github.com',
        }):
            with patch.object(mod, 'fetch_url', side_effect=side_effect):
                with self.assertRaises(AnsibleExitJson) as ctx:
                    mod.main()

        result = ctx.exception.args[0]
        assert result['changed'] is False
        assert result['result']['permission'] == 'pull'

    def test_user_absent_when_not_collaborator(self):
        def side_effect(module, url, **kwargs):
            method = kwargs.get('method', 'GET').upper()
            if method == 'GET' and url.endswith('/repos/myorg/myrepo/collaborators/alice/permission'):
                return _resp(404, {"message": "Not Found"})
            raise AssertionError("Unexpected HTTP call: %s %s" % (method, url))

        with set_module_args({
            'access_token': 't',
            'repository': 'myorg/myrepo',
            'username': 'alice',
            'state': 'absent',
            'api_url': 'https://api.github.com',
        }):
            with patch.object(mod, 'fetch_url', side_effect=side_effect):
                with self.assertRaises(AnsibleExitJson) as ctx:
                    mod.main()

        result = ctx.exception.args[0]
        assert result['changed'] is False

    def test_user_present_update_to_push(self):
        calls = []

        def side_effect(module, url, **kwargs):
            method = kwargs.get('method', 'GET').upper()
            calls.append((method, url))
            if method == 'GET' and url.endswith('/repos/myorg/myrepo/collaborators/bob/permission'):
                # Before PUT return read, after PUT return write
                if any(m == 'PUT' for m, url_value in calls):
                    return _resp(200, {"permission": "write"})
                return _resp(200, {"permission": "read"})
            if method == 'PUT' and url.endswith('/repos/myorg/myrepo/collaborators/bob'):
                body = json.loads(kwargs.get('data'))
                assert body == {'permission': 'push'}
                return _resp(201, {})
            raise AssertionError("Unexpected HTTP call: %s %s" % (method, url))

        with set_module_args({
            'access_token': 't',
            'repository': 'myorg/myrepo',
            'username': 'bob',
            'permission': 'push',
            'state': 'present',
            'api_url': 'https://api.github.com',
        }):
            with patch.object(mod, 'fetch_url', side_effect=side_effect):
                with self.assertRaises(AnsibleExitJson) as ctx:
                    mod.main()

        result = ctx.exception.args[0]
        assert result['changed'] is True
        assert result['result']['permission'] == 'push'


if __name__ == "__main__":
    unittest.main()

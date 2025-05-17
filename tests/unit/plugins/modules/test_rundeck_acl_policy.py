# -*- coding: utf-8 -*-

# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
from ansible_collections.community.general.plugins.modules import rundeck_acl_policy
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    set_module_args,
    AnsibleExitJson,
    exit_json,
    fail_json
)


@pytest.fixture(autouse=True)
def module():
    with patch.multiple(
        "ansible.module_utils.basic.AnsibleModule",
        exit_json=exit_json,
        fail_json=fail_json,
    ):
        yield


# define our two table entries: system ACL vs. project ACL
PROJECT_TABLE = [
    (None, "system/acl"),
    ("test_project", "project/test_project/acl"),
]


@pytest.mark.parametrize("project, prefix", PROJECT_TABLE)
@patch.object(rundeck_acl_policy, 'api_request')
def test_acl_create(api_request_mock, project, prefix):
    """Test creating a new ACL, both system-level and project-level."""
    name = "my_policy"
    policy = "test_policy_yaml"
    # simulate: GET→404, POST→201, final GET→200
    api_request_mock.side_effect = [
        (None, {'status': 404}),
        (None, {'status': 201}),
        ({"contents": policy}, {'status': 200}),
    ]
    args = {
        'name': name,
        'url': "https://rundeck.example.org",
        'api_token': "mytoken",
        'policy': policy,
    }
    if project:
        args['project'] = project

    with pytest.raises(AnsibleExitJson):
        with set_module_args(args):
            rundeck_acl_policy.main()

    # should have done GET → POST → GET
    assert api_request_mock.call_count == 3
    args, kwargs = api_request_mock.call_args_list[1]
    assert kwargs['endpoint'] == "%s/%s.aclpolicy" % (prefix, name)
    assert kwargs['method'] == 'POST'


@pytest.mark.parametrize("project, prefix", PROJECT_TABLE)
@patch.object(rundeck_acl_policy, 'api_request')
def test_acl_unchanged(api_request_mock, project, prefix):
    """Test no-op when existing ACL contents match the desired policy."""
    name = "unchanged_policy"
    policy = "same_policy_yaml"
    # first GET returns matching contents
    api_request_mock.return_value = ({"contents": policy}, {'status': 200})

    args = {
        'name': name,
        'url': "https://rundeck.example.org",
        'api_token': "mytoken",
        'policy': policy,
    }
    if project:
        args['project'] = project

    with pytest.raises(AnsibleExitJson):
        with set_module_args(args):
            rundeck_acl_policy.main()

    # only a single GET
    assert api_request_mock.call_count == 1
    args, kwargs = api_request_mock.call_args
    assert kwargs['endpoint'] == "%s/%s.aclpolicy" % (prefix, name)
    # default method is GET
    assert kwargs.get('method', 'GET') == 'GET'


@pytest.mark.parametrize("project, prefix", PROJECT_TABLE)
@patch.object(rundeck_acl_policy, 'api_request')
def test_acl_remove(api_request_mock, project, prefix):
    """Test removing an existing ACL, both system- and project-level."""
    name = "remove_me"
    # GET finds it, DELETE removes it
    api_request_mock.side_effect = [
        ({"contents": "old_yaml"}, {'status': 200}),
        (None, {'status': 204}),
    ]

    args = {
        'name': name,
        'url': "https://rundeck.example.org",
        'api_token': "mytoken",
        'state': 'absent',
    }
    if project:
        args['project'] = project

    with pytest.raises(AnsibleExitJson):
        with set_module_args(args):
            rundeck_acl_policy.main()

    # GET → DELETE
    assert api_request_mock.call_count == 2
    args, kwargs = api_request_mock.call_args_list[1]
    assert kwargs['endpoint'] == "%s/%s.aclpolicy" % (prefix, name)
    assert kwargs['method'] == 'DELETE'


@pytest.mark.parametrize("project, prefix", PROJECT_TABLE)
@patch.object(rundeck_acl_policy, 'api_request')
def test_acl_remove_nonexistent(api_request_mock, project, prefix):
    """Test removing a non-existent ACL results in no change."""
    name = "not_there"
    # GET returns 404
    api_request_mock.return_value = (None, {'status': 404})

    args = {
        'name': name,
        'url': "https://rundeck.example.org",
        'api_token': "mytoken",
        'state': 'absent',
    }
    if project:
        args['project'] = project

    with pytest.raises(AnsibleExitJson):
        with set_module_args(args):
            rundeck_acl_policy.main()

    # only the initial GET
    assert api_request_mock.call_count == 1
    args, kwargs = api_request_mock.call_args
    assert kwargs['endpoint'] == "%s/%s.aclpolicy" % (prefix, name)
    assert kwargs.get('method', 'GET') == 'GET'

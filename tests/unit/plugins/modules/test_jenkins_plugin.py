# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from io import BytesIO
import json
from collections import OrderedDict

from ansible_collections.community.general.plugins.modules.jenkins_plugin import JenkinsPlugin
from ansible.module_utils.six.moves.collections_abc import Mapping
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import (
    MagicMock,
    patch,
)
from ansible.module_utils.urls import basic_auth_header


def pass_function(*args, **kwargs):
    pass


GITHUB_DATA = {"url": u'https://api.github.com/repos/ansible/ansible',
               "response": b"""
{
  "id": 3638964,
  "name": "ansible",
  "full_name": "ansible/ansible",
  "owner": {
    "login": "ansible",
    "id": 1507452,
    "avatar_url": "https://avatars2.githubusercontent.com/u/1507452?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/ansible",
    "html_url": "https://github.com/ansible",
    "followers_url": "https://api.github.com/users/ansible/followers",
    "following_url": "https://api.github.com/users/ansible/following{/other_user}",
    "gists_url": "https://api.github.com/users/ansible/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/ansible/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/ansible/subscriptions",
    "organizations_url": "https://api.github.com/users/ansible/orgs",
    "repos_url": "https://api.github.com/users/ansible/repos",
    "events_url": "https://api.github.com/users/ansible/events{/privacy}",
    "received_events_url": "https://api.github.com/users/ansible/received_events",
    "type": "Organization",
    "site_admin": false
  },
  "private": false,
  "html_url": "https://github.com/ansible/ansible",
  "description": "Ansible is a radically simple IT automation platform that makes your applications and systems easier to deploy.",
  "fork": false,
  "url": "https://api.github.com/repos/ansible/ansible",
  "forks_url": "https://api.github.com/repos/ansible/ansible/forks",
  "keys_url": "https://api.github.com/repos/ansible/ansible/keys{/key_id}",
  "collaborators_url": "https://api.github.com/repos/ansible/ansible/collaborators{/collaborator}",
  "teams_url": "https://api.github.com/repos/ansible/ansible/teams",
  "hooks_url": "https://api.github.com/repos/ansible/ansible/hooks",
  "issue_events_url": "https://api.github.com/repos/ansible/ansible/issues/events{/number}",
  "events_url": "https://api.github.com/repos/ansible/ansible/events",
  "assignees_url": "https://api.github.com/repos/ansible/ansible/assignees{/user}",
  "branches_url": "https://api.github.com/repos/ansible/ansible/branches{/branch}",
  "tags_url": "https://api.github.com/repos/ansible/ansible/tags",
  "blobs_url": "https://api.github.com/repos/ansible/ansible/git/blobs{/sha}",
  "git_tags_url": "https://api.github.com/repos/ansible/ansible/git/tags{/sha}",
  "git_refs_url": "https://api.github.com/repos/ansible/ansible/git/refs{/sha}",
  "trees_url": "https://api.github.com/repos/ansible/ansible/git/trees{/sha}",
  "statuses_url": "https://api.github.com/repos/ansible/ansible/statuses/{sha}",
  "languages_url": "https://api.github.com/repos/ansible/ansible/languages",
  "stargazers_url": "https://api.github.com/repos/ansible/ansible/stargazers",
  "contributors_url": "https://api.github.com/repos/ansible/ansible/contributors",
  "subscribers_url": "https://api.github.com/repos/ansible/ansible/subscribers",
  "subscription_url": "https://api.github.com/repos/ansible/ansible/subscription",
  "commits_url": "https://api.github.com/repos/ansible/ansible/commits{/sha}",
  "git_commits_url": "https://api.github.com/repos/ansible/ansible/git/commits{/sha}",
  "comments_url": "https://api.github.com/repos/ansible/ansible/comments{/number}",
  "issue_comment_url": "https://api.github.com/repos/ansible/ansible/issues/comments{/number}",
  "contents_url": "https://api.github.com/repos/ansible/ansible/contents/{+path}",
  "compare_url": "https://api.github.com/repos/ansible/ansible/compare/{base}...{head}",
  "merges_url": "https://api.github.com/repos/ansible/ansible/merges",
  "archive_url": "https://api.github.com/repos/ansible/ansible/{archive_format}{/ref}",
  "downloads_url": "https://api.github.com/repos/ansible/ansible/downloads",
  "issues_url": "https://api.github.com/repos/ansible/ansible/issues{/number}",
  "pulls_url": "https://api.github.com/repos/ansible/ansible/pulls{/number}",
  "milestones_url": "https://api.github.com/repos/ansible/ansible/milestones{/number}",
  "notifications_url": "https://api.github.com/repos/ansible/ansible/notifications{?since,all,participating}",
  "labels_url": "https://api.github.com/repos/ansible/ansible/labels{/name}",
  "releases_url": "https://api.github.com/repos/ansible/ansible/releases{/id}",
  "deployments_url": "https://api.github.com/repos/ansible/ansible/deployments",
  "created_at": "2012-03-06T14:58:02Z",
  "updated_at": "2017-09-19T18:10:54Z",
  "pushed_at": "2017-09-19T18:04:51Z",
  "git_url": "git://github.com/ansible/ansible.git",
  "ssh_url": "git@github.com:ansible/ansible.git",
  "clone_url": "https://github.com/ansible/ansible.git",
  "svn_url": "https://github.com/ansible/ansible",
  "homepage": "https://www.ansible.com/",
  "size": 91174,
  "stargazers_count": 25552,
  "watchers_count": 25552,
  "language": "Python",
  "has_issues": true,
  "has_projects": true,
  "has_downloads": true,
  "has_wiki": false,
  "has_pages": false,
  "forks_count": 8893,
  "mirror_url": null,
  "open_issues_count": 4283,
  "forks": 8893,
  "open_issues": 4283,
  "watchers": 25552,
  "default_branch": "devel",
  "organization": {
    "login": "ansible",
    "id": 1507452,
    "avatar_url": "https://avatars2.githubusercontent.com/u/1507452?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/ansible",
    "html_url": "https://github.com/ansible",
    "followers_url": "https://api.github.com/users/ansible/followers",
    "following_url": "https://api.github.com/users/ansible/following{/other_user}",
    "gists_url": "https://api.github.com/users/ansible/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/ansible/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/ansible/subscriptions",
    "organizations_url": "https://api.github.com/users/ansible/orgs",
    "repos_url": "https://api.github.com/users/ansible/repos",
    "events_url": "https://api.github.com/users/ansible/events{/privacy}",
    "received_events_url": "https://api.github.com/users/ansible/received_events",
    "type": "Organization",
    "site_admin": false
  },
  "network_count": 8893,
  "subscribers_count": 1733
}
"""
               }


def test__get_json_data(mocker):
    "test the json conversion of _get_url_data"

    timeout = 30
    params = {
        'url': GITHUB_DATA['url'],
        'timeout': timeout
    }
    module = mocker.Mock()
    module.params = params

    JenkinsPlugin._csrf_enabled = pass_function
    JenkinsPlugin._get_installed_plugins = pass_function
    JenkinsPlugin._get_url_data = mocker.Mock()
    JenkinsPlugin._get_url_data.return_value = BytesIO(GITHUB_DATA['response'])
    jenkins_plugin = JenkinsPlugin(module)

    json_data = jenkins_plugin._get_json_data(
        "{url}".format(url=GITHUB_DATA['url']),
        'CSRF')

    assert isinstance(json_data, Mapping)


def test__new_fallback_urls(mocker):
    "test generation of new fallback URLs"

    params = {
        "url": "http://fake.jenkins.server",
        "timeout": 30,
        "name": "test-plugin",
        "version": "1.2.3",
        "updates_url": ["https://some.base.url"],
        "latest_plugins_url_segments": ["test_latest"],
        "versioned_plugins_url_segments": ["ansible", "versioned_plugins"],
        "update_json_url_segment": ["unreachable", "updates/update-center.json"],
    }
    module = mocker.Mock()
    module.params = params

    JenkinsPlugin._csrf_enabled = pass_function
    JenkinsPlugin._get_installed_plugins = pass_function

    jenkins_plugin = JenkinsPlugin(module)

    latest_urls = jenkins_plugin._get_latest_plugin_urls()
    assert isInList(latest_urls, "https://some.base.url/test_latest/test-plugin.hpi")
    versioned_urls = jenkins_plugin._get_versioned_plugin_urls()
    assert isInList(versioned_urls, "https://some.base.url/versioned_plugins/test-plugin/1.2.3/test-plugin.hpi")
    json_urls = jenkins_plugin._get_update_center_urls()
    assert isInList(json_urls, "https://some.base.url/updates/update-center.json")


def isInList(l, i):
    print("checking if %s in %s" % (i, l))
    for item in l:
        if item == i:
            return True
    return False


@patch("ansible_collections.community.general.plugins.modules.jenkins_plugin.fetch_url")
def test__get_latest_compatible_plugin_version(fetch_mock, mocker):
    "test the latest compatible plugin version retrieval"

    params = {
        "url": "http://fake.jenkins.server",
        "timeout": 30,
        "name": "git",
        "version": "latest",
        "updates_url": ["https://some.base.url"],
        "plugin_versions_url_segment": ["plugin-versions.json"],
        "latest_plugins_url_segments": ["test_latest"],
        "jenkins_home": "/var/lib/jenkins",
    }
    module = mocker.Mock()
    module.params = params

    jenkins_info = {"x-jenkins": "2.263.1"}
    jenkins_response = MagicMock()
    jenkins_response.read.return_value = b"{}"

    plugin_data = {
        "plugins": {
            "git": OrderedDict([
                ("4.8.2", {"requiredCore": "2.263.1"}),
                ("4.8.3", {"requiredCore": "2.263.1"}),
                ("4.9.0", {"requiredCore": "2.289.1"}),
                ("4.9.1", {"requiredCore": "2.289.1"}),
            ])
        }
    }
    plugin_versions_response = MagicMock()
    plugin_versions_response.read.return_value = json.dumps(plugin_data).encode("utf-8")
    plugin_versions_info = {"status": 200}

    def fetch_url_side_effect(module, url, **kwargs):
        if "plugin-versions.json" in url:
            return (plugin_versions_response, plugin_versions_info)
        else:
            return (jenkins_response, jenkins_info)

    fetch_mock.side_effect = fetch_url_side_effect

    JenkinsPlugin._csrf_enabled = lambda self: False
    JenkinsPlugin._get_installed_plugins = lambda self: None

    jenkins_plugin = JenkinsPlugin(module)
    latest_version = jenkins_plugin._get_latest_compatible_plugin_version()
    assert latest_version == '4.8.3'


@patch("ansible_collections.community.general.plugins.modules.jenkins_plugin.fetch_url")
def test__get_urls_data_sets_correct_headers(fetch_mock, mocker):
    params = {
        "url": "http://jenkins.example.com",
        "timeout": 30,
        "name": "git",
        "jenkins_home": "/var/lib/jenkins",
        "updates_url": ["http://updates.example.com"],
        "latest_plugins_url_segments": ["latest"],
        "update_json_url_segment": ["update-center.json"],
        "versioned_plugins_url_segments": ["plugins"],
        "url_username": "jenkins_user",
        "url_password": "jenkins_pass",
        "updates_url_username": "update_user",
        "updates_url_password": "update_pass",
    }
    module = mocker.Mock()
    module.params = params

    dummy_response = MagicMock()
    fetch_mock.return_value = (dummy_response, {"status": 200})

    JenkinsPlugin._csrf_enabled = lambda self: False
    JenkinsPlugin._get_installed_plugins = lambda self: None

    jp = JenkinsPlugin(module)

    update_url = "http://updates.example.com/plugin-versions.json"
    jp._get_urls_data([update_url])

    jenkins_url = "http://jenkins.example.com/some-endpoint"
    jp._get_urls_data([jenkins_url])

    calls = fetch_mock.call_args_list

    dummy, kwargs_2 = calls[1]
    jenkins_auth = basic_auth_header("jenkins_user", "jenkins_pass")
    assert kwargs_2["headers"]["Authorization"] == jenkins_auth

    dummy, kwargs_1 = calls[0]
    updates_auth = basic_auth_header("update_user", "update_pass")
    assert kwargs_1["headers"]["Authorization"] == updates_auth

# -*- coding: utf-8 -*-
# Author: Alexei Znamensky (russoz@gmail.com)
# Largely adapted from test_redhat_subscription by
# Jiri Hnidek (jhnidek@redhat.com)
#
# Copyright (c) Alexei Znamensky (russoz@gmail.com)
# Copyright (c) Jiri Hnidek (jhnidek@redhat.com)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from ansible_collections.community.general.plugins.modules import puppet

import pytest

TESTED_MODULE = puppet.__name__


@pytest.fixture
def patch_get_bin_path(mocker):
    """
    Function used for mocking AnsibleModule.get_bin_path
    """
    def mockie(self, path, *args, **kwargs):
        return "/testbin/{0}".format(path)
    mocker.patch("ansible.module_utils.basic.AnsibleModule.get_bin_path", mockie)


TEST_CASES = [
    [
        {},
        {
            "id": "puppet_agent_plain",
            "run_command.calls": [
                (
                    ["/testbin/puppet", "config", "print", "agent_disabled_lockfile"],
                    {"environ_update": {"LANGUAGE": "C", "LC_ALL": "C"}, "check_rc": False},
                    (0, "blah, anything", "",),  # output rc, out, err
                ),
                (
                    [
                        "/testbin/timeout", "-s", "9", "30m", "/testbin/puppet", "agent", "--onetime", "--no-daemonize",
                        "--no-usecacheonfailure", "--no-splay", "--detailed-exitcodes", "--verbose", "--color", "0"
                    ],
                    {"environ_update": {"LANGUAGE": "C", "LC_ALL": "C"}, "check_rc": False},
                    (0, "", "",),  # output rc, out, err
                ),
            ],
            "changed": False,
        }
    ],
    [
        {
            "certname": "potatobox"
        },
        {
            "id": "puppet_agent_certname",
            "run_command.calls": [
                (
                    ["/testbin/puppet", "config", "print", "agent_disabled_lockfile"],
                    {"environ_update": {"LANGUAGE": "C", "LC_ALL": "C"}, "check_rc": False},
                    (0, "blah, anything", "",),  # output rc, out, err
                ),
                (
                    [
                        "/testbin/timeout", "-s", "9", "30m", "/testbin/puppet", "agent", "--onetime", "--no-daemonize",
                        "--no-usecacheonfailure", "--no-splay", "--detailed-exitcodes", "--verbose", "--color", "0", "--certname=potatobox"
                    ],
                    {"environ_update": {"LANGUAGE": "C", "LC_ALL": "C"}, "check_rc": False},
                    (0, "", "",),  # output rc, out, err
                ),
            ],
            "changed": False,
        }
    ],
    [
        {
            "tags": ["a", "b", "c"]
        },
        {
            "id": "puppet_agent_tags_abc",
            "run_command.calls": [
                (
                    ["/testbin/puppet", "config", "print", "agent_disabled_lockfile"],
                    {"environ_update": {"LANGUAGE": "C", "LC_ALL": "C"}, "check_rc": False},
                    (0, "blah, anything", "",),  # output rc, out, err
                ),
                (
                    [
                        "/testbin/timeout", "-s", "9", "30m", "/testbin/puppet", "agent", "--onetime", "--no-daemonize",
                        "--no-usecacheonfailure", "--no-splay", "--detailed-exitcodes", "--verbose", "--color", "0", "--tags", "a,b,c"
                    ],
                    {"environ_update": {"LANGUAGE": "C", "LC_ALL": "C"}, "check_rc": False},
                    (0, "", "",),  # output rc, out, err
                ),
            ],
            "changed": False,
        }
    ],
    [
        {
            "skip_tags": ["d", "e", "f"]
        },
        {
            "id": "puppet_agent_skip_tags_def",
            "run_command.calls": [
                (
                    ["/testbin/puppet", "config", "print", "agent_disabled_lockfile"],
                    {"environ_update": {"LANGUAGE": "C", "LC_ALL": "C"}, "check_rc": False},
                    (0, "blah, anything", "",),  # output rc, out, err
                ),
                (
                    [
                        "/testbin/timeout", "-s", "9", "30m", "/testbin/puppet", "agent", "--onetime", "--no-daemonize",
                        "--no-usecacheonfailure", "--no-splay", "--detailed-exitcodes", "--verbose", "--color", "0", "--skip_tags", "d,e,f"
                    ],
                    {"environ_update": {"LANGUAGE": "C", "LC_ALL": "C"}, "check_rc": False},
                    (0, "", "",),  # output rc, out, err
                ),
            ],
            "changed": False,
        }
    ]
]
TEST_CASES_IDS = [item[1]["id"] for item in TEST_CASES]


@pytest.mark.parametrize("patch_ansible_module, testcase",
                         TEST_CASES,
                         ids=TEST_CASES_IDS,
                         indirect=["patch_ansible_module"])
@pytest.mark.usefixtures("patch_ansible_module")
def test_puppet(mocker, capfd, patch_get_bin_path, testcase):
    """
    Run unit tests for test cases listen in TEST_CASES
    """

    # Mock function used for running commands first
    call_results = [item[2] for item in testcase["run_command.calls"]]
    mock_run_command = mocker.patch(
        "ansible.module_utils.basic.AnsibleModule.run_command",
        side_effect=call_results)

    # Try to run test case
    with pytest.raises(SystemExit):
        puppet.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    print("results =\n%s" % results)

    assert mock_run_command.call_count == len(testcase["run_command.calls"])
    if mock_run_command.call_count:
        call_args_list = [(item[0][0], item[1]) for item in mock_run_command.call_args_list]
        expected_call_args_list = [(item[0], item[1]) for item in testcase["run_command.calls"]]
        print("call args list =\n%s" % call_args_list)
        print("expected args list =\n%s" % expected_call_args_list)
        assert call_args_list == expected_call_args_list

    assert results.get("changed", False) == testcase["changed"]
    if "failed" in testcase:
        assert results.get("failed", False) == testcase["failed"]
    if "msg" in testcase:
        assert results.get("msg", "") == testcase["msg"]

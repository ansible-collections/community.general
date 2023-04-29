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

from collections import namedtuple
from ansible_collections.community.general.plugins.modules import puppet

import pytest

TESTED_MODULE = puppet.__name__


ModuleTestCase = namedtuple("ModuleTestCase", ["id", "input", "output", "run_command_calls"])
RunCmdCall = namedtuple("RunCmdCall", ["command", "environ", "rc", "out", "err"])


@pytest.fixture
def patch_get_bin_path(mocker):
    """
    Function used for mocking AnsibleModule.get_bin_path
    """
    def mockie(self, path, *args, **kwargs):
        return "/testbin/{0}".format(path)
    mocker.patch("ansible.module_utils.basic.AnsibleModule.get_bin_path", mockie)


TEST_CASES = [
    ModuleTestCase(
        id="puppet_agent_plain",
        input={},
        output=dict(changed=False),
        run_command_calls=[
            RunCmdCall(
                command=["/testbin/puppet", "config", "print", "agent_disabled_lockfile"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="blah, anything",
                err="",
            ),
            RunCmdCall(
                command=[
                    "/testbin/timeout", "-s", "9", "30m", "/testbin/puppet", "agent", "--onetime", "--no-daemonize",
                    "--no-usecacheonfailure", "--no-splay", "--detailed-exitcodes", "--verbose", "--color", "0"
                ],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="",
                err="",
            ),
        ]
    ),
    ModuleTestCase(
        id="puppet_agent_certname",
        input={"certname": "potatobox"},
        output=dict(changed=False),
        run_command_calls=[
            RunCmdCall(
                command=["/testbin/puppet", "config", "print", "agent_disabled_lockfile"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="blah, anything",
                err="",
            ),
            RunCmdCall(
                command=[
                    "/testbin/timeout", "-s", "9", "30m", "/testbin/puppet", "agent", "--onetime", "--no-daemonize",
                    "--no-usecacheonfailure", "--no-splay", "--detailed-exitcodes", "--verbose", "--color", "0", "--certname=potatobox"
                ],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="",
                err="",
            ),
        ]
    ),
    ModuleTestCase(
        id="puppet_agent_tags_abc",
        input={"tags": ["a", "b", "c"]},
        output=dict(changed=False),
        run_command_calls=[
            RunCmdCall(
                command=["/testbin/puppet", "config", "print", "agent_disabled_lockfile"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="blah, anything",
                err="",
            ),
            RunCmdCall(
                command=[
                    "/testbin/timeout", "-s", "9", "30m", "/testbin/puppet", "agent", "--onetime", "--no-daemonize",
                    "--no-usecacheonfailure", "--no-splay", "--detailed-exitcodes", "--verbose", "--color", "0", "--tags", "a,b,c"
                ],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="",
                err="",
            ),
        ]
    ),
    ModuleTestCase(
        id="puppet_agent_skip_tags_def",
        input={"skip_tags": ["d", "e", "f"]},
        output=dict(changed=False),
        run_command_calls=[
            RunCmdCall(
                command=["/testbin/puppet", "config", "print", "agent_disabled_lockfile"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="blah, anything",
                err="",
            ),
            RunCmdCall(
                command=[
                    "/testbin/timeout", "-s", "9", "30m", "/testbin/puppet", "agent", "--onetime", "--no-daemonize",
                    "--no-usecacheonfailure", "--no-splay", "--detailed-exitcodes", "--verbose", "--color", "0", "--skip_tags", "d,e,f"
                ],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="",
                err="",
            ),
        ]
    ),
    ModuleTestCase(
        id="puppet_agent_noop_false",
        input={"noop": False},
        output=dict(changed=False),
        run_command_calls=[
            RunCmdCall(
                command=["/testbin/puppet", "config", "print", "agent_disabled_lockfile"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="blah, anything",
                err="",
            ),
            RunCmdCall(
                command=[
                    "/testbin/timeout", "-s", "9", "30m", "/testbin/puppet", "agent", "--onetime", "--no-daemonize",
                    "--no-usecacheonfailure", "--no-splay", "--detailed-exitcodes", "--verbose", "--color", "0", "--no-noop"
                ],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="",
                err="",
            ),
        ]
    ),
    ModuleTestCase(
        id="puppet_agent_noop_true",
        input={"noop": True},
        output=dict(changed=False),
        run_command_calls=[
            RunCmdCall(
                command=["/testbin/puppet", "config", "print", "agent_disabled_lockfile"],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="blah, anything",
                err="",
            ),
            RunCmdCall(
                command=[
                    "/testbin/timeout", "-s", "9", "30m", "/testbin/puppet", "agent", "--onetime", "--no-daemonize",
                    "--no-usecacheonfailure", "--no-splay", "--detailed-exitcodes", "--verbose", "--color", "0", "--noop"
                ],
                environ={'environ_update': {'LANGUAGE': 'C', 'LC_ALL': 'C'}, 'check_rc': False},
                rc=0,
                out="",
                err="",
            ),
        ]
    ),
]
TEST_CASES_IDS = [item.id for item in TEST_CASES]


@pytest.mark.parametrize("patch_ansible_module, testcase",
                         [[x.input, x] for x in TEST_CASES],
                         ids=TEST_CASES_IDS,
                         indirect=["patch_ansible_module"])
@pytest.mark.usefixtures("patch_ansible_module")
def test_puppet(mocker, capfd, patch_get_bin_path, testcase):
    """
    Run unit tests for test cases listen in TEST_CASES
    """

    run_cmd_calls = testcase.run_command_calls

    # Mock function used for running commands first
    call_results = [(x.rc, x.out, x.err) for x in run_cmd_calls]
    mock_run_command = mocker.patch(
        "ansible.module_utils.basic.AnsibleModule.run_command",
        side_effect=call_results)

    # Try to run test case
    with pytest.raises(SystemExit):
        puppet.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    print("testcase =\n%s" % str(testcase))
    print("results =\n%s" % results)

    assert mock_run_command.call_count == len(run_cmd_calls)
    if mock_run_command.call_count:
        call_args_list = [(item[0][0], item[1]) for item in mock_run_command.call_args_list]
        expected_call_args_list = [(item.command, item.environ) for item in run_cmd_calls]
        print("call args list =\n%s" % call_args_list)
        print("expected args list =\n%s" % expected_call_args_list)
        assert call_args_list == expected_call_args_list

    assert results.get("changed", False) == testcase.output["changed"]
    if "failed" in testcase:
        assert results.get("failed", False) == testcase.output["failed"]
    if "msg" in testcase:
        assert results.get("msg", "") == testcase.output["msg"]

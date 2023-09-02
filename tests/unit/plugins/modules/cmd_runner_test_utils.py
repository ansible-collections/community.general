# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from collections import namedtuple
from itertools import chain, repeat

import pytest
import yaml


ModuleTestCase = namedtuple("ModuleTestCase", ["id", "input", "output", "run_command_calls", "flags"])
RunCmdCall = namedtuple("RunCmdCall", ["command", "environ", "rc", "out", "err"])


class CmdRunnerTestHelper(object):
    def __init__(self, module_main, test_cases):
        self.module_main = module_main
        self._test_cases = test_cases
        if isinstance(test_cases, (list, tuple)):
            self.testcases = test_cases
        else:
            self.testcases = self._make_test_cases()

    @property
    def cmd_fixture(self):
        @pytest.fixture
        def patch_bin(mocker):
            def mockie(self, path, *args, **kwargs):
                return "/testbin/{0}".format(path)
            mocker.patch('ansible.module_utils.basic.AnsibleModule.get_bin_path', mockie)

        return patch_bin

    def _make_test_cases(self):
        test_cases = yaml.safe_load(self._test_cases)

        results = []
        for tc in test_cases:
            for tc_param in ["input", "output", "flags"]:
                if not tc.get(tc_param):
                    tc[tc_param] = {}
            if tc.get("run_command_calls"):
                tc["run_command_calls"] = [RunCmdCall(**r) for r in tc["run_command_calls"]]
            else:
                tc["run_command_calls"] = []
            results.append(ModuleTestCase(**tc))

        return results

    @property
    def testcases_params(self):
        return [[x.input, x] for x in self.testcases]

    @property
    def testcases_ids(self):
        return [item.id for item in self.testcases]

    def __call__(self, *args, **kwargs):
        return _Context(self, *args, **kwargs)


class _Context(object):
    def __init__(self, helper, testcase, mocker, capfd):
        self.helper = helper
        self.testcase = testcase
        self.mocker = mocker
        self.capfd = capfd

        self.run_cmd_calls = self.testcase.run_command_calls
        self.mock_run_cmd = self._make_mock_run_cmd()

    def _make_mock_run_cmd(self):
        call_results = [(x.rc, x.out, x.err) for x in self.run_cmd_calls]
        error_call_results = (123,
                              "OUT: testcase has not enough run_command calls",
                              "ERR: testcase has not enough run_command calls")
        mock_run_command = self.mocker.patch('ansible.module_utils.basic.AnsibleModule.run_command',
                                             side_effect=chain(call_results, repeat(error_call_results)))
        return mock_run_command

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def _run(self):
        with pytest.raises(SystemExit):
            self.helper.module_main()

        out, err = self.capfd.readouterr()
        results = json.loads(out)

        self.check_results(results)

    def test_flags(self, flag=None):
        flags = self.testcase.flags
        if flag:
            flags = flags.get(flag)
        return flags

    def run(self):
        func = self._run

        test_flags = self.test_flags()
        if test_flags.get("skip"):
            pytest.skip(reason=test_flags["skip"])
        if test_flags.get("xfail"):
            pytest.xfail(reason=test_flags["xfail"])

        func()

    def check_results(self, results):
        print("testcase =\n%s" % str(self.testcase))
        print("results =\n%s" % results)
        if 'exception' in results:
            print("exception = \n%s" % results["exception"])

        for test_result in self.testcase.output:
            assert results[test_result] == self.testcase.output[test_result], \
                "'{0}': '{1}' != '{2}'".format(test_result, results[test_result], self.testcase.output[test_result])

        call_args_list = [(item[0][0], item[1]) for item in self.mock_run_cmd.call_args_list]
        expected_call_args_list = [(item.command, item.environ) for item in self.run_cmd_calls]
        print("call args list =\n%s" % call_args_list)
        print("expected args list =\n%s" % expected_call_args_list)

        assert self.mock_run_cmd.call_count == len(self.run_cmd_calls)
        if self.mock_run_cmd.call_count:
            assert call_args_list == expected_call_args_list

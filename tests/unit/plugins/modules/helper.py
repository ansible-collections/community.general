# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import json

import yaml
import pytest


from ansible.module_utils.common._collections_compat import Sequence


class Helper(object):
    TEST_SPEC_VALID_SECTIONS = ["anchors", "test_cases"]

    @staticmethod
    def from_spec(test_module, ansible_module, test_spec, mocks=None):
        helper = Helper(test_module, ansible_module, test_spec=test_spec, mocks=mocks)
        return helper

    @staticmethod
    def from_file(test_module, ansible_module, filename, mocks=None):
        with open(filename, "r") as test_cases:
            test_spec = yaml.safe_load(test_cases)
        return Helper.from_spec(test_module, ansible_module, test_spec, mocks)

    @staticmethod
    def from_module(ansible_module, test_module_name, test_spec=None, mocks=None):
        test_module = sys.modules[test_module_name]
        if test_spec is None:
            test_spec = test_module.__file__.replace('.py', '.yaml')
        return Helper.from_file(test_module, ansible_module, test_spec)

    def add_func_to_test_module(self, name, func):
        setattr(self.test_module, name, func)

    def __init__(self, test_module, ansible_module, test_spec, mocks=None):
        self.test_module = test_module
        self.ansible_module = ansible_module
        self.test_cases = []
        self.fixtures = {}
        if isinstance(test_spec, Sequence):
            test_cases = test_spec
        else:  # it is a dict
            test_cases = test_spec['test_cases']
            spec_diff = set(test_spec.keys()) - set(self.TEST_SPEC_VALID_SECTIONS)
            if spec_diff:
                raise ValueError("Test specification contain unknown keys: {0}".format(", ".join(spec_diff)))
        self.mocks_map = {m.name: m for m in mocks} if mocks else {}

        for test_case in test_cases:
            tc = ModuleTestCase.make_test_case(test_case, test_module, self.mocks_map)
            self.test_cases.append(tc)
            self.fixtures.update(tc.fixtures)
        self.set_test_func()
        self.set_fixtures(self.fixtures)

    @property
    def runner(self):
        return Runner(self.ansible_module.main)

    def set_test_func(self):
        @pytest.mark.parametrize('test_case', self.test_cases, ids=[tc.id for tc in self.test_cases])
        @pytest.mark.usefixtures(*self.fixtures)
        def _test_module(mocker, capfd, patch_ansible_module, test_case):
            """
            Run unit tests for each test case in self.test_cases
            """
            patch_ansible_module(test_case.input)
            self.runner.run(mocker, capfd, test_case)

        self.add_func_to_test_module("test_module", _test_module)

        return _test_module

    def set_fixtures(self, fixtures):
        for name, fixture in fixtures.items():
            self.add_func_to_test_module(name, fixture)


class Runner:
    def __init__(self, module_main):
        self.module_main = module_main
        self.results = None

    def run(self, mocker, capfd, test_case):
        test_case.setup(mocker)
        self.pytest_module(capfd, test_case.flags)
        test_case.check(self.results)

    def pytest_module(self, capfd, flags):
        if flags.get("skip"):
            pytest.skip(flags.get("skip"))
        if flags.get("xfail"):
            pytest.xfail(flags.get("xfail"))

        with pytest.raises(SystemExit):
            (self.module_main)()

        out, err = capfd.readouterr()
        self.results = json.loads(out)


class ModuleTestCase:
    def __init__(self, id, input, output, mocks, flags):
        self.id = id
        self.input = input
        self.output = output
        self.mock_specs = mocks
        self.mocks = {}
        self.flags = flags

        self._fixtures = {}

    def __str__(self):
        return "<ModuleTestCase: id={id} {input}{output}mocks={mocks} flags={flags}>".format(
            id=self.id,
            input="input " if self.input else "",
            output="output " if self.output else "",
            mocks="({0})".format(", ".join(self.mocks.keys())),
            flags=self.flags
        )

    def __repr__(self):
        return "ModuleTestCase(id={id}, input={input}, output={output}, mocks={mocks}, flags={flags})".format(
            id=self.id,
            input=self.input,
            output=self.output,
            mocks=repr(self.mocks),
            flags=self.flags
        )

    @staticmethod
    def make_test_case(test_case_spec, test_module, mocks_map):
        tc = ModuleTestCase(
            id=test_case_spec["id"],
            input=test_case_spec.get("input", {}),
            output=test_case_spec.get("output", {}),
            mocks=test_case_spec.get("mocks", {}),
            flags=test_case_spec.get("flags", {})
        )
        tc.build_mocks(test_module, mocks_map)
        return tc

    def build_mocks(self, test_module, mocks_map):
        for mock_name, mock_spec in self.mock_specs.items():
            mock_class = mocks_map.get(mock_name, self.get_mock_class(test_module, mock_name))
            self.mocks[mock_name] = mock_class.build_mock(mock_spec)

            self._fixtures.update(self.mocks[mock_name].fixtures())

    @staticmethod
    def get_mock_class(test_module, mock):
        try:
            class_name = "".join(x.capitalize() for x in mock.split("_")) + "Mock"
            plugin_class = getattr(test_module, class_name)
            assert issubclass(plugin_class, TestCaseMock), "Class {0} is not a subclass of TestCaseMock".format(class_name)
            return plugin_class
        except AttributeError:
            raise ValueError("Cannot find class {0} for mock {1}".format(class_name, mock))

    @property
    def fixtures(self):
        return dict(self._fixtures)

    def setup(self, mocker):
        self.setup_testcase(mocker)
        self.setup_mocks(mocker)

    def check(self, results):
        self.check_testcase(results)
        self.check_mocks(self, results)

    def setup_testcase(self, mocker):
        pass

    def setup_mocks(self, mocker):
        for mock in self.mocks.values():
            mock.setup(mocker)

    def check_testcase(self, results):
        print("testcase =\n%s" % repr(self))
        print("results =\n%s" % results)
        if 'exception' in results:
            print("exception = \n%s" % results["exception"])

        for test_result in self.output:
            assert results[test_result] == self.output[test_result], \
                "'{0}': '{1}' != '{2}'".format(test_result, results[test_result], self.output[test_result])

    def check_mocks(self, test_case, results):
        for mock in self.mocks.values():
            mock.check(test_case, results)


class TestCaseMock:
    @property
    def name(self):
        raise NotImplementedError()

    @classmethod
    def build_mock(cls, mock_specs):
        return cls(mock_specs)

    def __init__(self, mock_specs):
        self.mock_specs = mock_specs

    def fixtures(self):
        return {}

    def setup(self, mocker):
        pass

    def check(self, test_case, results):
        raise NotImplementedError()


class RunCommandMock(TestCaseMock):
    @property
    def name(self):
        return "run_command"

    def __str__(self):
        return "<RunCommandMock specs={specs}>".format(specs=self.mock_specs)

    def __repr__(self):
        return "RunCommandMock({specs})".format(specs=self.mock_specs)

    def fixtures(self):
        @pytest.fixture
        def patch_bin(mocker):
            def mockie(self_, path, *args, **kwargs):
                return "/testbin/{0}".format(path)
            mocker.patch('ansible.module_utils.basic.AnsibleModule.get_bin_path', mockie)

        return {"patch_bin": patch_bin}

    def setup(self, mocker):
        def _results():
            for result in [(x['rc'], x['out'], x['err']) for x in self.mock_specs]:
                yield result
            raise Exception("testcase has not enough run_command calls")

        results = _results()

        def side_effect(self_, **kwargs):
            result = next(results)
            if kwargs.get("check_rc", False) and result[0] != 0:
                raise Exception("rc = {0}".format(result[0]))
            return result

        self.mock_run_cmd = mocker.patch('ansible.module_utils.basic.AnsibleModule.run_command', side_effect=side_effect)

    def check(self, test_case, results):
        call_args_list = [(item[0][0], item[1]) for item in self.mock_run_cmd.call_args_list]
        expected_call_args_list = [(item['command'], item['environ']) for item in self.mock_specs]
        print("call args list =\n%s" % call_args_list)
        print("expected args list =\n%s" % expected_call_args_list)

        assert self.mock_run_cmd.call_count == len(self.mock_specs), "{0} != {1}".format(self.mock_run_cmd.call_count, len(self.mock_specs))
        if self.mock_run_cmd.call_count:
            assert call_args_list == expected_call_args_list

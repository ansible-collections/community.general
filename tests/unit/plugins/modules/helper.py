# Copyright (c) Ansible project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import json

import yaml
import pytest


class Helper(object):
    # @staticmethod
    # def from_list(module_main, list_):
    #     # helper = Helper(module_main, test_cases=list_)
    #     # return helper
    #     pass

    @staticmethod
    def from_file(test_module, module, filename):
        with open(filename, "r") as test_cases:
            test_cases = yaml.safe_load(test_cases)
            helper = Helper(test_module, module, test_cases=test_cases)
            return helper

    @staticmethod
    def from_module(ansible_module, test_module_name, test_spec=None):
        test_module = sys.modules[test_module_name]
        if test_spec is None:
            test_spec = test_module.__file__.replace('.py', '.yaml')
        helper = Helper.from_file(test_module, ansible_module, test_spec)

        return helper

    def __init__(self, test_module, module, test_cases):
        self.test_module = test_module
        self.module = module
        self.test_cases = [
            ModuleTestCase(
                id=tc["id"],
                input=tc.get("input", {}),
                output=tc.get("output", {}),
                contexts=tc.get("contexts", {}),
                flags=tc.get("flags", {})
            )
            for tc in test_cases
        ]
        for mtc in self.test_cases:
            mtc.build_contexts(test_module)

        self.fixtures = {}
        for tc in self.test_cases:
            self.fixtures.update(tc.fixtures)
        self.set_fixtures(self.fixtures)
        for tc in self.test_cases:
            self.set_test_func(tc)

    @property
    def runner(self):
        return Runner(self)

    def set_test_func(self, test_case):
        fixtures = ['patch_ansible_module'] + list(self.fixtures.keys())

        @pytest.mark.parametrize('patch_ansible_module',
                                 [test_case.input], ids=["testing"],
                                 indirect=['patch_ansible_module'])
        @pytest.mark.usefixtures(*fixtures)
        def _test_module(mocker, capfd):
            """
            Run unit tests for each test case in self.test_cases
            """
            self.runner.run(mocker, capfd, test_case)

        setattr(self.test_module, "test_" + test_case.id, _test_module)

        return _test_module

    def set_fixtures(self, fixtures):
        for name, fixture in fixtures.items():
            try:
                getattr(self.test_module, name)
                # already exists, warning
            except AttributeError:
                setattr(self.test_module, name, fixture)


class Runner:
    def __init__(self, helper):
        self.module_main = helper.module.main
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
    def __init__(self, id, input, output, contexts, flags):
        self.id = id
        self.input = input
        self.output = output
        self._contexts = contexts
        self.contexts = {}
        self.flags = flags

        self._fixtures = {}

    def __str__(self):
        return "<ModuleTestCase: id={id} {input}{output}contexts={contexts} flags={flags}>".format(
            id=self.id,
            input="input " if self.input else "",
            output="output " if self.output else "",
            contexts="({0})".format(", ".join(self.contexts.keys())),
            flags=self.flags
        )

    def __repr__(self):
        return "ModuleTestCase(id={id}, input={input}, output={output}, contexts={contexts}, flags={flags})".format(
            id=self.id,
            input=self.input,
            output=self.output,
            contexts=repr(self.contexts),
            flags=self.flags
        )

    @staticmethod
    def make_test_case(test_case):
        tc = ModuleTestCase(**test_case)
        return tc

    def build_contexts(self, context_module):
        for context, context_spec in self._contexts.items():
            context_class = self.get_context_class(context_module, context)
            self.contexts[context] = context_class.build_context(context_spec)

            self._fixtures.update(self.contexts[context].fixtures())

    @staticmethod
    def get_context_class(context_module, context):
        try:
            class_name = "".join(x.capitalize() for x in context.split("_")) + "Context"
            plugin_class = getattr(context_module, class_name)
            assert issubclass(plugin_class, TestCaseContext), "Class {0} is not a subclass of BaseContext".format(class_name)
            return plugin_class
        except AttributeError:
            raise ValueError("Cannot find class {0} for context {1}".format(class_name, context))

    @property
    def fixtures(self):
        return dict(self._fixtures)

    def setup(self, mocker):
        self.setup_testcase(mocker)
        self.setup_contexts(mocker)

    def check(self, results):
        self.check_testcase(results)
        self.check_contexts(self, results)

    def setup_testcase(self, mocker):
        pass

    def setup_contexts(self, mocker):
        for context in self.contexts.values():
            context.setup(mocker)

    def check_testcase(self, results):
        print("testcase =\n%s" % repr(self))
        print("results =\n%s" % results)
        if 'exception' in results:
            print("exception = \n%s" % results["exception"])

        for test_result in self.output:
            assert results[test_result] == self.output[test_result], \
                "'{0}': '{1}' != '{2}'".format(test_result, results[test_result], self.output[test_result])

    def check_contexts(self, test_case, results):
        for context in self.contexts.values():
            context.check(test_case, results)


class TestCaseContext:
    @classmethod
    def build_context(cls, context_specs):
        return cls(context_specs)

    def __init__(self, context_specs):
        self.context_specs = context_specs

    def fixtures(self):
        return {}

    def setup(self, mocker):
        pass

    def check(self, test_case, results):
        raise NotImplementedError()


class RunCommandContext(TestCaseContext):
    def __str__(self):
        return "<RunCommandContext specs={specs}>".format(specs=self.context_specs)

    def __repr__(self):
        return "RunCommandContext({specs})".format(specs=self.context_specs)

    def fixtures(self):
        @pytest.fixture
        def patch_bin(mocker):
            def mockie(self, path, *args, **kwargs):
                return "/testbin/{0}".format(path)
            mocker.patch('ansible.module_utils.basic.AnsibleModule.get_bin_path', mockie)

        return {"patch_bin": patch_bin}

    def setup(self, mocker):
        def _results():
            for result in [(x['rc'], x['out'], x['err']) for x in self.context_specs]:
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
        expected_call_args_list = [(item['command'], item['environ']) for item in self.context_specs]
        print("call args list =\n%s" % call_args_list)
        print("expected args list =\n%s" % expected_call_args_list)

        assert self.mock_run_cmd.call_count == len(self.context_specs), "{0} != {1}".format(self.mock_run_cmd.call_count, len(self.context_specs))
        if self.mock_run_cmd.call_count:
            assert call_args_list == expected_call_args_list

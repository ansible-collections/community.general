# -*- coding: utf-8 -*-
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from sys import version_info

import pytest

from ansible_collections.community.general.tests.unit.compat.mock import MagicMock, PropertyMock
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, fmt


TC_FORMATS = dict(
    simple_boolean__true=(fmt.as_bool, ("--superflag",), True, ["--superflag"]),
    simple_boolean__false=(fmt.as_bool, ("--superflag",), False, []),
    simple_boolean__none=(fmt.as_bool, ("--superflag",), None, []),
    simple_boolean_not__true=(fmt.as_bool_not, ("--superflag",), True, []),
    simple_boolean_not__false=(fmt.as_bool_not, ("--superflag",), False, ["--superflag"]),
    simple_boolean_not__none=(fmt.as_bool_not, ("--superflag",), None, ["--superflag"]),
    simple_optval__str=(fmt.as_optval, ("-t",), "potatoes", ["-tpotatoes"]),
    simple_optval__int=(fmt.as_optval, ("-t",), 42, ["-t42"]),
    simple_opt_val__str=(fmt.as_opt_val, ("-t",), "potatoes", ["-t", "potatoes"]),
    simple_opt_val__int=(fmt.as_opt_val, ("-t",), 42, ["-t", "42"]),
    simple_opt_eq_val__str=(fmt.as_opt_eq_val, ("--food",), "potatoes", ["--food=potatoes"]),
    simple_opt_eq_val__int=(fmt.as_opt_eq_val, ("--answer",), 42, ["--answer=42"]),
    simple_list_potato=(fmt.as_list, (), "literal_potato", ["literal_potato"]),
    simple_list_42=(fmt.as_list, (), 42, ["42"]),
    simple_map=(fmt.as_map, ({'a': 1, 'b': 2, 'c': 3},), 'b', ["2"]),
    simple_default_type__list=(fmt.as_default_type, ("list",), [1, 2, 3, 5, 8], ["--1", "--2", "--3", "--5", "--8"]),
    simple_default_type__bool_true=(fmt.as_default_type, ("bool", "what"), True, ["--what"]),
    simple_default_type__bool_false=(fmt.as_default_type, ("bool", "what"), False, []),
    simple_default_type__potato=(fmt.as_default_type, ("any-other-type", "potato"), "42", ["--potato", "42"]),
    simple_fixed_true=(fmt.as_fixed, [("--always-here", "--forever")], True, ["--always-here", "--forever"]),
    simple_fixed_false=(fmt.as_fixed, [("--always-here", "--forever")], False, ["--always-here", "--forever"]),
    simple_fixed_none=(fmt.as_fixed, [("--always-here", "--forever")], None, ["--always-here", "--forever"]),
    simple_fixed_str=(fmt.as_fixed, [("--always-here", "--forever")], "something", ["--always-here", "--forever"]),
)
if tuple(version_info) >= (3, 1):
    from collections import OrderedDict

    # needs OrderedDict to provide a consistent key order
    TC_FORMATS["simple_default_type__dict"] = (  # type: ignore
        fmt.as_default_type,
        ("dict",),
        OrderedDict((('a', 1), ('b', 2))),
        ["--a=1", "--b=2"]
    )
TC_FORMATS_IDS = sorted(TC_FORMATS.keys())


@pytest.mark.parametrize('func, fmt_opt, value, expected',
                         (TC_FORMATS[tc] for tc in TC_FORMATS_IDS),
                         ids=TC_FORMATS_IDS)
def test_arg_format(func, fmt_opt, value, expected):
    fmt_func = func(*fmt_opt)
    actual = fmt_func(value, ctx_ignore_none=True)
    print("formatted string = {0}".format(actual))
    assert actual == expected, "actual = {0}".format(actual)


TC_RUNNER = dict(
    # SAMPLE: This shows all possible elements of a test case. It does not actually run.
    #
    # testcase_name=(
    #     # input
    #     dict(
    #         args_bundle = dict(
    #             param1=dict(
    #                 type="int",
    #                 value=11,
    #                 fmt_func=fmt.as_opt_eq_val,
    #                 fmt_arg="--answer",
    #             ),
    #             param2=dict(
    #                 fmt_func=fmt.as_bool,
    #                 fmt_arg="--bb-here",
    #             )
    #         ),
    #         runner_init_args = dict(
    #             command="testing",
    #             default_args_order=(),
    #             check_rc=False,
    #             force_lang="C",
    #             path_prefix=None,
    #             environ_update=None,
    #         ),
    #         runner_ctx_args = dict(
    #             args_order=['aa', 'bb'],
    #             output_process=None,
    #             ignore_value_none=True,
    #         ),
    #     ),
    #     # command execution
    #     dict(
    #         runner_ctx_run_args = dict(bb=True),
    #         rc = 0,
    #         out = "",
    #         err = "",
    #     ),
    #     # expected
    #     dict(
    #         results=(),
    #         run_info=dict(
    #             cmd=['/mock/bin/testing', '--answer=11', '--bb-here'],
    #             environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'},
    #         ),
    #         exc=None,
    #     ),
    # ),
    #
    aa_bb=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=11, fmt_func=fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=fmt.as_bool, fmt_arg="--bb-here"),
            ),
            runner_init_args=dict(),
            runner_ctx_args=dict(args_order=['aa', 'bb']),
        ),
        dict(runner_ctx_run_args=dict(bb=True), rc=0, out="", err=""),
        dict(
            run_info=dict(
                cmd=['/mock/bin/testing', '--answer=11', '--bb-here'],
                environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'},
                args_order=('aa', 'bb'),
            ),
        ),
    ),
    aa_bb_default_order=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=11, fmt_func=fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=fmt.as_bool, fmt_arg="--bb-here"),
            ),
            runner_init_args=dict(default_args_order=['bb', 'aa']),
            runner_ctx_args=dict(),
        ),
        dict(runner_ctx_run_args=dict(bb=True), rc=0, out="", err=""),
        dict(
            run_info=dict(
                cmd=['/mock/bin/testing', '--bb-here', '--answer=11'],
                environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'},
                args_order=('bb', 'aa'),
            ),
        ),
    ),
    aa_bb_default_order_args_order=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=11, fmt_func=fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=fmt.as_bool, fmt_arg="--bb-here"),
            ),
            runner_init_args=dict(default_args_order=['bb', 'aa']),
            runner_ctx_args=dict(args_order=['aa', 'bb']),
        ),
        dict(runner_ctx_run_args=dict(bb=True), rc=0, out="", err=""),
        dict(
            run_info=dict(
                cmd=['/mock/bin/testing', '--answer=11', '--bb-here'],
                environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'},
                args_order=('aa', 'bb'),
            ),
        ),
    ),
    aa_bb_dup_in_args_order=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=11, fmt_func=fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=fmt.as_bool, fmt_arg="--bb-here"),
            ),
            runner_init_args=dict(),
            runner_ctx_args=dict(args_order=['aa', 'bb', 'aa']),
        ),
        dict(runner_ctx_run_args=dict(bb=True), rc=0, out="", err=""),
        dict(
            run_info=dict(
                cmd=['/mock/bin/testing', '--answer=11', '--bb-here', '--answer=11'],
            ),
        ),
    ),
    aa_bb_process_output=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=11, fmt_func=fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=fmt.as_bool, fmt_arg="--bb-here"),
            ),
            runner_init_args=dict(default_args_order=['bb', 'aa']),
            runner_ctx_args=dict(
                args_order=['aa', 'bb'],
                output_process=lambda rc, out, err: '-/-'.join([str(rc), out, err])
            ),
        ),
        dict(runner_ctx_run_args=dict(bb=True), rc=0, out="ni", err="nu"),
        dict(
            run_info=dict(
                cmd=['/mock/bin/testing', '--answer=11', '--bb-here'],
            ),
            results="0-/-ni-/-nu"
        ),
    ),
    aa_bb_ignore_none_with_none=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=49, fmt_func=fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=fmt.as_bool, fmt_arg="--bb-here"),
            ),
            runner_init_args=dict(default_args_order=['bb', 'aa']),
            runner_ctx_args=dict(
                args_order=['aa', 'bb'],
                ignore_value_none=True,  # default
            ),
        ),
        dict(runner_ctx_run_args=dict(bb=None), rc=0, out="ni", err="nu"),
        dict(
            run_info=dict(
                cmd=['/mock/bin/testing', '--answer=49'],
            ),
        ),
    ),
    aa_bb_ignore_not_none_with_none=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=49, fmt_func=fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=fmt.as_bool, fmt_arg="--bb-here"),
            ),
            runner_init_args=dict(default_args_order=['bb', 'aa']),
            runner_ctx_args=dict(
                args_order=['aa', 'bb'],
                ignore_value_none=False,
            ),
        ),
        dict(runner_ctx_run_args=dict(aa=None, bb=True), rc=0, out="ni", err="nu"),
        dict(
            run_info=dict(
                cmd=['/mock/bin/testing', '--answer=None', '--bb-here'],
            ),
        ),
    ),
)
TC_RUNNER_IDS = sorted(TC_RUNNER.keys())


@pytest.mark.parametrize('runner_input, cmd_execution, expected',
                         (TC_RUNNER[tc] for tc in TC_RUNNER_IDS),
                         ids=TC_RUNNER_IDS)
def test_runner_context(runner_input, cmd_execution, expected):
    arg_spec = {}
    params = {}
    arg_formats = {}
    for k, v in runner_input['args_bundle'].items():
        try:
            arg_spec[k] = {'type': v['type']}
        except KeyError:
            pass
        try:
            params[k] = v['value']
        except KeyError:
            pass
        try:
            arg_formats[k] = v['fmt_func'](v['fmt_arg'])
        except KeyError:
            pass

    orig_results = tuple(cmd_execution[x] for x in ('rc', 'out', 'err'))

    print("arg_spec={0}\nparams={1}\narg_formats={2}\n".format(
        arg_spec,
        params,
        arg_formats,
    ))

    module = MagicMock()
    type(module).argument_spec = PropertyMock(return_value=arg_spec)
    type(module).params = PropertyMock(return_value=params)
    module.get_bin_path.return_value = '/mock/bin/testing'
    module.run_command.return_value = orig_results

    runner = CmdRunner(
        module=module,
        command="testing",
        arg_formats=arg_formats,
        **runner_input['runner_init_args']
    )

    def _assert_run_info(actual, expected):
        reduced = dict((k, actual[k]) for k in expected.keys())
        assert reduced == expected, "{0}".format(reduced)

    def _assert_run(runner_input, cmd_execution, expected, ctx, results):
        _assert_run_info(ctx.run_info, expected['run_info'])
        assert results == expected.get('results', orig_results)

    exc = expected.get("exc")
    if exc:
        with pytest.raises(exc):
            with runner.context(**runner_input['runner_ctx_args']) as ctx:
                results = ctx.run(**cmd_execution['runner_ctx_run_args'])
                _assert_run(runner_input, cmd_execution, expected, ctx, results)

    else:
        with runner.context(**runner_input['runner_ctx_args']) as ctx:
            results = ctx.run(**cmd_execution['runner_ctx_run_args'])
            _assert_run(runner_input, cmd_execution, expected, ctx, results)


@pytest.mark.parametrize('runner_input, cmd_execution, expected',
                         (TC_RUNNER[tc] for tc in TC_RUNNER_IDS),
                         ids=TC_RUNNER_IDS)
def test_runner_callable(runner_input, cmd_execution, expected):
    arg_spec = {}
    params = {}
    arg_formats = {}
    for k, v in runner_input['args_bundle'].items():
        try:
            arg_spec[k] = {'type': v['type']}
        except KeyError:
            pass
        try:
            params[k] = v['value']
        except KeyError:
            pass
        try:
            arg_formats[k] = v['fmt_func'](v['fmt_arg'])
        except KeyError:
            pass

    orig_results = tuple(cmd_execution[x] for x in ('rc', 'out', 'err'))

    print("arg_spec={0}\nparams={1}\narg_formats={2}\n".format(
        arg_spec,
        params,
        arg_formats,
    ))

    module = MagicMock()
    type(module).argument_spec = PropertyMock(return_value=arg_spec)
    type(module).params = PropertyMock(return_value=params)
    module.get_bin_path.return_value = '/mock/bin/testing'
    module.run_command.return_value = orig_results

    runner = CmdRunner(
        module=module,
        command="testing",
        arg_formats=arg_formats,
        **runner_input['runner_init_args']
    )

    def _assert_run_info(actual, expected):
        reduced = dict((k, actual[k]) for k in expected.keys())
        assert reduced == expected, "{0}".format(reduced)

    def _assert_run(runner_input, cmd_execution, expected, ctx, results):
        _assert_run_info(ctx.run_info, expected['run_info'])
        assert results == expected.get('results', orig_results)

    exc = expected.get("exc")
    if exc:
        with pytest.raises(exc):
            with runner(**runner_input['runner_ctx_args']) as ctx:
                results = ctx.run(**cmd_execution['runner_ctx_run_args'])
                _assert_run(runner_input, cmd_execution, expected, ctx, results)

    else:
        with runner(**runner_input['runner_ctx_args']) as ctx:
            results = ctx.run(**cmd_execution['runner_ctx_run_args'])
            _assert_run(runner_input, cmd_execution, expected, ctx, results)

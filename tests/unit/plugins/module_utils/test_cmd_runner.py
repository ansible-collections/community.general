# -*- coding: utf-8 -*-
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from functools import partial

import pytest

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import MagicMock, PropertyMock
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


TC_FORMATS = dict(
    simple_boolean__true=(partial(cmd_runner_fmt.as_bool, "--superflag"), True, ["--superflag"], None),
    simple_boolean__false=(partial(cmd_runner_fmt.as_bool, "--superflag"), False, [], None),
    simple_boolean__none=(partial(cmd_runner_fmt.as_bool, "--superflag"), None, [], None),
    simple_boolean_both__true=(partial(cmd_runner_fmt.as_bool, "--superflag", "--falseflag"), True, ["--superflag"], None),
    simple_boolean_both__false=(partial(cmd_runner_fmt.as_bool, "--superflag", "--falseflag"), False, ["--falseflag"], None),
    simple_boolean_both__none=(partial(cmd_runner_fmt.as_bool, "--superflag", "--falseflag"), None, ["--falseflag"], None),
    simple_boolean_both__none_ig=(partial(cmd_runner_fmt.as_bool, "--superflag", "--falseflag", True), None, [], None),
    simple_boolean_not__true=(partial(cmd_runner_fmt.as_bool_not, "--superflag"), True, [], None),
    simple_boolean_not__false=(partial(cmd_runner_fmt.as_bool_not, "--superflag"), False, ["--superflag"], None),
    simple_boolean_not__none=(partial(cmd_runner_fmt.as_bool_not, "--superflag"), None, ["--superflag"], None),
    simple_optval__str=(partial(cmd_runner_fmt.as_optval, "-t"), "potatoes", ["-tpotatoes"], None),
    simple_optval__int=(partial(cmd_runner_fmt.as_optval, "-t"), 42, ["-t42"], None),
    simple_opt_val__str=(partial(cmd_runner_fmt.as_opt_val, "-t"), "potatoes", ["-t", "potatoes"], None),
    simple_opt_val__int=(partial(cmd_runner_fmt.as_opt_val, "-t"), 42, ["-t", "42"], None),
    simple_opt_eq_val__str=(partial(cmd_runner_fmt.as_opt_eq_val, "--food"), "potatoes", ["--food=potatoes"], None),
    simple_opt_eq_val__int=(partial(cmd_runner_fmt.as_opt_eq_val, "--answer"), 42, ["--answer=42"], None),
    simple_list_empty=(cmd_runner_fmt.as_list, [], [], None),
    simple_list_potato=(cmd_runner_fmt.as_list, "literal_potato", ["literal_potato"], None),
    simple_list_42=(cmd_runner_fmt.as_list, 42, ["42"], None),
    simple_list_min_len_ok=(partial(cmd_runner_fmt.as_list, min_len=1), 42, ["42"], None),
    simple_list_min_len_fail=(partial(cmd_runner_fmt.as_list, min_len=10), 42, None, ValueError),
    simple_list_max_len_ok=(partial(cmd_runner_fmt.as_list, max_len=1), 42, ["42"], None),
    simple_list_max_len_fail=(partial(cmd_runner_fmt.as_list, max_len=2), [42, 42, 42], None, ValueError),
    simple_map=(partial(cmd_runner_fmt.as_map, {'a': 1, 'b': 2, 'c': 3}), 'b', ["2"], None),
    simple_fixed_true=(partial(cmd_runner_fmt.as_fixed, ["--always-here", "--forever"]), True, ["--always-here", "--forever"], None),
    simple_fixed_false=(partial(cmd_runner_fmt.as_fixed, ["--always-here", "--forever"]), False, ["--always-here", "--forever"], None),
    simple_fixed_none=(partial(cmd_runner_fmt.as_fixed, ["--always-here", "--forever"]), None, ["--always-here", "--forever"], None),
    simple_fixed_str=(partial(cmd_runner_fmt.as_fixed, ["--always-here", "--forever"]), "something", ["--always-here", "--forever"], None),
    stack_optval__str=(partial(cmd_runner_fmt.stack(cmd_runner_fmt.as_optval), "-t"), ["potatoes", "bananas"], ["-tpotatoes", "-tbananas"], None),
    stack_opt_val__str=(partial(cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val), "-t"), ["potatoes", "bananas"], ["-t", "potatoes", "-t", "bananas"], None),
    stack_opt_eq_val__int=(partial(cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_eq_val), "--answer"), [42, 17], ["--answer=42", "--answer=17"], None),
)
TC_FORMATS_IDS = sorted(TC_FORMATS.keys())


@pytest.mark.parametrize('func, value, expected, exception',
                         (TC_FORMATS[tc] for tc in TC_FORMATS_IDS),
                         ids=TC_FORMATS_IDS)
def test_arg_format(func, value, expected, exception):
    fmt_func = func()
    try:
        actual = fmt_func(value)
        print("formatted string = {0}".format(actual))
        assert actual == expected, "actual = {0}".format(actual)
    except Exception as e:
        if exception is None:
            raise
        assert isinstance(e, exception)


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
    #                 fmt_func=cmd_runner_fmt.as_opt_eq_val,
    #                 fmt_arg="--answer",
    #             ),
    #             param2=dict(
    #                 fmt_func=cmd_runner_fmt.as_bool,
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
                aa=dict(type="int", value=11, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_bool, fmt_arg="--bb-here"),
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
                aa=dict(type="int", value=11, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_bool, fmt_arg="--bb-here"),
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
                aa=dict(type="int", value=11, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_bool, fmt_arg="--bb-here"),
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
                aa=dict(type="int", value=11, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_bool, fmt_arg="--bb-here"),
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
                aa=dict(type="int", value=11, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_bool, fmt_arg="--bb-here"),
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
                aa=dict(type="int", value=49, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_bool, fmt_arg="--bb-here"),
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
                aa=dict(type="int", value=49, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_bool, fmt_arg="--bb-here"),
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
    aa_bb_fixed=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=11, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_fixed, fmt_arg=["fixed", "args"]),
            ),
            runner_init_args=dict(),
            runner_ctx_args=dict(args_order=['aa', 'bb']),
        ),
        dict(runner_ctx_run_args=dict(), rc=0, out="", err=""),
        dict(
            run_info=dict(
                cmd=['/mock/bin/testing', '--answer=11', 'fixed', 'args'],
                environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'},
                args_order=('aa', 'bb'),
            ),
        ),
    ),
    aa_bb_map=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=11, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_map, fmt_arg={"v1": 111, "v2": 222}),
            ),
            runner_init_args=dict(),
            runner_ctx_args=dict(args_order=['aa', 'bb']),
        ),
        dict(runner_ctx_run_args=dict(bb="v2"), rc=0, out="", err=""),
        dict(
            run_info=dict(
                cmd=['/mock/bin/testing', '--answer=11', '222'],
                environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'},
                args_order=('aa', 'bb'),
            ),
        ),
    ),
    aa_bb_map_default=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=11, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_map, fmt_arg={"v1": 111, "v2": 222}),
            ),
            runner_init_args=dict(),
            runner_ctx_args=dict(args_order=['aa', 'bb']),
        ),
        dict(runner_ctx_run_args=dict(bb="v123456789"), rc=0, out="", err=""),
        dict(
            run_info=dict(
                cmd=['/mock/bin/testing', '--answer=11'],
                environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'},
                args_order=('aa', 'bb'),
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
        reduced = {k: actual[k] for k in expected.keys()}
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

        with pytest.raises(exc):
            with runner(**runner_input['runner_ctx_args']) as ctx2:
                results2 = ctx2.run(**cmd_execution['runner_ctx_run_args'])
                _assert_run(runner_input, cmd_execution, expected, ctx2, results2)

    else:
        with runner.context(**runner_input['runner_ctx_args']) as ctx:
            results = ctx.run(**cmd_execution['runner_ctx_run_args'])
            _assert_run(runner_input, cmd_execution, expected, ctx, results)

        with runner(**runner_input['runner_ctx_args']) as ctx2:
            results2 = ctx2.run(**cmd_execution['runner_ctx_run_args'])
            _assert_run(runner_input, cmd_execution, expected, ctx2, results2)

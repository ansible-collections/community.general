# -*- coding: utf-8 -*-
# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os

import pytest

from ansible_collections.community.general.tests.unit.compat.mock import MagicMock, PropertyMock
from ansible_collections.community.general.plugins.module_utils.cmd_runner import cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.python_runner import PythonRunner


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
            runner_init_args=dict(command="testing"),
            runner_ctx_args=dict(args_order=['aa', 'bb']),
        ),
        dict(runner_ctx_run_args=dict(bb=True), rc=0, out="", err=""),
        dict(
            run_info=dict(
                cmd=['/mock/bin/python', 'testing', '--answer=11', '--bb-here'],
                environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'},
                args_order=('aa', 'bb'),
            ),
        ),
    ),
    aa_bb_py3=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=11, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_bool, fmt_arg="--bb-here"),
            ),
            runner_init_args=dict(command="toasting", python="python3"),
            runner_ctx_args=dict(args_order=['aa', 'bb']),
        ),
        dict(runner_ctx_run_args=dict(bb=True), rc=0, out="", err=""),
        dict(
            run_info=dict(
                cmd=['/mock/bin/python3', 'toasting', '--answer=11', '--bb-here'],
                environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'},
                args_order=('aa', 'bb'),
            ),
        ),
    ),
    aa_bb_abspath=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=11, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_bool, fmt_arg="--bb-here"),
            ),
            runner_init_args=dict(command="toasting", python="/crazy/local/bin/python3"),
            runner_ctx_args=dict(args_order=['aa', 'bb']),
        ),
        dict(runner_ctx_run_args=dict(bb=True), rc=0, out="", err=""),
        dict(
            run_info=dict(
                cmd=['/crazy/local/bin/python3', 'toasting', '--answer=11', '--bb-here'],
                environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C'},
                args_order=('aa', 'bb'),
            ),
        ),
    ),
    aa_bb_venv=(
        dict(
            args_bundle=dict(
                aa=dict(type="int", value=11, fmt_func=cmd_runner_fmt.as_opt_eq_val, fmt_arg="--answer"),
                bb=dict(fmt_func=cmd_runner_fmt.as_bool, fmt_arg="--bb-here"),
            ),
            runner_init_args=dict(command="toasting", venv="/venv"),
            runner_ctx_args=dict(args_order=['aa', 'bb']),
        ),
        dict(runner_ctx_run_args=dict(bb=True), rc=0, out="", err=""),
        dict(
            run_info=dict(
                cmd=['/venv/bin/python', 'toasting', '--answer=11', '--bb-here'],
                environ_update={'LANGUAGE': 'C', 'LC_ALL': 'C', 'VIRTUAL_ENV': '/venv', 'PATH': '/venv/bin'},
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
    module.get_bin_path.return_value = os.path.join(
        runner_input["runner_init_args"].get("venv", "/mock"),
        "bin",
        runner_input["runner_init_args"].get("python", "python")
    )
    module.run_command.return_value = orig_results

    runner = PythonRunner(
        module=module,
        arg_formats=arg_formats,
        **runner_input['runner_init_args']
    )

    def _extract_path(run_info):
        path = run_info.get("environ_update", {}).get("PATH")
        if path is not None:
            run_info["environ_update"] = {
                k: v
                for k, v in run_info["environ_update"].items()
                if k != "PATH"
            }
        return run_info, path

    def _assert_run_info_env_path(actual, expected):
        actual2 = set(actual.split(":"))
        assert expected in actual2, "Missing expected path {0} in output PATH: {1}".format(expected, actual)

    def _assert_run_info(actual, expected):
        reduced = {k: actual[k] for k in expected.keys()}
        reduced, act_path = _extract_path(reduced)
        expected, exp_path = _extract_path(expected)
        if exp_path is not None:
            _assert_run_info_env_path(act_path, exp_path)
        assert reduced == expected, "{0}".format(reduced)

    def _assert_run(expected, ctx, results):
        _assert_run_info(ctx.run_info, expected['run_info'])
        assert results == expected.get('results', orig_results)

    exc = expected.get("exc")
    if exc:
        with pytest.raises(exc):
            with runner.context(**runner_input['runner_ctx_args']) as ctx:
                results = ctx.run(**cmd_execution['runner_ctx_run_args'])
                _assert_run(expected, ctx, results)

    else:
        with runner.context(**runner_input['runner_ctx_args']) as ctx:
            results = ctx.run(**cmd_execution['runner_ctx_run_args'])
            _assert_run(expected, ctx, results)

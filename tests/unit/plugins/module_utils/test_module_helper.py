# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from collections import namedtuple

import pytest

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    ArgFormat, DependencyCtxMgr, ModuleHelper, VarMeta, cause_changes
)


def single_lambda_2star(x, y, z):
    return ["piggies=[{0},{1},{2}]".format(x, y, z)]


ARG_FORMATS = dict(
    simple_boolean_true=("--superflag", ArgFormat.BOOLEAN, 0, True, ["--superflag"]),
    simple_boolean_false=("--superflag", ArgFormat.BOOLEAN, 0, False, []),
    single_printf=("--param=%s", ArgFormat.PRINTF, 0, "potatoes", ["--param=potatoes"]),
    single_printf_no_substitution=("--param", ArgFormat.PRINTF, 0, "potatoes", ["--param"]),
    multiple_printf=(["--param", "free-%s"], ArgFormat.PRINTF, 0, "potatoes", ["--param", "free-potatoes"]),
    single_format=("--param={0}", ArgFormat.FORMAT, 0, "potatoes", ["--param=potatoes"]),
    single_format_no_substitution=("--param", ArgFormat.FORMAT, 0, "potatoes", ["--param"]),
    multiple_format=(["--param", "free-{0}"], ArgFormat.FORMAT, 0, "potatoes", ["--param", "free-potatoes"]),
    single_lambda_0star=((lambda v: ["piggies=[{0},{1},{2}]".format(v[0], v[1], v[2])]),
                         None, 0, ['a', 'b', 'c'], ["piggies=[a,b,c]"]),
    single_lambda_1star=((lambda a, b, c: ["piggies=[{0},{1},{2}]".format(a, b, c)]),
                         None, 1, ['a', 'b', 'c'], ["piggies=[a,b,c]"]),
    single_lambda_2star=(single_lambda_2star, None, 2, dict(z='c', x='a', y='b'), ["piggies=[a,b,c]"])
)
ARG_FORMATS_IDS = sorted(ARG_FORMATS.keys())


@pytest.mark.parametrize('fmt, style, stars, value, expected',
                         (ARG_FORMATS[tc] for tc in ARG_FORMATS_IDS),
                         ids=ARG_FORMATS_IDS)
def test_arg_format(fmt, style, stars, value, expected):
    af = ArgFormat('name', fmt, style, stars)
    actual = af.to_text(value)
    print("formatted string = {0}".format(actual))
    assert actual == expected


ARG_FORMATS_FAIL = dict(
    int_fmt=(3, None, 0, "", [""]),
    bool_fmt=(True, None, 0, "", [""]),
)
ARG_FORMATS_FAIL_IDS = sorted(ARG_FORMATS_FAIL.keys())


@pytest.mark.parametrize('fmt, style, stars, value, expected',
                         (ARG_FORMATS_FAIL[tc] for tc in ARG_FORMATS_FAIL_IDS),
                         ids=ARG_FORMATS_FAIL_IDS)
def test_arg_format_fail(fmt, style, stars, value, expected):
    with pytest.raises(TypeError):
        af = ArgFormat('name', fmt, style, stars)
        actual = af.to_text(value)
        print("formatted string = {0}".format(actual))


def test_dependency_ctxmgr():
    ctx = DependencyCtxMgr("POTATOES", "Potatoes must be installed")
    with ctx:
        import potatoes_that_will_never_be_there
    print("POTATOES: ctx.text={0}".format(ctx.text))
    assert ctx.text == "Potatoes must be installed"
    assert not ctx.has_it

    ctx = DependencyCtxMgr("POTATOES2")
    with ctx:
        import potatoes_that_will_never_be_there_again
    assert not ctx.has_it
    print("POTATOES2: ctx.text={0}".format(ctx.text))
    assert ctx.text.startswith("No module named")
    assert "potatoes_that_will_never_be_there_again" in ctx.text

    ctx = DependencyCtxMgr("TYPING")
    with ctx:
        import sys
    assert ctx.has_it


class MockMH(object):
    changed = None

    def _div(self, x, y):
        return x / y

    func_none = cause_changes()(_div)
    func_onsucc = cause_changes(on_success=True)(_div)
    func_onfail = cause_changes(on_failure=True)(_div)
    func_onboth = cause_changes(on_success=True, on_failure=True)(_div)


CAUSE_CHG_DECO_PARAMS = ['method', 'expect_exception', 'expect_changed']
CAUSE_CHG_DECO = dict(
    none_succ=dict(method='func_none', expect_exception=False, expect_changed=None),
    none_fail=dict(method='func_none', expect_exception=True, expect_changed=None),
    onsucc_succ=dict(method='func_onsucc', expect_exception=False, expect_changed=True),
    onsucc_fail=dict(method='func_onsucc', expect_exception=True, expect_changed=None),
    onfail_succ=dict(method='func_onfail', expect_exception=False, expect_changed=None),
    onfail_fail=dict(method='func_onfail', expect_exception=True, expect_changed=True),
    onboth_succ=dict(method='func_onboth', expect_exception=False, expect_changed=True),
    onboth_fail=dict(method='func_onboth', expect_exception=True, expect_changed=True),
)
CAUSE_CHG_DECO_IDS = sorted(CAUSE_CHG_DECO.keys())


@pytest.mark.parametrize(CAUSE_CHG_DECO_PARAMS,
                         [[CAUSE_CHG_DECO[tc][param]
                           for param in CAUSE_CHG_DECO_PARAMS]
                          for tc in CAUSE_CHG_DECO_IDS],
                         ids=CAUSE_CHG_DECO_IDS)
def test_cause_changes_deco(method, expect_exception, expect_changed):
    mh = MockMH()
    if expect_exception:
        with pytest.raises(Exception):
            getattr(mh, method)(1, 0)
    else:
        getattr(mh, method)(9, 3)

    assert mh.changed == expect_changed

# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    ArgFormat, DependencyCtxMgr, VarMeta, VarDict, cause_changes
)


def single_lambda_2star(x, y, z):
    return ["piggies=[{0},{1},{2}]".format(x, y, z)]


ARG_FORMATS = dict(
    simple_boolean_true=("--superflag", ArgFormat.BOOLEAN, 0,
                         True, ["--superflag"]),
    simple_boolean_false=("--superflag", ArgFormat.BOOLEAN, 0,
                          False, []),
    simple_boolean_none=("--superflag", ArgFormat.BOOLEAN, 0,
                         None, []),
    simple_boolean_not_true=("--superflag", ArgFormat.BOOLEAN_NOT, 0,
                             True, []),
    simple_boolean_not_false=("--superflag", ArgFormat.BOOLEAN_NOT, 0,
                              False, ["--superflag"]),
    simple_boolean_not_none=("--superflag", ArgFormat.BOOLEAN_NOT, 0,
                             None, ["--superflag"]),
    single_printf=("--param=%s", ArgFormat.PRINTF, 0,
                   "potatoes", ["--param=potatoes"]),
    single_printf_no_substitution=("--param", ArgFormat.PRINTF, 0,
                                   "potatoes", ["--param"]),
    single_printf_none=("--param=%s", ArgFormat.PRINTF, 0,
                        None, []),
    multiple_printf=(["--param", "free-%s"], ArgFormat.PRINTF, 0,
                     "potatoes", ["--param", "free-potatoes"]),
    single_format=("--param={0}", ArgFormat.FORMAT, 0,
                   "potatoes", ["--param=potatoes"]),
    single_format_none=("--param={0}", ArgFormat.FORMAT, 0,
                        None, []),
    single_format_no_substitution=("--param", ArgFormat.FORMAT, 0,
                                   "potatoes", ["--param"]),
    multiple_format=(["--param", "free-{0}"], ArgFormat.FORMAT, 0,
                     "potatoes", ["--param", "free-potatoes"]),
    multiple_format_none=(["--param", "free-{0}"], ArgFormat.FORMAT, 0,
                          None, []),
    single_lambda_0star=((lambda v: ["piggies=[{0},{1},{2}]".format(v[0], v[1], v[2])]), None, 0,
                         ['a', 'b', 'c'], ["piggies=[a,b,c]"]),
    single_lambda_0star_none=((lambda v: ["piggies=[{0},{1},{2}]".format(v[0], v[1], v[2])]), None, 0,
                              None, []),
    single_lambda_1star=((lambda a, b, c: ["piggies=[{0},{1},{2}]".format(a, b, c)]), None, 1,
                         ['a', 'b', 'c'], ["piggies=[a,b,c]"]),
    single_lambda_1star_none=((lambda a, b, c: ["piggies=[{0},{1},{2}]".format(a, b, c)]), None, 1,
                              None, []),
    single_lambda_2star=(single_lambda_2star, None, 2,
                         dict(z='c', x='a', y='b'), ["piggies=[a,b,c]"]),
    single_lambda_2star_none=(single_lambda_2star, None, 2,
                              None, []),
)
ARG_FORMATS_IDS = sorted(ARG_FORMATS.keys())


@pytest.mark.parametrize('fmt, style, stars, value, expected',
                         (ARG_FORMATS[tc] for tc in ARG_FORMATS_IDS),
                         ids=ARG_FORMATS_IDS)
def test_arg_format(fmt, style, stars, value, expected):
    af = ArgFormat('name', fmt, style, stars)
    actual = af.to_text(value)
    print("formatted string = {0}".format(actual))
    assert actual == expected, "actual = {0}".format(actual)


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


def test_variable_meta():
    meta = VarMeta()
    assert meta.output is True
    assert meta.diff is False
    assert meta.value is None
    meta.set_value("abc")
    assert meta.initial_value == "abc"
    assert meta.value == "abc"
    assert meta.diff_result is None
    meta.set_value("def")
    assert meta.initial_value == "abc"
    assert meta.value == "def"
    assert meta.diff_result is None


def test_variable_meta_diff():
    meta = VarMeta(diff=True)
    assert meta.output is True
    assert meta.diff is True
    assert meta.value is None
    meta.set_value("abc")
    assert meta.initial_value == "abc"
    assert meta.value == "abc"
    assert meta.diff_result is None
    meta.set_value("def")
    assert meta.initial_value == "abc"
    assert meta.value == "def"
    assert meta.diff_result == {"before": "abc", "after": "def"}
    meta.set_value("ghi")
    assert meta.initial_value == "abc"
    assert meta.value == "ghi"
    assert meta.diff_result == {"before": "abc", "after": "ghi"}


def test_vardict():
    vd = VarDict()
    vd.set('a', 123)
    assert vd['a'] == 123
    assert vd.a == 123
    assert 'a' in vd._meta
    assert vd.meta('a').output is True
    assert vd.meta('a').diff is False
    assert vd.meta('a').change is False
    vd['b'] = 456
    assert vd.meta('b').output is True
    assert vd.meta('b').diff is False
    assert vd.meta('b').change is False
    vd.set_meta('a', diff=True, change=True)
    vd.set_meta('b', diff=True, output=False)
    vd['c'] = 789
    assert vd.has_changed('c') is False
    vd['a'] = 'new_a'
    assert vd.has_changed('a') is True
    vd['c'] = 'new_c'
    assert vd.has_changed('c') is False
    vd['b'] = 'new_b'
    assert vd.has_changed('b') is False
    assert vd.a == 'new_a'
    assert vd.c == 'new_c'
    assert vd.output() == {'a': 'new_a', 'c': 'new_c'}
    assert vd.diff() == {'before': {'a': 123}, 'after': {'a': 'new_a'}}, "diff={0}".format(vd.diff())


def test_variable_meta_change():
    vd = VarDict()
    vd.set('a', 123, change=True)
    vd.set('b', [4, 5, 6], change=True)
    vd.set('c', {'m': 7, 'n': 8, 'o': 9}, change=True)
    vd.set('d', {'a1': {'a11': 33, 'a12': 34}}, change=True)

    vd.a = 1234
    assert vd.has_changed('a') is True
    vd.b.append(7)
    assert vd.b == [4, 5, 6, 7]
    assert vd.has_changed('b')
    vd.c.update({'p': 10})
    assert vd.c == {'m': 7, 'n': 8, 'o': 9, 'p': 10}
    assert vd.has_changed('c')
    vd.d['a1'].update({'a13': 35})
    assert vd.d == {'a1': {'a11': 33, 'a12': 34, 'a13': 35}}
    assert vd.has_changed('d')


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

# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    DependencyCtxMgr, VarMeta, VarDict, cause_changes
)


def test_dependency_ctxmgr():
    ctx = DependencyCtxMgr("POTATOES", "Potatoes must be installed")
    with ctx:
        import potatoes_that_will_never_be_there  # noqa: F401, pylint: disable=unused-import
    print("POTATOES: ctx.text={0}".format(ctx.text))
    assert ctx.text == "Potatoes must be installed"
    assert not ctx.has_it

    ctx = DependencyCtxMgr("POTATOES2")
    with ctx:
        import potatoes_that_will_never_be_there_again  # noqa: F401, pylint: disable=unused-import
    assert not ctx.has_it
    print("POTATOES2: ctx.text={0}".format(ctx.text))
    assert ctx.text.startswith("No module named")
    assert "potatoes_that_will_never_be_there_again" in ctx.text

    ctx = DependencyCtxMgr("TYPING")
    with ctx:
        import sys  # noqa: F401, pylint: disable=unused-import
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

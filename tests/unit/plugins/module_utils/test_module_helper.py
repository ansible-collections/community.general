# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.module_helper import (
    cause_changes
)


#
# DEPRECATION NOTICE
# Parameters on_success and on_failure are deprecated and will be removed in community.general 12.0.0
# Remove testcases with those params when releasing 12.0.0
#
CAUSE_CHG_DECO_PARAMS = ['deco_args', 'expect_exception', 'expect_changed']
CAUSE_CHG_DECO = dict(
    none_succ=dict(deco_args={}, expect_exception=False, expect_changed=None),
    none_fail=dict(deco_args={}, expect_exception=True, expect_changed=None),
    onsucc_succ=dict(deco_args=dict(on_success=True), expect_exception=False, expect_changed=True),
    onsucc_fail=dict(deco_args=dict(on_success=True), expect_exception=True, expect_changed=None),
    onfail_succ=dict(deco_args=dict(on_failure=True), expect_exception=False, expect_changed=None),
    onfail_fail=dict(deco_args=dict(on_failure=True), expect_exception=True, expect_changed=True),
    onboth_succ=dict(deco_args=dict(on_success=True, on_failure=True), expect_exception=False, expect_changed=True),
    onboth_fail=dict(deco_args=dict(on_success=True, on_failure=True), expect_exception=True, expect_changed=True),
    whensucc_succ=dict(deco_args=dict(when="success"), expect_exception=False, expect_changed=True),
    whensucc_fail=dict(deco_args=dict(when="success"), expect_exception=True, expect_changed=None),
    whenfail_succ=dict(deco_args=dict(when="failure"), expect_exception=False, expect_changed=None),
    whenfail_fail=dict(deco_args=dict(when="failure"), expect_exception=True, expect_changed=True),
    whenalways_succ=dict(deco_args=dict(when="always"), expect_exception=False, expect_changed=True),
    whenalways_fail=dict(deco_args=dict(when="always"), expect_exception=True, expect_changed=True),
)
CAUSE_CHG_DECO_IDS = sorted(CAUSE_CHG_DECO.keys())


@pytest.mark.parametrize(CAUSE_CHG_DECO_PARAMS,
                         [[CAUSE_CHG_DECO[tc][param]
                          for param in CAUSE_CHG_DECO_PARAMS]
                          for tc in CAUSE_CHG_DECO_IDS],
                         ids=CAUSE_CHG_DECO_IDS)
def test_cause_changes_deco(deco_args, expect_exception, expect_changed):

    class MockMH(object):
        changed = None

        @cause_changes(**deco_args)
        def div_(self, x, y):
            return x / y

    mh = MockMH()
    if expect_exception:
        with pytest.raises(Exception):
            mh.div_(1, 0)
    else:
        mh.div_(9, 3)

    assert mh.changed == expect_changed

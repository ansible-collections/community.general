# (c) 2023, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2023 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


from ansible_collections.community.general.plugins.module_utils.vardict import VarDict


def test_var_simple():
    vd = VarDict()
    vd["a"] = 123

    var = vd._var("a")
    assert var.output is True
    assert var.diff is False
    assert var.change is False
    assert var.fact is False
    assert var.initial_value == 123
    assert var.value == 123

    vd.a = 456
    assert var.output is True
    assert var.diff is False
    assert var.change is False
    assert var.fact is False
    assert var.initial_value == 123
    assert var.value == 456


def test_var_diff_scalar():
    vd = VarDict()
    vd.set("aa", 123, diff=True)

    var = vd._var("aa")
    assert var.output is True
    assert var.diff is True
    assert var.change is True
    assert var.fact is False
    assert var.initial_value == 123
    assert var.value == 123
    assert vd.diff() is None

    vd.aa = 456
    assert var.output is True
    assert var.diff is True
    assert var.change is True
    assert var.fact is False
    assert var.initial_value == 123
    assert var.value == 456
    assert vd.diff() == {"before": {"aa": 123}, "after": {"aa": 456}}, f"actual={vd.diff()}"


def test_var_diff_dict():
    val_before = dict(x=0, y=10, z=10)
    val_after = dict(x=0, y=30, z=10)

    vd = VarDict()
    vd.set("dd", val_before, diff=True)

    var = vd._var("dd")
    assert var.output is True
    assert var.diff is True
    assert var.change is True
    assert var.fact is False
    assert var.initial_value == val_before
    assert var.value == val_before
    assert vd.diff() is None

    vd.dd = val_after
    assert var.output is True
    assert var.diff is True
    assert var.change is True
    assert var.fact is False
    assert var.initial_value == val_before
    assert var.value == val_after
    assert vd.diff() == {"before": {"dd": val_before}, "after": {"dd": val_after}}, f"actual={vd.diff()}"

    vd.set("aa", 123, diff=True)
    vd.aa = 456
    assert vd.diff() == {"before": {"aa": 123, "dd": val_before}, "after": {"aa": 456, "dd": val_after}}, (
        f"actual={vd.diff()}"
    )


def test_vardict_set_meta():
    vd = VarDict()
    vd["jj"] = 123

    var = vd._var("jj")
    assert var.output is True
    assert var.diff is False
    assert var.change is False
    assert var.fact is False
    assert var.initial_value == 123
    assert var.value == 123

    vd.set_meta("jj", diff=True)
    assert var.diff is True
    assert var.change is True

    vd.set_meta("jj", diff=False)
    assert var.diff is False
    assert var.change is False

    vd.set_meta("jj", change=False)
    vd.set_meta("jj", diff=True)
    assert var.diff is True
    assert var.change is False


def test_vardict_change():
    vd = VarDict()
    vd.set("xx", 123, change=True)
    vd.set("yy", 456, change=True)
    vd.set("zz", 789, change=True)

    vd.xx = 123
    vd.yy = 456
    assert vd.has_changed is False
    vd.xx = 12345
    assert vd.has_changed is True


def test_vardict_dict():
    vd = VarDict()
    vd.set("xx", 123)
    vd.set("yy", 456)
    vd.set("zz", 789)

    assert vd.as_dict() == {"xx": 123, "yy": 456, "zz": 789}
    assert vd.get_meta("xx") == {"output": True, "change": False, "diff": False, "fact": False, "verbosity": 0}

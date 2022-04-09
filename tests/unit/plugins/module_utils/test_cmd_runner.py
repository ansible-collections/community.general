# -*- coding: utf-8 -*-
# (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from sys import version_info

import pytest

from ansible_collections.community.general.plugins.module_utils.cmd_runner import (
    CmdRunner, fmt_bool, fmt_bool_not, fmt_opt_val, fmt_optval,
    fmt_opt_eq_val, fmt_str, fmt_mapped, fmt_default_type
)


ARG_FORMATS = dict(
    simple_boolean__true=(fmt_bool, ("--superflag",), True, ["--superflag"]),
    simple_boolean__false=(fmt_bool, ("--superflag",), False, []),
    simple_boolean__none=(fmt_bool, ("--superflag",), None, []),
    simple_boolean_not__true=(fmt_bool_not, ("--superflag",), True, []),
    simple_boolean_not__false=(fmt_bool_not, ("--superflag",), False, ["--superflag"]),
    simple_boolean_not__none=(fmt_bool_not, ("--superflag",), None, ["--superflag"]),
    simple_optval__str=(fmt_optval, ("-t",), "potatoes", ["-tpotatoes"]),
    simple_optval__int=(fmt_optval, ("-t",), 42, ["-t42"]),
    simple_opt_val__str=(fmt_opt_val, ("-t",), "potatoes", ["-t", "potatoes"]),
    simple_opt_val__int=(fmt_opt_val, ("-t",), 42, ["-t", "42"]),
    simple_opt_eq_val__str=(fmt_opt_eq_val, ("--food",), "potatoes", ["--food=potatoes"]),
    simple_opt_eq_val__int=(fmt_opt_eq_val, ("--answer",), 42, ["--answer=42"]),
    simple_str=(fmt_str, (), "literal_potato", ["literal_potato"]),
    simple_mapped=(fmt_mapped, ({'a': 1, 'b': 2, 'c': 3},), 'b', ["2"]),
    simple_default_type__list=(fmt_default_type, ("list",), [1, 2, 3, 5, 8], ["1", "2", "3", "5", "8"]),
    simple_default_type__bool_true=(fmt_default_type, ("bool", "what"), True, ["--what"]),
    simple_default_type__bool_false=(fmt_default_type, ("bool", "what"), False, []),
    simple_default_type__potato=(fmt_default_type, ("else", "potato"), "42", ["--potato", "42"]),
)
if tuple(version_info) >= (3, 1):
    from collections import OrderedDict

    ARG_FORMATS["simple_default_type__dict"] = (  # type: ignore
        fmt_default_type,
        ("dict",),
        OrderedDict((('a', 1), ('b', 2))),
        ["a=1", "b=2"]
    )
ARG_FORMATS_IDS = sorted(ARG_FORMATS.keys())


@pytest.mark.parametrize('func, fmt_opt, value, expected',
                         (ARG_FORMATS[tc] for tc in ARG_FORMATS_IDS),
                         ids=ARG_FORMATS_IDS)
def test_arg_format(func, fmt_opt, value, expected):
    fmt = func(*fmt_opt)
    actual = fmt(value)
    print("formatted string = {0}".format(actual))
    assert actual == expected, "actual = {0}".format(actual)

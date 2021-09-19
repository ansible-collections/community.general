# -*- coding: utf-8 -*-
# (c) 2021, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2021 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.general.plugins.module_utils.cmd_runner import (
    CmdRunner, fmt_bool, fmt_bool_not, fmt_opt_val, fmt_opt_eq_val, fmt_str
)


def single_lambda_2star(x, y, z):
    return ["piggies=[{0},{1},{2}]".format(x, y, z)]


ARG_FORMATS = dict(
    simple_boolean__true=(fmt_bool("--superflag"), True, ["--superflag"]),
    simple_boolean__false=(fmt_bool("--superflag"), False, []),
    simple_boolean__none=(fmt_bool("--superflag"), False, []),
    simple_boolean_not__true=(fmt_bool_not("--superflag"), True, []),
    simple_boolean_not__false=(fmt_bool_not("--superflag"), False, ["--superflag"]),
    simple_boolean_not__none=(fmt_bool_not("--superflag"), False, ["--superflag"]),
    simple_opt_val__str=(fmt_opt_val("-t"), "potatoes", ["-t", "potatoes"]),
    simple_opt_val__int=(fmt_opt_val("-t"), 42, ["-t", "42"]),
    simple_opt_eq_val__str=(fmt_opt_eq_val("--food"), "potatoes", ["--food=potatoes"]),
    simple_opt_eq_val__int=(fmt_opt_eq_val("--answer"), 42, ["--answer=42"]),
)
ARG_FORMATS_IDS = sorted(ARG_FORMATS.keys())


@pytest.mark.parametrize('fmt, value, expected',
                         (ARG_FORMATS[tc] for tc in ARG_FORMATS_IDS),
                         ids=ARG_FORMATS_IDS)
def test_arg_format(fmt, value, expected):
    actual = fmt(value)
    print("formatted string = {0}".format(actual))
    assert actual == expected, "actual = {0}".format(actual)

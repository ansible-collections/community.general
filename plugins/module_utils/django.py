# -*- coding: utf-8 -*-
# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


from ansible_collections.community.general.plugins.module_utils.cmd_runner import cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.python_runner import PythonRunner
from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper


django_std_args = dict(
    # environmental options
    venv=dict(type="path"),
    # default options of django-admin
    settings=dict(type="str", required=True),
    pythonpath=dict(type="path"),
    traceback=dict(type="bool"),
    verbosity=dict(type="int", choices=[0, 1, 2, 3]),
    skip_checks=dict(type="bool"),
)

_django_std_arg_fmts = dict(
    command=cmd_runner_fmt.as_list(),
    settings=cmd_runner_fmt.as_opt_eq_val("--settings"),
    pythonpath=cmd_runner_fmt.as_opt_eq_val("--pythonpath"),
    traceback=cmd_runner_fmt.as_bool("--traceback"),
    verbosity=cmd_runner_fmt.as_opt_val("--verbosity"),
    no_color=cmd_runner_fmt.as_fixed("--no-color"),
    skip_checks=cmd_runner_fmt.as_bool("--skip-checks"),
)


class _DjangoRunner(PythonRunner):
    def __init__(self, module, arg_formats=None, **kwargs):
        arg_fmts = dict(arg_formats) if arg_formats else {}
        arg_fmts.update(_django_std_arg_fmts)

        super(_DjangoRunner, self).__init__(module, ["-m", "django"], arg_formats=arg_fmts, **kwargs)

    def __call__(self, output_process=None, ignore_value_none=True, check_mode_skip=False, check_mode_return=None, **kwargs):
        args_order = (
            ("command", "no_color", "settings", "pythonpath", "traceback", "verbosity", "skip_checks") + self._prepare_args_order(self.default_args_order)
        )
        return super(_DjangoRunner, self).__call__(args_order, output_process, ignore_value_none, check_mode_skip, check_mode_return, **kwargs)


class DjangoModuleHelper(ModuleHelper):
    module = {}
    use_old_vardict = False
    django_admin_cmd = None
    arg_formats = {}
    django_admin_arg_order = ()

    def __init__(self):
        argument_spec = dict(django_std_args)
        argument_spec.update(self.module.get("argument_spec", {}))
        self.module["argument_spec"] = argument_spec
        super(DjangoModuleHelper, self).__init__(self.module)
        if self.django_admin_cmd is not None:
            self.vars.command = self.django_admin_cmd

    def __run__(self):
        runner = _DjangoRunner(self.module,
                               default_args_order=self.django_admin_arg_order,
                               arg_formats=self.arg_formats,
                               venv=self.vars.venv,
                               check_rc=True)
        with runner() as ctx:
            results = ctx.run()
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd
            if self.verbosity >= 3:
                self.vars.run_info = ctx.run_info

        return results

    @classmethod
    def execute(cls):
        cls().run()

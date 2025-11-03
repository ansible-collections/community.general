# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t

from ansible.module_utils.common.dict_transformations import dict_merge
from ansible_collections.community.general.plugins.module_utils import cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils.python_runner import PythonRunner
from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper

if t.TYPE_CHECKING:
    from .cmd_runner_fmt import ArgFormatType


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
_database_dash = dict(
    database=dict(type="str", default="default"),
)
_data = dict(
    excludes=dict(type="list", elements="str"),
    format=dict(type="str", default="json", choices=["xml", "json", "jsonl", "yaml"]),
)
_pks = dict(
    primary_keys=dict(type="list", elements="str"),
)

_django_std_arg_fmts: dict[str, ArgFormatType] = dict(
    all=cmd_runner_fmt.as_bool("--all"),
    app=cmd_runner_fmt.as_opt_val("--app"),
    apps=cmd_runner_fmt.as_list(),
    apps_models=cmd_runner_fmt.as_list(),
    check=cmd_runner_fmt.as_bool("--check"),
    command=cmd_runner_fmt.as_list(),
    database_dash=cmd_runner_fmt.as_opt_eq_val("--database"),
    database_stacked_dash=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("--database"),
    deploy=cmd_runner_fmt.as_bool("--deploy"),
    dry_run=cmd_runner_fmt.as_bool("--dry-run"),
    excludes=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("--exclude"),
    fail_level=cmd_runner_fmt.as_opt_val("--fail-level"),
    fixture=cmd_runner_fmt.as_opt_val("--output"),
    fixtures=cmd_runner_fmt.as_list(),
    format=cmd_runner_fmt.as_opt_val("--format"),
    ignore_non_existent=cmd_runner_fmt.as_bool("--ignorenonexistent"),
    indent=cmd_runner_fmt.as_opt_val("--indent"),
    natural_foreign=cmd_runner_fmt.as_bool("--natural-foreign"),
    natural_primary=cmd_runner_fmt.as_bool("--natural-primary"),
    no_color=cmd_runner_fmt.as_fixed("--no-color"),
    noinput=cmd_runner_fmt.as_fixed("--noinput"),
    primary_keys=lambda v: ["--pks", ",".join(v)],
    pythonpath=cmd_runner_fmt.as_opt_eq_val("--pythonpath"),
    settings=cmd_runner_fmt.as_opt_eq_val("--settings"),
    skip_checks=cmd_runner_fmt.as_bool("--skip-checks"),
    tags=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("--tag"),
    traceback=cmd_runner_fmt.as_bool("--traceback"),
    verbosity=cmd_runner_fmt.as_opt_val("--verbosity"),
    version=cmd_runner_fmt.as_fixed("--version"),
)

# keys can be used in _django_args
_args_menu = dict(
    std=(django_std_args, _django_std_arg_fmts),
    database=(_database_dash, {"database": _django_std_arg_fmts["database_dash"]}),  # deprecate, remove in 13.0.0
    noinput=({}, {"noinput": cmd_runner_fmt.as_fixed("--noinput")}),  # deprecate, remove in 13.0.0
    dry_run=({}, {"dry_run": cmd_runner_fmt.as_bool("--dry-run")}),  # deprecate, remove in 13.0.0
    check=({}, {"check": cmd_runner_fmt.as_bool("--check")}),  # deprecate, remove in 13.0.0
    database_dash=(_database_dash, {}),
    data=(_data, {}),
)


class _DjangoRunner(PythonRunner):
    def __init__(self, module, arg_formats=None, **kwargs):
        arg_fmts = dict(arg_formats) if arg_formats else {}
        arg_fmts.update(_django_std_arg_fmts)

        super().__init__(module, ["-m", "django"], arg_formats=arg_fmts, **kwargs)

    def __call__(self, output_process=None, check_mode_skip=False, check_mode_return=None, **kwargs):
        args_order = (
            "command",
            "no_color",
            "settings",
            "pythonpath",
            "traceback",
            "verbosity",
            "skip_checks",
        ) + self._prepare_args_order(self.default_args_order)
        return super().__call__(
            args_order, output_process, check_mode_skip=check_mode_skip, check_mode_return=check_mode_return, **kwargs
        )

    def bare_context(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class DjangoModuleHelper(ModuleHelper):
    module = {}
    django_admin_cmd: str | None = None
    arg_formats: dict[str, ArgFormatType] = {}
    django_admin_arg_order: tuple[str, ...] | str = ()
    _django_args: list[str] = []
    _check_mode_arg: str = ""

    def __init__(self):
        self.module["argument_spec"], self.arg_formats = self._build_args(
            self.module.get("argument_spec", {}), self.arg_formats, *(["std"] + self._django_args)
        )
        super().__init__(self.module)
        if self.django_admin_cmd is not None:
            self.vars.command = self.django_admin_cmd

    @staticmethod
    def _build_args(arg_spec, arg_format, *names):
        res_arg_spec = {}
        res_arg_fmts = {}
        for name in names:
            args, fmts = _args_menu[name]
            res_arg_spec = dict_merge(res_arg_spec, args)
            res_arg_fmts = dict_merge(res_arg_fmts, fmts)
        res_arg_spec = dict_merge(res_arg_spec, arg_spec)
        res_arg_fmts = dict_merge(res_arg_fmts, arg_format)

        return res_arg_spec, res_arg_fmts

    def __run__(self):
        runner = _DjangoRunner(
            self.module,
            default_args_order=self.django_admin_arg_order,
            arg_formats=self.arg_formats,
            venv=self.vars.venv,
            check_rc=True,
        )

        run_params = self.vars.as_dict()
        if self._check_mode_arg:
            run_params.update({self._check_mode_arg: self.check_mode})

        rc, out, err = runner.bare_context("version").run()
        self.vars.version = out.strip()

        with runner() as ctx:
            results = ctx.run(**run_params)
            self.vars.stdout = ctx.results_out
            self.vars.stderr = ctx.results_err
            self.vars.cmd = ctx.cmd
            self.vars.set("run_info", ctx.run_info, verbosity=3)

        return results

    @classmethod
    def execute(cls):
        cls().run()

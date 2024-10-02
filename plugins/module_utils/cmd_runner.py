# -*- coding: utf-8 -*-
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

from ansible.module_utils.common.collections import is_sequence
from ansible.module_utils.common.locale import get_best_parsable_locale
from ansible_collections.community.general.plugins.module_utils import cmd_runner_fmt


def _ensure_list(value):
    return list(value) if is_sequence(value) else [value]


def _process_as_is(rc, out, err):
    return rc, out, err


class CmdRunnerException(Exception):
    pass


class MissingArgumentFormat(CmdRunnerException):
    def __init__(self, arg, args_order, args_formats):
        self.args_order = args_order
        self.arg = arg
        self.args_formats = args_formats

    def __repr__(self):
        return "MissingArgumentFormat({0!r}, {1!r}, {2!r})".format(
            self.arg,
            self.args_order,
            self.args_formats,
        )

    def __str__(self):
        return "Cannot find format for parameter {0} {1} in: {2}".format(
            self.arg,
            self.args_order,
            self.args_formats,
        )


class MissingArgumentValue(CmdRunnerException):
    def __init__(self, args_order, arg):
        self.args_order = args_order
        self.arg = arg

    def __repr__(self):
        return "MissingArgumentValue({0!r}, {1!r})".format(
            self.args_order,
            self.arg,
        )

    def __str__(self):
        return "Cannot find value for parameter {0} in {1}".format(
            self.arg,
            self.args_order,
        )


class FormatError(CmdRunnerException):
    def __init__(self, name, value, args_formats, exc):
        self.name = name
        self.value = value
        self.args_formats = args_formats
        self.exc = exc
        super(FormatError, self).__init__()

    def __repr__(self):
        return "FormatError({0!r}, {1!r}, {2!r}, {3!r})".format(
            self.name,
            self.value,
            self.args_formats,
            self.exc,
        )

    def __str__(self):
        return "Failed to format parameter {0} with value {1}: {2}".format(
            self.name,
            self.value,
            self.exc,
        )


class CmdRunner(object):
    """
    Wrapper for ``AnsibleModule.run_command()``.

    It aims to provide a reusable runner with consistent argument formatting
    and sensible defaults.
    """

    @staticmethod
    def _prepare_args_order(order):
        return tuple(order) if is_sequence(order) else tuple(order.split())

    def __init__(self, module, command, arg_formats=None, default_args_order=(),
                 check_rc=False, force_lang="C", path_prefix=None, environ_update=None):
        self.module = module
        self.command = _ensure_list(command)
        self.default_args_order = self._prepare_args_order(default_args_order)
        if arg_formats is None:
            arg_formats = {}
        self.arg_formats = {}
        for fmt_name, fmt in arg_formats.items():
            if not cmd_runner_fmt.is_argformat(fmt):
                fmt = cmd_runner_fmt.as_func(func=fmt, ignore_none=True)
            self.arg_formats[fmt_name] = fmt
        self.check_rc = check_rc
        if force_lang == "auto":
            try:
                self.force_lang = get_best_parsable_locale(module)
            except RuntimeWarning:
                self.force_lang = "C"
        else:
            self.force_lang = force_lang
        self.path_prefix = path_prefix
        if environ_update is None:
            environ_update = {}
        self.environ_update = environ_update

        _cmd = self.command[0]
        self.command[0] = _cmd if (os.path.isabs(_cmd) or '/' in _cmd) else module.get_bin_path(_cmd, opt_dirs=path_prefix, required=True)

    @property
    def binary(self):
        return self.command[0]

    # remove parameter ignore_value_none in community.general 12.0.0
    def __call__(self, args_order=None, output_process=None, ignore_value_none=None, check_mode_skip=False, check_mode_return=None, **kwargs):
        if ignore_value_none is None:
            ignore_value_none = True
        else:
            self.module.deprecate(
                "Using ignore_value_none when creating the runner context is now deprecated, "
                "and the parameter will be removed in community.general 12.0.0. ",
                version="12.0.0", collection_name="community.general"
            )
        if output_process is None:
            output_process = _process_as_is
        if args_order is None:
            args_order = self.default_args_order
        args_order = self._prepare_args_order(args_order)
        for p in args_order:
            if p not in self.arg_formats:
                raise MissingArgumentFormat(p, args_order, tuple(self.arg_formats.keys()))
        return _CmdRunnerContext(runner=self,
                                 args_order=args_order,
                                 output_process=output_process,
                                 ignore_value_none=ignore_value_none,           # DEPRECATION: remove in community.general 12.0.0
                                 check_mode_skip=check_mode_skip,
                                 check_mode_return=check_mode_return, **kwargs)

    def has_arg_format(self, arg):
        return arg in self.arg_formats

    # not decided whether to keep it or not, but if deprecating it will happen in a farther future.
    context = __call__


class _CmdRunnerContext(object):
    def __init__(self, runner, args_order, output_process, ignore_value_none, check_mode_skip, check_mode_return, **kwargs):
        self.runner = runner
        self.args_order = tuple(args_order)
        self.output_process = output_process
        # DEPRECATION: parameter ignore_value_none at the context level is deprecated and will be removed in community.general 12.0.0
        self.ignore_value_none = ignore_value_none
        self.check_mode_skip = check_mode_skip
        self.check_mode_return = check_mode_return
        self.run_command_args = dict(kwargs)

        self.environ_update = runner.environ_update
        self.environ_update.update(self.run_command_args.get('environ_update', {}))
        if runner.force_lang:
            self.environ_update.update({
                'LANGUAGE': runner.force_lang,
                'LC_ALL': runner.force_lang,
            })
        self.run_command_args['environ_update'] = self.environ_update

        if 'check_rc' not in self.run_command_args:
            self.run_command_args['check_rc'] = runner.check_rc
        self.check_rc = self.run_command_args['check_rc']

        self.cmd = None
        self.results_rc = None
        self.results_out = None
        self.results_err = None
        self.results_processed = None

    def run(self, **kwargs):
        runner = self.runner
        module = self.runner.module
        self.cmd = list(runner.command)
        self.context_run_args = dict(kwargs)

        named_args = dict(module.params)
        named_args.update(kwargs)
        for arg_name in self.args_order:
            value = None
            try:
                if arg_name in named_args:
                    value = named_args[arg_name]
                elif not runner.arg_formats[arg_name].ignore_missing_value:
                    raise MissingArgumentValue(self.args_order, arg_name)
                # DEPRECATION: remove parameter ctx_ignore_none in 12.0.0
                self.cmd.extend(runner.arg_formats[arg_name](value, ctx_ignore_none=self.ignore_value_none))
            except MissingArgumentValue:
                raise
            except Exception as e:
                raise FormatError(arg_name, value, runner.arg_formats[arg_name], e)

        if self.check_mode_skip and module.check_mode:
            return self.check_mode_return
        results = module.run_command(self.cmd, **self.run_command_args)
        self.results_rc, self.results_out, self.results_err = results
        self.results_processed = self.output_process(*results)
        return self.results_processed

    @property
    def run_info(self):
        return dict(
            ignore_value_none=self.ignore_value_none,         # DEPRECATION: remove in community.general 12.0.0
            check_rc=self.check_rc,
            environ_update=self.environ_update,
            args_order=self.args_order,
            cmd=self.cmd,
            run_command_args=self.run_command_args,
            context_run_args=self.context_run_args,
            results_rc=self.results_rc,
            results_out=self.results_out,
            results_err=self.results_err,
            results_processed=self.results_processed,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

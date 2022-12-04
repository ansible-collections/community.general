# -*- coding: utf-8 -*-
# Copyright (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from functools import wraps

from ansible.module_utils.common.collections import is_sequence
from ansible.module_utils.six import iteritems


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


class _ArgFormat(object):
    def __init__(self, func, ignore_none=None, ignore_missing_value=False):
        self.func = func
        self.ignore_none = ignore_none
        self.ignore_missing_value = ignore_missing_value

    def __call__(self, value, ctx_ignore_none):
        ignore_none = self.ignore_none if self.ignore_none is not None else ctx_ignore_none
        if value is None and ignore_none:
            return []
        f = self.func
        return [str(x) for x in f(value)]


class _Format(object):
    @staticmethod
    def as_bool(args_true, args_false=None, ignore_none=None):
        if args_false is not None:
            if ignore_none is None:
                ignore_none = False
        else:
            args_false = []
        return _ArgFormat(lambda value: _ensure_list(args_true) if value else _ensure_list(args_false), ignore_none=ignore_none)

    @staticmethod
    def as_bool_not(args):
        return _ArgFormat(lambda value: [] if value else _ensure_list(args), ignore_none=False)

    @staticmethod
    def as_optval(arg, ignore_none=None):
        return _ArgFormat(lambda value: ["{0}{1}".format(arg, value)], ignore_none=ignore_none)

    @staticmethod
    def as_opt_val(arg, ignore_none=None):
        return _ArgFormat(lambda value: [arg, value], ignore_none=ignore_none)

    @staticmethod
    def as_opt_eq_val(arg, ignore_none=None):
        return _ArgFormat(lambda value: ["{0}={1}".format(arg, value)], ignore_none=ignore_none)

    @staticmethod
    def as_list(ignore_none=None):
        return _ArgFormat(_ensure_list, ignore_none=ignore_none)

    @staticmethod
    def as_fixed(args):
        return _ArgFormat(lambda value: _ensure_list(args), ignore_none=False, ignore_missing_value=True)

    @staticmethod
    def as_func(func, ignore_none=None):
        return _ArgFormat(func, ignore_none=ignore_none)

    @staticmethod
    def as_map(_map, default=None, ignore_none=None):
        if default is None:
            default = []
        return _ArgFormat(lambda value: _ensure_list(_map.get(value, default)), ignore_none=ignore_none)

    @staticmethod
    def as_default_type(_type, arg="", ignore_none=None):
        fmt = _Format
        if _type == "dict":
            return fmt.as_func(lambda d: ["--{0}={1}".format(*a) for a in iteritems(d)], ignore_none=ignore_none)
        if _type == "list":
            return fmt.as_func(lambda value: ["--{0}".format(x) for x in value], ignore_none=ignore_none)
        if _type == "bool":
            return fmt.as_bool("--{0}".format(arg))

        return fmt.as_opt_val("--{0}".format(arg), ignore_none=ignore_none)

    @staticmethod
    def unpack_args(func):
        @wraps(func)
        def wrapper(v):
            return func(*v)
        return wrapper

    @staticmethod
    def unpack_kwargs(func):
        @wraps(func)
        def wrapper(v):
            return func(**v)
        return wrapper


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
        self.arg_formats = dict(arg_formats)
        self.check_rc = check_rc
        self.force_lang = force_lang
        self.path_prefix = path_prefix
        if environ_update is None:
            environ_update = {}
        self.environ_update = environ_update

        self.command[0] = module.get_bin_path(self.command[0], opt_dirs=path_prefix, required=True)

        for mod_param_name, spec in iteritems(module.argument_spec):
            if mod_param_name not in self.arg_formats:
                self.arg_formats[mod_param_name] = _Format.as_default_type(spec['type'], mod_param_name)

    def __call__(self, args_order=None, output_process=None, ignore_value_none=True, check_mode_skip=False, check_mode_return=None, **kwargs):
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
                                 ignore_value_none=ignore_value_none,
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
            ignore_value_none=self.ignore_value_none,
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


cmd_runner_fmt = _Format()

#
# The fmt form is deprecated and will be removed in community.general 7.0.0
# Please use:
#   cmd_runner_fmt
# Or, to retain the same effect, use:
#   from ansible_collections.community.general.plugins.module_utils.cmd_runner import cmd_runner_fmt as fmt
fmt = cmd_runner_fmt

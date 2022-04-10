# -*- coding: utf-8 -*-
# (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.common.collections import is_sequence
from ansible.module_utils.six import iteritems


def _process_as_is(rc, out, err):
    return rc, out, err


class MissingArgumentFormat(Exception):
    def __init__(self, param, params_order, args_formats):
        self.params_order = params_order
        self.param = param
        self.args_formats = args_formats

    def __repr__(self):
        return "<MissingArgumentFormat: {0} order: {1} formats: {2}>".format(
            self.param,
            self.params_order,
            self.args_formats,
        )

    def __str__(self):
        return "Cannot find format for parameter {0} {1} in: {2}".format(
            self.param,
            self.params_order,
            self.args_formats,
        )


class MissingArgumentValue(Exception):
    def __init__(self, params_order, param):
        self.params_order = params_order
        self.param = param

    def __repr__(self):
        return "<MissingArgumentValue: {0} order: {1}>".format(
            self.param,
            self.params_order,
        )

    def __str__(self):
        return "Cannot find value for parameter {0} in {1}".format(
            self.param,
            self.params_order,
        )


class FormatError(Exception):
    def __init__(self, name, value, args_formats, exc):
        self.name = name
        self.value = value
        self.args_formats = args_formats
        self.exc = exc
        super(FormatError, self).__init__()

    def __repr__(self):
        return "<FormatError: name: {0} value: {1} exc: {2}>".format(
            self.name,
            self.value,
            self.exc,
        )

    def __str__(self):
        return "Failed to format parameter {0} with value {1}: {2}".format(
            self.name,
            self.value,
            self.exc,
        )


def fmt_bool(option):
    return lambda value: [option] if value else []


def fmt_bool_not(option):
    return lambda value: [] if value else [option]


def fmt_optval(option):
    return lambda value: ["{0}{1}".format(option, str(value))]


def fmt_opt_val(option):
    return lambda value: [option, str(value)]


def fmt_opt_eq_val(option):
    return lambda value: ["{0}={1}".format(option, value)]


def fmt_str():
    return lambda value: [str(value)]


def fmt_mapped(_map, default=None, list_around=True):
    def fmt(value):
        res = _map.get(value, default)
        return [str(res)] if list_around else [str(x) for x in res]
    return fmt


def fmt_default_type(_type, option=""):
    if _type == "dict":
        return lambda value: ["{0}={1}".format(k, v) for k, v in iteritems(value)]
    if _type == "list":
        return lambda value: [str(x) for x in value]
    if _type == "bool":
        return fmt_bool("--{0}".format(option))

    return fmt_opt_val("--{0}".format(option))


def fmt_unpack(stars):
    if stars == 1:
        def deco(f):
            return lambda v: f(*v)
        return deco
    elif stars == 2:
        def deco(f):
            return lambda v: f(**v)
        return deco

    return lambda f: f


class CmdRunner:
    def __init__(self, module, command, arg_formats=None, default_param_order=(), check_rc=False, force_lang="C", path_prefix=None):
        self.module = module
        self.command = list(command) if is_sequence(command) else [command]
        self.default_param_order = tuple(default_param_order)
        if arg_formats is None:
            arg_formats = {}
        self.arg_formats = dict(arg_formats)
        self.check_rc = check_rc
        self.force_lang = force_lang
        self.path_prefix = path_prefix

        self.command[0] = module.get_bin_path(command[0], opt_dirs=path_prefix)

        for mod_param_name, spec in iteritems(module.argument_spec):
            if mod_param_name not in self.arg_formats:
                self.arg_formats[mod_param_name] = fmt_default_type(spec['type'], mod_param_name)

    def context(self, params_order=None, output_process=None, ignore_value_none=True, **kwargs):
        if output_process is None:
            output_process = _process_as_is
        if params_order is None:
            params_order = self.default_param_order
        params_order = tuple(params_order)
        for p in params_order:
            if p not in self.arg_formats:
                raise MissingArgumentFormat(p, params_order, tuple(self.arg_formats.keys()))
        return _CmdRunnerContext(runner=self, params_order=params_order, output_process=output_process, ignore_value_none=ignore_value_none, **kwargs)

    def has_arg_format(self, arg):
        return arg in self.arg_formats


class _CmdRunnerContext:
    def __init__(self, runner, params_order, output_process, ignore_value_none=True, **kwargs):
        self.runner = runner
        self.params_order = tuple(params_order)
        self.output_process = output_process
        self.ignore_value_none = ignore_value_none
        self.run_command_args = dict(kwargs)

        self.env_update = self.run_command_args.get('environ_update', {})
        if runner.force_lang:
            self.env_update.update({
                'LANGUAGE': runner.force_lang,
                'LC_ALL': runner.force_lang,
            })
        self.run_command_args['environ_update'] = self.env_update

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
        self.run_args = dict(kwargs)

        named_params = dict(module.params)
        named_params.update(kwargs)
        for param_name in self.params_order:
            value = None
            try:
                value = named_params[param_name]
                if self.ignore_value_none and value is None:
                    continue
                self.cmd.extend(runner.arg_formats[param_name](value))
            except KeyError:
                raise MissingArgumentValue(self.params_order, param_name)
            except Exception as e:
                raise FormatError(param_name, value, runner.arg_formats[param_name], e)

        results = module.run_command(self.cmd, **self.run_command_args)
        self.results_rc, self.results_out, self.results_err = results
        self.results_processed = self.output_process(*results)
        return self.results_processed

    @property
    def run_info(self):
        return dict(
            params_order=self.params_order,
            ignore_value_none=self.ignore_value_none,
            run_command_args=self.run_command_args,
            check_rc=self.check_rc,
            env_update=self.env_update,
            cmd=self.cmd,
            run_args=self.run_args,
            results_rc=self.results_rc,
            results_out=self.results_out,
            results_err=self.results_err,
            results_processed=self.results_processed,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

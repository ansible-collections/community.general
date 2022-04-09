# -*- coding: utf-8 -*-
# (c) 2022, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.common.collections import is_sequence
from ansible.module_utils.six import iteritems


def _process_as_is(rc, out, err):
    return rc, out, err


class InvalidParameterName(Exception):
    def __init__(self, name):
        super(InvalidParameterName, self).__init__("Parameter '{0}' is not recognized by runner".format(name))


class MissingArgumentValue(Exception):
    def __init__(self, params_order, param):
        self.params_order = params_order
        self.param = param


class CmdRunnerException(Exception):
    def __init__(self, name, value, args_formats, exc):
        self.name = name
        self.value = value
        self.args_formats = args_formats
        self.exc = exc
        super(CmdRunnerException, self).__init__()


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


class CmdRunner:
    def __init__(self, module, command, arg_formats=None, default_param_order=(), check_rc=False, force_lang="C", path_prefix=None):
        self.module = module
        self.command = list(command) if is_sequence(command) else [command]
        self.default_param_order = tuple(default_param_order)
        self.args_formats = dict(arg_formats) or {}
        self.check_rc = check_rc
        self.force_lang = force_lang
        self.path_prefix = path_prefix

        self.command[0] = module.get_bin_path(command[0], opt_dirs=path_prefix)

        for mod_param_name, spec in iteritems(module.argument_spec):
            if mod_param_name not in self.args_formats:
                self.args_formats[mod_param_name] = fmt_default_type(spec['type'], mod_param_name)

    def context(self, params_order=None, output_process=None, ignore_value_none=True, **kwargs):
        if output_process is None:
            output_process = _process_as_is
        if params_order is None:
            params_order = self.default_param_order
        return _CmdRunnerContext(runner=self, params_order=params_order, output_process=output_process, ignore_value_none=ignore_value_none, **kwargs)

    def has_arg_format(self, arg):
        return arg in self.args_formats

class _CmdRunnerContext:
    def __init__(self, runner, params_order, output_process, ignore_value_none=True, **kwargs):
        self.runner = runner
        self.params_order = params_order
        self.output_process = output_process
        self.ignore_value_none = ignore_value_none
        self.kwargs = dict(kwargs)

        for p in params_order:
            if p not in runner.args_formats:
                raise InvalidParameterName(p)

        self.env_update = dict(kwargs.get('environ_update', {}))
        if runner.force_lang:
            self.env_update.update({
                'LANGUAGE': runner.force_lang,
                'LC_ALL': runner.force_lang,
            })

    def run(self, *args, **kwargs):
        runner = self.runner
        module = self.runner.module
        cmd = list(runner.command)

        arg_stack = list(reversed(args))
        named_params = dict(kwargs)
        named_params.update(module.params)
        params = []
        for p in self.params_order:
            try:
                try:
                    params.append(named_params[p])
                except KeyError:
                    # only want to pop an arg from the stack if it's not a module param
                    params.append(arg_stack.pop())
            except IndexError:
                raise MissingArgumentValue(self.params_order, p)

        for name, value in zip(self.params_order, params):
            if self.ignore_value_none and value is None:
                continue
            try:
                cmd.extend(runner.args_formats[name](value))
            except Exception as e:
                raise CmdRunnerException(name, value, runner.args_formats[name], e)

        environ_update = self.env_update
        check_rc = self.kwargs.get('check_rc', runner.check_rc)
        results = module.run_command(cmd, environ_update=environ_update, check_rc=check_rc, **self.kwargs)
        return self.output_process(*results)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

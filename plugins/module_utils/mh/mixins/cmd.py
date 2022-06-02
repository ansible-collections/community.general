# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from functools import partial


class ArgFormat(object):
    """
    Argument formatter for use as a command line parameter. Used in CmdMixin.
    """
    BOOLEAN = 0
    PRINTF = 1
    FORMAT = 2
    BOOLEAN_NOT = 3

    @staticmethod
    def stars_deco(num):
        if num == 1:
            def deco(f):
                return lambda v: f(*v)
            return deco
        elif num == 2:
            def deco(f):
                return lambda v: f(**v)
            return deco

        return lambda f: f

    def __init__(self, name, fmt=None, style=FORMAT, stars=0):
        """
        Creates a CLI-formatter for one specific argument. The argument may be a module parameter or just a named parameter for
        the CLI command execution.
        :param name: Name of the argument to be formatted
        :param fmt: Either a str to be formatted (using or not printf-style) or a callable that does that
        :param style: Whether arg_format (as str) should use printf-style formatting.
                             Ignored if arg_format is None or not a str (should be callable).
        :param stars: A int with 0, 1 or 2 value, indicating to formatting the value as: value, *value or **value
        """
        def printf_fmt(_fmt, v):
            try:
                return [_fmt % v]
            except TypeError as e:
                if e.args[0] != 'not all arguments converted during string formatting':
                    raise
                return [_fmt]

        _fmts = {
            ArgFormat.BOOLEAN: lambda _fmt, v: ([_fmt] if bool(v) else []),
            ArgFormat.BOOLEAN_NOT: lambda _fmt, v: ([] if bool(v) else [_fmt]),
            ArgFormat.PRINTF: printf_fmt,
            ArgFormat.FORMAT: lambda _fmt, v: [_fmt.format(v)],
        }

        self.name = name
        self.stars = stars
        self.style = style

        if fmt is None:
            fmt = "{0}"
            style = ArgFormat.FORMAT

        if isinstance(fmt, str):
            func = _fmts[style]
            self.arg_format = partial(func, fmt)
        elif isinstance(fmt, list) or isinstance(fmt, tuple):
            self.arg_format = lambda v: [_fmts[style](f, v)[0] for f in fmt]
        elif hasattr(fmt, '__call__'):
            self.arg_format = fmt
        else:
            raise TypeError('Parameter fmt must be either: a string, a list/tuple of '
                            'strings or a function: type={0}, value={1}'.format(type(fmt), fmt))

        if stars:
            self.arg_format = (self.stars_deco(stars))(self.arg_format)

    def to_text(self, value):
        if value is None and self.style != ArgFormat.BOOLEAN_NOT:
            return []
        func = self.arg_format
        return [str(p) for p in func(value)]


class CmdMixin(object):
    """
    Mixin for mapping module options to running a CLI command with its arguments.
    """
    command = None
    command_args_formats = {}
    run_command_fixed_options = {}
    check_rc = False
    force_lang = "C"

    @property
    def module_formats(self):
        result = {}
        for param in self.module.params.keys():
            result[param] = ArgFormat(param)
        return result

    @property
    def custom_formats(self):
        result = {}
        for param, fmt_spec in self.command_args_formats.items():
            result[param] = ArgFormat(param, **fmt_spec)
        return result

    def _calculate_args(self, extra_params=None, params=None):
        def add_arg_formatted_param(_cmd_args, arg_format, _value):
            args = list(arg_format.to_text(_value))
            return _cmd_args + args

        def find_format(_param):
            return self.custom_formats.get(_param, self.module_formats.get(_param))

        extra_params = extra_params or dict()
        cmd_args = list([self.command]) if isinstance(self.command, str) else list(self.command)
        try:
            cmd_args[0] = self.module.get_bin_path(cmd_args[0], required=True)
        except ValueError:
            pass
        param_list = params if params else self.vars.keys()

        for param in param_list:
            if isinstance(param, dict):
                if len(param) != 1:
                    self.do_raise("run_command parameter as a dict must contain only one key: {0}".format(param))
                _param = list(param.keys())[0]
                fmt = find_format(_param)
                value = param[_param]
            elif isinstance(param, str):
                if param in self.vars.keys():
                    fmt = find_format(param)
                    value = self.vars[param]
                elif param in extra_params:
                    fmt = find_format(param)
                    value = extra_params[param]
                else:
                    self.do_raise('Cannot determine value for parameter: {0}'.format(param))
            else:
                self.do_raise("run_command parameter must be either a str or a dict: {0}".format(param))
            cmd_args = add_arg_formatted_param(cmd_args, fmt, value)

        return cmd_args

    def process_command_output(self, rc, out, err):
        return rc, out, err

    def run_command(self,
                    extra_params=None,
                    params=None,
                    process_output=None,
                    publish_rc=True,
                    publish_out=True,
                    publish_err=True,
                    publish_cmd=True,
                    *args, **kwargs):
        cmd_args = self._calculate_args(extra_params, params)
        options = dict(self.run_command_fixed_options)
        options['check_rc'] = options.get('check_rc', self.check_rc)
        options.update(kwargs)
        env_update = dict(options.get('environ_update', {}))
        if self.force_lang:
            env_update.update({
                'LANGUAGE': self.force_lang,
                'LC_ALL': self.force_lang,
            })
            self.update_output(force_lang=self.force_lang)
            options['environ_update'] = env_update
        rc, out, err = self.module.run_command(cmd_args, *args, **options)
        if publish_rc:
            self.update_output(rc=rc)
        if publish_out:
            self.update_output(stdout=out)
        if publish_err:
            self.update_output(stderr=err)
        if publish_cmd:
            self.update_output(cmd_args=cmd_args)
        if process_output is None:
            _process = self.process_command_output
        else:
            _process = process_output

        return _process(rc, out, err)

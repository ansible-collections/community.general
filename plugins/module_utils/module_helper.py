# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from functools import partial, wraps
import traceback

from ansible.module_utils.basic import AnsibleModule


class ModuleHelperException(Exception):
    @staticmethod
    def _get_remove(key, kwargs):
        if key in kwargs:
            result = kwargs[key]
            del kwargs[key]
            return result
        return None

    def __init__(self, *args, **kwargs):
        self.msg = self._get_remove('msg', kwargs) or "Module failed with exception: {0}".format(self)
        self.update_output = self._get_remove('update_output', kwargs) or {}
        super(ModuleHelperException, self).__init__(*args, **kwargs)


class ArgFormat(object):
    """
    Argument formatter
    """
    BOOLEAN = 0
    PRINTF = 1
    FORMAT = 2

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
        Creates a new formatter
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
            ArgFormat.PRINTF: printf_fmt,
            ArgFormat.FORMAT: lambda _fmt, v: [_fmt.format(v)],
        }

        self.name = name
        self.stars = stars

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
        func = self.arg_format
        return [str(p) for p in func(value)]


def cause_changes(func, on_success=True, on_failure=False):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            func(*args, **kwargs)
            if on_success:
                self.changed = True
        except Exception as e:
            if on_failure:
                self.changed = True
            raise
    return wrapper


def module_fails_on_exception(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except SystemExit:
            raise
        except ModuleHelperException as e:
            if e.update_output:
                self.update_output(e.update_output)
        except Exception as e:
            self.vars.msg = "Module failed with exception: {0}".format(str(e).strip())
            self.vars.exception = traceback.format_exc()
            self.module.fail_json(changed=False, msg=self.vars.msg, exception=self.vars.exception, output=self.output, vars=self.vars)
    return wrapper


class DependencyCtxMgr(object):
    def __init__(self, name, msg=None):
        self.name = name
        self.msg = msg
        self.has_it = False
        self.exc_type = None
        self.exc_val = None
        self.exc_tb = None

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.has_it = exc_type is None
        self.exc_type = exc_type
        self.exc_val = exc_val
        self.exc_tb = exc_tb
        return not self.has_it

    @property
    def text(self):
        return self.msg or str(self.exc_val)


class ModuleHelper(object):
    _dependencies = []
    module = {}
    facts_name = None

    class AttrDict(dict):
        def __getattr__(self, item):
            return self[item]

    def __init__(self, module=None):
        self.vars = ModuleHelper.AttrDict()
        self.output_dict = dict()
        self.facts_dict = dict()
        self._changed = False

        if module:
            self.module = module

        if isinstance(self.module, dict):
            self.module = AnsibleModule(**self.module)

    def update_output(self, **kwargs):
        self.output_dict.update(kwargs)

    def update_facts(self, **kwargs):
        self.facts_dict.update(kwargs)

    def __init_module__(self):
        pass

    def __run__(self):
        raise NotImplementedError()

    def __quit_module__(self):
        pass

    @property
    def changed(self):
        return self._changed

    @changed.setter
    def changed(self, value):
        self._changed = value

    @property
    def output(self):
        result = dict(self.vars)
        result.update(self.output_dict)
        if self.facts_name:
            result['ansible_facts'] = {self.facts_name: self.facts_dict}
        return result

    @module_fails_on_exception
    def run(self):
        self.fail_on_missing_deps()
        self.__init_module__()
        self.__run__()
        self.__quit_module__()
        self.module.exit_json(changed=self.changed, **self.output_dict)

    @classmethod
    def dependency(cls, name, msg):
        cls._dependencies.append(DependencyCtxMgr(name, msg))
        return cls._dependencies[-1]

    def fail_on_missing_deps(self):
        for d in self._dependencies:
            if not d.has_it:
                self.module.fail_json(changed=False,
                                      exception=d.exc_val.__traceback__.format_exc(),
                                      msg=d.text,
                                      **self.output_dict)


class StateMixin(object):
    state_param = 'state'
    default_state = None

    def _state(self):
        state = self.module.params.get(self.state_param)
        return self.default_state if state is None else state

    def _method(self, state):
        return "{0}_{1}".format(self.state_param, state)

    def __run__(self):
        state = self._state()
        self.vars.state = state

        # resolve aliases
        if state not in self.module.params:
            aliased = [name for name, param in self.module.argument_spec.items() if state in param.get('aliases', [])]
            if aliased:
                state = aliased[0]
                self.vars.effective_state = state

        method = self._method(state)
        if not hasattr(self, method):
            return self.__state_fallback__()
        func = getattr(self, method)
        return func()

    def __state_fallback__(self):
        raise ValueError("Cannot find method: {0}".format(self._method(self._state())))


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
            args = [x for x in arg_format.to_text(_value)]
            return _cmd_args + args

        def find_format(_param):
            return self.custom_formats.get(_param, self.module_formats.get(_param))

        extra_params = extra_params or dict()
        cmd_args = list([self.command]) if isinstance(self.command, str) else list(self.command)
        cmd_args[0] = self.module.get_bin_path(cmd_args[0])
        param_list = params if params else self.module.params.keys()

        for param in param_list:
            if param in self.module.argument_spec:
                if param not in self.module.params:
                    continue
                fmt = find_format(param)
                value = self.module.params[param]
            else:
                if param not in extra_params:
                    continue
                fmt = find_format(param)
                value = extra_params[param]
            self.cmd_args = cmd_args
            cmd_args = add_arg_formatted_param(cmd_args, fmt, value)

        return cmd_args

    def process_command_output(self, rc, out, err):
        return rc, out, err

    def run_command(self, extra_params=None, params=None, *args, **kwargs):
        self.vars['cmd_args'] = self._calculate_args(extra_params, params)
        options = dict(self.run_command_fixed_options)
        env_update = dict(options.get('environ_update', {}))
        options['check_rc'] = options.get('check_rc', self.check_rc)
        if self.force_lang:
            env_update.update({'LANGUAGE': self.force_lang})
            self.update_output(force_lang=self.force_lang)
            options['environ_update'] = env_update
        options.update(kwargs)
        rc, out, err = self.module.run_command(self.vars['cmd_args'], *args, **options)
        self.update_output(rc=rc, stdout=out, stderr=err)
        return self.process_command_output(rc, out, err)


class StateModuleHelper(StateMixin, ModuleHelper):
    pass


class CmdModuleHelper(CmdMixin, ModuleHelper):
    pass


class CmdStateModuleHelper(CmdMixin, StateMixin, ModuleHelper):
    pass

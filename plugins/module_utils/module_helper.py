# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from functools import partial, wraps
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.dict_transformations import dict_merge


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
        super(ModuleHelperException, self).__init__(*args)


class ArgFormat(object):
    """
    Argument formatter for use as a command line parameter. Used in CmdMixin.
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
        if value is None:
            return []
        func = self.arg_format
        return [str(p) for p in func(value)]


def cause_changes(on_success=None, on_failure=None):

    def deco(func):
        if on_success is None and on_failure is None:
            return func

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                self = args[0]
                func(*args, **kwargs)
                if on_success is not None:
                    self.changed = on_success
            except Exception:
                if on_failure is not None:
                    self.changed = on_failure
                raise

        return wrapper

    return deco


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
            self.module.fail_json(msg=e.msg, exception=traceback.format_exc(),
                                  output=self.output, vars=self.vars.output(), **self.output)
        except Exception as e:
            msg = "Module failed with exception: {0}".format(str(e).strip())
            self.module.fail_json(msg=msg, exception=traceback.format_exc(),
                                  output=self.output, vars=self.vars.output(), **self.output)
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
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.has_it = exc_type is None
        self.exc_type = exc_type
        self.exc_val = exc_val
        self.exc_tb = exc_tb
        return not self.has_it

    @property
    def text(self):
        return self.msg or str(self.exc_val)


class VarMeta(object):
    NOTHING = object()

    def __init__(self, diff=False, output=True, change=None, fact=False):
        self.init = False
        self.initial_value = None
        self.value = None

        self.diff = diff
        self.change = diff if change is None else change
        self.output = output
        self.fact = fact

    def set(self, diff=None, output=None, change=None, fact=None, initial_value=NOTHING):
        if diff is not None:
            self.diff = diff
        if output is not None:
            self.output = output
        if change is not None:
            self.change = change
        if fact is not None:
            self.fact = fact
        if initial_value is not self.NOTHING:
            self.initial_value = initial_value

    def set_value(self, value):
        if not self.init:
            self.initial_value = value
            self.init = True
        self.value = value
        return self

    @property
    def has_changed(self):
        return self.change and (self.initial_value != self.value)

    @property
    def diff_result(self):
        return None if not (self.diff and self.has_changed) else {
            'before': self.initial_value,
            'after': self.value,
        }

    def __str__(self):
        return "<VarMeta: value={0}, initial={1}, diff={2}, output={3}, change={4}>".format(
            self.value, self.initial_value, self.diff, self.output, self.change
        )


class ModuleHelper(object):
    _output_conflict_list = ('msg', 'exception', 'output', 'vars', 'changed')
    _dependencies = []
    module = None
    facts_name = None
    output_params = ()
    diff_params = ()
    change_params = ()
    facts_params = ()

    class VarDict(object):
        def __init__(self):
            self._data = dict()
            self._meta = dict()

        def __getitem__(self, item):
            return self._data[item]

        def __setitem__(self, key, value):
            self.set(key, value)

        def __getattr__(self, item):
            try:
                return self._data[item]
            except KeyError:
                return getattr(self._data, item)

        def __setattr__(self, key, value):
            if key in ('_data', '_meta'):
                super(ModuleHelper.VarDict, self).__setattr__(key, value)
            else:
                self.set(key, value)

        def meta(self, name):
            return self._meta[name]

        def set_meta(self, name, **kwargs):
            self.meta(name).set(**kwargs)

        def set(self, name, value, **kwargs):
            if name in ('_data', '_meta'):
                raise ValueError("Names _data and _meta are reserved for use by ModuleHelper")
            self._data[name] = value
            if name in self._meta:
                meta = self.meta(name)
            else:
                meta = VarMeta(**kwargs)
            meta.set_value(value)
            self._meta[name] = meta

        def output(self):
            return dict((k, v) for k, v in self._data.items() if self.meta(k).output)

        def diff(self):
            diff_results = [(k, self.meta(k).diff_result) for k in self._data]
            diff_results = [dr for dr in diff_results if dr[1] is not None]
            if diff_results:
                before = dict((dr[0], dr[1]['before']) for dr in diff_results)
                after = dict((dr[0], dr[1]['after']) for dr in diff_results)
                return {'before': before, 'after': after}
            return None

        def facts(self):
            facts_result = dict((k, v) for k, v in self._data.items() if self._meta[k].fact)
            return facts_result if facts_result else None

        def change_vars(self):
            return [v for v in self._data if self.meta(v).change]

        def has_changed(self, v):
            return self._meta[v].has_changed

    def __init__(self, module=None):
        self.vars = ModuleHelper.VarDict()
        self._changed = False

        if module:
            self.module = module

        if not isinstance(self.module, AnsibleModule):
            self.module = AnsibleModule(**self.module)

        for name, value in self.module.params.items():
            self.vars.set(
                name, value,
                diff=name in self.diff_params,
                output=name in self.output_params,
                change=None if not self.change_params else name in self.change_params,
                fact=name in self.facts_params,
            )

    def update_vars(self, meta=None, **kwargs):
        if meta is None:
            meta = {}
        for k, v in kwargs.items():
            self.vars.set(k, v, **meta)

    def update_output(self, **kwargs):
        self.update_vars(meta={"output": True}, **kwargs)

    def update_facts(self, **kwargs):
        self.update_vars(meta={"fact": True}, **kwargs)

    def __init_module__(self):
        pass

    def __run__(self):
        raise NotImplementedError()

    def __quit_module__(self):
        pass

    def _vars_changed(self):
        return any(self.vars.has_changed(v) for v in self.vars.change_vars())

    @property
    def changed(self):
        return self._changed

    @changed.setter
    def changed(self, value):
        self._changed = value

    def has_changed(self):
        return self.changed or self._vars_changed()

    @property
    def output(self):
        result = dict(self.vars.output())
        if self.facts_name:
            facts = self.vars.facts()
            if facts is not None:
                result['ansible_facts'] = {self.facts_name: facts}
        if self.module._diff:
            diff = result.get('diff', {})
            vars_diff = self.vars.diff() or {}
            result['diff'] = dict_merge(dict(diff), vars_diff)

        for varname in result:
            if varname in self._output_conflict_list:
                result["_" + varname] = result[varname]
                del result[varname]
        return result

    @module_fails_on_exception
    def run(self):
        self.fail_on_missing_deps()
        self.__init_module__()
        self.__run__()
        self.__quit_module__()
        self.module.exit_json(changed=self.has_changed(), **self.output)

    @classmethod
    def dependency(cls, name, msg):
        cls._dependencies.append(DependencyCtxMgr(name, msg))
        return cls._dependencies[-1]

    def fail_on_missing_deps(self):
        for d in self._dependencies:
            if not d.has_it:
                self.module.fail_json(changed=False,
                                      exception="\n".join(traceback.format_exception(d.exc_type, d.exc_val, d.exc_tb)),
                                      msg=d.text,
                                      **self.output)


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
        param_list = params if params else self.module.params.keys()

        for param in param_list:
            if isinstance(param, dict):
                if len(param) != 1:
                    raise ModuleHelperException("run_command parameter as a dict must "
                                                "contain only one key: {0}".format(param))
                _param = list(param.keys())[0]
                fmt = find_format(_param)
                value = param[_param]
            elif isinstance(param, str):
                if param in self.module.argument_spec:
                    fmt = find_format(param)
                    value = self.module.params[param]
                elif param in extra_params:
                    fmt = find_format(param)
                    value = extra_params[param]
                else:
                    self.module.deprecate("Cannot determine value for parameter: {0}. "
                                          "From version 4.0.0 onwards this will generate an exception".format(param),
                                          version="4.0.0", collection_name="community.general")
                    continue

            else:
                raise ModuleHelperException("run_command parameter must be either a str or a dict: {0}".format(param))
            cmd_args = add_arg_formatted_param(cmd_args, fmt, value)

        return cmd_args

    def process_command_output(self, rc, out, err):
        return rc, out, err

    def run_command(self, extra_params=None, params=None, *args, **kwargs):
        self.vars.cmd_args = self._calculate_args(extra_params, params)
        options = dict(self.run_command_fixed_options)
        env_update = dict(options.get('environ_update', {}))
        options['check_rc'] = options.get('check_rc', self.check_rc)
        if self.force_lang:
            env_update.update({'LANGUAGE': self.force_lang})
            self.update_output(force_lang=self.force_lang)
            options['environ_update'] = env_update
        options.update(kwargs)
        rc, out, err = self.module.run_command(self.vars.cmd_args, *args, **options)
        self.update_output(rc=rc, stdout=out, stderr=err)
        return self.process_command_output(rc, out, err)


class StateModuleHelper(StateMixin, ModuleHelper):
    pass


class CmdModuleHelper(CmdMixin, ModuleHelper):
    pass


class CmdStateModuleHelper(CmdMixin, StateMixin, ModuleHelper):
    pass

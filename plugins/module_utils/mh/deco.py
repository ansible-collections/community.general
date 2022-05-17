# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# ()  2022, Maxime DEMAREST <maxime@indelog.fr>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import traceback
from functools import wraps
import typing
import inspect

from ansible_collections.community.general.plugins.module_utils.mh.exceptions import ModuleHelperException


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


def check_mode_skip(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.module.check_mode:
            return func(self, *args, **kwargs)
    return wrapper


def check_mode_skip_returns(callable=None, value=None):

    def deco(func):
        if callable is not None:
            @wraps(func)
            def wrapper_callable(self, *args, **kwargs):
                if self.module.check_mode:
                    return callable(self, *args, **kwargs)
                return func(self, *args, **kwargs)
            return wrapper_callable

        if value is not None:
            @wraps(func)
            def wrapper_value(self, *args, **kwargs):
                if self.module.check_mode:
                    return value
                return func(self, *args, **kwargs)
            return wrapper_value

    if callable is None and value is None:
        return check_mode_skip

    return deco


def basic_annotation_type_checking(func: typing.Callable) -> typing.Callable:
    """
    Function or method decorator to do very basic type checking based on
    annotations. It raises a TypeError if arguments passed to the function or
    the method doesn't match the type expected in the annotation. If an
    argument has no annotation, it will be ignored.

    You can use Union if your argument can have several types (like this :
    "Union[str, int]" but it can't do complicated type checking like type of
    element in a list or a dict. If you need to do this, you have to use more
    complete library like https://github.com/agronholm/typeguard .

    It's possible to use variable length arguments (named or not) but they type
    will not be checked.

    Sample of use :

        @basic_annotation_type_checking
        def foo(mystr: str, mydictorlist: Union[dict, list], *args, **kwargs):

    Here, if "mystr" is not of type str and "mydictorlrist" is not a dict or a
    list this will raise TypeError exception. *args and **kwargs are ignored.
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> typing.Any:
        bound_args = inspect.Signature.from_callable(
            func).bind(*args, **kwargs)
        bound_args.apply_defaults()
        call_args = bound_args.arguments
        func_params = inspect.signature(func).parameters
        for name, value in call_args.items():
            annot = func_params[name].annotation
            if annot != inspect.Signature.empty:
                if (typing.get_origin(annot) is typing.Union
                        and not isinstance(value, typing.get_args(annot)))\
                    or (not typing.get_origin(annot) is typing.Union
                        and not isinstance(value, annot)):
                    raise TypeError('Bad type of argument ' + name +
                                    ', expected : ' + str(annot) +
                                    ', given : ' + str(
                                        type(value)))
        return func(*args, **kwargs)

    return wrapper

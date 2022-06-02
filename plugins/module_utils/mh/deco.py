# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import traceback
from functools import wraps

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

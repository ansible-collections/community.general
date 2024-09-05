# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import traceback
from functools import wraps

from ansible_collections.community.general.plugins.module_utils.mh.exceptions import ModuleHelperException


def cause_changes(on_success=None, on_failure=None, when=None):
    # Parameters on_success and on_failure are deprecated and should be removed in community.general 12.0.0

    def deco(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
                if on_success is not None:
                    self.changed = on_success
                elif when == "success":
                    self.changed = True
            except Exception:
                if on_failure is not None:
                    self.changed = on_failure
                elif when == "failure":
                    self.changed = True
                raise
            finally:
                if when == "always":
                    self.changed = True

        return wrapper

    return deco


def module_fails_on_exception(func):
    conflict_list = ('msg', 'exception', 'output', 'vars', 'changed')

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        def fix_key(k):
            return k if k not in conflict_list else "_" + k

        def fix_var_conflicts(output):
            result = {fix_key(k): v for k, v in output.items()}
            return result

        try:
            func(self, *args, **kwargs)
        except ModuleHelperException as e:
            if e.update_output:
                self.update_output(e.update_output)
            # patchy solution to resolve conflict with output variables
            output = fix_var_conflicts(self.output)
            self.module.fail_json(msg=e.msg, exception=traceback.format_exc(),
                                  output=self.output, vars=self.vars.output(), **output)
        except Exception as e:
            # patchy solution to resolve conflict with output variables
            output = fix_var_conflicts(self.output)
            msg = "Module failed with exception: {0}".format(str(e).strip())
            self.module.fail_json(msg=msg, exception=traceback.format_exc(),
                                  output=self.output, vars=self.vars.output(), **output)
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

        else:
            @wraps(func)
            def wrapper_value(self, *args, **kwargs):
                if self.module.check_mode:
                    return value
                return func(self, *args, **kwargs)
            return wrapper_value

    return deco

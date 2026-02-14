# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

import traceback
import typing as t
from functools import wraps

from ansible_collections.community.general.plugins.module_utils.mh.exceptions import ModuleHelperException

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from .base import ModuleHelperBase

    P = t.ParamSpec("P")
    S = t.TypeVar("S", bound=ModuleHelperBase)
    T = t.TypeVar("T")


def cause_changes(when=None) -> Callable[[Callable[t.Concatenate[S, P], T]], Callable[t.Concatenate[S, P], None]]:
    def deco(func: Callable[t.Concatenate[S, P], T]) -> Callable[t.Concatenate[S, P], None]:
        @wraps(func)
        def wrapper(self: S, *args: P.args, **kwargs: P.kwargs) -> None:
            try:
                func(self, *args, **kwargs)
                if when == "success":
                    self.changed = True
            except Exception:
                if when == "failure":
                    self.changed = True
                raise
            finally:
                if when == "always":
                    self.changed = True

        return wrapper

    return deco


def module_fails_on_exception(func: Callable[t.Concatenate[S, P], T]) -> Callable[t.Concatenate[S, P], None]:
    conflict_list = ("msg", "exception", "output", "vars", "changed")

    @wraps(func)
    def wrapper(self: S, *args: P.args, **kwargs: P.kwargs) -> None:
        def fix_key(k):
            return k if k not in conflict_list else f"_{k}"

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
            self._module.fail_json(
                msg=e.msg, exception=traceback.format_exc(), output=self.output, vars=self.vars.output(), **output
            )
        except Exception as e:
            # patchy solution to resolve conflict with output variables
            output = fix_var_conflicts(self.output)
            msg = f"Module failed with exception: {str(e).strip()}"
            self._module.fail_json(
                msg=msg, exception=traceback.format_exc(), output=self.output, vars=self.vars.output(), **output
            )

    return wrapper


def check_mode_skip(func: Callable[t.Concatenate[S, P], T]) -> Callable[t.Concatenate[S, P], T | None]:
    @wraps(func)
    def wrapper(self: S, *args: P.args, **kwargs: P.kwargs) -> T | None:
        if not self._module.check_mode:
            return func(self, *args, **kwargs)
        return None

    return wrapper


@t.overload
def check_mode_skip_returns(
    callable: Callable[t.Concatenate[S, P], T], value: T | None = None
) -> Callable[[Callable[t.Concatenate[S, P], T]], Callable[t.Concatenate[S, P], T]]: ...


@t.overload
def check_mode_skip_returns(
    callable: None, value: T
) -> Callable[[Callable[t.Concatenate[S, P], T]], Callable[t.Concatenate[S, P], T]]: ...


@t.overload
def check_mode_skip_returns(
    callable: None = None, *, value: T
) -> Callable[[Callable[t.Concatenate[S, P], T]], Callable[t.Concatenate[S, P], T]]: ...


def check_mode_skip_returns(
    callable: Callable[t.Concatenate[S, P], T] | None = None, value: T | None = None
) -> Callable[[Callable[t.Concatenate[S, P], T]], Callable[t.Concatenate[S, P], T]]:
    def deco(func: Callable[t.Concatenate[S, P], T]) -> Callable[t.Concatenate[S, P], T]:
        if callable is not None:

            @wraps(func)
            def wrapper_callable(self: S, *args: P.args, **kwargs: P.kwargs) -> T:
                if self._module.check_mode:
                    return callable(self, *args, **kwargs)
                return func(self, *args, **kwargs)

            return wrapper_callable

        else:

            @wraps(func)
            def wrapper_value(self: S, *args: P.args, **kwargs: P.kwargs) -> T:
                if self._module.check_mode:
                    return value  # type: ignore  # must be of type T due to the overloads
                return func(self, *args, **kwargs)

            return wrapper_value

    return deco

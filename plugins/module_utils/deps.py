# (c) 2022, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2022, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

import traceback
import typing as t
from contextlib import contextmanager
from enum import Enum

from ansible.module_utils.basic import missing_required_lib

if t.TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule


_deps: dict[str, _Dependency] = dict()


class _State(Enum):
    PENDING = "pending"
    FAILURE = "failure"
    SUCCESS = "success"


class _Dependency:
    def __init__(self, name: str, reason: str | None = None, url: str | None = None, msg: str | None = None) -> None:
        self.name = name
        self.reason = reason
        self.url = url
        self.msg = msg

        self.state = _State.PENDING
        self.trace: str | None = None
        self.exc: Exception | None = None

    def succeed(self) -> None:
        self.state = _State.SUCCESS

    def fail(self, exc: Exception, trace: str) -> None:
        self.state = _State.FAILURE
        self.exc = exc
        self.trace = trace

    @property
    def message(self) -> str:
        if self.msg:
            return str(self.msg)
        else:
            return missing_required_lib(self.name, reason=self.reason, url=self.url)

    @property
    def failed(self) -> bool:
        return self.state == _State.FAILURE

    def validate(self, module: AnsibleModule) -> None:
        if self.failed:
            module.fail_json(msg=self.message, exception=self.trace)

    def __str__(self) -> str:
        return f"<dependency: {self.name} [{self.state.value}]>"


@contextmanager
def declare(name: str, *args, **kwargs) -> t.Generator[_Dependency]:
    dep = _Dependency(name, *args, **kwargs)
    try:
        yield dep
    except Exception as e:
        dep.fail(e, traceback.format_exc())
    else:
        dep.succeed()
    finally:
        _deps[name] = dep


def _select_names(spec: str | None) -> list[str]:
    dep_names = sorted(_deps)

    if spec:
        if spec.startswith("-"):
            spec_split = spec[1:].split(":")
            for d in spec_split:
                dep_names.remove(d)
        else:
            spec_split = spec.split(":")
            dep_names = []
            for d in spec_split:
                _deps[d]  # ensure it exists
                dep_names.append(d)

    return dep_names


def validate(module: AnsibleModule, spec: str | None = None) -> None:
    for dep in _select_names(spec):
        _deps[dep].validate(module)


def failed(spec: str | None = None) -> bool:
    return any(_deps[d].failed for d in _select_names(spec))


def clear() -> None:
    _deps.clear()

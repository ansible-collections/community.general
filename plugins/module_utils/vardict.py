# (c) 2023, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2023, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

import copy
import typing as t


class _Variable:
    NOTHING = object()

    def __init__(
        self,
        diff: bool = False,
        output: bool = True,
        change: bool | None = None,
        fact: bool = False,
        verbosity: int = 0,
    ):
        self.init = False
        self.initial_value: t.Any = None
        self.value: t.Any = None

        self.diff: bool = None  # type: ignore # will be changed in set_meta() call
        self._change: bool | None = None
        self.output: bool = None  # type: ignore # will be changed in set_meta() call
        self.fact: bool = None  # type: ignore # will be changed in set_meta() call
        self._verbosity: int = None  # type: ignore # will be changed in set_meta() call
        self.set_meta(output=output, diff=diff, change=change, fact=fact, verbosity=verbosity)

    def getchange(self) -> bool:
        return self.diff if self._change is None else self._change

    def setchange(self, value: bool | None) -> None:
        self._change = value

    def getverbosity(self) -> int:
        return self._verbosity

    def setverbosity(self, v: int) -> None:
        if not (0 <= v <= 4):
            raise ValueError("verbosity must be an int in the range 0 to 4")
        self._verbosity = v

    change = property(getchange, setchange)
    verbosity = property(getverbosity, setverbosity)

    def set_meta(
        self,
        output: bool | None = None,
        diff: bool | None = None,
        change: bool | None = None,
        fact: bool | None = None,
        initial_value: t.Any = NOTHING,
        verbosity: int | None = None,
    ) -> None:
        """Set the metadata for the variable

        Args:
            output (bool, optional): flag indicating whether the variable should be in the output of the module. Defaults to None.
            diff (bool, optional): flag indicating whether to generate diff mode output for this variable. Defaults to None.
            change (bool, optional): flag indicating whether to track if changes happened to this variable. Defaults to None.
            fact (bool, optional): flag indicating whether the variable should be exposed as a fact of the module. Defaults to None.
            initial_value (any, optional): initial value of the variable, to be used with `change`. Defaults to NOTHING.
            verbosity (int, optional): level of verbosity in which this variable is reported by the module as `output`, `fact` or `diff`. Defaults to None.
        """
        if output is not None:
            self.output = output
        if change is not None:
            self.change = change
        if diff is not None:
            self.diff = diff
        if fact is not None:
            self.fact = fact
        if initial_value is not _Variable.NOTHING:
            self.initial_value = copy.deepcopy(initial_value)
        if verbosity is not None:
            self.verbosity = verbosity

    def as_dict(self, meta_only: bool = False) -> dict[str, t.Any]:
        d = {
            "diff": self.diff,
            "change": self.change,
            "output": self.output,
            "fact": self.fact,
            "verbosity": self.verbosity,
        }
        if not meta_only:
            d["initial_value"] = copy.deepcopy(self.initial_value)
            d["value"] = self.value
        return d

    def set_value(self, value: t.Any) -> t.Self:
        if not self.init:
            self.initial_value = copy.deepcopy(value)
            self.init = True
        self.value = value
        return self

    def is_visible(self, verbosity: int) -> bool:
        return self.verbosity <= verbosity

    @property
    def has_changed(self) -> bool:
        return self.change and (self.initial_value != self.value)

    @property
    def diff_result(self) -> dict[str, t.Any] | None:
        if self.diff and self.has_changed:
            return {"before": self.initial_value, "after": self.value}
        return None

    def __str__(self) -> str:
        return (
            f"<Variable: value={self.value!r}, initial={self.initial_value!r}, diff={self.diff}, "
            f"output={self.output}, change={self.change}, verbosity={self.verbosity}>"
        )


class VarDict:
    reserved_names = (
        "__vars__",
        "_var",
        "var",
        "set_meta",
        "get_meta",
        "set",
        "output",
        "diff",
        "facts",
        "has_changed",
        "as_dict",
    )

    def __init__(self) -> None:
        self.__vars__: dict[str, _Variable] = dict()

    def __getitem__(self, item: str):
        return self.__vars__[item].value

    def __setitem__(self, key: str, value) -> None:
        self.set(key, value)

    def __getattr__(self, item: str):
        try:
            return self.__vars__[item].value
        except KeyError:
            return getattr(super(), item)

    def __setattr__(self, key: str, value) -> None:
        if key == "__vars__":
            super().__setattr__(key, value)
        else:
            self.set(key, value)

    def _var(self, name: str) -> _Variable:
        return self.__vars__[name]

    def var(self, name: str) -> dict[str, t.Any]:
        return self._var(name).as_dict()

    def set_meta(self, name: str, **kwargs):
        """Set the metadata for the variable

        Args:
            name (str): name of the variable having its metadata changed
            output (bool, optional): flag indicating whether the variable should be in the output of the module. Defaults to None.
            diff (bool, optional): flag indicating whether to generate diff mode output for this variable. Defaults to None.
            change (bool, optional): flag indicating whether to track if changes happened to this variable. Defaults to None.
            fact (bool, optional): flag indicating whether the variable should be exposed as a fact of the module. Defaults to None.
            initial_value (any, optional): initial value of the variable, to be used with `change`. Defaults to NOTHING.
            verbosity (int, optional): level of verbosity in which this variable is reported by the module as `output`, `fact` or `diff`. Defaults to None.
        """
        self._var(name).set_meta(**kwargs)

    def get_meta(self, name: str) -> dict[str, t.Any]:
        return self._var(name).as_dict(meta_only=True)

    def set(self, name: str, value, **kwargs) -> None:
        """Set the value and optionally metadata for a variable. The variable is not required to exist prior to calling `set`.

        For details on the accepted metada see the documentation for method `set_meta`.

        Args:
            name (str): name of the variable being changed
            value (any): the value of the variable, it can be of any type

        Raises:
            ValueError: Raised if trying to set a variable with a reserved name.
        """
        if name in self.reserved_names:
            raise ValueError(f"Name {name} is reserved")
        if name in self.__vars__:
            var = self._var(name)
            var.set_meta(**kwargs)
        else:
            var = _Variable(**kwargs)
        var.set_value(value)
        self.__vars__[name] = var

    def output(self, verbosity: int = 0) -> dict[str, t.Any]:
        return {n: v.value for n, v in self.__vars__.items() if v.output and v.is_visible(verbosity)}

    def diff(self, verbosity: int = 0) -> dict[str, dict[str, t.Any]] | None:
        diff_results = [
            (n, v.diff_result) for n, v in self.__vars__.items() if v.diff_result and v.is_visible(verbosity)
        ]
        if diff_results:
            before = {n: dr["before"] for n, dr in diff_results}
            after = {n: dr["after"] for n, dr in diff_results}
            return {"before": before, "after": after}
        return None

    def facts(self, verbosity: int = 0) -> dict[str, t.Any] | None:
        facts_result = {n: v.value for n, v in self.__vars__.items() if v.fact and v.is_visible(verbosity)}
        return facts_result if facts_result else None

    @property
    def has_changed(self) -> bool:
        return any(var.has_changed for var in self.__vars__.values())

    def as_dict(self) -> dict[str, t.Any]:
        return {name: var.value for name, var in self.__vars__.items()}

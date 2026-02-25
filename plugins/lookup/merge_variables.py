# Copyright (c) 2020, Thales Netherlands
# Copyright (c) 2021, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
author:
  - Roy Lenferink (@rlenferink)
  - Mark Ettema (@m-a-r-k-e)
  - Alexander Petrenz (@alpex8)
  - Christoph Fiehe (@cfiehe)
name: merge_variables
short_description: Merge variables whose names match a given pattern
description:
  - This lookup returns the merged result of all variables in scope that match the given prefixes, suffixes, or regular expressions,
    optionally.
version_added: 6.5.0
options:
  _terms:
    description:
      - Depending on the value of O(pattern_type), this is a list of prefixes, suffixes, or regular expressions that is used
        to match all variables that should be merged.
    required: true
    type: list
    elements: str
  pattern_type:
    description:
      - Change the way of searching for the specified pattern.
    type: str
    default: 'regex'
    choices:
      - prefix
      - suffix
      - regex
    env:
      - name: ANSIBLE_MERGE_VARIABLES_PATTERN_TYPE
    ini:
      - section: merge_variables_lookup
        key: pattern_type
  initial_value:
    description:
      - An initial value to start with.
    type: raw
  override:
    description:
      - Return an error, print a warning or ignore it when a key is overwritten.
      - The default behavior V(error) makes the plugin fail when a key would be overwritten.
      - When V(warn) and V(ignore) are used, note that it is important to know that the variables are sorted by name before
        being merged. Keys for later variables in this order overwrite keys of the same name for variables earlier in this
        order. To avoid potential confusion, better use O(override=error) whenever possible.
    type: str
    default: 'error'
    choices:
      - error
      - warn
      - ignore
    env:
      - name: ANSIBLE_MERGE_VARIABLES_OVERRIDE
    ini:
      - section: merge_variables_lookup
        key: override
  groups:
    description:
      - Search for variables across hosts that belong to the given groups. This allows to collect configuration pieces across
        different hosts (for example a service on a host with its database on another host).
    type: list
    elements: str
    version_added: 8.5.0
  dict_merge:
    description:
      - Behavior when encountering dictionary values.
    type: str
    default: deep
    choices:
      deep: merge dictionaries recursively.
      shallow: merge only top-level values.
      replace: overwrite older dict with newer one.
      keep: discard newer dict.
    version_added: 12.5.0
  list_merge:
    description:
      - Behavior when encountering list values.
    type: str
    default: append
    choices:
      replace: overwrite older entries with newer ones.
      keep: discard newer entries.
      append: append newer entries to the older ones.
      prepend: insert newer entries in front of the older ones.
      append_rp: append newer entries to the older ones, overwrite duplicates.
      prepend_rp: insert newer entries in front of the older ones, discard duplicates.
      merge: take the index as key and merge the entries.
    version_added: 12.5.0
  type_conflict_merge:
    description:
      - Merge strategy to apply on type conflicts.
    type: str
    default: replace
    choices:
      replace: overwrite older value with newer one.
      keep: discard newer value.
    version_added: 12.5.0
  default_merge:
    description:
      - Merge strategy applied to other types.
    type: str
    default: replace
    choices:
      replace: overwrite older value with newer one.
      keep: discard newer value.
    version_added: 12.5.0
  list_transformations:
    description:
      - List transformations applied to list types. The definition order corresponds to the order in which these transformations are applied.
      - Elements can be a dict with the keys mentioned below or a string naming the transformation to apply.
    type: list
    elements: raw
    suboptions:
      name:
        description:
          - Name of the list transformation.
        required: true
        type: str
        choices:
          flatten: flatten lists, converting nested lists into single lists.
          dedup: remove duplicates from lists.
      options:
        description:
          - Options as key value pairs. V(flatten) and V(dedup) do not support any additional options.
        type: dict
    default: []
    version_added: 12.5.0
"""

EXAMPLES = r"""
# Some example variables, they can be defined anywhere as long as they are in scope
test_init_list:
  - "list init item 1"
  - "list init item 2"

testa__test_list:
  - "test a item 1"

testb__test_list:
  - "test b item 1"

testa__test_dict:
  ports:
    - 1

testb__test_dict:
  ports:
    - 3

# Merge variables that end with '__test_dict' and store the result in a variable 'example_a'
example_a: "{{ lookup('community.general.merge_variables', '__test_dict', pattern_type='suffix') }}"

# The variable example_a now contains:
# ports:
#   - 1
#   - 3

# Merge variables that match the '^.+__test_list$' regular expression, starting with an initial value and store the
# result in a variable 'example_b'
example_b: "{{ lookup('community.general.merge_variables', '^.+__test_list$', initial_value=test_init_list) }}"

# The variable example_b now contains:
#   - "list init item 1"
#   - "list init item 2"
#   - "test a item 1"
#   - "test b item 1"
"""

RETURN = r"""
_raw:
  description: In case the search matches list items, a list is returned. In case the search matches dicts, a dict is returned.
  type: raw
  elements: raw
"""

import re
import typing as t
from abc import ABC, abstractmethod

if t.TYPE_CHECKING:
    from collections.abc import Callable

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.template import Templar
from ansible.utils.display import Display

display = Display()


def _verify_and_get_type(variable: t.Any) -> str:
    if isinstance(variable, list):
        return "list"
    elif isinstance(variable, dict):
        return "dict"
    else:
        raise AnsibleError(f"Not supported type detected, variable must be a list or a dict: '{variable}'")


class LookupModule(LookupBase):
    def run(self, terms: list[str], variables: dict[str, t.Any], **kwargs) -> list[t.Any]:
        self.set_options(direct=kwargs)
        initial_value = self.get_option("initial_value", None)
        self._override_behavior = self.get_option("override", "error")
        self._pattern_type = self.get_option("pattern_type", "regex")
        self._groups = self.get_option("groups", None)
        self._dict_merge = self.get_option("dict_merge", "deep")
        self._list_merge = self.get_option("list_merge", "append")
        self._type_conflict_merge = self.get_option("type_conflict_merge", "replace")
        self._default_merge = self.get_option("default_merge", "replace")
        self._list_transformations = self.get_option("list_transformations", [])

        ret = []
        for term in terms:
            if not isinstance(term, str):
                raise AnsibleError(f"Non-string type '{type(term)}' passed, only 'str' types are allowed!")

            if not self._groups:  # consider only own variables
                ret.append(self._merge_vars(term, initial_value, variables))
            else:  # consider variables of hosts in given groups
                cross_host_merge_result = initial_value
                for host in variables["hostvars"]:
                    if self._is_host_in_allowed_groups(variables["hostvars"][host]["group_names"]):
                        host_variables = dict(variables["hostvars"].raw_get(host))
                        host_variables["hostvars"] = variables["hostvars"]  # re-add hostvars
                        cross_host_merge_result = self._merge_vars(term, cross_host_merge_result, host_variables)
                ret.append(cross_host_merge_result)

        return ret

    def _is_host_in_allowed_groups(self, host_groups: list[str]) -> bool:
        if "all" in self._groups:
            return True

        group_intersection = [host_group_name for host_group_name in host_groups if host_group_name in self._groups]
        return bool(group_intersection)

    def _var_matches(self, key: str, search_pattern: str) -> bool:
        if self._pattern_type == "prefix":
            return key.startswith(search_pattern)
        elif self._pattern_type == "suffix":
            return key.endswith(search_pattern)
        elif self._pattern_type == "regex":
            matcher = re.compile(search_pattern)
            return matcher.search(key) is not None

        return False

    def _merge_vars(self, search_pattern: str, initial_value: t.Any, variables: dict[str, t.Any]) -> t.Any:
        display.vvv(f"Merge variables with {self._pattern_type}: {search_pattern}")
        var_merge_names = sorted([key for key in variables.keys() if self._var_matches(key, search_pattern)])
        display.vvv(f"The following variables will be merged: {var_merge_names}")
        prev_var_type = None
        result = None

        if initial_value is not None:
            prev_var_type = _verify_and_get_type(initial_value)
            result = initial_value

        builder = (
            MergerBuilder()
            .with_type_strategy(list, ListMergeStrategies.from_name(self._list_merge))
            .with_type_conflict_strategy(BaseMergeStrategies.from_name(self._type_conflict_merge))
            .with_default_strategy(BaseMergeStrategies.from_name(self._default_merge))
            .with_override_behavior(self._override_behavior)
        )

        if self._dict_merge == "deep":
            builder.with_type_strategy(dict, DictMergeStrategies.Merge())
        elif self._dict_merge == "shallow":
            builder.with_shallow_merge()
        else:
            builder.with_type_strategy(dict, DictMergeStrategies.from_name(self._dict_merge))

        for transformation in self._list_transformations:
            if isinstance(transformation, str):
                builder.with_transformation(list, ListTransformations.from_name(transformation))
            elif isinstance(transformation, dict):
                name = transformation["name"]
                options = transformation.get("options", {})
                builder.with_transformation(list, ListTransformations.from_name(name, **options))
            else:
                raise AnsibleError(
                    f"Transformations must be specified through values of type 'str' or 'dict', but a value of type '{type(transformation)}' was given."
                )

        merger = builder.build()

        if self._templar is not None:
            templar = self._templar.copy_with_new_env(available_variables=variables)
        else:
            templar = Templar(loader=self._loader, variables=variables)

        for var_name in var_merge_names:
            var_value = templar.template(variables[var_name])  # Render jinja2 templates
            var_type = _verify_and_get_type(var_value)

            if prev_var_type is None:
                prev_var_type = var_type
            elif prev_var_type != var_type:
                raise AnsibleError("Unable to merge, not all variables are of the same type")

            if result is None:
                result = var_value
                continue

            result = merger.merge(path=[var_name], left=result, right=var_value)

        return result


class MergeStrategy(ABC):
    """
    Implements custom merge logic for combining two values.
    """

    @abstractmethod
    def merge(self, merger: ObjectMerger, path: list[str], left: t.Any, right: t.Any) -> t.Any:
        raise NotImplementedError


class MergeStrategies:
    @classmethod
    def from_name(cls, name: str, *args, **kwargs) -> MergeStrategy:
        if name in cls.strategies:
            return cls.strategies[name](*args, **kwargs)
        else:
            raise AnsibleError(f"Unknown merge strategy '{name}'")

    strategies: dict[str, Callable[..., t.Any]] = {}


class BaseMergeStrategies(MergeStrategies):
    """
    Collection of base merge strategies.
    """

    class Replace(MergeStrategy):
        """
        Overwrite older value with newer one.
        """

        def merge(self, merger: ObjectMerger, path: list[str], left: t.Any, right: t.Any) -> t.Any:
            return right

    class Keep(MergeStrategy):
        """
        Discard newer value.
        """

        def merge(self, merger: ObjectMerger, path: list[str], left: t.Any, right: t.Any) -> t.Any:
            return left

    strategies = {
        "replace": Replace,
        "keep": Keep,
    }


class DictMergeStrategies(MergeStrategies):
    """
    Collection of dictionary merge strategies.
    """

    class Merge(MergeStrategy):
        """
        Recursively merge dictionaries.
        """

        def merge(
            self, merger: ObjectMerger, path: list[str], left: dict[str, t.Any], right: dict[str, t.Any]
        ) -> dict[str, t.Any]:
            result = left
            for key, value in right.items():
                if key not in result:
                    result[key] = value
                else:
                    path.append(key)
                    merged = merger.merge(path=path, left=result[key], right=value)
                    merger.before_override(path=path, old_value=result[key], new_value=merged)
                    result[key] = merged

            return result

    strategies = {
        "merge": Merge,
        "replace": BaseMergeStrategies.Replace,
        "keep": BaseMergeStrategies.Keep,
    }


class ListMergeStrategies(MergeStrategies):
    """
    Collection of list merge strategies.
    """

    class Append(MergeStrategy):
        """
        Append newer entries to the older ones.
        """

        def merge(self, merger: ObjectMerger, path: list[str], left: list[t.Any], right: list[t.Any]) -> list[t.Any]:
            return left + right

    class Prepend(MergeStrategy):
        """
        Insert newer entries in front of the older ones.
        """

        def merge(self, merger: ObjectMerger, path: list[str], left: list[t.Any], right: list[t.Any]) -> list[t.Any]:
            return right + left

    class AppendRp(MergeStrategy):
        """
        Append newer entries to the older ones, overwrite duplicates.
        """

        def merge(self, merger: ObjectMerger, path: list[str], left: list[t.Any], right: list[t.Any]) -> list[t.Any]:
            return [item for item in left if item not in right] + right

    class PrependRp(MergeStrategy):
        """
        Insert newer entries in front of the older ones, discard duplicates.
        """

        def merge(self, merger: ObjectMerger, path: list[str], left: list[t.Any], right: list[t.Any]) -> list[t.Any]:
            return right + [item for item in left if item not in right]

    class Merge(MergeStrategy):
        """
        Take the index as key and merge the entries.
        """

        def merge(self, merger: ObjectMerger, path: list[str], left: list[t.Any], right: list[t.Any]) -> list[t.Any]:
            result = left
            for i, value in enumerate(right):
                if i >= len(result):
                    result.extend(right[i:])
                    break

                path.append(str(i))
                merged = merger.merge(path=path, left=result[i], right=value)
                merger.before_override(path=path, old_value=result[i], new_value=merged)
                result[i] = merged

            return result

    strategies = {
        "append": Append,
        "prepend": Prepend,
        "append_rp": AppendRp,
        "prepend_rp": PrependRp,
        "merge": Merge,
        "replace": BaseMergeStrategies.Replace,
        "keep": BaseMergeStrategies.Keep,
    }


class Transformation(ABC):
    """
    Implements custom transformation logic for converting a value to another representation.
    """

    @abstractmethod
    def transform(self, merger: ObjectMerger, value: t.Any) -> t.Any:
        raise NotImplementedError


class Transformations:
    @classmethod
    def from_name(cls, name: str, *args, **kwargs) -> Transformation:
        if name in cls.transformations:
            return cls.transformations[name](*args, **kwargs)
        else:
            raise AnsibleError(f"Unknown transformation '{name}'")

    transformations: dict[str, Callable[..., t.Any]] = {}


class ListTransformations(Transformations):
    """
    Collection of list transformations.
    """

    class Dedup(Transformation):
        """
        Removes duplicates from a list.
        """

        def transform(self, merger: ObjectMerger, value: list[t.Any]) -> list[t.Any]:
            result = []
            for item in value:
                if item not in result:
                    result.append(item)
            return result

    class Flatten(Transformation):
        """
        Takes a list and replaces any elements that are lists with a flattened sequence of the list contents.
        If any of the nested lists also contain directly-nested lists, these are flattened recursively.
        """

        def transform(self, merger: ObjectMerger, value: list[t.Any]) -> list[t.Any]:
            result = []
            for item in value:
                if isinstance(item, list):
                    result.extend(self.transform(merger, item))
                else:
                    result.append(item)
            return result

    transformations = {
        "dedup": Dedup,
        "flatten": Flatten,
    }


class MergerBuilder:
    """
    Helper that builds a merger based on provided strategies.
    """

    def __init__(self) -> None:
        self.type_strategies: list[tuple[type, MergeStrategy]] = []
        self.type_conflict_strategy: MergeStrategy = BaseMergeStrategies.Replace()
        self.default_strategy: MergeStrategy = BaseMergeStrategies.Replace()
        self.transformations: list[tuple[type, Transformation]] = []
        self.override_behavior: str = "error"
        self.shallow_merge: bool = False

    def with_shallow_merge(self, shallow_merge: bool = True) -> MergerBuilder:
        self.shallow_merge = shallow_merge
        return self

    def with_override_behavior(self, override_behavior: str) -> MergerBuilder:
        self.override_behavior = override_behavior
        return self

    def with_type_strategy(self, cls, merge_strategy: MergeStrategy) -> MergerBuilder:
        self.type_strategies.append((cls, merge_strategy))
        return self

    def with_default_strategy(self, merge_strategy: MergeStrategy) -> MergerBuilder:
        self.default_strategy = merge_strategy
        return self

    def with_type_conflict_strategy(self, merge_strategy: MergeStrategy) -> MergerBuilder:
        self.type_conflict_strategy = merge_strategy
        return self

    def with_transformation(self, cls, *args: Transformation) -> MergerBuilder:
        for transformation in args:
            self.transformations.append((cls, transformation))
        return self

    def build(self) -> Merger:
        merger = ObjectMerger(
            type_strategies=self.type_strategies,
            type_conflict_strategy=self.type_conflict_strategy,
            default_strategy=self.default_strategy,
            transformations=self.transformations,
            override_behavior=self.override_behavior,
        )

        if self.shallow_merge:
            return ShallowMerger(merger)

        return merger


class Merger(ABC):
    @abstractmethod
    def merge(self, path: list[str], left: t.Any, right: t.Any) -> t.Any:
        raise NotImplementedError


class ObjectMerger(Merger):
    """
    Merges objects based on provided strategies.
    """

    def __init__(
        self,
        type_strategies: list[tuple[type, MergeStrategy]],
        type_conflict_strategy: MergeStrategy,
        default_strategy: MergeStrategy,
        transformations: list[tuple[type, Transformation]],
        override_behavior: str,
    ) -> None:
        self.type_strategies = type_strategies
        self.type_conflict_strategy = type_conflict_strategy
        self.default_strategy = default_strategy
        self.transformations = transformations
        self.override_behavior = override_behavior

    def before_override(self, path: list[str], old_value: t.Any, new_value: t.Any) -> None:
        if (
            not isinstance(old_value, type(new_value))
            and not isinstance(new_value, type(old_value))
            or not isinstance(new_value, dict)
            and not isinstance(new_value, list)
            and old_value != new_value
        ):
            # This behavior has been implemented for reasons of backward compatibility.
            # An override is regarded as a value type conflict or
            # when both values are neither dicts nor lists and
            # have different values
            msg = f"The key '{path[-1]}' with value '{old_value}' will be overwritten with value '{new_value}' from '{'.'.join(path)}'"
            if self.override_behavior == "error":
                raise AnsibleError(msg)
            elif self.override_behavior == "warn":
                display.warning(msg)

    def transform(self, value: t.Any) -> t.Any:
        for cls, transformation in self.transformations:
            if isinstance(value, cls):
                value = transformation.transform(self, value)
        return value

    def lookup_merge_strategy(self, left: t.Any, right: t.Any) -> MergeStrategy:
        for cls, merge_strategy in self.type_strategies:
            if isinstance(left, cls) and isinstance(right, cls):
                return merge_strategy

        if not isinstance(left, type(right)) and not isinstance(right, type(left)):
            return self.type_conflict_strategy

        return self.default_strategy

    def apply_merge_strategy(self, merge_strategy: MergeStrategy, path: list[str], left: t.Any, right: t.Any) -> t.Any:
        return self.transform(merge_strategy.merge(self, path, left, right))

    def merge(self, path: list[str], left: t.Any, right: t.Any) -> t.Any:
        return self.apply_merge_strategy(self.lookup_merge_strategy(left, right), path, left, right)


class ShallowMerger(Merger):
    """
    Wrapper around merger that combines the top-level values of two given dictionaries.
    """

    def __init__(self, merger: ObjectMerger) -> None:
        self.merger = merger

    def merge(self, path: list[str], left: t.Any, right: t.Any) -> t.Any:
        if isinstance(left, dict) and isinstance(right, dict):
            return self.merger.apply_merge_strategy(DictMergeStrategies.Merge(), path, left, right)

        return self.merger.merge(path, left, right)

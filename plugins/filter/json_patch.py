# -*- coding: utf-8 -*-
# Copyright (c) Stanislav Meduna (@numo68)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, annotations, division, print_function
from json import loads
from typing import TYPE_CHECKING
from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native

__metaclass__ = type  # pylint: disable=C0103

if TYPE_CHECKING:
    from typing import Any, Callable, Union

try:
    import jsonpatch

except ImportError as exc:
    HAS_LIB = False
    JSONPATCH_IMPORT_ERROR = exc
else:
    HAS_LIB = True
    JSONPATCH_IMPORT_ERROR = None

OPERATIONS_AVAILABLE = ["add", "copy", "move", "remove", "replace", "test"]
OPERATIONS_NEEDING_FROM = ["copy", "move"]
OPERATIONS_NEEDING_VALUE = ["add", "replace", "test"]


class FilterModule:
    """Filter plugin."""

    def check_json_object(
        self, filter_name: str, object_name: str, inp: Union[str, list, dict]
    ):
        if not isinstance(inp, (str, list, dict)):
            raise AnsibleFilterError(
                f"{filter_name}: {object_name} is not dictionary, list or string"
            )

    def check_patch_arguments(self, filter_name: str, args: dict):

        if "op" not in args or not isinstance(args["op"], str):
            raise AnsibleFilterError(f"{filter_name}: 'op' argument is not a string")

        if args["op"] not in OPERATIONS_AVAILABLE:
            raise AnsibleFilterError(
                f"{filter_name}: unsupported 'op' argument: {args['op']}"
            )

        if "path" not in args or not isinstance(args["path"], str):
            raise AnsibleFilterError(f"{filter_name}: 'path' argument is not a string")

        if args["op"] in OPERATIONS_NEEDING_FROM:
            if "from" not in args:
                raise AnsibleFilterError(
                    f"{filter_name}: 'from' argument missing for '{args['op']}' operation"
                )
            if not isinstance(args["from"], str):
                raise AnsibleFilterError(
                    f"{filter_name}: 'from' argument is not a string"
                )

    def json_patch(
        self,
        inp: Union[str, list, dict],
        op: str,
        path: str,
        value: Any = None,
        **kwargs: dict,
    ) -> Any:

        if not HAS_LIB:
            raise AnsibleFilterError(
                "You need to install 'jsonpatch' package prior to running 'json_patch' filter"
            ) from JSONPATCH_IMPORT_ERROR

        self.check_json_object("json_patch", "input", inp)

        args = {"op": op, "path": path}
        from_arg = kwargs.pop("from", None)

        if kwargs:
            raise AnsibleFilterError(
                f"json_patch: unexpected keywords arguments: {', '.join(kwargs.keys())}"
            )

        if op in OPERATIONS_NEEDING_VALUE:
            args["value"] = value
        if op in OPERATIONS_NEEDING_FROM and from_arg is not None:
            args["from"] = from_arg

        self.check_patch_arguments("json_patch", args)

        result = None

        try:
            result = jsonpatch.apply_patch(
                inp if isinstance(inp, (dict, list)) else loads(inp),
                [args],
            )
        except jsonpatch.JsonPatchTestFailed:
            pass
        except Exception as e:
            raise AnsibleFilterError(f"json_patch: patch failed: {to_native(e)}") from e

        return result

    def json_patch_recipe(self, inp: Union[str, list, dict], operations: list) -> Any:

        if not HAS_LIB:
            raise AnsibleFilterError(
                "You need to install 'jsonpatch' package prior to running 'json_patch_recipe' filter"
            ) from JSONPATCH_IMPORT_ERROR

        self.check_json_object("json_patch_recipe", "input", inp)

        if not isinstance(operations, list):
            raise AnsibleFilterError(
                "json_patch_recipe: 'operations' needs to be a list"
            )

        result = None

        for args in operations:
            self.check_patch_arguments("json_patch_recipe", args)

        try:
            result = jsonpatch.apply_patch(
                inp if isinstance(inp, (dict, list)) else loads(inp),
                operations,
            )
        except jsonpatch.JsonPatchTestFailed:
            pass
        except Exception as e:
            raise AnsibleFilterError(
                f"json_patch_recipe: patch failed: {to_native(e)}"
            ) from e

        return result

    def json_diff(
        self, inp: Union[str, list, dict], target: Union[str, list, dict]
    ) -> list:

        if not HAS_LIB:
            raise AnsibleFilterError(
                "You need to install 'jsonpatch' package prior to running 'json_diff' filter"
            ) from JSONPATCH_IMPORT_ERROR

        self.check_json_object("json_diff", "input", inp)
        self.check_json_object("json_diff", "target", target)

        source = inp if isinstance(inp, (dict, list)) else loads(inp)
        destination = target if isinstance(target, (dict, list)) else loads(target)

        try:
            result = list(jsonpatch.make_patch(source, destination))
        except Exception as e:
            raise AnsibleFilterError(f"JSON diff failed: {to_native(e)}") from e

        return result

    def filters(self) -> dict[str, Callable[[object, str, str, object], object]]:
        """Map filter plugin names to their functions.

        Returns:
            dict: The filter plugin functions.
        """
        return {
            "json_patch": self.json_patch,
            "json_patch_recipe": self.json_patch_recipe,
            "json_diff": self.json_diff,
        }

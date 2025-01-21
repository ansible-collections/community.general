# -*- coding: utf-8 -*-
# Copyright (c) Stanislav Meduna (@numo68)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
from json import loads
from typing import TYPE_CHECKING
from ansible.errors import AnsibleFilterError

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

    def check_json_object(self, filter_name: str, object_name: str, inp: Any):
        if isinstance(inp, (str, bytes, bytearray)):
            try:
                return loads(inp)
            except Exception as e:
                raise AnsibleFilterError(
                    f"{filter_name}: could not decode JSON from {object_name}: {e}"
                ) from e

        if not isinstance(inp, (list, dict)):
            raise AnsibleFilterError(
                f"{filter_name}: {object_name} is not dictionary, list or string"
            )

        return inp

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
        inp: Union[str, list, dict, bytes, bytearray],
        op: str,
        path: str,
        value: Any = None,
        **kwargs: dict,
    ) -> Any:

        if not HAS_LIB:
            raise AnsibleFilterError(
                "You need to install 'jsonpatch' package prior to running 'json_patch' filter"
            ) from JSONPATCH_IMPORT_ERROR

        args = {"op": op, "path": path}
        from_arg = kwargs.pop("from", None)
        fail_test = kwargs.pop("fail_test", False)

        if kwargs:
            raise AnsibleFilterError(
                f"json_patch: unexpected keywords arguments: {', '.join(sorted(kwargs))}"
            )

        if not isinstance(fail_test, bool):
            raise AnsibleFilterError("json_patch: 'fail_test' argument is not a bool")

        if op in OPERATIONS_NEEDING_VALUE:
            args["value"] = value
        if op in OPERATIONS_NEEDING_FROM and from_arg is not None:
            args["from"] = from_arg

        inp = self.check_json_object("json_patch", "input", inp)
        self.check_patch_arguments("json_patch", args)

        result = None

        try:
            result = jsonpatch.apply_patch(inp, [args])
        except jsonpatch.JsonPatchTestFailed as e:
            if fail_test:
                raise AnsibleFilterError(
                    f"json_patch: test operation failed: {e}"
                ) from e
            else:
                pass
        except Exception as e:
            raise AnsibleFilterError(f"json_patch: patch failed: {e}") from e

        return result

    def json_patch_recipe(
        self,
        inp: Union[str, list, dict, bytes, bytearray],
        operations: list,
        /,
        fail_test: bool = False,
    ) -> Any:

        if not HAS_LIB:
            raise AnsibleFilterError(
                "You need to install 'jsonpatch' package prior to running 'json_patch_recipe' filter"
            ) from JSONPATCH_IMPORT_ERROR

        if not isinstance(operations, list):
            raise AnsibleFilterError(
                "json_patch_recipe: 'operations' needs to be a list"
            )

        if not isinstance(fail_test, bool):
            raise AnsibleFilterError("json_patch: 'fail_test' argument is not a bool")

        result = None

        inp = self.check_json_object("json_patch_recipe", "input", inp)
        for args in operations:
            self.check_patch_arguments("json_patch_recipe", args)

        try:
            result = jsonpatch.apply_patch(inp, operations)
        except jsonpatch.JsonPatchTestFailed as e:
            if fail_test:
                raise AnsibleFilterError(
                    f"json_patch_recipe: test operation failed: {e}"
                ) from e
            else:
                pass
        except Exception as e:
            raise AnsibleFilterError(f"json_patch_recipe: patch failed: {e}") from e

        return result

    def json_diff(
        self,
        inp: Union[str, list, dict, bytes, bytearray],
        target: Union[str, list, dict, bytes, bytearray],
    ) -> list:

        if not HAS_LIB:
            raise AnsibleFilterError(
                "You need to install 'jsonpatch' package prior to running 'json_diff' filter"
            ) from JSONPATCH_IMPORT_ERROR

        inp = self.check_json_object("json_diff", "input", inp)
        target = self.check_json_object("json_diff", "target", target)

        try:
            result = list(jsonpatch.make_patch(inp, target))
        except Exception as e:
            raise AnsibleFilterError(f"JSON diff failed: {e}") from e

        return result

    def filters(self) -> dict[str, Callable[..., Any]]:
        """Map filter plugin names to their functions.

        Returns:
            dict: The filter plugin functions.
        """
        return {
            "json_patch": self.json_patch,
            "json_patch_recipe": self.json_patch_recipe,
            "json_diff": self.json_diff,
        }

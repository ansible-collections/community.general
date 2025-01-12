# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, annotations, division, print_function
from json import loads
from typing import TYPE_CHECKING
from ansible.errors import AnsibleError, AnsibleFilterError, AnsibleOptionsError
from ansible.module_utils.common.text.converters import to_native

__metaclass__ = type  # pylint: disable=C0103

if TYPE_CHECKING:
    from typing import Callable

try:
    import jsonpatch

    HAS_LIB = True
except ImportError:
    HAS_LIB = False


class FilterModule:
    """Filter plugin."""

    def json_patch(
        self, inp: object, op: str, path: str, value: object = None, **kwargs: dict
    ) -> object:

        if not HAS_LIB:
            raise AnsibleError(
                'You need to install "jsonpatch" package prior to running "json_patch" filter'
            )

        args = {"op": op, "path": path}

        if op not in ["remove"]:
            args["value"] = value

        if op in ["move", "copy"]:
            if "from" in kwargs:
                args["from"] = kwargs["from"]
            else:
                raise AnsibleOptionsError(f'"{op}" operation requires "from" parameter')

        result = None

        try:
            result = jsonpatch.apply_patch(
                inp if isinstance(inp, (dict, list)) else loads(inp),
                [args],
            )
        except jsonpatch.JsonPatchTestFailed:
            pass
        except Exception as e:
            raise AnsibleFilterError("JSON patch failed: %s" % to_native(e)) from e

        return result

    def json_patch_recipe(self, inp: object, operations: list) -> object:

        if not HAS_LIB:
            raise AnsibleError(
                'You need to install "jsonpatch" package prior to running "json_patch_recipe" filter'
            )

        if not isinstance(operations, list):
            raise AnsibleOptionsError('"operations" needs to be a list')

        result = None

        try:
            result = jsonpatch.apply_patch(
                inp if isinstance(inp, (dict, list)) else loads(inp),
                operations,
            )
        except jsonpatch.JsonPatchTestFailed:
            pass
        except Exception as e:
            raise AnsibleFilterError("JSON patch failed: %s" % to_native(e)) from e

        return result

    def json_diff(self, inp: object, target: object) -> list:

        if not HAS_LIB:
            raise AnsibleError(
                'You need to install "jsonpatch" package prior to running "json_patch_recipe" filter'
            )

        source = inp if isinstance(inp, (dict, list)) else loads(inp)
        destination = target if isinstance(target, (dict, list)) else loads(target)

        try:
            result = list(jsonpatch.make_patch(source, destination))
        except Exception as e:
            raise AnsibleFilterError("JSON patch failed: %s" % to_native(e)) from e

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

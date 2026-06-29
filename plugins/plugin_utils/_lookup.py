# Copyright (c) 2026 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this plugin util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import typing as t

from ansible.errors import AnsibleLookupError

if t.TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ansible.plugins.lookup import LookupBase


def check_for_wrong_terms(plugin: LookupBase, *, direct: Mapping[str, t.Any]) -> None:
    # Note that we don't check "terms" here since the keyword argument "terms"
    # is mapped by Python to the run() positional argument "terms".
    for opt in ("_terms",):
        if opt in direct:
            raise AnsibleLookupError(
                f"The {opt!r} keyword argument is not supported, you must provide terms as positional arguments: use"
                f" lookup({plugin.ansible_name!r}, arg1, arg2) instead of lookup({plugin.ansible_name!r}, {opt}=[arg1, arg2])"
            )


def check_for_no_terms(plugin: LookupBase, *, terms: Sequence[t.Any], direct: Mapping[str, t.Any]) -> None:
    if terms:
        raise AnsibleLookupError("The lookup plugin does not accept positional arguments")
    # Note that we don't check "terms" here since the keyword argument "terms"
    # is mapped by Python to the run() positional argument "terms".
    for opt in ("_terms",):
        if opt in direct:
            raise AnsibleLookupError(f"The {opt!r} keyword argument is not supported")

# Copyright (c) 2020, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:  # pragma: no cover
    import datetime
    from collections.abc import Callable, Mapping, MutableMapping, MutableSequence, Sequence

    _T = t.TypeVar("_T")
    _Seq = t.TypeVar("_Seq", bound=Sequence)

    ######################################################################################################
    # Module argument spec

    ArgSpecType = t.Literal[
        "bits",
        "bool",
        "bytes",
        "dict",
        "float",
        "int",
        "json",
        "jsonarg",
        "list",
        "path",
        "raw",
        "sid",
        "str",
    ]
    MutuallyExclusiveT = t.Union[Sequence[str], Sequence[Sequence[str]]]  # noqa: UP007
    MutuallyExclusiveMutT = MutableSequence[Sequence[str]]
    RequiredTogetherT = Sequence[Sequence[str]]
    RequiredTogetherMutT = MutableSequence[Sequence[str]]
    RequiredOneOfT = Sequence[Sequence[str]]
    RequiredOneOfMutT = MutableSequence[Sequence[str]]
    RequiredIfT = Sequence[
        t.Union[  # noqa: UP007
            list[object],
            tuple[str, object, Sequence[str]],
            tuple[str, object, Sequence[str], bool],
        ]
    ]
    RequiredIfMutT = MutableSequence[
        t.Union[  # noqa: UP007
            list[object],
            tuple[str, object, Sequence[str]],
            tuple[str, object, Sequence[str], bool],
        ]
    ]
    RequiredByT = Mapping[str, Sequence[str]]
    RequiredByMutT = MutableMapping[str, Sequence[str]]

    class DeprecatedAlias(t.TypedDict):
        name: str
        date: t.NotRequired[datetime.date | str]
        version: t.NotRequired[str]
        collection_name: str

    class OneArgumentSpecT(t.TypedDict):
        type: t.NotRequired[ArgSpecType | Callable[[object], object]]
        elements: t.NotRequired[ArgSpecType]
        default: t.NotRequired[object]
        # For fallback elements, the first element of the sequence has to be a callable, the others sequences or dicts.
        # Unfortunately there is no way to specify this in a generic way...
        fallback: t.NotRequired[Sequence[Callable[[object], object] | Sequence[object] | Mapping[str, object]]]
        choices: t.NotRequired[Sequence[object]]
        context: t.NotRequired[Mapping[object, object]]
        required: t.NotRequired[bool]
        no_log: t.NotRequired[bool]
        aliases: t.NotRequired[Sequence[str]]
        apply_defaults: t.NotRequired[bool]
        removed_in_version: t.NotRequired[str]
        removed_at_date: t.NotRequired[datetime.date | str]
        removed_from_collection: t.NotRequired[str]
        options: t.NotRequired[Mapping[str, OneArgumentSpecT]]  # recursive!
        deprecated_aliases: t.NotRequired[Sequence[DeprecatedAlias]]

        mutually_exclusive: t.NotRequired[MutuallyExclusiveT]
        required_together: t.NotRequired[RequiredTogetherT]
        required_one_of: t.NotRequired[RequiredOneOfT]
        required_if: t.NotRequired[RequiredIfT]
        required_by: t.NotRequired[RequiredByT]

    ArgumentSpecT = Mapping[str, OneArgumentSpecT]
    ArgumentSpecMutT = MutableMapping[str, OneArgumentSpecT]

    ######################################################################################################
    # Module return values
    # (https://docs.ansible.com/projects/ansible/latest/reference_appendices/common_return_values.html)

    # Changed indication

    class ModuleReturnChanged(t.TypedDict):
        changed: t.NotRequired[bool]

    class ModuleReturnChangedReq(t.TypedDict):
        changed: bool

    # Message

    class ModuleReturnMsg(t.TypedDict):
        msg: t.NotRequired[str]

    class ModuleReturnMsgReq(t.TypedDict):
        msg: str

    # Standard out

    class ModuleReturnStdout(t.TypedDict):
        stdout: t.NotRequired[str]

    class ModuleReturnStdoutReq(t.TypedDict):
        stdout: str

    # Standard error

    class ModuleReturnStderr(t.TypedDict):
        stderr: t.NotRequired[str]

    class ModuleReturnStderrReq(t.TypedDict):
        stderr: str

    # Return code

    class ModuleReturnRc(t.TypedDict):
        rc: t.NotRequired[int]

    class ModuleReturnRcReq(t.TypedDict):
        rc: int

    # Backup file

    class ModuleReturnBackupFile(t.TypedDict):
        backup_file: t.NotRequired[str | None]

    class ModuleReturnBackupFileReq(t.TypedDict):
        backup_file: str | None

    # Diff

    class ModuleDiffValue(t.TypedDict, t.Generic[_T]):
        before: str | Mapping[str, _T]
        before_header: t.NotRequired[str]
        after: str | Mapping[str, _T]
        after_header: t.NotRequired[str]

    class ModuleReturnDiff(t.TypedDict, t.Generic[_T]):
        diff: t.NotRequired[ModuleDiffValue[_T]]

    class ModuleReturnDiffReq(t.TypedDict, t.Generic[_T]):
        diff: ModuleDiffValue[_T]

    class ModuleReturnDiffList(t.TypedDict, t.Generic[_T]):
        diff: t.NotRequired[MutableSequence[ModuleDiffValue[_T]]]

    class ModuleReturnDiffListReq(t.TypedDict, t.Generic[_T]):
        diff: MutableSequence[ModuleDiffValue[_T]]

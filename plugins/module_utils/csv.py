# Copyright (c) 2021, Andrew Pantuso (@ajpantuso) <ajpantuso@gmail.com>
# Copyright (c) 2018, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import csv
import typing as t
from io import StringIO

from ansible.module_utils.common.text.converters import to_native

if t.TYPE_CHECKING:
    from collections.abc import Sequence

    class DialectParamsOrNone(t.TypedDict):
        delimiter: t.NotRequired[str | None]
        doublequote: t.NotRequired[bool | None]
        escapechar: t.NotRequired[str | None]
        lineterminator: t.NotRequired[str | None]
        quotechar: t.NotRequired[str | None]
        quoting: t.NotRequired[int | None]
        skipinitialspace: t.NotRequired[bool | None]
        strict: t.NotRequired[bool | None]


class CustomDialectFailureError(Exception):
    pass


class DialectNotAvailableError(Exception):
    pass


CSVError = csv.Error


def initialize_dialect(dialect: str, **kwargs: t.Unpack[DialectParamsOrNone]) -> str:
    # Add Unix dialect from Python 3
    class unix_dialect(csv.Dialect):
        """Describe the usual properties of Unix-generated CSV files."""

        delimiter = ","
        quotechar = '"'
        doublequote = True
        skipinitialspace = False
        lineterminator = "\n"
        quoting = csv.QUOTE_ALL

    csv.register_dialect("unix", unix_dialect)

    if dialect not in csv.list_dialects():
        raise DialectNotAvailableError(f"Dialect '{dialect}' is not supported by your version of python.")

    # Create a dictionary from only set options
    dialect_params = {k: v for k, v in kwargs.items() if v is not None}
    if dialect_params:
        try:
            csv.register_dialect("custom", dialect, **dialect_params)  # type: ignore
        except TypeError as e:
            raise CustomDialectFailureError(f"Unable to create custom dialect: {e}") from e
        dialect = "custom"

    return dialect


def read_csv(data: str, dialect: str, fieldnames: Sequence[str] | None = None) -> csv.DictReader:
    BOM = "\ufeff"
    data = to_native(data, errors="surrogate_or_strict")
    if data.startswith(BOM):
        data = data[len(BOM) :]

    fake_fh = StringIO(data)

    reader = csv.DictReader(fake_fh, fieldnames=fieldnames, dialect=dialect)

    return reader

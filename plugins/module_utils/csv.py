# Copyright (c) 2021, Andrew Pantuso (@ajpantuso) <ajpantuso@gmail.com>
# Copyright (c) 2018, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import csv
from io import StringIO

from ansible.module_utils.common.text.converters import to_native


class CustomDialectFailureError(Exception):
    pass


class DialectNotAvailableError(Exception):
    pass


CSVError = csv.Error


def initialize_dialect(dialect, **kwargs):
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
            csv.register_dialect("custom", dialect, **dialect_params)
        except TypeError as e:
            raise CustomDialectFailureError(f"Unable to create custom dialect: {e}")
        dialect = "custom"

    return dialect


def read_csv(data, dialect, fieldnames=None):
    BOM = to_native("\ufeff")
    data = to_native(data, errors="surrogate_or_strict")
    if data.startswith(BOM):
        data = data[len(BOM) :]

    fake_fh = StringIO(data)

    reader = csv.DictReader(fake_fh, fieldnames=fieldnames, dialect=dialect)

    return reader

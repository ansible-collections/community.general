#
# Copyright (c) 2023 Felix Fontein <felix@fontein.de>
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations

import datetime as _datetime


def ensure_timezone_info(value):
    if value.tzinfo is not None:
        return value
    return value.astimezone(_datetime.timezone.utc)


def fromtimestamp(value):
    return _datetime.fromtimestamp(value, tz=_datetime.timezone.utc)


def now():
    return _datetime.datetime.now(tz=_datetime.timezone.utc)

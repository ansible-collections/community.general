# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 Felix Fontein <felix@fontein.de>
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import datetime as _datetime
import sys


_USE_TIMEZONE = sys.version_info >= (3, 6)


def ensure_timezone_info(value):
    if not _USE_TIMEZONE or value.tzinfo is not None:
        return value
    return value.astimezone(_datetime.timezone.utc)


def fromtimestamp(value):
    if _USE_TIMEZONE:
        return _datetime.fromtimestamp(value, tz=_datetime.timezone.utc)
    return _datetime.utcfromtimestamp(value)


def now():
    if _USE_TIMEZONE:
        return _datetime.datetime.now(tz=_datetime.timezone.utc)
    return _datetime.datetime.utcnow()

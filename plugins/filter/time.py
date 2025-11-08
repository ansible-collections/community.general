# Copyright (c) 2020, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re
from ansible.errors import AnsibleFilterError


UNIT_FACTORS = {
    "ms": [],
    "s": [1000],
    "m": [1000, 60],
    "h": [1000, 60, 60],
    "d": [1000, 60, 60, 24],
    "w": [1000, 60, 60, 24, 7],
    "mo": [1000, 60, 60, 24, 30],
    "y": [1000, 60, 60, 24, 365],
}


UNIT_TO_SHORT_FORM = {
    "millisecond": "ms",
    "msec": "ms",
    "msecond": "ms",
    "sec": "s",
    "second": "s",
    "hour": "h",
    "min": "m",
    "minute": "m",
    "day": "d",
    "week": "w",
    "month": "mo",
    "year": "y",
}


def multiply(factors):
    result = 1
    for factor in factors:
        result = result * factor
    return result


def to_time_unit(human_time, unit="ms", **kwargs):
    """Return a time unit from a human readable string"""

    # No need to handle 0
    if human_time == "0":
        return 0

    unit_to_short_form = UNIT_TO_SHORT_FORM
    unit_factors = UNIT_FACTORS

    unit = unit_to_short_form.get(unit.rstrip("s"), unit)
    if unit not in unit_factors:
        raise AnsibleFilterError(
            f"to_time_unit() can not convert to the following unit: {unit}. Available units (singular or plural):"
            f"{', '.join(unit_to_short_form.keys())}. Available short units: {', '.join(unit_factors.keys())}"
        )

    if "year" in kwargs:
        unit_factors["y"] = unit_factors["y"][:-1] + [kwargs.pop("year")]
    if "month" in kwargs:
        unit_factors["mo"] = unit_factors["mo"][:-1] + [kwargs.pop("month")]

    if kwargs:
        raise AnsibleFilterError(f"to_time_unit() got unknown keyword arguments: {', '.join(kwargs.keys())}")

    result = 0
    for h_time_string in human_time.split():
        res = re.match(r"(-?\d+)(\w+)", h_time_string)
        if not res:
            raise AnsibleFilterError(f"to_time_unit() can not interpret following string: {human_time}")

        h_time_int = int(res.group(1))
        h_time_unit = res.group(2)

        h_time_unit = unit_to_short_form.get(h_time_unit.rstrip("s"), h_time_unit)
        if h_time_unit not in unit_factors:
            raise AnsibleFilterError(f"to_time_unit() can not interpret following string: {human_time}")

        time_in_milliseconds = h_time_int * multiply(unit_factors[h_time_unit])
        result += time_in_milliseconds
    return round(result / multiply(unit_factors[unit]), 12)


def to_milliseconds(human_time, **kwargs):
    """Return milli seconds from a human readable string"""
    return to_time_unit(human_time, "ms", **kwargs)


def to_seconds(human_time, **kwargs):
    """Return seconds from a human readable string"""
    return to_time_unit(human_time, "s", **kwargs)


def to_minutes(human_time, **kwargs):
    """Return minutes from a human readable string"""
    return to_time_unit(human_time, "m", **kwargs)


def to_hours(human_time, **kwargs):
    """Return hours from a human readable string"""
    return to_time_unit(human_time, "h", **kwargs)


def to_days(human_time, **kwargs):
    """Return days from a human readable string"""
    return to_time_unit(human_time, "d", **kwargs)


def to_weeks(human_time, **kwargs):
    """Return weeks from a human readable string"""
    return to_time_unit(human_time, "w", **kwargs)


def to_months(human_time, **kwargs):
    """Return months from a human readable string"""
    return to_time_unit(human_time, "mo", **kwargs)


def to_years(human_time, **kwargs):
    """Return years from a human readable string"""
    return to_time_unit(human_time, "y", **kwargs)


class FilterModule:
    """Ansible time jinja2 filters"""

    def filters(self):
        filters = {
            "to_time_unit": to_time_unit,
            "to_milliseconds": to_milliseconds,
            "to_seconds": to_seconds,
            "to_minutes": to_minutes,
            "to_hours": to_hours,
            "to_days": to_days,
            "to_weeks": to_weeks,
            "to_months": to_months,
            "to_years": to_years,
        }

        return filters

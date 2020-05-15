# -*- coding: utf-8 -*-
# Copyright (c) 2020, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
from ansible.errors import AnsibleFilterError


UNIT_FACTORS = {
    'ms': [],
    's': [1000],
    'm': [1000, 60],
    'h': [1000, 60, 60],
    'd': [1000, 60, 60, 24],
    'w': [1000, 60, 60, 24, 7],
    'y': [1000, 60, 60, 24, 365],
}


UNIT_TO_SHORT_FORM = {
    'millisecond': 'ms',
    'milliseconds': 'ms',
    'msecond': 'ms',
    'mseconds': 'ms',
    'second': 's',
    'seconds': 's',
    'hour': 'h',
    'hours': 'h',
    'minute': 'm',
    'minutes': 'm',
    'day': 'd',
    'days': 'd',
    'week': 'w',
    'weeks': 'w',
    'year': 'y',
    'years': 'y',
}


def multiply(factors):
    result = 1
    for factor in factors:
         result = result * factor
    return result


def divide(divisors):
    result = 1
    for divisor in divisors:
         result = result / divisor
    return result


def to_time_unit(human_time, unit='ms'):
    ''' Return a time unit from a human readable string '''
    unit = UNIT_TO_SHORT_FORM.get(unit, unit)
    if unit not in UNIT_FACTORS:
        available_units = sorted(UNIT_FACTORS.keys() + UNIT_TO_SHORT_FORM.keys())
        raise AnsibleFilterError("to_time_unit() can not convert to the following unit: %s. "
                                 "Available units: %s" % (unit, ', '.join(available_units)))
    result = 0
    for h_time_string in human_time.split():
        res = re.match(r'(-?\d+)(\w+)', h_time_string)
        if not res:
            raise AnsibleFilterError(
                "to_time_unit() can not interpret following string: %s" % human_time)

        h_time_int = int(res.group(1))
        h_time_unit = res.group(2)

        if h_time_unit not in UNIT_FACTORS:
            raise AnsibleFilterError(
                "to_time_unit() can not interpret following string: %s" % human_time)

        time_in_milliseconds = h_time_int * multiply(UNIT_FACTORS[h_time_unit])
        result += time_in_milliseconds
    return round(result * divide(UNIT_FACTORS[unit]), 12)


def to_milliseconds(human_time):
    ''' Return milli seconds from a human readable string '''
    return to_time_unit(human_time, 'ms')


def to_seconds(human_time):
    ''' Return seconds from a human readable string '''
    return to_time_unit(human_time, 's')


def to_minutes(human_time):
    ''' Return minutes from a human readable string '''
    return to_time_unit(human_time, 'm')


def to_hours(human_time):
    ''' Return hours from a human readable string '''
    return to_time_unit(human_time, 'h')


def to_days(human_time):
    ''' Return days from a human readable string '''
    return to_time_unit(human_time, 'd')


def to_weeks(human_time):
    ''' Return weeks from a human readable string '''
    return to_time_unit(human_time, 'w')


def to_years(human_time):
    ''' Return years from a human readable string '''
    return to_time_unit(human_time, 'y')


class FilterModule(object):
    ''' Ansible time jinja2 filters '''

    def filters(self):
        filters = {
            'to_time_unit': to_time_unit,
            'to_milliseconds': to_milliseconds,
            'to_seconds': to_seconds,
            'to_minutes': to_minutes,
            'to_hours': to_hours,
            'to_days': to_days,
            'to_weeks': to_weeks,
            'to_years': to_years,
        }

        return filters

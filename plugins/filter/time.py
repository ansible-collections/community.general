# -*- coding: utf-8 -*-
# Copyright (c) 2020, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError


UNIT_FACTORS = {
    'second': {
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 24 * 60 * 60,
    },
    'minute': {
        's': 1 / 60,
        'm': 1,
        'h': 60,
        'd': 24 * 60,
    },
    'hour': {
        's': 1 / 60 / 60,
        'm': 1 / 60,
        'h': 1,
        'd': 24,
    }
}


def to_time_unit(human_time, unit='second'):
    ''' Return a time unit from a human readable string '''
    if unit not in UNIT_FACTORS:
        raise AnsibleFilterError("to_time_unit() can not convert to the following unit: %s, "
                                 "available units: %s" % (unit, ', '.join(UNIT_FACTORS.keys())))
    result = 0
    try:
        for time in human_time.split():
            for short_unit, factor in UNIT_FACTORS[unit].items():
                if time.endswith(short_unit):
                    time_int = int(time.replace(short_unit, ""))
                    result += time_int * factor
        return result
    except Exception:
        raise AnsibleFilterError(
            "to_time_unit() can't interpret following string: %s" % human_time)


def to_seconds(human_time):
    ''' Return seconds from a human readable string '''
    return to_time_unit(human_time, 'second')


def to_minutes(human_time):
    ''' Return minutes from a human readable string '''
    return to_time_unit(human_time, 'minute')


def to_hours(human_time):
    ''' Return hours from a human readable string '''
    return to_time_unit(human_time, 'hour')


class FilterModule(object):
    ''' Ansible time jinja2 filters '''

    def filters(self):
        filters = {
            'to_time_unit': to_time_unit,
            'to_seconds': to_seconds,
            'to_minutes': to_minutes,
            'to_hours': to_hours,
        }

        return filters

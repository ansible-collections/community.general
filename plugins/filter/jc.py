# -*- coding: utf-8 -*-
# (c) 2015, Filipe Niero Felisbino <filipenf@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
# contributed by Kelly Brazil <kellyjonbrazil@gmail.com>

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError, AnsibleFilterError
import importlib

try:
    import jc
    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def jc(data, parser, quiet=True, raw=False):
    """Convert returned command output to JSON using the JC library

    Arguments:

        parser      required    (string) the correct parser for the input data (e.g. 'ifconfig')
                                see https://github.com/kellyjonbrazil/jc#parsers for latest list of parsers.
        quiet       optional    (bool) True to suppress warning messages (default is True)
        raw         optional    (bool) True to return pre-processed JSON (default is False)

    Returns:

        dictionary or list of dictionaries

    Example:

        - name: run date command
          hosts: ubuntu
          tasks:
          - shell: date
            register: result
          - set_fact:
              myvar: "{{ result.stdout | community.general.jc('date') }}"
          - debug:
              msg: "{{ myvar }}"

        produces:

        ok: [192.168.1.239] => {
            "msg": {
                "day": 9,
                "hour": 22,
                "minute": 6,
                "month": "Aug",
                "month_num": 8,
                "second": 22,
                "timezone": "UTC",
                "weekday": "Sun",
                "weekday_num": 1,
                "year": 2020
            }
        }
    """

    if not HAS_LIB:
        raise AnsibleError('You need to install "jc" prior to running jc filter')

    try:
        jc_parser = importlib.import_module('jc.parsers.' + parser)
        return jc_parser.parse(data, quiet=quiet, raw=raw)

    except Exception as e:
        raise AnsibleFilterError('Error in jc filter plugin:  %s' % e)


class FilterModule(object):
    ''' Query filter '''

    def filters(self):
        return {
            'jc': jc
        }

# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andrew Pantuso (@ajpantuso) <ajpantuso@gmail.com>
# Copyright: (c) 2018, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.csv import (initialize_dialect, read_csv, CSVError,
                                                                            DialectNotAvailableError,
                                                                            CustomDialectFailureError)


def from_csv(data, dialect='excel', fieldnames=None, delimiter=None, skipinitialspace=None, strict=None):

    dialect_params = {
        "delimiter": delimiter,
        "skipinitialspace": skipinitialspace,
        "strict": strict,
    }

    try:
        dialect = initialize_dialect(dialect, **dialect_params)
    except (CustomDialectFailureError, DialectNotAvailableError) as e:
        raise AnsibleFilterError(to_native(e))

    reader = read_csv(data, dialect, fieldnames)

    data_list = []

    try:
        for row in reader:
            data_list.append(row)
    except CSVError as e:
        raise AnsibleFilterError("Unable to process file: %s" % to_native(e))

    return data_list


class FilterModule(object):

    def filters(self):
        return {
            'from_csv': from_csv
        }

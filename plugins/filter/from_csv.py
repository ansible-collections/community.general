# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andrew Pantuso (@ajpantuso) <ajpantuso@gmail.com>
# Copyright: (c) 2018, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import csv
from io import BytesIO, StringIO

from ansible.errors import AnsibleFilterError
from ansible.module_utils._text import to_native
from ansible.module_utils.six import PY3


# Add Unix dialect from Python 3
class unix_dialect(csv.Dialect):
    """Describe the usual properties of Unix-generated CSV files."""
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = csv.QUOTE_ALL


csv.register_dialect("unix", unix_dialect)


def from_csv(data, dialect='excel', fieldnames=None, delimiter=None, skipinitialspace=None, strict=None):

    if dialect not in csv.list_dialects():
        raise AnsibleFilterError("Dialect '%s' is not supported by your version of python." % dialect)

    dialect_options = dict(
        delimiter=delimiter,
        skipinitialspace=skipinitialspace,
        strict=strict,
    )

    # Create a dictionary from only set options
    dialect_params = dict((k, v) for k, v in dialect_options.items() if v is not None)
    if dialect_params:
        try:
            csv.register_dialect('custom', dialect, **dialect_params)
        except TypeError as e:
            raise AnsibleFilterError("Unable to create custom dialect: %s" % to_native(e))
        dialect = 'custom'

    data = to_native(data, errors='surrogate_or_strict')

    if PY3:
        fake_fh = StringIO(data)
    else:
        fake_fh = BytesIO(data)

    reader = csv.DictReader(fake_fh, fieldnames=fieldnames, dialect=dialect)

    data_list = []

    try:
        for row in reader:
            data_list.append(row)
    except csv.Error as e:
        raise AnsibleFilterError("Unable to process file: %s" % to_native(e))

    return data_list


class FilterModule(object):

    def filters(self):
        return {
            'from_csv': from_csv
        }

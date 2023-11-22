#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2019, John Westcott <john.westcott.iv@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: odbc
author: "John Westcott IV (@john-westcott-iv)"
version_added: "1.0.0"
short_description: Execute SQL via ODBC
description:
    - Read/Write info via ODBC drivers.
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none
options:
    dsn:
      description:
        - The connection string passed into ODBC.
      required: true
      type: str
    query:
      description:
        - The SQL query to perform.
      required: true
      type: str
    params:
      description:
        - Parameters to pass to the SQL query.
      type: list
      elements: str
    commit:
      description:
        - Perform a commit after the execution of the SQL query.
        - Some databases allow a commit after a select whereas others raise an exception.
        - Default is V(true) to support legacy module behavior.
      type: bool
      default: true
      version_added: 1.3.0
requirements:
  - "pyodbc"

notes:
  - "Like the command module, this module always returns changed = yes whether or not the query would change the database."
  - "To alter this behavior you can use C(changed_when): [yes or no]."
  - "For details about return values (description and row_count) see U(https://github.com/mkleehammer/pyodbc/wiki/Cursor)."
'''

EXAMPLES = '''
- name: Set some values in the test db
  community.general.odbc:
    dsn: "DRIVER={ODBC Driver 13 for SQL Server};Server=db.ansible.com;Database=my_db;UID=admin;PWD=password;"
    query: "Select * from table_a where column1 = ?"
    params:
      - "value1"
    commit: false
  changed_when: false
'''

RETURN = '''
results:
    description: List of lists of strings containing selected rows, likely empty for DDL statements.
    returned: success
    type: list
    elements: list
description:
    description: "List of dicts about the columns selected from the cursors, likely empty for DDL statements. See notes."
    returned: success
    type: list
    elements: dict
row_count:
    description: "The number of rows selected or modified according to the cursor defaults to -1. See notes."
    returned: success
    type: str
'''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

HAS_PYODBC = None
try:
    import pyodbc
    HAS_PYODBC = True
except ImportError as e:
    HAS_PYODBC = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            dsn=dict(type='str', required=True, no_log=True),
            query=dict(type='str', required=True),
            params=dict(type='list', elements='str'),
            commit=dict(type='bool', default=True),
        ),
    )

    dsn = module.params.get('dsn')
    query = module.params.get('query')
    params = module.params.get('params')
    commit = module.params.get('commit')

    if not HAS_PYODBC:
        module.fail_json(msg=missing_required_lib('pyodbc'))

    # Try to make a connection with the DSN
    connection = None
    try:
        connection = pyodbc.connect(dsn)
    except Exception as e:
        module.fail_json(msg='Failed to connect to DSN: {0}'.format(to_native(e)))

    result = dict(
        changed=True,
        description=[],
        row_count=-1,
        results=[],
    )

    try:
        cursor = connection.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        if commit:
            cursor.commit()
        try:
            # Get the rows out into an 2d array
            for row in cursor.fetchall():
                new_row = []
                for column in row:
                    new_row.append("{0}".format(column))
                result['results'].append(new_row)

            # Return additional information from the cursor
            for row_description in cursor.description:
                description = {}
                description['name'] = row_description[0]
                description['type'] = row_description[1].__name__
                description['display_size'] = row_description[2]
                description['internal_size'] = row_description[3]
                description['precision'] = row_description[4]
                description['scale'] = row_description[5]
                description['nullable'] = row_description[6]
                result['description'].append(description)

            result['row_count'] = cursor.rowcount
        except pyodbc.ProgrammingError as pe:
            pass
        except Exception as e:
            module.fail_json(msg="Exception while reading rows: {0}".format(to_native(e)))

        cursor.close()
    except Exception as e:
        module.fail_json(msg="Failed to execute query: {0}".format(to_native(e)))
    finally:
        connection.close()

    module.exit_json(**result)


if __name__ == '__main__':
    main()

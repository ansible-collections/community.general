#!/usr/bin/python

# Copyright: (c) 2021, Rainer Leber <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hana_query

short_description: Execute SQL on HANA.

version_added: "3.2.0"

description: This module executes SQL statements on HANA with hdbsql.

options:
    sid:
        description: The system ID.
        type: str
    instance:
        description: The instance number.
        type: str
    user:
        description: A dedicated username. Defaults to C(SYSTEM).
        type: str
        default: SYSTEM
    password:
        description: The password to connect to the database.
        type: str
    autocommit:
        description: Autocommit the statement.
        type: bool
        default: True
    host:
        description: The Host IP address. The port can be defined as well.
        type: str
    database:
        description: Define the database on which to connect.
        type: str
    encrypted:
        description: Use encrypted connection. Defaults to C(false).
        type: bool
        default: false
    filepath:
        description:
        - One or more files each containing one SQL query to run.
        - Must be a string or list containing strings.
        type: list
        elements: path
    query:
        description:
        - SQL query to run. Multiple queries can be passed using YAML list syntax.
        - Must be a string or list containing strings.
        type: list

author:
    - Rainer Leber (@rainerleber)
'''

EXAMPLES = r'''

- name: Simple select query
  community.general.hana_query:
    sid: "hdb"
    instance: "01"
    password: "Test123"
    query: "select user_name from users"

- name: Run several queries
  community.general.hana_query:
    sid: "hdb"
    instance: "01"
    password: "Test123"
    query:
    - "select user_name from users"
    - select user_name from users
    host: "localhost"
    autocommit: False

- name: Run several queries from file
  community.general.hana_query:
    sid: "hdb"
    instance: "01"
    password: "Test123"
    filepath:
    - /tmp/HANA_CPU_UtilizationPerCore_2.00.020+.txt
    - /tmp/HANA.txt
    host: "localhost"


'''

import io
import csv
import json
from ansible.module_utils.basic import AnsibleModule


def csv_to_json(rawcsv):
    lines = rawcsv[:rawcsv.rfind('\n')]
    reader_raw = csv.DictReader(io.StringIO(lines))
    reader = [dict((k, v.strip()) for k, v in row.items()) for row in reader_raw]
    tolist = list(reader)
    return json.dumps(tolist)


def main():
    global module

    module = AnsibleModule(
        argument_spec=dict(
            sid=dict(type='str', required=True),
            instance=dict(type='str', required=False),
            encrypted=dict(type='bool', required=False, default=False),
            host=dict(type='str', required=False),
            user=dict(type='str', required=False, default="SYSTEM"),
            password=dict(type='str', required=True, no_log=True),
            database=dict(type='str', required=False),
            query=dict(type='list', required=False),
            filepath=dict(type='list', required=False),
            autocommit=dict(type='bool', required=False, default=True)
        )
    )
    rc, out, err, out_raw = [0, "", "", ""]

    params = module.params

    sid = (params['sid']).upper()
    instance = params['instance']
    user = params['user']
    password = params['password']
    autocommit = params['autocommit']
    host = params['host']
    database = params['database']
    encrypted = params['encrypted']

    filepath = params['filepath']
    query = params['query']

    bin_path = f"/usr/sap/{sid}/HDB{instance}/exe/hdbsql"

    present = filepath is not None or query is not None

    try:
        command = [module.get_bin_path(bin_path, required=True)]
    except Exception:
        'hdbsql not found {0}. \r\nSTDOUT: {1}\r\n\r\nSTDERR: {2}'.format(
            rc, out, err)

    if present:
        if encrypted is True:
            command.extend(['-attemptencrypt'])
        if autocommit is False:
            command.extend(['-z'])
        if host is not None:
            command.extend(['-n', host])
        if database is not None:
            command.extend(['-d', database])
        # -x Suppresses additional output, such as the number of selected rows in a result set.
        command.extend(['-x', '-i', instance, '-u', user, '-p', password])

        if filepath is not None:
            command.extend(['-I'])
            for p in filepath:
                # makes a command like hdbsql -i 01 -u SYSTEM -p secret123# -I /tmp/HANA_CPU_UtilizationPerCore_2.00.020+.txt,
                # iterates through files and append the output to var out.
                command.extend([p])
                (rc, out_raw, err) = module.run_command(command)
                del command[-1]

                out = out + csv_to_json(out_raw)
        if query is not None:
            for q in query:
                command.extend([q])
                # makes a command like hdbsql -i 01 -u SYSTEM -p secret123# "select user_name from users",
                # iterates through multiple commands and append the output to var out.
                (rc, out_raw, err) = module.run_command(command)
                del command[-1]

                out = out + csv_to_json(out_raw)
        changed = True
    else:
        changed = False
        out = "nothing to do, no command provided"

    module.exit_json(changed=changed, message=rc, stdout=out,
                     stderr=err, command=' '.join(command))


if __name__ == '__main__':
    main()

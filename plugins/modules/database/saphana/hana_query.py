#!/usr/bin/python

# Copyright: (c) 2021, Rainer Leber <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: hana_query
<<<<<<< HEAD
<<<<<<< HEAD
short_description: Execute SQL on HANA
=======

short_description: Execute SQL on HANA

version_added: "3.2.0"

>>>>>>> 4e8527be... Update plugins/modules/database/saphana/hana_query.py
=======
short_description: Execute SQL on HANA
>>>>>>> 3fccb73c... fix checkmode
description: This module executes SQL statements on HANA with hdbsql.
options:
    sid:
        description: The system ID.
        type: str
        required: true
    instance:
        description: The instance number.
        type: str
        required: true
    user:
        description: A dedicated username. Defaults to C(SYSTEM).
        type: str
        default: SYSTEM
    password:
        description: The password to connect to the database.
        type: str
        required: true
    autocommit:
        description: Autocommit the statement.
        type: bool
        default: true
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
<<<<<<< HEAD
<<<<<<< HEAD
        - SQL query to run.
        - Must be a string or list containing strings. Please note that if you supply a string, it will be split by commas (C(,)) to a list.
          It is better to supply a one-element list instead to avoid mangled input.
<<<<<<< HEAD
=======
        - SQL query to run. Multiple queries can be passed using YAML list syntax.
=======
        - SQL query to run.
>>>>>>> aa532df1... Update plugins/modules/database/saphana/hana_query.py
        - Must be a string or list containing strings. Please note that if you supply a string, it will be split by commas (C(,)) to a list.
          It's better to supply a one-element list instead to avoid mangled input.
>>>>>>> 098ad042... Update plugins/modules/database/saphana/hana_query.py
=======
>>>>>>> 2a56c343... Update plugins/modules/database/saphana/hana_query.py
        type: list
        elements: str
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
notes:
    - Does not support C(check_mode).
=======

<<<<<<< HEAD
>>>>>>> 5173c975... change documentation
=======
    notes: Does not support C(check_mode).

>>>>>>> e429b48b... Update plugins/modules/database/saphana/hana_query.py
=======
notes: Does not support C(check_mode).
>>>>>>> 3fccb73c... fix checkmode
=======
notes: 
<<<<<<< HEAD
  - Does not support C(check_mode).
>>>>>>> 0f5a841c... change notes
=======
=======
notes:
>>>>>>> ec16e697... remove white space
    - Does not support C(check_mode).
>>>>>>> d286ab2d... change
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
    - "select user_name from users;"
    - select * from SYSTEM;
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
<<<<<<< HEAD
'''

RETURN = r'''
query_result:
    description: List containing results of all queries executed (one sublist for every query).
    returned: on success
    type: list
    elements: list
    sample: [[{"Column": "Value1"}, {"Column": "Value2"}], [{"Column": "Value1"}, {"Column": "Value2"}]]
=======
>>>>>>> dd12b922... Update plugins/modules/database/saphana/hana_query.py
'''

<<<<<<< HEAD
=======
RETURN = r'''
query_result:
    description: List containing results of all queries executed (one sublist for every query).
    returned: on success
    type: list
    elements: list
    sample: [[{"Column": "Value1"}, {"Column": "Value2"}], [{"Column": "Value1"}, {"Column": "Value2"}]]
'''

<<<<<<< HEAD
import io
>>>>>>> 181d9f65... add return description, improvements
=======
>>>>>>> 2421789e... change StringIO module
import csv
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import StringIO
<<<<<<< HEAD
<<<<<<< HEAD
from ansible.module_utils._text import to_native
=======
>>>>>>> 2421789e... change StringIO module

=======
from ansible.module_utils._text import to_native
>>>>>>> 879579ba... add module

<<<<<<< HEAD
<<<<<<< HEAD
def csv_to_list(rawcsv):
=======
def csv_to_json(rawcsv):
<<<<<<< HEAD
    reader_raw = None
>>>>>>> 43dad80e... change to None for compatibility
=======
>>>>>>> 2421789e... change StringIO module
    lines = rawcsv[:rawcsv.rfind('\n')]
    reader_raw = csv.DictReader(StringIO(lines))
    reader = [dict((k, v.strip()) for k, v in row.items()) for row in reader_raw]
    return list(reader)
=======
def csv_to_list(rawcsv):
    lines = rawcsv[:rawcsv.rfind('\n')]
    reader_raw = csv.DictReader(StringIO(lines))
    reader = [dict((k, v.strip()) for k, v in row.items()) for row in reader_raw]
<<<<<<< HEAD
    return reader
>>>>>>> 22bc01e8... move to list of list, change output
=======
    return list(reader)
>>>>>>> 731d37b4... Update plugins/modules/database/saphana/hana_query.py


def main():
    module = AnsibleModule(
        argument_spec=dict(
            sid=dict(type='str', required=True),
            instance=dict(type='str', required=True),
            encrypted=dict(type='bool', required=False, default=False),
            host=dict(type='str', required=False),
            user=dict(type='str', required=False, default="SYSTEM"),
            password=dict(type='str', required=True, no_log=True),
            database=dict(type='str', required=False),
            query=dict(type='list', elements='str', required=False),
            filepath=dict(type='list', elements='path', required=False),
<<<<<<< HEAD
<<<<<<< HEAD
            autocommit=dict(type='bool', required=False, default=True),
        ),
        required_one_of=[('query', 'filepath')],
        supports_check_mode=False,
=======
            autocommit=dict(type='bool', required=False, default=True)
=======
            autocommit=dict(type='bool', required=False, default=True),
<<<<<<< HEAD
>>>>>>> c39f844a... Update plugins/modules/database/saphana/hana_query.py
        )
>>>>>>> 54a595e2... Update plugins/modules/database/saphana/hana_query.py
=======
        ),
<<<<<<< HEAD
        require_one_of=[('query', 'filepath')],
>>>>>>> b694a498... Update plugins/modules/database/saphana/hana_query.py
=======
        required_one_of=[('query', 'filepath')],
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 181d9f65... add return description, improvements
=======
        supports_checkmode=False,
>>>>>>> 85bcab15... Update plugins/modules/database/saphana/hana_query.py
=======
        supports_check_mode=False,
>>>>>>> 3fccb73c... fix checkmode
    )
    rc, out, err, out_raw = [0, [], "", ""]

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

    bin_path = "/usr/sap/{sid}/HDB{instance}/exe/hdbsql".format(sid=sid, instance=instance)
<<<<<<< HEAD
=======

<<<<<<< HEAD
    present = filepath is not None or query is not None
>>>>>>> 3db4fc83... Update plugins/modules/database/saphana/hana_query.py

=======
>>>>>>> 181d9f65... add return description, improvements
    try:
        command = [module.get_bin_path(bin_path, required=True)]
<<<<<<< HEAD
<<<<<<< HEAD
    except Exception as e:
        module.fail_json(msg='Failed to find hdbsql at the expected path "{0}". Please check SID and instance number: "{1}"'.format(bin_path, to_native(e)))

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

<<<<<<< HEAD
    if filepath is not None:
        command.extend(['-I'])
        for p in filepath:
            # makes a command like hdbsql -i 01 -u SYSTEM -p secret123# -I /tmp/HANA_CPU_UtilizationPerCore_2.00.020+.txt,
            # iterates through files and append the output to var out.
            query_command = command + [p]
            (rc, out_raw, err) = module.run_command(query_command)
            out.append(csv_to_list(out_raw))
    if query is not None:
        for q in query:
            # makes a command like hdbsql -i 01 -u SYSTEM -p secret123# "select user_name from users",
            # iterates through multiple commands and append the output to var out.
            query_command = command + [q]
            (rc, out_raw, err) = module.run_command(query_command)
            out.append(csv_to_list(out_raw))
    changed = True

    module.exit_json(changed=changed, message=rc, query_result=out, stderr=err)
=======
=======
    except Exception:
        module.fail_json(msg='hdbsql not found at "{0}". Please check SID and instance number.'.format(bin_path))
=======
    except Exception as e:
        module.fail_json(msg='Failed to find hdbsql at the expected path "{0}". Please check SID and instance number: "{1}"'.format(bin_path, to_native(e)))
>>>>>>> 2a19428e... Update plugins/modules/database/saphana/hana_query.py

<<<<<<< HEAD
>>>>>>> 8358dba9... change hana_query add test
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
                query_command = command + [p]
                (rc, out_raw, err) = module.run_command(query_command)
                out = out + csv_to_json(out_raw)
        if query is not None:
            for q in query:
                # makes a command like hdbsql -i 01 -u SYSTEM -p secret123# "select user_name from users",
                # iterates through multiple commands and append the output to var out.
                query_command = command + [q]
                (rc, out_raw, err) = module.run_command(query_command)
                out = out + csv_to_json(out_raw)
        changed = True
    else:
        changed = False
        out = "nothing to do, no command provided"
=======
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
            query_command = command + [p]
            (rc, out_raw, err) = module.run_command(query_command)
            out.append(csv_to_list(out_raw))
    if query is not None:
        for q in query:
            # makes a command like hdbsql -i 01 -u SYSTEM -p secret123# "select user_name from users",
            # iterates through multiple commands and append the output to var out.
            query_command = command + [q]
            (rc, out_raw, err) = module.run_command(query_command)
            out.append(csv_to_list(out_raw))
    changed = True

<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 181d9f65... add return description, improvements

<<<<<<< HEAD
    module.exit_json(changed=changed, message=rc, stdout=out,
                     stderr=err, command=' '.join(command))
>>>>>>> 39ae1ee2... Update plugins/modules/database/saphana/hana_query.py
=======
=======
>>>>>>> e40f395f... change return
    module.exit_json(changed=changed, message=rc, stdout=out, stderr=err)
>>>>>>> 8358dba9... change hana_query add test
=======
    module.exit_json(changed=changed, message=rc, query_result=out, stderr=err)
>>>>>>> 22bc01e8... move to list of list, change output


if __name__ == '__main__':
    main()

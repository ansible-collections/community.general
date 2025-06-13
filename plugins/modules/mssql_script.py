#!/usr/bin/python

# Copyright (c) 2021, Kris Budde <kris@budd.ee
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
module: mssql_script

short_description: Execute SQL scripts on a MSSQL database

version_added: "4.0.0"

description:
  - Execute SQL scripts on a MSSQL database.
extends_documentation_fragment:
  - community.general.attributes

attributes:
  check_mode:
    support: partial
    details:
      - The script will not be executed in check mode.
  diff_mode:
    support: none

options:
  name:
    description: Database to run script against.
    aliases: [db]
    default: ''
    type: str
  login_user:
    description: The username used to authenticate with.
    type: str
  login_password:
    description: The password used to authenticate with.
    type: str
  login_host:
    description: Host running the database.
    type: str
    required: true
  login_port:
    description: Port of the MSSQL server. Requires O(login_host) be defined as well.
    default: 1433
    type: int
  script:
    description:
      - The SQL script to be executed.
      - Script can contain multiple SQL statements. Multiple Batches can be separated by V(GO) command.
      - Each batch must return at least one result set.
      - Mutually exclusive with O(script_path).
    type: str
  script_path:
    description:
      - Path to a file containing the SQL script to be executed.
      - Script can contain multiple SQL statements. Multiple Batches can be separated by V(GO) command.
      - Each batch must return at least one result set.
      - If the file contains a Byte Order Mark (BOM), it will be automatically detected and removed.
      - Mutually exclusive with O(script).
    type: path
    version_added: 10.8.0
  transaction:
    description:
      - If transactional mode is requested, start a transaction and commit the change only if the script succeed. Otherwise,
        rollback the transaction.
      - If transactional mode is not requested (default), automatically commit the change.
    type: bool
    default: false
    version_added: 8.4.0
  output:
    description:
      - With V(default) each row will be returned as a list of values. See RV(query_results).
      - Output format V(dict) will return dictionary with the column names as keys. See RV(query_results_dict).
      - V(dict) requires named columns to be returned by each query otherwise an error is thrown.
    choices: ["dict", "default"]
    default: 'default'
    type: str
  params:
    description: |-
      Parameters passed to the script as SQL parameters.
      (Query V('SELECT %(name\)s"') with V(example: '{"name": "John Doe"}).)'.
    type: dict
notes:
  - Requires the pymssql Python package on the remote host. For Ubuntu, this is as easy as C(pip install pymssql) (See M(ansible.builtin.pip)).
requirements:
  - pymssql

author:
  - Kris Budde (@kbudde)
  - Joe Zollo (@zollo)
"""

EXAMPLES = r"""
- name: Check DB connection
  community.general.mssql_script:
    login_user: "{{ mssql_login_user }}"
    login_password: "{{ mssql_login_password }}"
    login_host: "{{ mssql_host }}"
    login_port: "{{ mssql_port }}"
    db: master
    script: "SELECT 1"

- name: Query with parameter
  community.general.mssql_script:
    login_user: "{{ mssql_login_user }}"
    login_password: "{{ mssql_login_password }}"
    login_host: "{{ mssql_host }}"
    login_port: "{{ mssql_port }}"
    script: |
      SELECT name, state_desc FROM sys.databases WHERE name = %(dbname)s
    params:
      dbname: msdb
  register: result_params

- assert:
    that:
      - result_params.query_results[0][0][0][0] == 'msdb'
      - result_params.query_results[0][0][0][1] == 'ONLINE'

- name: Execute script from file with BOM present
  community.general.mssql_script:
    login_user: "{{ mssql_login_user }}"
    login_password: "{{ mssql_login_password }}"
    login_host: "{{ mssql_host }}"
    login_port: "{{ mssql_port }}"
    script_path: /path/to/sql/script_with_bom.sql
  register: result_bom

- assert:
    that:
      - result_bom.script_source = 'file'
      - result_bom.bom_removed = True
      - result_bom.bom_type = 'UTF-8'

- name: Query within a transaction
  community.general.mssql_script:
    login_user: "{{ mssql_login_user }}"
    login_password: "{{ mssql_login_password }}"
    login_host: "{{ mssql_host }}"
    login_port: "{{ mssql_port }}"
    script: |
      UPDATE sys.SomeTable SET desc = 'some_table_desc' WHERE name = %(dbname)s
      UPDATE sys.AnotherTable SET desc = 'another_table_desc' WHERE name = %(dbname)s
    transaction: true
    params:
      dbname: msdb

- name: two batches with default output
  community.general.mssql_script:
    login_user: "{{ mssql_login_user }}"
    login_password: "{{ mssql_login_password }}"
    login_host: "{{ mssql_host }}"
    login_port: "{{ mssql_port }}"
    script: |
      SELECT 'Batch 0 - Select 0'
      SELECT 'Batch 0 - Select 1'
      GO
      SELECT 'Batch 1 - Select 0'
  register: result_batches
- assert:
    that:
      - result_batches.query_results | length == 2 # two batch results
      - result_batches.query_results[0] | length == 2 # two selects in first batch
      - result_batches.query_results[0][0] | length == 1 # one row in first select
      - result_batches.query_results[0][0][0] | length == 1 # one column in first row
      - result_batches.query_results[0][0][0][0] == 'Batch 0 - Select 0' # each row contains a list of values.

- name: two batches with dict output
  community.general.mssql_script:
    login_user: "{{ mssql_login_user }}"
    login_password: "{{ mssql_login_password }}"
    login_host: "{{ mssql_host }}"
    login_port: "{{ mssql_port }}"
    output: dict
    script: |
      SELECT 'Batch 0 - Select 0' as b0s0
      SELECT 'Batch 0 - Select 1' as b0s1
      GO
      SELECT 'Batch 1 - Select 0' as b1s0
  register: result_batches_dict
- assert:
    that:
      - result_batches_dict.query_results_dict | length == 2 # two batch results
      - result_batches_dict.query_results_dict[0] | length == 2 # two selects in first batch
      - result_batches_dict.query_results_dict[0][0] | length == 1 # one row in first select
      - result_batches_dict.query_results_dict[0][0][0]['b0s0'] == 'Batch 0 - Select 0' # column 'b0s0' of first row
"""

RETURN = r"""
script_source:
  description: Source of the executed script.
  type: str
  returned: always
  sample: "file"
  choices: ["file", "parameter"]
script_path:
  description: Path to the script file that was executed.
  type: str
  returned: when script_path parameter is used
  sample: "/path/to/script.sql"
bom_removed:
  description: Whether a Byte Order Mark was detected and removed from the script file.
  type: bool
  returned: when script_path parameter is used and BOM was found
  sample: true
bom_type:
  description: Type of Byte Order Mark that was detected and removed.
  type: str
  returned: when script_path parameter is used and BOM was found
  sample: "UTF-8"
query_results:
  description: List of batches (queries separated by V(GO) keyword).
  type: list
  elements: list
  returned: success and O(output=default)
  sample: [[[["Batch 0 - Select 0"]], [["Batch 0 - Select 1"]]], [[["Batch 1 - Select 0"]]]]
  contains:
    queries:
      description:
        - List of result sets of each query.
        - If a query returns no results, the results of this and all the following queries will not be included in the output.
        - Use the V(GO) keyword in O(script) to separate queries.
      type: list
      elements: list
      contains:
        rows:
          description: List of rows returned by query.
          type: list
          elements: list
          contains:
            column_value:
              description:
                - List of column values.
                - Any non-standard JSON type is converted to string.
              type: list
              example: ["Batch 0 - Select 0"]
              returned: success, if output is default
query_results_dict:
  description: List of batches (queries separated by V(GO) keyword).
  type: list
  elements: list
  returned: success and O(output=dict)
  sample: [[[["Batch 0 - Select 0"]], [["Batch 0 - Select 1"]]], [[["Batch 1 - Select 0"]]]]
  contains:
    queries:
      description:
        - List of result sets of each query.
        - If a query returns no results, the results of this and all the following queries will not be included in the output.
          Use V(GO) keyword to separate queries.
      type: list
      elements: list
      contains:
        rows:
          description: List of rows returned by query.
          type: list
          elements: list
          contains:
            column_dict:
              description:
                - Dictionary of column names and values.
                - Any non-standard JSON type is converted to string.
              type: dict
              example: {"col_name": "Batch 0 - Select 0"}
              returned: success, if output is dict
"""

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import traceback
import json
import os
import codecs

PYMSSQL_IMP_ERR = None
try:
    import pymssql
except ImportError:
    PYMSSQL_IMP_ERR = traceback.format_exc()
    MSSQL_FOUND = False
else:
    MSSQL_FOUND = True


def clean_output(o):
    return str(o)


def detect_and_remove_bom(content):
    """
    Detect and remove Byte Order Mark (BOM) from content.
    Returns tuple (cleaned_content, bom_removed, bom_type)
    """
    bom_removed = False
    bom_type = None

    # Common BOM patterns
    boms = [
        (codecs.BOM_UTF8, 'UTF-8'),
        (codecs.BOM_UTF16_LE, 'UTF-16 LE'),
        (codecs.BOM_UTF16_BE, 'UTF-16 BE'),
        (codecs.BOM_UTF32_LE, 'UTF-32 LE'),
        (codecs.BOM_UTF32_BE, 'UTF-32 BE'),
    ]

    # Check if content is bytes or string
    if isinstance(content, str):
        content_bytes = content.encode('utf-8')
    else:
        content_bytes = content

    # Check for BOM
    for bom, bom_name in boms:
        if content_bytes.startswith(bom):
            content_bytes = content_bytes[len(bom):]
            bom_removed = True
            bom_type = bom_name
            break

    # Convert back to string if original was string
    if isinstance(content, str):
        try:
            cleaned_content = content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback to original encoding detection
            cleaned_content = content_bytes.decode('utf-8', errors='replace')
    else:
        cleaned_content = content_bytes

    return cleaned_content, bom_removed, bom_type


def read_script_file(script_path):
    """
    Read SQL script file and remove BOM if present.
    Returns tuple (script_content, bom_info)
    """
    if not os.path.exists(script_path):
        raise IOError(f"Script file not found: {script_path}")

    if not os.path.isfile(script_path):
        raise IOError(f"Path is not a file: {script_path}")

    try:
        with open(script_path, 'rb') as f:
            raw_content = f.read()

        # Convert to string for processing
        try:
            script_content = raw_content.decode('utf-8')
        except UnicodeDecodeError:
            # Try other common encodings
            for encoding in ['utf-16', 'latin1', 'cp1252']:
                try:
                    script_content = raw_content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                # Last resort - decode with error replacement
                script_content = raw_content.decode('utf-8', errors='replace')

        # Detect and remove BOM
        cleaned_content, bom_removed, bom_type = detect_and_remove_bom(
            script_content)

        bom_info = {
            'bom_found': bom_removed,
            'bom_type': bom_type,
            'file_path': script_path
        }

        return cleaned_content, bom_info

    except IOError as e:
        raise IOError(f"Error reading script file \
                      {script_path}: {str(e)}") from e

def run_module():
    module_args = dict(
        name=dict(required=False, aliases=['db'], default=''),
        login_user=dict(),
        login_password=dict(no_log=True),
        login_host=dict(required=True),
        login_port=dict(type='int', default=1433),
        script=dict(),
        script_path=dict(type='path'),
        output=dict(default='default', choices=['dict', 'default']),
        params=dict(type='dict'),
        transaction=dict(type='bool', default=False),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[('script', 'script_path')],
        required_one_of=[('script', 'script_path')],
    )
    if not MSSQL_FOUND:
        module.fail_json(msg=missing_required_lib(
            'pymssql'), exception=PYMSSQL_IMP_ERR)

    db = module.params['name']
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    login_host = module.params['login_host']
    login_port = module.params['login_port']
    script = module.params['script']
    script_path = module.params['script_path']
    output = module.params['output']
    sql_params = module.params['params']
    # Added param to set the transactional mode (true/false)
    transaction = module.params['transaction']

    # Handle script source - either from direct script or file
    bom_info = None
    if script_path:
        try:
            script, bom_info = read_script_file(script_path)
            result['script_source'] = 'file'
            result['script_path'] = script_path
            if bom_info['bom_found']:
                result['bom_removed'] = True
                result['bom_type'] = bom_info['bom_type']
        except (IOError, OSError) as e:
            module.fail_json(msg=f"Error reading script file: {str(e)}")
    else:
        result['script_source'] = 'parameter'

    login_querystring = login_host
    if login_port != 1433:
        login_querystring = "%s:%s" % (login_host, login_port)

    if login_user is not None and login_password is None:
        module.fail_json(
            msg="when supplying login_user argument, login_password must also be provided")

    try:
        conn = pymssql.connect(
            user=login_user, password=login_password, host=login_querystring, database=db)
        cursor = conn.cursor()
    except Exception as e:
        if "Unknown database" in str(e):
            errno, errstr = e.args
            module.fail_json(msg="ERROR: %s %s" % (errno, errstr))
        else:
            module.fail_json(msg="unable to connect, check login_user and login_password are correct, or alternatively check your "
                                 "@sysconfdir@/freetds.conf / ${HOME}/.freetds.conf")

    # If transactional mode is requested, start a transaction
    conn.autocommit(not transaction)

    query_results_key = 'query_results'
    if output == 'dict':
        cursor = conn.cursor(as_dict=True)
        query_results_key = 'query_results_dict'

    # Process the script into batches
    queries = []
    current_batch = []
    for statement in script.splitlines(True):
        # Ignore the Byte Order Mark, if found
        if statement.strip() == '\uFEFF':
            continue

        # Assume each 'GO' is on its own line but may have leading/trailing whitespace
        # and be of mixed-case
        if statement.strip().upper() != 'GO':
            current_batch.append(statement)
        else:
            queries.append(''.join(current_batch))
            current_batch = []
    if len(current_batch) > 0:
        queries.append(''.join(current_batch))

    result['changed'] = True
    if module.check_mode:
        module.exit_json(**result)

    query_results = []
    for query in queries:
        # Catch and exit on any bad query errors
        try:
            cursor.execute(query, sql_params)
            qry_result = []
            rows = cursor.fetchall()
            while rows:
                qry_result.append(rows)
                rows = cursor.fetchall()
            query_results.append(qry_result)
        except Exception as e:
            # We know we executed the statement so this error just means we have no resultset
            # which is ok (eg UPDATE/INSERT)
            if (
                type(e).__name__ == 'OperationalError' and
                str(e) == 'Statement not executed or executed statement has no resultset'
            ):
                query_results.append([])
            else:
                # Rollback transaction before failing the module in case of error
                if transaction:
                    conn.rollback()
                error_msg = '%s: %s' % (type(e).__name__, str(e))
                module.fail_json(msg="query failed", query=query, error=error_msg, **result)

    # Commit transaction before exiting the module in case of no error
    if transaction:
        conn.commit()

    # ensure that the result is json serializable
    qry_results = json.loads(json.dumps(query_results, default=clean_output))

    result[query_results_key] = qry_results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

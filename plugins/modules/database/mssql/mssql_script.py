#!/usr/bin/python

# Copyright: (c) 2021, Kris Budde <kris@budd.ee
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: mssql_script

short_description: Execute SQL scripts on a MSSQL database

version_added: "4.0.0"

description:
  - Execute SQL scripts on a MSSQL database.

options:
    name:
        description: Database to run script against.
        aliases: [ db ]
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
        description: Port of the MSSQL server. Requires I(login_host) be defined as well.
        default: 1433
        type: int
    script:
        description:
          - The SQL script to be executed.
          - Script can contain multiple SQL statements. Multiple Batches can be separated by C(GO) command.
          - Each batch must return at least one result set.
        required: true
        type: str
    output:
        description:
          - With C(default) each row will be returned as a list of values. See C(query_results).
          - Output format C(dict) will return dictionary with the column names as keys. See C(query_results_dict).
          - C(dict) requires named columns to be returned by each query otherwise an error is thrown.
        choices: [ "dict", "default" ]
        default: 'default'
        type: str
    params:
        description: |
            Parameters passed to the script as SQL parameters. ('SELECT %(name)s"' with C(example: '{"name": "John Doe"}).)'
        type: dict
notes:
   - Requires the pymssql Python package on the remote host. For Ubuntu, this
     is as easy as C(pip install pymssql) (See M(ansible.builtin.pip).)
requirements:
   - python >= 2.7
   - pymssql

author:
    - Kris Budde (@kbudde)
'''

EXAMPLES = r'''
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
      - result_batches.query_results | length == 2  # two batch results
      - result_batches.query_results[0] | length == 2  # two selects in first batch
      - result_batches.query_results[0][0] | length == 1  # one row in first select
      - result_batches.query_results[0][0][0] | length == 1  # one column in first row
      - result_batches.query_results[0][0][0][0] == 'Batch 0 - Select 0'  # each row contains a list of values.

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
      - result_batches_dict.query_results_dict | length == 2  # two batch results
      - result_batches_dict.query_results_dict[0] | length == 2  # two selects in first batch
      - result_batches_dict.query_results_dict[0][0] | length == 1  # one row in first select
      - result_batches_dict.query_results_dict[0][0][0]['b0s0'] == 'Batch 0 - Select 0'  # column 'b0s0' of first row
'''

RETURN = r'''
query_results:
    description: List of batches (queries separated by C(GO) keyword).
    type: list
    elements: list
    returned: success and I(output=default)
    sample: [[[["Batch 0 - Select 0"]], [["Batch 0 - Select 1"]]], [[["Batch 1 - Select 0"]]]]
    contains:
        queries:
            description:
              - List of result sets of each query.
              - If a query returns no results, the results of this and all the following queries will not be included in the output.
              - Use the C(GO) keyword in I(script) to separate queries.
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
    description: List of batches (queries separated by C(GO) keyword).
    type: list
    elements: list
    returned: success and I(output=dict)
    sample: [[[["Batch 0 - Select 0"]], [["Batch 0 - Select 1"]]], [[["Batch 1 - Select 0"]]]]
    contains:
        queries:
            description:
              - List of result sets of each query.
              - If a query returns no results, the results of this and all the following queries will not be included in the output.
                Use 'GO' keyword to separate queries.
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
'''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import traceback
import json
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


def run_module():
    module_args = dict(
        name=dict(required=False, aliases=['db'], default=''),
        login_user=dict(),
        login_password=dict(no_log=True),
        login_host=dict(required=True),
        login_port=dict(type='int', default=1433),
        script=dict(required=True),
        output=dict(default='default', choices=['dict', 'default']),
        params=dict(type='dict'),
    )

    result = dict(
        changed=False,
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
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
    output = module.params['output']
    sql_params = module.params['params']

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

    conn.autocommit(True)

    query_results_key = 'query_results'
    if output == 'dict':
        cursor = conn.cursor(as_dict=True)
        query_results_key = 'query_results_dict'

    queries = script.split('\nGO\n')
    result['changed'] = True
    if module.check_mode:
        module.exit_json(**result)

    query_results = []
    try:
        for query in queries:
            cursor.execute(query, sql_params)
            qry_result = []
            rows = cursor.fetchall()
            while rows:
                qry_result.append(rows)
                rows = cursor.fetchall()
            query_results.append(qry_result)
    except Exception as e:
        return module.fail_json(msg="query failed", query=query, error=str(e), **result)

    # ensure that the result is json serializable
    qry_results = json.loads(json.dumps(query_results, default=clean_output))

    result[query_results_key] = qry_results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

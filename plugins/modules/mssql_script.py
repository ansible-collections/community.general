#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2014, Vedit Firat Arig <firatarig@gmail.com>
# Outline and parts are reused from Mark Theunissen's mysql_db module
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
import traceback
import os
__metaclass__ = type


DOCUMENTATION = '''
---
module: mssql_script
short_description: Run simple, file based, or templated mssql scripts
description:
   - Run simple, file based, or templated mssql scripts
options:
  db:
    description:
      - name of the database to select
    required: true
    type: str
  login_user:
    description:
      - The username used to authenticate with
    type: str
  login_password:
    description:
      - The password used to authenticate with
    type: str
  login_host:
    description:
      - Host running the database
    type: str
    required: true
  login_port:
    description:
      - Port of the MSSQL server. Requires login_host be defined as other than localhost if login_port is used
    default: '1433'
    type: str
  script:
    description:
      - The script you'd like to run.
    type: str
  return_rows:
    description:
      - When true, returns an array of rows in the return values. (Always false.)
    default: false
    type: Boolean
notes:
   - Requires the pymssql Python package on the remote host. For Ubuntu, this
     is as easy as pip install pymssql (See M(ansible.builtin.pip).)
requirements:
   - python >= 2.7
   - pymssql
author: Steven Tobias (github.com/stobias123)
'''

EXAMPLES = '''
- name: run a simple script to check 
  mssql_script:
    db: mydb
    login_user: user
    login_password: pass
    login_host: foo.bar
    script: "drop table foo"

- name: Seed the db.
  community.general.mssql_script:
    db: mydb
    script: "{{lookup('file', 'seed.sql')}}"

- name: Run Migrations
  community.general.mssql_script:
    db: mydb
    script: "{{lookup('file', item)}}"
  with_fileglob:
    - "/path_to_scripts/*.sql'

'''

RETURN = '''
#
'''


PYMSSQL_IMP_ERR = None
try:
    import pymssql
except ImportError:
    PYMSSQL_IMP_ERR = traceback.format_exc()
    mssql_found = False
else:
    mssql_found = True


def db_exists(conn, cursor, db):
    cursor.execute("SELECT name FROM master.sys.databases WHERE name = %s", db)
    conn.commit()
    return bool(cursor.rowcount)

def db_execute(conn, cursor,script):
    try:
      cursor.execute(script)
      conn.commit()
    except Exception as e:
      return 1, f"Exception running. \n {e}"
    return 0, "Execution Sucessful"


def main():
    module = AnsibleModule(
        argument_spec=dict(
            db=dict(default=None, required=True),
            login_user=dict(default=''),
            login_password=dict(default='', no_log=True),
            login_host=dict(required=True),
            login_port=dict(default='1433'),
            script=dict(default=None,required=True),
            return_rows=dict(default=False)
        )
    )

    if not mssql_found:
        module.fail_json(msg=missing_required_lib(
            'pymssql'), exception=PYMSSQL_IMP_ERR)

    db = module.params['db']
    script = module.params['script']
    #return_rows = module.params['return_rows']
    return_rows = False
    
    
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    login_host = module.params['login_host']
    login_port = module.params['login_port']

    login_querystring = login_host
    if login_port != "1433":
        login_querystring = "%s:%s" % (login_host, login_port)

    if login_user != "" and login_password == "":
        module.fail_json(
            msg="when supplying login_user arguments login_password must be provided")

    if return_rows:
      module.fail_json(
            msg="return rows must be set to false. Returning results from large queries could cause unintended problems.")

    try:
        conn = pymssql.connect(
            user=login_user, password=login_password, host=login_querystring, database=db)
        cursor = conn.cursor()
    except Exception as e:
        if "Unknown database" in str(e):
            errno, errstr = e.args
            module.fail_json(msg="ERROR: %s %s" % (errno, errstr))
        else:
            module.fail_json(msg="unable to connect, check login_user and login_password are correct")

    conn.autocommit(True)

    msg = "Nothing happened"

    try:
        rc, msg = db_execute(conn, cursor, script)
    except Exception as e:
        module.fail_json(msg="error running script database: " + str(e))

    if rc != 0:
        module.fail_json(msg="%s" % msg)
    else:
        module.exit_json(changed=True, msg=msg)

    module.exit_json(changed=True, msg=msg)


if __name__ == '__main__':
    main()

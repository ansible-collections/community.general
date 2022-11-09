#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, Vedit Firat Arig <firatarig@gmail.com>
# Outline and parts are reused from Mark Theunissen's mysql_db module
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: mssql_db
short_description: Add or remove MSSQL databases from a remote host
description:
   - Add or remove MSSQL databases from a remote host.
options:
  name:
    description:
      - name of the database to add or remove
    required: true
    aliases: [ db ]
    type: str
  login_user:
    description:
      - The username used to authenticate with
    type: str
    default: ''
  login_password:
    description:
      - The password used to authenticate with
    type: str
    default: ''
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
  state:
    description:
      - The database state
    default: present
    choices: [ "present", "absent", "import" ]
    type: str
  target:
    description:
      - Location, on the remote host, of the dump file to read from or write to. Uncompressed SQL
        files (C(.sql)) files are supported.
    type: str
  autocommit:
    description:
      - Automatically commit the change only if the import succeed. Sometimes it is necessary to use autocommit=true, since some content can't be changed
        within a transaction.
    type: bool
    default: false
notes:
   - Requires the pymssql Python package on the remote host. For Ubuntu, this
     is as easy as pip install pymssql (See M(ansible.builtin.pip).)
requirements:
   - python >= 2.7
   - pymssql
author: Vedit Firat Arig (@vedit)
'''

EXAMPLES = '''
- name: Create a new database with name 'jackdata'
  community.general.mssql_db:
    name: jackdata
    state: present

# Copy database dump file to remote host and restore it to database 'my_db'
- name: Copy database dump file to remote host
  ansible.builtin.copy:
    src: dump.sql
    dest: /tmp

- name: Restore the dump file to database 'my_db'
  community.general.mssql_db:
    name: my_db
    state: import
    target: /tmp/dump.sql
'''

RETURN = '''
#
'''

import os
import traceback

PYMSSQL_IMP_ERR = None
try:
    import pymssql
except ImportError:
    PYMSSQL_IMP_ERR = traceback.format_exc()
    mssql_found = False
else:
    mssql_found = True

from ansible.module_utils.basic import AnsibleModule, missing_required_lib


def db_exists(conn, cursor, db):
    cursor.execute("SELECT name FROM master.sys.databases WHERE name = %s", db)
    conn.commit()
    return bool(cursor.rowcount)


def db_create(conn, cursor, db):
    cursor.execute("CREATE DATABASE [%s]" % db)
    return db_exists(conn, cursor, db)


def db_delete(conn, cursor, db):
    try:
        cursor.execute("ALTER DATABASE [%s] SET single_user WITH ROLLBACK IMMEDIATE" % db)
    except Exception:
        pass
    cursor.execute("DROP DATABASE [%s]" % db)
    return not db_exists(conn, cursor, db)


def db_import(conn, cursor, module, db, target):
    if os.path.isfile(target):
        with open(target, 'r') as backup:
            sqlQuery = "USE [%s]\n" % db
            for line in backup:
                if line is None:
                    break
                elif line.startswith('GO'):
                    cursor.execute(sqlQuery)
                    sqlQuery = "USE [%s]\n" % db
                else:
                    sqlQuery += line
            cursor.execute(sqlQuery)
            conn.commit()
        return 0, "import successful", ""
    else:
        return 1, "cannot find target file", "cannot find target file"


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True, aliases=['db']),
            login_user=dict(default=''),
            login_password=dict(default='', no_log=True),
            login_host=dict(required=True),
            login_port=dict(default='1433'),
            target=dict(default=None),
            autocommit=dict(type='bool', default=False),
            state=dict(
                default='present', choices=['present', 'absent', 'import'])
        )
    )

    if not mssql_found:
        module.fail_json(msg=missing_required_lib('pymssql'), exception=PYMSSQL_IMP_ERR)

    db = module.params['name']
    state = module.params['state']
    autocommit = module.params['autocommit']
    target = module.params["target"]

    login_user = module.params['login_user']
    login_password = module.params['login_password']
    login_host = module.params['login_host']
    login_port = module.params['login_port']

    login_querystring = login_host
    if login_port != "1433":
        login_querystring = "%s:%s" % (login_host, login_port)

    if login_user != "" and login_password == "":
        module.fail_json(msg="when supplying login_user arguments login_password must be provided")

    try:
        conn = pymssql.connect(user=login_user, password=login_password, host=login_querystring, database='master')
        cursor = conn.cursor()
    except Exception as e:
        if "Unknown database" in str(e):
            errno, errstr = e.args
            module.fail_json(msg="ERROR: %s %s" % (errno, errstr))
        else:
            module.fail_json(msg="unable to connect, check login_user and login_password are correct, or alternatively check your "
                                 "@sysconfdir@/freetds.conf / ${HOME}/.freetds.conf")

    conn.autocommit(True)
    changed = False

    if db_exists(conn, cursor, db):
        if state == "absent":
            try:
                changed = db_delete(conn, cursor, db)
            except Exception as e:
                module.fail_json(msg="error deleting database: " + str(e))
        elif state == "import":
            conn.autocommit(autocommit)
            rc, stdout, stderr = db_import(conn, cursor, module, db, target)

            if rc != 0:
                module.fail_json(msg="%s" % stderr)
            else:
                module.exit_json(changed=True, db=db, msg=stdout)
    else:
        if state == "present":
            try:
                changed = db_create(conn, cursor, db)
            except Exception as e:
                module.fail_json(msg="error creating database: " + str(e))
        elif state == "import":
            try:
                changed = db_create(conn, cursor, db)
            except Exception as e:
                module.fail_json(msg="error creating database: " + str(e))

            conn.autocommit(autocommit)
            rc, stdout, stderr = db_import(conn, cursor, module, db, target)

            if rc != 0:
                module.fail_json(msg="%s" % stderr)
            else:
                module.exit_json(changed=True, db=db, msg=stdout)

    module.exit_json(changed=changed, db=db)


if __name__ == '__main__':
    main()

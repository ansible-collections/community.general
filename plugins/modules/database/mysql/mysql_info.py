#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Andrew Klychkov (@Andersson007) <aaklychkov@mail.ru>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: mysql_info
short_description: Gather information about MySQL servers
description:
- Gathers information about MySQL servers.

options:
  filter:
    description:
    - Limit the collected information by comma separated string or YAML list.
    - Allowable values are C(version), C(databases), C(settings), C(global_status),
      C(users), C(engines), C(master_status), C(slave_status), C(slave_hosts).
    - By default, collects all subsets.
    - You can use '!' before value (for example, C(!settings)) to exclude it from the information.
    - If you pass including and excluding values to the filter, for example, I(filter=!settings,version),
      the excluding values, C(!settings) in this case, will be ignored.
    type: list
    elements: str
  login_db:
    description:
    - Database name to connect to.
    - It makes sense if I(login_user) is allowed to connect to a specific database only.
    type: str
  exclude_fields:
    description:
    - List of fields which are not needed to collect.
    - "Supports elements: C(db_size). Unsupported elements will be ignored"
    type: list
    elements: str
    version_added: '0.2.0'
  return_empty_dbs:
    description:
    - Includes names of empty databases to returned dictionary.
    type: bool
    default: no

notes:
- Calculating the size of a database might be slow, depending on the number and size of tables in it.
  To avoid this, use I(exclude_fields=db_size).

seealso:
- module: community.general.mysql_variables
- module: community.general.mysql_db
- module: community.general.mysql_user
- module: community.general.mysql_replication

author:
- Andrew Klychkov (@Andersson007)

extends_documentation_fragment:
- community.general.mysql

'''

EXAMPLES = r'''
# Display info from mysql-hosts group (using creds from ~/.my.cnf to connect):
# ansible mysql-hosts -m mysql_info

# Display only databases and users info:
# ansible mysql-hosts -m mysql_info -a 'filter=databases,users'

# Display only slave status:
# ansible standby -m mysql_info -a 'filter=slave_status'

# Display all info from databases group except settings:
# ansible databases -m mysql_info -a 'filter=!settings'

- name: Collect all possible information using passwordless root access
  mysql_info:
    login_user: root

- name: Get MySQL version with non-default credentials
  mysql_info:
    login_user: mysuperuser
    login_password: mysuperpass
    filter: version

- name: Collect all info except settings and users by root
  mysql_info:
    login_user: root
    login_password: rootpass
    filter: "!settings,!users"

- name: Collect info about databases and version using ~/.my.cnf as a credential file
  become: yes
  mysql_info:
    filter:
    - databases
    - version

- name: Collect info about databases and version using ~alice/.my.cnf as a credential file
  become: yes
  mysql_info:
    config_file: /home/alice/.my.cnf
    filter:
    - databases
    - version

- name: Collect info about databases including empty and excluding their sizes
  become: yes
  mysql_info:
    config_file: /home/alice/.my.cnf
    filter:
    - databases
    exclude_fields: db_size
    return_empty_dbs: yes
'''

RETURN = r'''
version:
  description: Database server version.
  returned: if not excluded by filter
  type: dict
  sample: { "version": { "major": 5, "minor": 5, "release": 60 } }
  contains:
    major:
      description: Major server version.
      returned: if not excluded by filter
      type: int
      sample: 5
    minor:
      description: Minor server version.
      returned: if not excluded by filter
      type: int
      sample: 5
    release:
      description: Release server version.
      returned: if not excluded by filter
      type: int
      sample: 60
databases:
  description: Information about databases.
  returned: if not excluded by filter
  type: dict
  sample:
  - { "mysql": { "size": 656594 }, "information_schema": { "size": 73728 } }
  contains:
    size:
      description: Database size in bytes.
      returned: if not excluded by filter
      type: dict
      sample: { 'size': 656594 }
settings:
  description: Global settings (variables) information.
  returned: if not excluded by filter
  type: dict
  sample:
  - { "innodb_open_files": 300, innodb_page_size": 16384 }
global_status:
  description: Global status information.
  returned: if not excluded by filter
  type: dict
  sample:
  - { "Innodb_buffer_pool_read_requests": 123, "Innodb_buffer_pool_reads": 32 }
users:
  description: Users information.
  returned: if not excluded by filter
  type: dict
  sample:
  - { "localhost": { "root": { "Alter_priv": "Y", "Alter_routine_priv": "Y" } } }
engines:
  description: Information about the server's storage engines.
  returned: if not excluded by filter
  type: dict
  sample:
  - { "CSV": { "Comment": "CSV storage engine", "Savepoints": "NO", "Support": "YES", "Transactions": "NO", "XA": "NO" } }
master_status:
  description: Master status information.
  returned: if master
  type: dict
  sample:
  - { "Binlog_Do_DB": "", "Binlog_Ignore_DB": "mysql", "File": "mysql-bin.000001", "Position": 769 }
slave_status:
  description: Slave status information.
  returned: if standby
  type: dict
  sample:
  - { "192.168.1.101": { "3306": { "replication_user": { "Connect_Retry": 60, "Exec_Master_Log_Pos": 769,  "Last_Errno": 0 } } } }
slave_hosts:
  description: Slave status information.
  returned: if master
  type: dict
  sample:
  - { "2": { "Host": "", "Master_id": 1, "Port": 3306 } }
'''

from decimal import Decimal

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.mysql import (
    mysql_connect,
    mysql_common_argument_spec,
    mysql_driver,
    mysql_driver_fail_msg,
)
from ansible.module_utils.six import iteritems
from ansible.module_utils._text import to_native


# ===========================================
# MySQL module specific support methods.
#

class MySQL_Info(object):

    """Class for collection MySQL instance information.

    Arguments:
        module (AnsibleModule): Object of AnsibleModule class.
        cursor (pymysql/mysql-python): Cursor class for interaction with
            the database.

    Note:
        If you need to add a new subset:
        1. add a new key with the same name to self.info attr in self.__init__()
        2. add a new private method to get the information
        3. add invocation of the new method to self.__collect()
        4. add info about the new subset to the DOCUMENTATION block
        5. add info about the new subset with an example to RETURN block
    """

    def __init__(self, module, cursor):
        self.module = module
        self.cursor = cursor
        self.info = {
            'version': {},
            'databases': {},
            'settings': {},
            'global_status': {},
            'engines': {},
            'users': {},
            'master_status': {},
            'slave_hosts': {},
            'slave_status': {},
        }

    def get_info(self, filter_, exclude_fields, return_empty_dbs):
        """Get MySQL instance information based on filter_.

        Arguments:
            filter_ (list): List of collected subsets (e.g., databases, users, etc.),
                when it is empty, return all available information.
        """

        inc_list = []
        exc_list = []

        if filter_:
            partial_info = {}

            for fi in filter_:
                if fi.lstrip('!') not in self.info:
                    self.module.warn('filter element: %s is not allowable, ignored' % fi)
                    continue

                if fi[0] == '!':
                    exc_list.append(fi.lstrip('!'))

                else:
                    inc_list.append(fi)

            if inc_list:
                self.__collect(exclude_fields, return_empty_dbs, set(inc_list))

                for i in self.info:
                    if i in inc_list:
                        partial_info[i] = self.info[i]

            else:
                not_in_exc_list = list(set(self.info) - set(exc_list))
                self.__collect(exclude_fields, return_empty_dbs, set(not_in_exc_list))

                for i in self.info:
                    if i not in exc_list:
                        partial_info[i] = self.info[i]

            return partial_info

        else:
            self.__collect(exclude_fields, return_empty_dbs, set(self.info))
            return self.info

    def __collect(self, exclude_fields, return_empty_dbs, wanted):
        """Collect all possible subsets."""
        if 'version' in wanted or 'settings' in wanted:
            self.__get_global_variables()

        if 'databases' in wanted:
            self.__get_databases(exclude_fields, return_empty_dbs)

        if 'global_status' in wanted:
            self.__get_global_status()

        if 'engines' in wanted:
            self.__get_engines()

        if 'users' in wanted:
            self.__get_users()

        if 'master_status' in wanted:
            self.__get_master_status()

        if 'slave_status' in wanted:
            self.__get_slave_status()

        if 'slave_hosts' in wanted:
            self.__get_slaves()

    def __get_engines(self):
        """Get storage engines info."""
        res = self.__exec_sql('SHOW ENGINES')

        if res:
            for line in res:
                engine = line['Engine']
                self.info['engines'][engine] = {}

                for vname, val in iteritems(line):
                    if vname != 'Engine':
                        self.info['engines'][engine][vname] = val

    def __convert(self, val):
        """Convert unserializable data."""
        try:
            if isinstance(val, Decimal):
                val = float(val)
            else:
                val = int(val)

        except ValueError:
            pass

        except TypeError:
            pass

        return val

    def __get_global_variables(self):
        """Get global variables (instance settings)."""
        res = self.__exec_sql('SHOW GLOBAL VARIABLES')

        if res:
            for var in res:
                self.info['settings'][var['Variable_name']] = self.__convert(var['Value'])

            ver = self.info['settings']['version'].split('.')
            release = ver[2].split('-')[0]

            self.info['version'] = dict(
                major=int(ver[0]),
                minor=int(ver[1]),
                release=int(release),
            )

    def __get_global_status(self):
        """Get global status."""
        res = self.__exec_sql('SHOW GLOBAL STATUS')

        if res:
            for var in res:
                self.info['global_status'][var['Variable_name']] = self.__convert(var['Value'])

    def __get_master_status(self):
        """Get master status if the instance is a master."""
        res = self.__exec_sql('SHOW MASTER STATUS')
        if res:
            for line in res:
                for vname, val in iteritems(line):
                    self.info['master_status'][vname] = self.__convert(val)

    def __get_slave_status(self):
        """Get slave status if the instance is a slave."""
        res = self.__exec_sql('SHOW SLAVE STATUS')
        if res:
            for line in res:
                host = line['Master_Host']
                if host not in self.info['slave_status']:
                    self.info['slave_status'][host] = {}

                port = line['Master_Port']
                if port not in self.info['slave_status'][host]:
                    self.info['slave_status'][host][port] = {}

                user = line['Master_User']
                if user not in self.info['slave_status'][host][port]:
                    self.info['slave_status'][host][port][user] = {}

                for vname, val in iteritems(line):
                    if vname not in ('Master_Host', 'Master_Port', 'Master_User'):
                        self.info['slave_status'][host][port][user][vname] = self.__convert(val)

    def __get_slaves(self):
        """Get slave hosts info if the instance is a master."""
        res = self.__exec_sql('SHOW SLAVE HOSTS')
        if res:
            for line in res:
                srv_id = line['Server_id']
                if srv_id not in self.info['slave_hosts']:
                    self.info['slave_hosts'][srv_id] = {}

                for vname, val in iteritems(line):
                    if vname != 'Server_id':
                        self.info['slave_hosts'][srv_id][vname] = self.__convert(val)

    def __get_users(self):
        """Get user info."""
        res = self.__exec_sql('SELECT * FROM mysql.user')
        if res:
            for line in res:
                host = line['Host']
                if host not in self.info['users']:
                    self.info['users'][host] = {}

                user = line['User']
                self.info['users'][host][user] = {}

                for vname, val in iteritems(line):
                    if vname not in ('Host', 'User'):
                        self.info['users'][host][user][vname] = self.__convert(val)

    def __get_databases(self, exclude_fields, return_empty_dbs):
        """Get info about databases."""
        if not exclude_fields:
            query = ('SELECT table_schema AS "name", '
                     'SUM(data_length + index_length) AS "size" '
                     'FROM information_schema.TABLES GROUP BY table_schema')
        else:
            if 'db_size' in exclude_fields:
                query = ('SELECT table_schema AS "name" '
                         'FROM information_schema.TABLES GROUP BY table_schema')

        res = self.__exec_sql(query)

        if res:
            for db in res:
                self.info['databases'][db['name']] = {}

                if not exclude_fields or 'db_size' not in exclude_fields:
                    self.info['databases'][db['name']]['size'] = int(db['size'])

        # If empty dbs are not needed in the returned dict, exit from the method
        if not return_empty_dbs:
            return None

        # Add info about empty databases (issue #65727):
        res = self.__exec_sql('SHOW DATABASES')
        if res:
            for db in res:
                if db['Database'] not in self.info['databases']:
                    self.info['databases'][db['Database']] = {}

                    if not exclude_fields or 'db_size' not in exclude_fields:
                        self.info['databases'][db['Database']]['size'] = 0

    def __exec_sql(self, query, ddl=False):
        """Execute SQL.

        Arguments:
            ddl (bool): If True, return True or False.
                Used for queries that don't return any rows
                (mainly for DDL queries) (default False).
        """
        try:
            self.cursor.execute(query)

            if not ddl:
                res = self.cursor.fetchall()
                return res
            return True

        except Exception as e:
            self.module.fail_json(msg="Cannot execute SQL '%s': %s" % (query, to_native(e)))
        return False


# ===========================================
# Module execution.
#


def main():
    argument_spec = mysql_common_argument_spec()
    argument_spec.update(
        login_db=dict(type='str'),
        filter=dict(type='list'),
        exclude_fields=dict(type='list'),
        return_empty_dbs=dict(type='bool', default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    db = module.params['login_db']
    connect_timeout = module.params['connect_timeout']
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    ssl_cert = module.params['client_cert']
    ssl_key = module.params['client_key']
    ssl_ca = module.params['ca_cert']
    config_file = module.params['config_file']
    filter_ = module.params['filter']
    exclude_fields = module.params['exclude_fields']
    return_empty_dbs = module.params['return_empty_dbs']

    if filter_:
        filter_ = [f.strip() for f in filter_]

    if exclude_fields:
        exclude_fields = set([f.strip() for f in exclude_fields])

    if mysql_driver is None:
        module.fail_json(msg=mysql_driver_fail_msg)

    try:
        cursor, db_conn = mysql_connect(module, login_user, login_password,
                                        config_file, ssl_cert, ssl_key, ssl_ca, db,
                                        connect_timeout=connect_timeout, cursor_class='DictCursor')
    except Exception as e:
        module.fail_json(msg="unable to connect to database, check login_user and login_password are correct or %s has the credentials. "
                             "Exception message: %s" % (config_file, to_native(e)))

    ###############################
    # Create object and do main job

    mysql = MySQL_Info(module, cursor)

    module.exit_json(changed=False, **mysql.get_info(filter_, exclude_fields, return_empty_dbs))


if __name__ == '__main__':
    main()

# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Ted Timmons <ted@timmons.me>, 2017.
# Most of this was originally added by other creators in the postgresql_user module.
#
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

psycopg2 = None  # This line needs for unit tests
try:
    import psycopg2
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils._text import to_native
from ansible.module_utils.six import iteritems
from distutils.version import LooseVersion


def postgres_common_argument_spec():
    """
    Return a dictionary with connection options.

    The options are commonly used by most of PostgreSQL modules.
    """
    return dict(
        login_user=dict(default='postgres'),
        login_password=dict(default='', no_log=True),
        login_host=dict(default=''),
        login_unix_socket=dict(default=''),
        port=dict(type='int', default=5432, aliases=['login_port']),
        ssl_mode=dict(default='prefer', choices=['allow', 'disable', 'prefer', 'require', 'verify-ca', 'verify-full']),
        ca_cert=dict(aliases=['ssl_rootcert']),
    )


def ensure_required_libs(module):
    """Check required libraries."""
    if not HAS_PSYCOPG2:
        module.fail_json(msg=missing_required_lib('psycopg2'))

    if module.params.get('ca_cert') and LooseVersion(psycopg2.__version__) < LooseVersion('2.4.3'):
        module.fail_json(msg='psycopg2 must be at least 2.4.3 in order to use the ca_cert parameter')


def connect_to_db(module, conn_params, autocommit=False, fail_on_conn=True):
    """Connect to a PostgreSQL database.

    Return psycopg2 connection object.

    Args:
        module (AnsibleModule) -- object of ansible.module_utils.basic.AnsibleModule class
        conn_params (dict) -- dictionary with connection parameters

    Kwargs:
        autocommit (bool) -- commit automatically (default False)
        fail_on_conn (bool) -- fail if connection failed or just warn and return None (default True)
    """
    ensure_required_libs(module)

    db_connection = None
    try:
        db_connection = psycopg2.connect(**conn_params)
        if autocommit:
            if LooseVersion(psycopg2.__version__) >= LooseVersion('2.4.2'):
                db_connection.set_session(autocommit=True)
            else:
                db_connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        # Switch role, if specified:
        if module.params.get('session_role'):
            cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

            try:
                cursor.execute('SET ROLE "%s"' % module.params['session_role'])
            except Exception as e:
                module.fail_json(msg="Could not switch role: %s" % to_native(e))
            finally:
                cursor.close()

    except TypeError as e:
        if 'sslrootcert' in e.args[0]:
            module.fail_json(msg='Postgresql server must be at least '
                                 'version 8.4 to support sslrootcert')

        if fail_on_conn:
            module.fail_json(msg="unable to connect to database: %s" % to_native(e))
        else:
            module.warn("PostgreSQL server is unavailable: %s" % to_native(e))
            db_connection = None

    except Exception as e:
        if fail_on_conn:
            module.fail_json(msg="unable to connect to database: %s" % to_native(e))
        else:
            module.warn("PostgreSQL server is unavailable: %s" % to_native(e))
            db_connection = None

    return db_connection


def exec_sql(obj, query, query_params=None, return_bool=False, add_to_executed=True, dont_exec=False):
    """Execute SQL.

    Auxiliary function for PostgreSQL user classes.

    Returns a query result if possible or a boolean value.

    Args:
        obj (obj) -- must be an object of a user class.
            The object must have module (AnsibleModule class object) and
            cursor (psycopg cursor object) attributes
        query (str) -- SQL query to execute

    Kwargs:
        query_params (dict or tuple) -- Query parameters to prevent SQL injections,
            could be a dict or tuple
        return_bool (bool) -- return True instead of rows if a query was successfully executed.
            It's necessary for statements that don't return any result like DDL queries (default False).
        add_to_executed (bool) -- append the query to obj.executed_queries attribute
        dont_exec (bool) -- used with add_to_executed=True to generate a query, add it
            to obj.executed_queries list and return True (default False)
    """

    if dont_exec:
        # This is usually needed to return queries in check_mode
        # without execution
        query = obj.cursor.mogrify(query, query_params)
        if add_to_executed:
            obj.executed_queries.append(query)

        return True

    try:
        if query_params is not None:
            obj.cursor.execute(query, query_params)
        else:
            obj.cursor.execute(query)

        if add_to_executed:
            if query_params is not None:
                obj.executed_queries.append(obj.cursor.mogrify(query, query_params))
            else:
                obj.executed_queries.append(query)

        if not return_bool:
            res = obj.cursor.fetchall()
            return res
        return True
    except Exception as e:
        obj.module.fail_json(msg="Cannot execute SQL '%s': %s" % (query, to_native(e)))
    return False


def get_conn_params(module, params_dict, warn_db_default=True):
    """Get connection parameters from the passed dictionary.

    Return a dictionary with parameters to connect to PostgreSQL server.

    Args:
        module (AnsibleModule) -- object of ansible.module_utils.basic.AnsibleModule class
        params_dict (dict) -- dictionary with variables

    Kwargs:
        warn_db_default (bool) -- warn that the default DB is used (default True)
    """
    # To use defaults values, keyword arguments must be absent, so
    # check which values are empty and don't include in the return dictionary
    params_map = {
        "login_host": "host",
        "login_user": "user",
        "login_password": "password",
        "port": "port",
        "ssl_mode": "sslmode",
        "ca_cert": "sslrootcert"
    }

    # Might be different in the modules:
    if params_dict.get('db'):
        params_map['db'] = 'database'
    elif params_dict.get('database'):
        params_map['database'] = 'database'
    elif params_dict.get('login_db'):
        params_map['login_db'] = 'database'
    else:
        if warn_db_default:
            module.warn('Database name has not been passed, '
                        'used default database to connect to.')

    kw = dict((params_map[k], v) for (k, v) in iteritems(params_dict)
              if k in params_map and v != '' and v is not None)

    # If a login_unix_socket is specified, incorporate it here.
    is_localhost = "host" not in kw or kw["host"] is None or kw["host"] == "localhost"
    if is_localhost and params_dict["login_unix_socket"] != "":
        kw["host"] = params_dict["login_unix_socket"]

    return kw


class PgMembership(object):
    def __init__(self, module, cursor, groups, target_roles, fail_on_role=True):
        self.module = module
        self.cursor = cursor
        self.target_roles = [r.strip() for r in target_roles]
        self.groups = [r.strip() for r in groups]
        self.executed_queries = []
        self.granted = {}
        self.revoked = {}
        self.fail_on_role = fail_on_role
        self.non_existent_roles = []
        self.changed = False
        self.__check_roles_exist()

    def grant(self):
        for group in self.groups:
            self.granted[group] = []

            for role in self.target_roles:
                # If role is in a group now, pass:
                if self.__check_membership(group, role):
                    continue

                query = 'GRANT "%s" TO "%s"' % (group, role)
                self.changed = exec_sql(self, query, return_bool=True)

                if self.changed:
                    self.granted[group].append(role)

        return self.changed

    def revoke(self):
        for group in self.groups:
            self.revoked[group] = []

            for role in self.target_roles:
                # If role is not in a group now, pass:
                if not self.__check_membership(group, role):
                    continue

                query = 'REVOKE "%s" FROM "%s"' % (group, role)
                self.changed = exec_sql(self, query, return_bool=True)

                if self.changed:
                    self.revoked[group].append(role)

        return self.changed

    def __check_membership(self, src_role, dst_role):
        query = ("SELECT ARRAY(SELECT b.rolname FROM "
                 "pg_catalog.pg_auth_members m "
                 "JOIN pg_catalog.pg_roles b ON (m.roleid = b.oid) "
                 "WHERE m.member = r.oid) "
                 "FROM pg_catalog.pg_roles r "
                 "WHERE r.rolname = %(dst_role)s")

        res = exec_sql(self, query, query_params={'dst_role': dst_role}, add_to_executed=False)
        membership = []
        if res:
            membership = res[0][0]

        if not membership:
            return False

        if src_role in membership:
            return True

        return False

    def __check_roles_exist(self):
        existent_groups = self.__roles_exist(self.groups)
        existent_roles = self.__roles_exist(self.target_roles)

        for group in self.groups:
            if group not in existent_groups:
                if self.fail_on_role:
                    self.module.fail_json(msg="Role %s does not exist" % group)
                else:
                    self.module.warn("Role %s does not exist, pass" % group)
                    self.non_existent_roles.append(group)

        for role in self.target_roles:
            if role not in existent_roles:
                if self.fail_on_role:
                    self.module.fail_json(msg="Role %s does not exist" % role)
                else:
                    self.module.warn("Role %s does not exist, pass" % role)

                if role not in self.groups:
                    self.non_existent_roles.append(role)

                else:
                    if self.fail_on_role:
                        self.module.exit_json(msg="Role role '%s' is a member of role '%s'" % (role, role))
                    else:
                        self.module.warn("Role role '%s' is a member of role '%s', pass" % (role, role))

        # Update role lists, excluding non existent roles:
        self.groups = [g for g in self.groups if g not in self.non_existent_roles]

        self.target_roles = [r for r in self.target_roles if r not in self.non_existent_roles]

    def __roles_exist(self, roles):
        tmp = ["'" + x + "'" for x in roles]
        query = "SELECT rolname FROM pg_roles WHERE rolname IN (%s)" % ','.join(tmp)
        return [x[0] for x in exec_sql(self, query, add_to_executed=False)]

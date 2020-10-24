#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Flavien Chantelot (@Dorn-)
# Copyright: (c) 2018, Antoine Levy-Lambert (@antoinell)
# Copyright: (c) 2019, Andrew Klychkov (@Andersson007) <aaklychkov@mail.ru>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: postgresql_tablespace
short_description: Add or remove PostgreSQL tablespaces from remote hosts
description:
- Adds or removes PostgreSQL tablespaces from remote hosts.
options:
  tablespace:
    description:
    - Name of the tablespace to add or remove.
    required: true
    type: str
    aliases:
    - name
  location:
    description:
    - Path to the tablespace directory in the file system.
    - Ensure that the location exists and has right privileges.
    type: path
    aliases:
    - path
  state:
    description:
    - Tablespace state.
    - I(state=present) implies the tablespace must be created if it doesn't exist.
    - I(state=absent) implies the tablespace must be removed if present.
      I(state=absent) is mutually exclusive with I(location), I(owner), i(set).
    - See the Notes section for information about check mode restrictions.
    type: str
    default: present
    choices: [ absent, present ]
  owner:
    description:
    - Name of the role to set as an owner of the tablespace.
    - If this option is not specified, the tablespace owner is a role that creates the tablespace.
    type: str
  set:
    description:
    - Dict of tablespace options to set. Supported from PostgreSQL 9.0.
    - For more information see U(https://www.postgresql.org/docs/current/sql-createtablespace.html).
    - When reset is passed as an option's value, if the option was set previously, it will be removed.
    type: dict
  rename_to:
    description:
    - New name of the tablespace.
    - The new name cannot begin with pg_, as such names are reserved for system tablespaces.
    type: str
  session_role:
    description:
    - Switch to session_role after connecting. The specified session_role must
      be a role that the current login_user is a member of.
    - Permissions checking for SQL commands is carried out as though
      the session_role were the one that had logged in originally.
    type: str
  db:
    description:
    - Name of database to connect to and run queries against.
    type: str
    aliases:
    - login_db
  trust_input:
    description:
    - If C(no), check whether values of parameters I(tablespace), I(location), I(owner),
      I(rename_to), I(session_role), I(settings_list) are potentially dangerous.
    - It makes sense to use C(no) only when SQL injections via the parameters are possible.
    type: bool
    default: yes
    version_added: '0.2.0'

notes:
- I(state=absent) and I(state=present) (the second one if the tablespace doesn't exist) do not
  support check mode because the corresponding PostgreSQL DROP and CREATE TABLESPACE commands
  can not be run inside the transaction block.

seealso:
- name: PostgreSQL tablespaces
  description: General information about PostgreSQL tablespaces.
  link: https://www.postgresql.org/docs/current/manage-ag-tablespaces.html
- name: CREATE TABLESPACE reference
  description: Complete reference of the CREATE TABLESPACE command documentation.
  link: https://www.postgresql.org/docs/current/sql-createtablespace.html
- name: ALTER TABLESPACE reference
  description: Complete reference of the ALTER TABLESPACE command documentation.
  link: https://www.postgresql.org/docs/current/sql-altertablespace.html
- name: DROP TABLESPACE reference
  description: Complete reference of the DROP TABLESPACE command documentation.
  link: https://www.postgresql.org/docs/current/sql-droptablespace.html

author:
- Flavien Chantelot (@Dorn-)
- Antoine Levy-Lambert (@antoinell)
- Andrew Klychkov (@Andersson007)

extends_documentation_fragment:
- community.general.postgres

'''

EXAMPLES = r'''
- name: Create a new tablespace called acme and set bob as an its owner
  community.general.postgresql_tablespace:
    name: acme
    owner: bob
    location: /data/foo

- name: Create a new tablespace called bar with tablespace options
  community.general.postgresql_tablespace:
    name: bar
    set:
      random_page_cost: 1
      seq_page_cost: 1

- name: Reset random_page_cost option
  community.general.postgresql_tablespace:
    name: bar
    set:
      random_page_cost: reset

- name: Rename the tablespace from bar to pcie_ssd
  community.general.postgresql_tablespace:
    name: bar
    rename_to: pcie_ssd

- name: Drop tablespace called bloat
  community.general.postgresql_tablespace:
    name: bloat
    state: absent
'''

RETURN = r'''
queries:
    description: List of queries that was tried to be executed.
    returned: always
    type: str
    sample: [ "CREATE TABLESPACE bar LOCATION '/incredible/ssd'" ]
tablespace:
    description: Tablespace name.
    returned: always
    type: str
    sample: 'ssd'
owner:
    description: Tablespace owner.
    returned: always
    type: str
    sample: 'Bob'
options:
    description: Tablespace options.
    returned: always
    type: dict
    sample: { 'random_page_cost': 1, 'seq_page_cost': 1 }
location:
    description: Path to the tablespace in the file system.
    returned: always
    type: str
    sample: '/incredible/fast/ssd'
newname:
    description: New tablespace name
    returned: if existent
    type: str
    sample: new_ssd
state:
    description: Tablespace state at the end of execution.
    returned: always
    type: str
    sample: 'present'
'''

try:
    from psycopg2 import __version__ as PSYCOPG2_VERSION
    from psycopg2.extras import DictCursor
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT as AUTOCOMMIT
    from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED as READ_COMMITTED
except ImportError:
    # psycopg2 is checked by connect_to_db()
    # from ansible.module_utils.postgres
    pass

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems

from ansible_collections.community.general.plugins.module_utils.database import (
    check_input,
    pg_quote_identifier,
)
from ansible_collections.community.general.plugins.module_utils.postgres import (
    connect_to_db,
    exec_sql,
    get_conn_params,
    postgres_common_argument_spec,
)


class PgTablespace(object):

    """Class for working with PostgreSQL tablespaces.

    Args:
        module (AnsibleModule) -- object of AnsibleModule class
        cursor (cursor) -- cursor object of psycopg2 library
        name (str) -- name of the tablespace

    Attrs:
        module (AnsibleModule) -- object of AnsibleModule class
        cursor (cursor) -- cursor object of psycopg2 library
        name (str) -- name of the tablespace
        exists (bool) -- flag the tablespace exists in the DB or not
        owner (str) -- tablespace owner
        location (str) -- path to the tablespace directory in the file system
        executed_queries (list) -- list of executed queries
        new_name (str) -- new name for the tablespace
        opt_not_supported (bool) -- flag indicates a tablespace option is supported or not
    """

    def __init__(self, module, cursor, name):
        self.module = module
        self.cursor = cursor
        self.name = name
        self.exists = False
        self.owner = ''
        self.settings = {}
        self.location = ''
        self.executed_queries = []
        self.new_name = ''
        self.opt_not_supported = False
        # Collect info:
        self.get_info()

    def get_info(self):
        """Get tablespace information."""
        # Check that spcoptions exists:
        opt = exec_sql(self, "SELECT 1 FROM information_schema.columns "
                             "WHERE table_name = 'pg_tablespace' "
                             "AND column_name = 'spcoptions'", add_to_executed=False)

        # For 9.1 version and earlier:
        location = exec_sql(self, "SELECT 1 FROM information_schema.columns "
                                  "WHERE table_name = 'pg_tablespace' "
                                  "AND column_name = 'spclocation'", add_to_executed=False)
        if location:
            location = 'spclocation'
        else:
            location = 'pg_tablespace_location(t.oid)'

        if not opt:
            self.opt_not_supported = True
            query = ("SELECT r.rolname, (SELECT Null), %s "
                     "FROM pg_catalog.pg_tablespace AS t "
                     "JOIN pg_catalog.pg_roles AS r "
                     "ON t.spcowner = r.oid " % location)
        else:
            query = ("SELECT r.rolname, t.spcoptions, %s "
                     "FROM pg_catalog.pg_tablespace AS t "
                     "JOIN pg_catalog.pg_roles AS r "
                     "ON t.spcowner = r.oid " % location)

        res = exec_sql(self, query + "WHERE t.spcname = %(name)s",
                       query_params={'name': self.name}, add_to_executed=False)

        if not res:
            self.exists = False
            return False

        if res[0][0]:
            self.exists = True
            self.owner = res[0][0]

            if res[0][1]:
                # Options exist:
                for i in res[0][1]:
                    i = i.split('=')
                    self.settings[i[0]] = i[1]

            if res[0][2]:
                # Location exists:
                self.location = res[0][2]

    def create(self, location):
        """Create tablespace.

        Return True if success, otherwise, return False.

        args:
            location (str) -- tablespace directory path in the FS
        """
        query = ('CREATE TABLESPACE "%s" LOCATION \'%s\'' % (self.name, location))
        return exec_sql(self, query, return_bool=True)

    def drop(self):
        """Drop tablespace.

        Return True if success, otherwise, return False.
        """
        return exec_sql(self, 'DROP TABLESPACE "%s"' % self.name, return_bool=True)

    def set_owner(self, new_owner):
        """Set tablespace owner.

        Return True if success, otherwise, return False.

        args:
            new_owner (str) -- name of a new owner for the tablespace"
        """
        if new_owner == self.owner:
            return False

        query = 'ALTER TABLESPACE "%s" OWNER TO "%s"' % (self.name, new_owner)
        return exec_sql(self, query, return_bool=True)

    def rename(self, newname):
        """Rename tablespace.

        Return True if success, otherwise, return False.

        args:
            newname (str) -- new name for the tablespace"
        """
        query = 'ALTER TABLESPACE "%s" RENAME TO "%s"' % (self.name, newname)
        self.new_name = newname
        return exec_sql(self, query, return_bool=True)

    def set_settings(self, new_settings):
        """Set tablespace settings (options).

        If some setting has been changed, set changed = True.
        After all settings list is handling, return changed.

        args:
            new_settings (list) -- list of new settings
        """
        # settings must be a dict {'key': 'value'}
        if self.opt_not_supported:
            return False

        changed = False

        # Apply new settings:
        for i in new_settings:
            if new_settings[i] == 'reset':
                if i in self.settings:
                    changed = self.__reset_setting(i)
                    self.settings[i] = None

            elif (i not in self.settings) or (str(new_settings[i]) != self.settings[i]):
                changed = self.__set_setting("%s = '%s'" % (i, new_settings[i]))

        return changed

    def __reset_setting(self, setting):
        """Reset tablespace setting.

        Return True if success, otherwise, return False.

        args:
            setting (str) -- string in format "setting_name = 'setting_value'"
        """
        query = 'ALTER TABLESPACE "%s" RESET (%s)' % (self.name, setting)
        return exec_sql(self, query, return_bool=True)

    def __set_setting(self, setting):
        """Set tablespace setting.

        Return True if success, otherwise, return False.

        args:
            setting (str) -- string in format "setting_name = 'setting_value'"
        """
        query = 'ALTER TABLESPACE "%s" SET (%s)' % (self.name, setting)
        return exec_sql(self, query, return_bool=True)


# ===========================================
# Module execution.
#


def main():
    argument_spec = postgres_common_argument_spec()
    argument_spec.update(
        tablespace=dict(type='str', required=True, aliases=['name']),
        state=dict(type='str', default="present", choices=["absent", "present"]),
        location=dict(type='path', aliases=['path']),
        owner=dict(type='str'),
        set=dict(type='dict'),
        rename_to=dict(type='str'),
        db=dict(type='str', aliases=['login_db']),
        session_role=dict(type='str'),
        trust_input=dict(type='bool', default=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=(('positional_args', 'named_args'),),
        supports_check_mode=True,
    )

    tablespace = module.params["tablespace"]
    state = module.params["state"]
    location = module.params["location"]
    owner = module.params["owner"]
    rename_to = module.params["rename_to"]
    settings = module.params["set"]
    session_role = module.params["session_role"]
    trust_input = module.params["trust_input"]

    if state == 'absent' and (location or owner or rename_to or settings):
        module.fail_json(msg="state=absent is mutually exclusive location, "
                             "owner, rename_to, and set")

    if not trust_input:
        # Check input for potentially dangerous elements:
        if not settings:
            settings_list = None
        else:
            settings_list = ['%s = %s' % (k, v) for k, v in iteritems(settings)]

        check_input(module, tablespace, location, owner,
                    rename_to, session_role, settings_list)

    conn_params = get_conn_params(module, module.params, warn_db_default=False)
    db_connection = connect_to_db(module, conn_params, autocommit=True)
    cursor = db_connection.cursor(cursor_factory=DictCursor)

    # Change autocommit to False if check_mode:
    if module.check_mode:
        if PSYCOPG2_VERSION >= '2.4.2':
            db_connection.set_session(autocommit=False)
        else:
            db_connection.set_isolation_level(READ_COMMITTED)

    # Set defaults:
    autocommit = False
    changed = False

    ##############
    # Create PgTablespace object and do main job:
    tblspace = PgTablespace(module, cursor, tablespace)

    # If tablespace exists with different location, exit:
    if tblspace.exists and location and location != tblspace.location:
        module.fail_json(msg="Tablespace '%s' exists with "
                             "different location '%s'" % (tblspace.name, tblspace.location))

    # Create new tablespace:
    if not tblspace.exists and state == 'present':
        if rename_to:
            module.fail_json(msg="Tablespace %s does not exist, nothing to rename" % tablespace)

        if not location:
            module.fail_json(msg="'location' parameter must be passed with "
                                 "state=present if the tablespace doesn't exist")

        # Because CREATE TABLESPACE can not be run inside the transaction block:
        autocommit = True
        if PSYCOPG2_VERSION >= '2.4.2':
            db_connection.set_session(autocommit=True)
        else:
            db_connection.set_isolation_level(AUTOCOMMIT)

        changed = tblspace.create(location)

    # Drop non-existing tablespace:
    elif not tblspace.exists and state == 'absent':
        # Nothing to do:
        module.fail_json(msg="Tries to drop nonexistent tablespace '%s'" % tblspace.name)

    # Drop existing tablespace:
    elif tblspace.exists and state == 'absent':
        # Because DROP TABLESPACE can not be run inside the transaction block:
        autocommit = True
        if PSYCOPG2_VERSION >= '2.4.2':
            db_connection.set_session(autocommit=True)
        else:
            db_connection.set_isolation_level(AUTOCOMMIT)

        changed = tblspace.drop()

    # Rename tablespace:
    elif tblspace.exists and rename_to:
        if tblspace.name != rename_to:
            changed = tblspace.rename(rename_to)

    if state == 'present':
        # Refresh information:
        tblspace.get_info()

    # Change owner and settings:
    if state == 'present' and tblspace.exists:
        if owner:
            changed = tblspace.set_owner(owner)

        if settings:
            changed = tblspace.set_settings(settings)

        tblspace.get_info()

    # Rollback if it's possible and check_mode:
    if not autocommit:
        if module.check_mode:
            db_connection.rollback()
        else:
            db_connection.commit()

    cursor.close()
    db_connection.close()

    # Make return values:
    kw = dict(
        changed=changed,
        state='present',
        tablespace=tblspace.name,
        owner=tblspace.owner,
        queries=tblspace.executed_queries,
        options=tblspace.settings,
        location=tblspace.location,
    )

    if state == 'present':
        kw['state'] = 'present'

        if tblspace.new_name:
            kw['newname'] = tblspace.new_name

    elif state == 'absent':
        kw['state'] = 'absent'

    module.exit_json(**kw)


if __name__ == '__main__':
    main()

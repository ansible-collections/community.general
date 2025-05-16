#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018-2019, Andrew Klychkov (@Andersson007) <aaklychkov@mail.ru>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: postgresql_idx
short_description: Create or drop indexes from a PostgreSQL database
description:
- Create or drop indexes from a PostgreSQL database.

options:
  idxname:
    description:
    - Name of the index to create or drop.
    type: str
    required: true
    aliases:
    - name
  db:
    description:
    - Name of database to connect to and where the index will be created/dropped.
    type: str
    aliases:
    - login_db
  session_role:
    description:
    - Switch to session_role after connecting.
      The specified session_role must be a role that the current login_user is a member of.
    - Permissions checking for SQL commands is carried out as though
      the session_role were the one that had logged in originally.
    type: str
  schema:
    description:
    - Name of a database schema where the index will be created.
    type: str
  state:
    description:
    - Index state.
    - C(present) implies the index will be created if it does not exist.
    - C(absent) implies the index will be dropped if it exists.
    type: str
    default: present
    choices: [ absent, present ]
  table:
    description:
    - Table to create index on it.
    - Mutually exclusive with I(state=absent).
    type: str
  columns:
    description:
    - List of index columns that need to be covered by index.
    - Mutually exclusive with I(state=absent).
    type: list
    elements: str
    aliases:
    - column
  cond:
    description:
    - Index conditions.
    - Mutually exclusive with I(state=absent).
    type: str
  idxtype:
    description:
    - Index type (like btree, gist, gin, etc.).
    - Mutually exclusive with I(state=absent).
    type: str
    aliases:
    - type
  concurrent:
    description:
    - Enable or disable concurrent mode (CREATE / DROP INDEX CONCURRENTLY).
    - Pay attention, if I(concurrent=no), the table will be locked (ACCESS EXCLUSIVE) during the building process.
      For more information about the lock levels see U(https://www.postgresql.org/docs/current/explicit-locking.html).
    - If the building process was interrupted for any reason when I(cuncurrent=yes), the index becomes invalid.
      In this case it should be dropped and created again.
    - Mutually exclusive with I(cascade=yes).
    type: bool
    default: yes
  unique:
    description:
    - Enable unique index.
    - Only btree currently supports unique indexes.
    type: bool
    default: no
    version_added: '0.2.0'
  tablespace:
    description:
    - Set a tablespace for the index.
    - Mutually exclusive with I(state=absent).
    required: false
    type: str
  storage_params:
    description:
    - Storage parameters like fillfactor, vacuum_cleanup_index_scale_factor, etc.
    - Mutually exclusive with I(state=absent).
    type: list
    elements: str
  cascade:
    description:
    - Automatically drop objects that depend on the index,
      and in turn all objects that depend on those objects.
    - It used only with I(state=absent).
    - Mutually exclusive with I(concurrent=yes)
    type: bool
    default: no
  trust_input:
    description:
    - If C(no), check whether values of parameters I(idxname), I(session_role),
      I(schema), I(table), I(columns), I(tablespace), I(storage_params),
      I(cond) are potentially dangerous.
    - It makes sense to use C(yes) only when SQL injections via the parameters are possible.
    type: bool
    default: yes
    version_added: '0.2.0'

seealso:
- module: community.general.postgresql_table
- module: community.general.postgresql_tablespace
- name: PostgreSQL indexes reference
  description: General information about PostgreSQL indexes.
  link: https://www.postgresql.org/docs/current/indexes.html
- name: CREATE INDEX reference
  description: Complete reference of the CREATE INDEX command documentation.
  link: https://www.postgresql.org/docs/current/sql-createindex.html
- name: ALTER INDEX reference
  description: Complete reference of the ALTER INDEX command documentation.
  link: https://www.postgresql.org/docs/current/sql-alterindex.html
- name: DROP INDEX reference
  description: Complete reference of the DROP INDEX command documentation.
  link: https://www.postgresql.org/docs/current/sql-dropindex.html

notes:
- The index building process can affect database performance.
- To avoid table locks on production databases, use I(concurrent=yes) (default behavior).

author:
- Andrew Klychkov (@Andersson007)
- Thomas O'Donnell (@andytom)

extends_documentation_fragment:
- community.general.postgres

'''

EXAMPLES = r'''
- name: Create btree index if not exists test_idx concurrently covering columns id and name of table products
  community.general.postgresql_idx:
    db: acme
    table: products
    columns: id,name
    name: test_idx

- name: Create btree index test_idx concurrently with tablespace called ssd and storage parameter
  community.general.postgresql_idx:
    db: acme
    table: products
    columns:
    - id
    - name
    idxname: test_idx
    tablespace: ssd
    storage_params:
    - fillfactor=90

- name: Create gist index test_gist_idx concurrently on column geo_data of table map
  community.general.postgresql_idx:
    db: somedb
    table: map
    idxtype: gist
    columns: geo_data
    idxname: test_gist_idx

# Note: for the example below pg_trgm extension must be installed for gin_trgm_ops
- name: Create gin index gin0_idx not concurrently on column comment of table test
  community.general.postgresql_idx:
    idxname: gin0_idx
    table: test
    columns: comment gin_trgm_ops
    concurrent: no
    idxtype: gin

- name: Drop btree test_idx concurrently
  community.general.postgresql_idx:
    db: mydb
    idxname: test_idx
    state: absent

- name: Drop test_idx cascade
  community.general.postgresql_idx:
    db: mydb
    idxname: test_idx
    state: absent
    cascade: yes
    concurrent: no

- name: Create btree index test_idx concurrently on columns id,comment where column id > 1
  community.general.postgresql_idx:
    db: mydb
    table: test
    columns: id,comment
    idxname: test_idx
    cond: id > 1

- name: Create unique btree index if not exists test_unique_idx on column name of table products
  community.general.postgresql_idx:
    db: acme
    table: products
    columns: name
    name: test_unique_idx
    unique: yes
    concurrent: no
'''

RETURN = r'''
name:
  description: Index name.
  returned: always
  type: str
  sample: 'foo_idx'
state:
  description: Index state.
  returned: always
  type: str
  sample: 'present'
schema:
  description: Schema where index exists.
  returned: always
  type: str
  sample: 'public'
tablespace:
  description: Tablespace where index exists.
  returned: always
  type: str
  sample: 'ssd'
query:
  description: Query that was tried to be executed.
  returned: always
  type: str
  sample: 'CREATE INDEX CONCURRENTLY foo_idx ON test_table USING BTREE (id)'
storage_params:
  description: Index storage parameters.
  returned: always
  type: list
  sample: [ "fillfactor=90" ]
valid:
  description: Index validity.
  returned: always
  type: bool
  sample: true
'''

try:
    from psycopg2.extras import DictCursor
except ImportError:
    # psycopg2 is checked by connect_to_db()
    # from ansible.module_utils.postgres
    pass

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.database import check_input
from ansible_collections.community.general.plugins.module_utils.postgres import (
    connect_to_db,
    exec_sql,
    get_conn_params,
    postgres_common_argument_spec,
)


VALID_IDX_TYPES = ('BTREE', 'HASH', 'GIST', 'SPGIST', 'GIN', 'BRIN')


# ===========================================
# PostgreSQL module specific support methods.
#

class Index(object):

    """Class for working with PostgreSQL indexes.

    TODO:
        1. Add possibility to change ownership
        2. Add possibility to change tablespace
        3. Add list called executed_queries (executed_query should be left too)
        4. Use self.module instead of passing arguments to the methods whenever possible

    Args:
        module (AnsibleModule) -- object of AnsibleModule class
        cursor (cursor) -- cursor object of psycopg2 library
        schema (str) -- name of the index schema
        name (str) -- name of the index

    Attrs:
        module (AnsibleModule) -- object of AnsibleModule class
        cursor (cursor) -- cursor object of psycopg2 library
        schema (str) -- name of the index schema
        name (str) -- name of the index
        exists (bool) -- flag the index exists in the DB or not
        info (dict) -- dict that contents information about the index
        executed_query (str) -- executed query
    """

    def __init__(self, module, cursor, schema, name):
        self.name = name
        if schema:
            self.schema = schema
        else:
            self.schema = 'public'
        self.module = module
        self.cursor = cursor
        self.info = {
            'name': self.name,
            'state': 'absent',
            'schema': '',
            'tblname': '',
            'tblspace': '',
            'valid': True,
            'storage_params': [],
        }
        self.exists = False
        self.__exists_in_db()
        self.executed_query = ''

    def get_info(self):
        """Refresh index info.

        Return self.info dict.
        """
        self.__exists_in_db()
        return self.info

    def __exists_in_db(self):
        """Check index existence, collect info, add it to self.info dict.

        Return True if the index exists, otherwise, return False.
        """
        query = ("SELECT i.schemaname, i.tablename, i.tablespace, "
                 "pi.indisvalid, c.reloptions "
                 "FROM pg_catalog.pg_indexes AS i "
                 "JOIN pg_catalog.pg_class AS c "
                 "ON i.indexname = c.relname "
                 "JOIN pg_catalog.pg_index AS pi "
                 "ON c.oid = pi.indexrelid "
                 "WHERE i.indexname = %(name)s")

        res = exec_sql(self, query, query_params={'name': self.name}, add_to_executed=False)
        if res:
            self.exists = True
            self.info = dict(
                name=self.name,
                state='present',
                schema=res[0][0],
                tblname=res[0][1],
                tblspace=res[0][2] if res[0][2] else '',
                valid=res[0][3],
                storage_params=res[0][4] if res[0][4] else [],
            )
            return True

        else:
            self.exists = False
            return False

    def create(self, tblname, idxtype, columns, cond, tblspace,
               storage_params, concurrent=True, unique=False):
        """Create PostgreSQL index.

        Return True if success, otherwise, return False.

        Args:
            tblname (str) -- name of a table for the index
            idxtype (str) -- type of the index like BTREE, BRIN, etc
            columns (str) -- string of comma-separated columns that need to be covered by index
            tblspace (str) -- tablespace for storing the index
            storage_params (str) -- string of comma-separated storage parameters

        Kwargs:
            concurrent (bool) -- build index in concurrent mode, default True
        """
        if self.exists:
            return False

        if idxtype is None:
            idxtype = "BTREE"

        query = 'CREATE'

        if unique:
            query += ' UNIQUE'

        query += ' INDEX'

        if concurrent:
            query += ' CONCURRENTLY'

        query += ' "%s"' % self.name

        query += ' ON "%s"."%s" ' % (self.schema, tblname)

        query += 'USING %s (%s)' % (idxtype, columns)

        if storage_params:
            query += ' WITH (%s)' % storage_params

        if tblspace:
            query += ' TABLESPACE "%s"' % tblspace

        if cond:
            query += ' WHERE %s' % cond

        self.executed_query = query

        return exec_sql(self, query, return_bool=True, add_to_executed=False)

    def drop(self, cascade=False, concurrent=True):
        """Drop PostgreSQL index.

        Return True if success, otherwise, return False.

        Args:
            schema (str) -- name of the index schema

        Kwargs:
            cascade (bool) -- automatically drop objects that depend on the index,
                default False
            concurrent (bool) -- build index in concurrent mode, default True
        """
        if not self.exists:
            return False

        query = 'DROP INDEX'

        if concurrent:
            query += ' CONCURRENTLY'

        query += ' "%s"."%s"' % (self.schema, self.name)

        if cascade:
            query += ' CASCADE'

        self.executed_query = query

        return exec_sql(self, query, return_bool=True, add_to_executed=False)


# ===========================================
# Module execution.
#


def main():
    argument_spec = postgres_common_argument_spec()
    argument_spec.update(
        idxname=dict(type='str', required=True, aliases=['name']),
        db=dict(type='str', aliases=['login_db']),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        concurrent=dict(type='bool', default=True),
        unique=dict(type='bool', default=False),
        table=dict(type='str'),
        idxtype=dict(type='str', aliases=['type']),
        columns=dict(type='list', elements='str', aliases=['column']),
        cond=dict(type='str'),
        session_role=dict(type='str'),
        tablespace=dict(type='str'),
        storage_params=dict(type='list', elements='str'),
        cascade=dict(type='bool', default=False),
        schema=dict(type='str'),
        trust_input=dict(type='bool', default=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    idxname = module.params["idxname"]
    state = module.params["state"]
    concurrent = module.params["concurrent"]
    unique = module.params["unique"]
    table = module.params["table"]
    idxtype = module.params["idxtype"]
    columns = module.params["columns"]
    cond = module.params["cond"]
    tablespace = module.params["tablespace"]
    storage_params = module.params["storage_params"]
    cascade = module.params["cascade"]
    schema = module.params["schema"]
    session_role = module.params["session_role"]
    trust_input = module.params["trust_input"]

    if not trust_input:
        # Check input for potentially dangerous elements:
        check_input(module, idxname, session_role, schema, table, columns,
                    tablespace, storage_params, cond)

    if concurrent and cascade:
        module.fail_json(msg="Concurrent mode and cascade parameters are mutually exclusive")

    if unique and (idxtype and idxtype != 'btree'):
        module.fail_json(msg="Only btree currently supports unique indexes")

    if state == 'present':
        if not table:
            module.fail_json(msg="Table must be specified")
        if not columns:
            module.fail_json(msg="At least one column must be specified")
    else:
        if table or columns or cond or idxtype or tablespace:
            module.fail_json(msg="Index %s is going to be removed, so it does not "
                                 "make sense to pass a table name, columns, conditions, "
                                 "index type, or tablespace" % idxname)

    if cascade and state != 'absent':
        module.fail_json(msg="cascade parameter used only with state=absent")

    conn_params = get_conn_params(module, module.params)
    db_connection = connect_to_db(module, conn_params, autocommit=True)
    cursor = db_connection.cursor(cursor_factory=DictCursor)

    # Set defaults:
    changed = False

    # Do job:
    index = Index(module, cursor, schema, idxname)
    kw = index.get_info()
    kw['query'] = ''

    #
    # check_mode start
    if module.check_mode:
        if state == 'present' and index.exists:
            kw['changed'] = False
            module.exit_json(**kw)

        elif state == 'present' and not index.exists:
            kw['changed'] = True
            module.exit_json(**kw)

        elif state == 'absent' and not index.exists:
            kw['changed'] = False
            module.exit_json(**kw)

        elif state == 'absent' and index.exists:
            kw['changed'] = True
            module.exit_json(**kw)
    # check_mode end
    #

    if state == "present":
        if idxtype and idxtype.upper() not in VALID_IDX_TYPES:
            module.fail_json(msg="Index type '%s' of %s is not in valid types" % (idxtype, idxname))

        columns = ','.join(columns)

        if storage_params:
            storage_params = ','.join(storage_params)

        changed = index.create(table, idxtype, columns, cond, tablespace, storage_params, concurrent, unique)

        if changed:
            kw = index.get_info()
            kw['state'] = 'present'
            kw['query'] = index.executed_query

    else:
        changed = index.drop(cascade, concurrent)

        if changed:
            kw['state'] = 'absent'
            kw['query'] = index.executed_query

    if not kw['valid']:
        db_connection.rollback()
        module.warn("Index %s is invalid! ROLLBACK" % idxname)

    if not concurrent:
        db_connection.commit()

    kw['changed'] = changed
    db_connection.close()
    module.exit_json(**kw)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Andrew Klychkov (@Andersson007) <aaklychkov@mail.ru>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: postgresql_ping
short_description: Check remote PostgreSQL server availability
description:
- Simple module to check remote PostgreSQL server availability.
options:
  db:
    description:
    - Name of a database to connect to.
    type: str
    aliases:
    - login_db
seealso:
- module: postgresql_info
author:
- Andrew Klychkov (@Andersson007)
extends_documentation_fragment:
- community.general.postgres

'''

EXAMPLES = r'''
# PostgreSQL ping dbsrv server from the shell:
# ansible dbsrv -m postgresql_ping

# In the example below you need to generate certificates previously.
# See https://www.postgresql.org/docs/current/libpq-ssl.html for more information.
- name: PostgreSQL ping dbsrv server using not default credentials and ssl
  postgresql_ping:
    db: protected_db
    login_host: dbsrv
    login_user: secret
    login_password: secret_pass
    ca_cert: /root/root.crt
    ssl_mode: verify-full
'''

RETURN = r'''
is_available:
  description: PostgreSQL server availability.
  returned: always
  type: bool
  sample: true
server_version:
  description: PostgreSQL server version.
  returned: always
  type: dict
  sample: { major: 10, minor: 1 }
'''

try:
    from psycopg2.extras import DictCursor
except ImportError:
    # psycopg2 is checked by connect_to_db()
    # from ansible.module_utils.postgres
    pass

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.postgres import (
    connect_to_db,
    exec_sql,
    get_conn_params,
    postgres_common_argument_spec,
)


# ===========================================
# PostgreSQL module specific support methods.
#


class PgPing(object):
    def __init__(self, module, cursor):
        self.module = module
        self.cursor = cursor
        self.is_available = False
        self.version = {}

    def do(self):
        self.get_pg_version()
        return (self.is_available, self.version)

    def get_pg_version(self):
        query = "SELECT version()"
        raw = exec_sql(self, query, add_to_executed=False)[0][0]
        if raw:
            self.is_available = True
            raw = raw.split()[1].split('.')
            self.version = dict(
                major=int(raw[0]),
                minor=int(raw[1]),
            )


# ===========================================
# Module execution.
#


def main():
    argument_spec = postgres_common_argument_spec()
    argument_spec.update(
        db=dict(type='str', aliases=['login_db']),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # Set some default values:
    cursor = False
    db_connection = False
    result = dict(
        changed=False,
        is_available=False,
        server_version=dict(),
    )

    conn_params = get_conn_params(module, module.params, warn_db_default=False)
    db_connection = connect_to_db(module, conn_params, fail_on_conn=False)

    if db_connection is not None:
        cursor = db_connection.cursor(cursor_factory=DictCursor)

    # Do job:
    pg_ping = PgPing(module, cursor)
    if cursor:
        # If connection established:
        result["is_available"], result["server_version"] = pg_ping.do()
        db_connection.rollback()

    module.exit_json(**result)


if __name__ == '__main__':
    main()

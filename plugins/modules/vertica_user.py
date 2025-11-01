#!/usr/bin/python
# Copyright Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: vertica_user
short_description: Adds or removes Vertica database users and assigns roles
description:
  - Adds or removes Vertica database user and, optionally, assigns roles.
  - A user is not removed until all the dependencies have been dropped.
  - In such a situation, if the module tries to remove the user it fails and only remove roles granted to the user.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  user:
    description:
      - Name of the user to add or remove.
    required: true
    type: str
    aliases: ['name']
  profile:
    description:
      - Sets the user's profile.
    type: str
  resource_pool:
    description:
      - Sets the user's resource pool.
    type: str
  password:
    description:
      - The user's password encrypted by the MD5 algorithm.
      - The password must be generated with the format C("md5" + md5[password + username]), resulting in a total of 35 characters.
        An easy way to do this is by querying the Vertica database with select V('md5'|| md5('<user_password><user_name>'\)).
    type: str
  expired:
    description:
      - Sets the user's password expiration.
    type: bool
  ldap:
    description:
      - Set to V(true) if users are authenticated using LDAP.
      - The user is created with password expired and set to V($ldap$).
    type: bool
  roles:
    description:
      - Comma separated list of roles to assign to the user.
    aliases: ['role']
    type: str
  state:
    description:
      - Whether to create (V(present)), drop (V(absent)), or lock (V(locked)) a user.
    choices: ['present', 'absent', 'locked']
    default: present
    type: str
  db:
    description:
      - Name of the Vertica database.
    type: str
  cluster:
    description:
      - Name of the Vertica cluster.
    default: localhost
    type: str
  port:
    description:
      - Vertica cluster port to connect to.
    default: '5433'
    type: str
  login_user:
    description:
      - The username used to authenticate with.
    default: dbadmin
    type: str
  login_password:
    description:
      - The password used to authenticate with.
    type: str
notes:
  - The default authentication assumes that you are either logging in as or sudo'ing to the C(dbadmin) account on the host.
  - This module uses C(pyodbc), a Python ODBC database adapter. You must ensure that C(unixODBC) and C(pyodbc) is installed
    on the host and properly configured.
  - Configuring C(unixODBC) for Vertica requires C(Driver = /opt/vertica/lib64/libverticaodbc.so) to be added to the C(Vertica)
    section of either C(/etc/odbcinst.ini) or C($HOME/.odbcinst.ini) and both C(ErrorMessagesPath = /opt/vertica/lib64) and
    C(DriverManagerEncoding = UTF-16) to be added to the C(Driver) section of either C(/etc/vertica.ini) or C($HOME/.vertica.ini).
requirements: ['unixODBC', 'pyodbc']
author: "Dariusz Owczarek (@dareko)"
"""

EXAMPLES = r"""
- name: Creating a new vertica user with password
  community.general.vertica_user: name=user_name password=md5<encrypted_password> db=db_name state=present

- name: Creating a new vertica user authenticated via ldap with roles assigned
  community.general.vertica_user: name=user_name ldap=true db=db_name roles=schema_name_ro state=present
"""
import traceback

PYODBC_IMP_ERR = None
try:
    import pyodbc
except ImportError:
    PYODBC_IMP_ERR = traceback.format_exc()
    pyodbc_found = False
else:
    pyodbc_found = True

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


class NotSupportedError(Exception):
    pass


class CannotDropError(Exception):
    pass


# module specific functions


def get_user_facts(cursor, user=""):
    facts = {}
    cursor.execute(
        """
        select u.user_name, u.is_locked, u.lock_time,
        p.password, p.acctexpired as is_expired,
        u.profile_name, u.resource_pool,
        u.all_roles, u.default_roles
        from users u join password_auditor p on p.user_id = u.user_id
        where not u.is_super_user
        and (? = '' or u.user_name ilike ?)
    """,
        user,
        user,
    )
    while True:
        rows = cursor.fetchmany(100)
        if not rows:
            break
        for row in rows:
            user_key = row.user_name.lower()
            facts[user_key] = {
                "name": row.user_name,
                "locked": str(row.is_locked),
                "password": row.password,
                "expired": str(row.is_expired),
                "profile": row.profile_name,
                "resource_pool": row.resource_pool,
                "roles": [],
                "default_roles": [],
            }
            if row.is_locked:
                facts[user_key]["locked_time"] = str(row.lock_time)
            if row.all_roles:
                facts[user_key]["roles"] = row.all_roles.replace(" ", "").split(",")
            if row.default_roles:
                facts[user_key]["default_roles"] = row.default_roles.replace(" ", "").split(",")
    return facts


def update_roles(user_facts, cursor, user, existing_all, existing_default, required):
    del_roles = list(set(existing_all) - set(required))
    if del_roles:
        cursor.execute(f"revoke {','.join(del_roles)} from {user}")
    new_roles = list(set(required) - set(existing_all))
    if new_roles:
        cursor.execute(f"grant {','.join(new_roles)} to {user}")
    if required:
        cursor.execute(f"alter user {user} default role {','.join(required)}")


def check(user_facts, user, profile, resource_pool, locked, password, expired, ldap, roles):
    user_key = user.lower()
    if user_key not in user_facts:
        return False
    if profile and profile != user_facts[user_key]["profile"]:
        return False
    if resource_pool and resource_pool != user_facts[user_key]["resource_pool"]:
        return False
    if locked != (user_facts[user_key]["locked"] == "True"):
        return False
    if password and password != user_facts[user_key]["password"]:
        return False
    if (
        expired is not None
        and expired != (user_facts[user_key]["expired"] == "True")
        or ldap is not None
        and ldap != (user_facts[user_key]["expired"] == "True")
    ):
        return False
    if roles and (
        sorted(roles) != sorted(user_facts[user_key]["roles"])
        or sorted(roles) != sorted(user_facts[user_key]["default_roles"])
    ):
        return False
    return True


def present(user_facts, cursor, user, profile, resource_pool, locked, password, expired, ldap, roles):
    user_key = user.lower()
    if user_key not in user_facts:
        query_fragments = [f"create user {user}"]
        if locked:
            query_fragments.append("account lock")
        if password or ldap:
            if password:
                query_fragments.append(f"identified by '{password}'")
            else:
                query_fragments.append("identified by '$ldap$'")
        if expired or ldap:
            query_fragments.append("password expire")
        if profile:
            query_fragments.append(f"profile {profile}")
        if resource_pool:
            query_fragments.append(f"resource pool {resource_pool}")
        cursor.execute(" ".join(query_fragments))
        if resource_pool and resource_pool != "general":
            cursor.execute(f"grant usage on resource pool {resource_pool} to {user}")
        update_roles(user_facts, cursor, user, [], [], roles)
        user_facts.update(get_user_facts(cursor, user))
        return True
    else:
        changed = False
        query_fragments = [f"alter user {user}"]
        if locked is not None and locked != (user_facts[user_key]["locked"] == "True"):
            if locked:
                state = "lock"
            else:
                state = "unlock"
            query_fragments.append(f"account {state}")
            changed = True
        if password and password != user_facts[user_key]["password"]:
            query_fragments.append(f"identified by '{password}'")
            changed = True
        if ldap:
            if ldap != (user_facts[user_key]["expired"] == "True"):
                query_fragments.append("password expire")
                changed = True
        elif expired is not None and expired != (user_facts[user_key]["expired"] == "True"):
            if expired:
                query_fragments.append("password expire")
                changed = True
            else:
                raise NotSupportedError("Unexpiring user password is not supported.")
        if profile and profile != user_facts[user_key]["profile"]:
            query_fragments.append(f"profile {profile}")
            changed = True
        if resource_pool and resource_pool != user_facts[user_key]["resource_pool"]:
            query_fragments.append(f"resource pool {resource_pool}")
            if user_facts[user_key]["resource_pool"] != "general":
                cursor.execute(f"revoke usage on resource pool {user_facts[user_key]['resource_pool']} from {user}")
            if resource_pool != "general":
                cursor.execute(f"grant usage on resource pool {resource_pool} to {user}")
            changed = True
        if changed:
            cursor.execute(" ".join(query_fragments))
        if roles and (
            sorted(roles) != sorted(user_facts[user_key]["roles"])
            or sorted(roles) != sorted(user_facts[user_key]["default_roles"])
        ):
            update_roles(
                user_facts, cursor, user, user_facts[user_key]["roles"], user_facts[user_key]["default_roles"], roles
            )
            changed = True
        if changed:
            user_facts.update(get_user_facts(cursor, user))
        return changed


def absent(user_facts, cursor, user, roles):
    user_key = user.lower()
    if user_key in user_facts:
        update_roles(user_facts, cursor, user, user_facts[user_key]["roles"], user_facts[user_key]["default_roles"], [])
        try:
            cursor.execute(f"drop user {user_facts[user_key]['name']}")
        except pyodbc.Error:
            raise CannotDropError("Dropping user failed due to dependencies.")
        del user_facts[user_key]
        return True
    else:
        return False


# module logic


def main():
    module = AnsibleModule(
        argument_spec=dict(
            user=dict(required=True, aliases=["name"]),
            profile=dict(),
            resource_pool=dict(),
            password=dict(no_log=True),
            expired=dict(type="bool"),
            ldap=dict(type="bool"),
            roles=dict(aliases=["role"]),
            state=dict(default="present", choices=["absent", "present", "locked"]),
            db=dict(),
            cluster=dict(default="localhost"),
            port=dict(default="5433"),
            login_user=dict(default="dbadmin"),
            login_password=dict(no_log=True),
        ),
        supports_check_mode=True,
    )

    if not pyodbc_found:
        module.fail_json(msg=missing_required_lib("pyodbc"), exception=PYODBC_IMP_ERR)

    user = module.params["user"]
    profile = module.params["profile"]
    if profile:
        profile = profile.lower()
    resource_pool = module.params["resource_pool"]
    if resource_pool:
        resource_pool = resource_pool.lower()
    password = module.params["password"]
    expired = module.params["expired"]
    ldap = module.params["ldap"]
    roles = []
    if module.params["roles"]:
        roles = module.params["roles"].split(",")
        roles = [_f for _f in roles if _f]
    state = module.params["state"]
    if state == "locked":
        locked = True
    else:
        locked = False
    db = ""
    if module.params["db"]:
        db = module.params["db"]

    changed = False

    try:
        dsn = (
            "Driver=Vertica;"
            f"Server={module.params['cluster']};"
            f"Port={module.params['port']};"
            f"Database={db};"
            f"User={module.params['login_user']};"
            f"Password={module.params['login_password']};"
            f"ConnectionLoadBalance=true"
        )
        db_conn = pyodbc.connect(dsn, autocommit=True)
        cursor = db_conn.cursor()
    except Exception as e:
        module.fail_json(msg=f"Unable to connect to database: {e}.")

    try:
        user_facts = get_user_facts(cursor)
        if module.check_mode:
            changed = not check(user_facts, user, profile, resource_pool, locked, password, expired, ldap, roles)
        elif state == "absent":
            try:
                changed = absent(user_facts, cursor, user, roles)
            except pyodbc.Error as e:
                module.fail_json(msg=to_native(e), exception=traceback.format_exc())
        elif state in ["present", "locked"]:
            try:
                changed = present(
                    user_facts, cursor, user, profile, resource_pool, locked, password, expired, ldap, roles
                )
            except pyodbc.Error as e:
                module.fail_json(msg=to_native(e), exception=traceback.format_exc())
    except NotSupportedError as e:
        module.fail_json(msg=to_native(e), ansible_facts={"vertica_users": user_facts})
    except CannotDropError as e:
        module.fail_json(msg=to_native(e), ansible_facts={"vertica_users": user_facts})
    except SystemExit:
        # avoid catching this on python 2.4
        raise
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())

    module.exit_json(changed=changed, user=user, ansible_facts={"vertica_users": user_facts})


if __name__ == "__main__":
    main()

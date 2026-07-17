#!/usr/bin/python

# Copyright (c) 2016, Adfinis SyGroup AG
# @keachi
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: udm_user
author:
  - keachi (@keachi)
short_description: Manage posix users on a univention corporate server
description:
  - This module allows to manage posix users on a univention corporate server (UCS). It uses the Python API of the UCS to
    create a new object or edit it.
notes:
  - This module uses L(passlib, https://pypi.org/project/passlib/) for password hashing when available,
    falling back to the Python C(crypt) module or L(legacycrypt, https://pypi.org/project/legacycrypt/).
requirements:
  - passlib (Python library, recommended), or legacycrypt on Python 3.13 or newer
  - It requires no dependency on Python 3.12 and earlier, but then it relies on the deprecated standard library C(crypt).
extends_documentation_fragment:
  - community.general._attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: partial
options:
  state:
    default: "present"
    choices: [present, absent]
    description:
      - Whether the user is present or not.
    type: str
  username:
    required: true
    description:
      - User name.
    aliases: ['name']
    type: str
  firstname:
    description:
      - First name. Required if O(state=present).
    type: str
  lastname:
    description:
      - Last name. Required if O(state=present).
    type: str
  password:
    description:
      - Password. Required if O(state=present).
    type: str
  birthday:
    description:
      - Birthday.
    type: str
  city:
    description:
      - City of users business address.
    type: str
  country:
    description:
      - Country of users business address.
    type: str
  department_number:
    description:
      - Department number of users business address.
    aliases: [departmentNumber]
    type: str
  description:
    description:
      - Description (not gecos).
    type: str
  display_name:
    description:
      - Display name (not gecos).
    aliases: [displayName]
    type: str
  email:
    default: ['']
    description:
      - A list of e-mail addresses.
    type: list
    elements: str
  employee_number:
    description:
      - Employee number.
    aliases: [employeeNumber]
    type: str
  employee_type:
    description:
      - Employee type.
    aliases: [employeeType]
    type: str
  gecos:
    description:
      - GECOS.
    type: str
  groups:
    default: []
    description:
      - 'POSIX groups, the LDAP DNs of the groups is found with the LDAP filter for each group as $GROUP: V((&(objectClass=posixGroup\)(cn=$GROUP\)\)).'
    type: list
    elements: str
  home_share:
    description:
      - Home NFS share. Must be a LDAP DN, for example V(cn=home,cn=shares,ou=school,dc=example,dc=com).
    aliases: [homeShare]
    type: str
  home_share_path:
    description:
      - Path to home NFS share, inside the homeShare.
    aliases: [homeSharePath]
    type: str
  home_telephone_number:
    default: []
    description:
      - List of private telephone numbers.
    aliases: [homeTelephoneNumber]
    type: list
    elements: str
  homedrive:
    description:
      - Windows home drive, for example V("H:").
    type: str
  mail_alternative_address:
    default: []
    description:
      - List of alternative e-mail addresses.
    aliases: [mailAlternativeAddress]
    type: list
    elements: str
  mail_home_server:
    description:
      - FQDN of mail server.
    aliases: [mailHomeServer]
    type: str
  mail_primary_address:
    description:
      - Primary e-mail address.
    aliases: [mailPrimaryAddress]
    type: str
  mobile_telephone_number:
    default: []
    description:
      - Mobile phone number.
    aliases: [mobileTelephoneNumber]
    type: list
    elements: str
  organisation:
    description:
      - Organisation.
    aliases: [organization]
    type: str
  overridePWHistory:
    type: bool
    default: false
    description:
      - Override password history.
    aliases: [override_pw_history]
  overridePWLength:
    type: bool
    default: false
    description:
      - Override password check.
    aliases: [override_pw_length]
  pager_telephonenumber:
    default: []
    description:
      - List of pager telephone numbers.
    aliases: [pagerTelephonenumber]
    type: list
    elements: str
  phone:
    description:
      - List of telephone numbers.
    type: list
    elements: str
    default: []
  postcode:
    description:
      - Postal code of users business address.
    type: str
  primary_group:
    description:
      - Primary group. This must be the group LDAP DN.
      - If not specified, it defaults to V(cn=Domain Users,cn=groups,$LDAP_BASE_DN).
    aliases: [primaryGroup]
    type: str
  profilepath:
    description:
      - Windows profile directory.
    type: str
  pwd_change_next_login:
    choices: ['0', '1']
    description:
      - Change password on next login.
    aliases: [pwdChangeNextLogin]
    type: str
  room_number:
    description:
      - Room number of users business address.
    aliases: [roomNumber]
    type: str
  samba_privileges:
    description:
      - Samba privilege, like allow printer administration, do domain join.
    aliases: [sambaPrivileges]
    type: list
    elements: str
    default: []
  samba_user_workstations:
    description:
      - Allow the authentication only on this Microsoft Windows host.
    aliases: [sambaUserWorkstations]
    type: list
    elements: str
    default: []
  sambahome:
    description:
      - Windows home path, for example V('\\\\$FQDN\\$USERNAME').
    type: str
  scriptpath:
    description:
      - Windows logon script.
    type: str
  secretary:
    default: []
    description:
      - A list of superiors as LDAP DNs.
    type: list
    elements: str
  serviceprovider:
    default: ['']
    description:
      - Enable user for the following service providers.
    type: list
    elements: str
  shell:
    default: '/bin/bash'
    description:
      - Login shell.
    type: str
  street:
    description:
      - Street of users business address.
    type: str
  title:
    description:
      - Title, for example V(Prof.).
    type: str
  unixhome:
    description:
      - Unix home directory.
      - If not specified, it defaults to C(/home/$USERNAME).
    type: str
  userexpiry:
    description:
      - Account expiry date, for example V(1999-12-31).
      - If not specified, it defaults to the current day plus one year.
    type: str
  position:
    default: ''
    description:
      - Define the whole position of users object inside the LDAP tree, for example V(cn=employee,cn=users,ou=school,dc=example,dc=com).
    type: str
  update_password:
    default: always
    choices: [always, on_create]
    description:
      - V(always) updates passwords if they differ.
      - V(on_create) only sets the password for newly created users.
    type: str
  ou:
    default: ''
    description:
      - Organizational Unit inside the LDAP Base DN, for example V(school) for LDAP OU C(ou=school,dc=example,dc=com).
    type: str
  subpath:
    default: 'cn=users'
    description:
      - LDAP subpath inside the organizational unit, for example V(cn=teachers,cn=users) for LDAP container C(cn=teachers,cn=users,dc=example,dc=com).
    type: str
"""


EXAMPLES = r"""
- name: Create a user on a UCS
  community.general.udm_user:
    name: FooBar
    password: secure_password
    firstname: Foo
    lastname: Bar

- name: Create a user with the DN uid=foo,cn=teachers,cn=users,ou=school,dc=school,dc=example,dc=com
  community.general.udm_user:
    name: foo
    password: secure_password
    firstname: Foo
    lastname: Bar
    ou: school
    subpath: 'cn=teachers,cn=users'

# or define the position
- name: Create a user with the DN uid=foo,cn=teachers,cn=users,ou=school,dc=school,dc=example,dc=com
  community.general.udm_user:
    name: foo
    password: secure_password
    firstname: Foo
    lastname: Bar
    position: 'cn=teachers,cn=users,ou=school,dc=school,dc=example,dc=com'
"""


RETURN = """#"""


from datetime import date, timedelta

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils import _deps as deps

with deps.declare("crypt_context"):
    from ansible_collections.community.general.plugins.module_utils._crypt import CryptContext, has_crypt_context

    if not has_crypt_context:
        raise ImportError("Failed to import any of: passlib, crypt, legacycrypt")

from ansible_collections.community.general.plugins.module_utils._univention_umc import (
    base_dn,
    ldap_search,
    umc_module_for_add,
    umc_module_for_edit,
)


def main():
    expiry = date.strftime(date.today() + timedelta(days=365), "%Y-%m-%d")
    module = AnsibleModule(
        argument_spec=dict(
            birthday=dict(type="str"),
            city=dict(type="str"),
            country=dict(type="str"),
            department_number=dict(type="str", aliases=["departmentNumber"]),
            description=dict(type="str"),
            display_name=dict(type="str", aliases=["displayName"]),
            email=dict(default=[""], type="list", elements="str"),
            employee_number=dict(type="str", aliases=["employeeNumber"]),
            employee_type=dict(type="str", aliases=["employeeType"]),
            firstname=dict(type="str"),
            gecos=dict(type="str"),
            groups=dict(default=[], type="list", elements="str"),
            home_share=dict(type="str", aliases=["homeShare"]),
            home_share_path=dict(type="str", aliases=["homeSharePath"]),
            home_telephone_number=dict(default=[], type="list", elements="str", aliases=["homeTelephoneNumber"]),
            homedrive=dict(type="str"),
            lastname=dict(type="str"),
            mail_alternative_address=dict(default=[], type="list", elements="str", aliases=["mailAlternativeAddress"]),
            mail_home_server=dict(type="str", aliases=["mailHomeServer"]),
            mail_primary_address=dict(type="str", aliases=["mailPrimaryAddress"]),
            mobile_telephone_number=dict(default=[], type="list", elements="str", aliases=["mobileTelephoneNumber"]),
            organisation=dict(type="str", aliases=["organization"]),
            overridePWHistory=dict(default=False, type="bool", aliases=["override_pw_history"]),
            overridePWLength=dict(default=False, type="bool", aliases=["override_pw_length"]),
            pager_telephonenumber=dict(default=[], type="list", elements="str", aliases=["pagerTelephonenumber"]),
            password=dict(type="str", no_log=True),
            phone=dict(default=[], type="list", elements="str"),
            postcode=dict(type="str"),
            primary_group=dict(type="str", aliases=["primaryGroup"]),
            profilepath=dict(type="str"),
            pwd_change_next_login=dict(type="str", choices=["0", "1"], aliases=["pwdChangeNextLogin"]),
            room_number=dict(type="str", aliases=["roomNumber"]),
            samba_privileges=dict(default=[], type="list", elements="str", aliases=["sambaPrivileges"]),
            samba_user_workstations=dict(default=[], type="list", elements="str", aliases=["sambaUserWorkstations"]),
            sambahome=dict(type="str"),
            scriptpath=dict(type="str"),
            secretary=dict(default=[], type="list", elements="str"),
            serviceprovider=dict(default=[""], type="list", elements="str"),
            shell=dict(default="/bin/bash", type="str"),
            street=dict(type="str"),
            title=dict(type="str"),
            unixhome=dict(type="str"),
            userexpiry=dict(type="str"),
            username=dict(required=True, aliases=["name"], type="str"),
            position=dict(default="", type="str"),
            update_password=dict(default="always", choices=["always", "on_create"], type="str"),
            ou=dict(default="", type="str"),
            subpath=dict(default="cn=users", type="str"),
            state=dict(default="present", choices=["present", "absent"], type="str"),
        ),
        supports_check_mode=True,
        required_if=([("state", "present", ["firstname", "lastname", "password"])]),
    )

    deps.validate(module)

    crypt_context = CryptContext(schemes=["sha512_crypt", "sha256_crypt", "md5_crypt", "des_crypt"])

    username = module.params["username"]
    position = module.params["position"]
    ou = module.params["ou"]
    subpath = module.params["subpath"]
    state = module.params["state"]
    changed = False
    diff = None

    users = list(ldap_search(f"(&(objectClass=posixAccount)(uid={username}))", attr=["uid"]))
    if position != "":
        container = position
    else:
        if ou != "":
            ou = f"ou={ou},"
        if subpath != "":
            subpath = f"{subpath},"
        container = f"{subpath}{ou}{base_dn()}"
    user_dn = f"uid={username},{container}"

    exists = bool(len(users))

    if state == "present":
        try:
            if not exists:
                obj = umc_module_for_add("users/user", container)
            else:
                obj = umc_module_for_edit("users/user", user_dn)

            if module.params["display_name"] is None:
                module.params["display_name"] = f"{module.params['firstname']} {module.params['lastname']}"
            if module.params["unixhome"] is None:
                module.params["unixhome"] = f"/home/{module.params['username']}"
            # Build a mapping from alias names to canonical param names,
            # so that UDM object keys (camelCase) can be resolved to the
            # corresponding module.params keys (snake_case).
            alias_to_param = {}
            for param_name, param_spec in module.argument_spec.items():
                for alias in param_spec.get("aliases", []):
                    alias_to_param[alias] = param_name
            for k in obj.keys():
                param_name = alias_to_param.get(k, k)
                if (
                    k != "password"
                    and k != "groups"
                    and k != "overridePWHistory"
                    and param_name in module.params
                    and module.params[param_name] is not None
                ):
                    obj[k] = module.params[param_name]
            # handle some special values
            obj["e-mail"] = module.params["email"]
            if "userexpiry" in obj and obj.get("userexpiry") is None:
                obj["userexpiry"] = expiry
            password = module.params["password"]
            if obj["password"] is None:
                obj["password"] = password
            if module.params["update_password"] == "always":
                old_password = obj["password"].split("}", 2)[1]
                if not crypt_context.verify(password, old_password):
                    obj["overridePWHistory"] = module.params["overridePWHistory"]
                    obj["overridePWLength"] = module.params["overridePWLength"]
                    obj["password"] = password

            diff = obj.diff()
            if exists:
                for k in obj.keys():
                    if obj.hasChanged(k):
                        changed = True
            else:
                changed = True
            if not module.check_mode:
                if not exists:
                    obj.create()
                elif changed:
                    obj.modify()
        except Exception:
            module.fail_json(msg=f"Creating/editing user {username} in {container} failed")
        try:
            groups = module.params["groups"]
            if groups:
                filter = f"(&(objectClass=posixGroup)(|(cn={')(cn='.join(groups)})))"
                group_dns = list(ldap_search(filter, attr=["dn"]))
                for dn in group_dns:
                    grp = umc_module_for_edit("groups/group", dn[0])
                    if user_dn not in grp["users"]:
                        grp["users"].append(user_dn)
                        if not module.check_mode:
                            grp.modify()
                        changed = True
        except Exception:
            module.fail_json(msg=f"Adding groups to user {username} failed")

    if state == "absent" and exists:
        try:
            obj = umc_module_for_edit("users/user", user_dn)
            if not module.check_mode:
                obj.remove()
            changed = True
        except Exception:
            module.fail_json(msg=f"Removing user {username} failed")

    module.exit_json(changed=changed, username=username, diff=diff, container=container)


if __name__ == "__main__":
    main()

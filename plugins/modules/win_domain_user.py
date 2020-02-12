#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# this is a windows documentation stub.  actual code lives in the .ps1
# file of the same name

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: win_domain_user
short_description: Manages Windows Active Directory user accounts
description:
     - Manages Windows Active Directory user accounts.
options:
  name:
    description:
      - Name of the user to create, remove or modify.
    type: str
    required: true
  identity:
    description:
      - Identity parameter used to find the User in the Active Directory.
      - This value can be in the forms C(Distinguished Name), C(objectGUID),
        C(objectSid) or C(sAMAccountName).
      - Default to C(name) if not set.
    type: str
  state:
    description:
      - When C(present), creates or updates the user account.
      - When C(absent), removes the user account if it exists.
      - When C(query), retrieves the user account details without making any changes.
    type: str
    choices: [ absent, present, query ]
    default: present
  enabled:
    description:
      - C(yes) will enable the user account.
      - C(no) will disable the account.
    type: bool
    default: yes
  account_locked:
    description:
      - C(no) will unlock the user account if locked.
      - Note that there is not a way to lock an account as an administrator.
      - Accounts are locked due to user actions; as an admin, you may only unlock a locked account.
      - If you wish to administratively disable an account, set I(enabled) to C(no).
    choices: [ no ]
  description:
    description:
      - Description of the user
    type: str
  groups:
    description:
      - Adds or removes the user from this list of groups,
        depending on the value of I(groups_action).
      - To remove all but the Principal Group, set C(groups=<principal group name>) and
        I(groups_action=replace).
      - Note that users cannot be removed from their principal group (for example, "Domain Users").
    type: list
  groups_action:
    description:
      - If C(add), the user is added to each group in I(groups) where not already a member.
      - If C(remove), the user is removed from each group in I(groups).
      - If C(replace), the user is added as a member of each group in
        I(groups) and removed from any other groups.
    type: str
    choices: [ add, remove, replace ]
    default: replace
  password:
    description:
      - Optionally set the user's password to this (plain text) value.
      - To enable an account - I(enabled) - a password must already be
        configured on the account, or you must provide a password here.
    type: str
  update_password:
    description:
      - C(always) will always update passwords.
      - C(on_create) will only set the password for newly created users.
      - C(when_changed) will only set the password when changed (added in ansible 2.9).
    type: str
    choices: [ always, on_create, when_changed ]
    default: always
  password_expired:
    description:
      - C(yes) will require the user to change their password at next login.
      - C(no) will clear the expired password flag.
      - This is mutually exclusive with I(password_never_expires).
    type: bool
  password_never_expires:
    description:
      - C(yes) will set the password to never expire.
      - C(no) will allow the password to expire.
      - This is mutually exclusive with I(password_expired).
    type: bool
  user_cannot_change_password:
    description:
      - C(yes) will prevent the user from changing their password.
      - C(no) will allow the user to change their password.
    type: bool
  firstname:
    description:
      - Configures the user's first name (given name).
    type: str
  surname:
    description:
      - Configures the user's last name (surname).
    type: str
  company:
    description:
      - Configures the user's company name.
    type: str
  upn:
    description:
      - Configures the User Principal Name (UPN) for the account.
      - This is not required, but is best practice to configure for modern
        versions of Active Directory.
      - The format is C(<username>@<domain>).
    type: str
  email:
    description:
      - Configures the user's email address.
      - This is a record in AD and does not do anything to configure any email
        servers or systems.
    type: str
  street:
    description:
      - Configures the user's street address.
    type: str
  city:
    description:
      - Configures the user's city.
    type: str
  state_province:
    description:
      - Configures the user's state or province.
    type: str
  postal_code:
    description:
      - Configures the user's postal code / zip code.
    type: str
  country:
    description:
      - Configures the user's country code.
      - Note that this is a two-character ISO 3166 code.
    type: str
  path:
    description:
      - Container or OU for the new user; if you do not specify this, the
        user will be placed in the default container for users in the domain.
      - Setting the path is only available when a new user is created;
        if you specify a path on an existing user, the user's path will not
        be updated - you must delete (e.g., C(state=absent)) the user and
        then re-add the user with the appropriate path.
    type: str
  attributes:
    description:
      - A dict of custom LDAP attributes to set on the user.
      - This can be used to set custom attributes that are not exposed as module
        parameters, e.g. C(telephoneNumber).
      - See the examples on how to format this parameter.
    type: str
  domain_username:
    description:
    - The username to use when interacting with AD.
    - If this is not set then the user Ansible used to log in with will be
      used instead when using CredSSP or Kerberos with credential delegation.
    type: str
  domain_password:
    description:
    - The password for I(username).
    type: str
  domain_server:
    description:
    - Specifies the Active Directory Domain Services instance to connect to.
    - Can be in the form of an FQDN or NetBIOS name.
    - If not specified then the value is based on the domain of the computer
      running PowerShell.
    type: str
notes:
  - Works with Windows 2012R2 and newer.
  - If running on a server that is not a Domain Controller, credential
    delegation through CredSSP or Kerberos with delegation must be used or the
    I(domain_username), I(domain_password) must be set.
  - Note that some individuals have confirmed successful operation on Windows
    2008R2 servers with AD and AD Web Services enabled, but this has not
    received the same degree of testing as Windows 2012R2.
seealso:
- module: win_domain
- module: win_domain_controller
- module: win_domain_computer
- module: win_domain_group
- module: win_domain_membership
- module: win_user
- module: win_user_profile
author:
    - Nick Chandler (@nwchandler)
'''

EXAMPLES = r'''
- name: Ensure user bob is present with address information
  win_domain_user:
    name: bob
    firstname: Bob
    surname: Smith
    company: BobCo
    password: B0bP4ssw0rd
    state: present
    groups:
      - Domain Admins
    street: 123 4th St.
    city: Sometown
    state_province: IN
    postal_code: 12345
    country: US
    attributes:
      telephoneNumber: 555-123456

- name: Ensure user bob is created and use custom credentials to create the user
  win_domain_user:
    name: bob
    firstname: Bob
    surname: Smith
    password: B0bP4ssw0rd
    state: present
    domain_username: DOMAIN\admin-account
    domain_password: SomePas2w0rd
    domain_server: domain@DOMAIN.COM

- name: Ensure user bob is present in OU ou=test,dc=domain,dc=local
  win_domain_user:
    name: bob
    password: B0bP4ssw0rd
    state: present
    path: ou=test,dc=domain,dc=local
    groups:
      - Domain Admins

- name: Ensure user bob is absent
  win_domain_user:
    name: bob
    state: absent
'''

RETURN = r'''
account_locked:
    description: true if the account is locked
    returned: always
    type: bool
    sample: false
changed:
    description: true if the account changed during execution
    returned: always
    type: bool
    sample: false
city:
    description: The user city
    returned: always
    type: str
    sample: Indianapolis
company:
    description: The user company
    returned: always
    type: str
    sample: RedHat
country:
    description: The user country
    returned: always
    type: str
    sample: US
description:
    description: A description of the account
    returned: always
    type: str
    sample: Server Administrator
distinguished_name:
    description: DN of the user account
    returned: always
    type: str
    sample: CN=nick,OU=test,DC=domain,DC=local
email:
    description: The user email address
    returned: always
    type: str
    sample: nick@domain.local
enabled:
    description: true if the account is enabled and false if disabled
    returned: always
    type: str
    sample: true
firstname:
    description: The user first name
    returned: always
    type: str
    sample: Nick
groups:
    description: AD Groups to which the account belongs
    returned: always
    type: list
    sample: [ "Domain Admins", "Domain Users" ]
msg:
    description: Summary message of whether the user is present or absent
    returned: always
    type: str
    sample: User nick is present
name:
    description: The username on the account
    returned: always
    type: str
    sample: nick
password_expired:
    description: true if the account password has expired
    returned: always
    type: bool
    sample: false
password_updated:
    description: true if the password changed during this execution
    returned: always
    type: bool
    sample: true
postal_code:
    description: The user postal code
    returned: always
    type: str
    sample: 46033
sid:
    description: The SID of the account
    returned: always
    type: str
    sample: S-1-5-21-2752426336-228313920-2202711348-1175
state:
    description: The state of the user account
    returned: always
    type: str
    sample: present
state_province:
    description: The user state or province
    returned: always
    type: str
    sample: IN
street:
    description: The user street address
    returned: always
    type: str
    sample: 123 4th St.
surname:
    description: The user last name
    returned: always
    type: str
    sample: Doe
upn:
    description: The User Principal Name of the account
    returned: always
    type: str
    sample: nick@domain.local
user_cannot_change_password:
    description: true if the user is not allowed to change password
    returned: always
    type: str
    sample: false
created:
  description: Whether a user was created
  returned: always
  type: bool
  sample: true
'''

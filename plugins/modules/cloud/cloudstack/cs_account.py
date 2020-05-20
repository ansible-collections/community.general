#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2015, René Moser <mail@renemoser.net>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: cs_account
short_description: Manages accounts on Apache CloudStack based clouds.
description:
    - Create, disable, lock, enable and remove accounts.
author: René Moser (@resmo)
options:
  name:
    description:
      - Name of account.
    type: str
    required: true
  username:
    description:
      - Username of the user to be created if account did not exist.
      - Required on I(state=present).
    type: str
  password:
    description:
      - Password of the user to be created if account did not exist.
      - Required on I(state=present) if I(ldap_domain) is not set.
    type: str
  first_name:
    description:
      - First name of the user to be created if account did not exist.
      - Required on I(state=present) if I(ldap_domain) is not set.
    type: str
  last_name:
    description:
      - Last name of the user to be created if account did not exist.
      - Required on I(state=present) if I(ldap_domain) is not set.
    type: str
  email:
    description:
      - Email of the user to be created if account did not exist.
      - Required on I(state=present) if I(ldap_domain) is not set.
    type: str
  timezone:
    description:
      - Timezone of the user to be created if account did not exist.
    type: str
  network_domain:
    description:
      - Network domain of the account.
    type: str
  account_type:
    description:
      - Type of the account.
    type: str
    choices: [ user, root_admin, domain_admin ]
    default: user
  domain:
    description:
      - Domain the account is related to.
    type: str
    default: ROOT
  role:
    description:
      - Creates the account under the specified role name or id.
    type: str
  ldap_domain:
    description:
      - Name of the LDAP group or OU to bind.
      - If set, account will be linked to LDAP.
    type: str
  ldap_type:
    description:
      - Type of the ldap name. GROUP or OU, defaults to GROUP.
    type: str
    choices: [ GROUP, OU ]
    default: GROUP
  state:
    description:
      - State of the account.
      - C(unlocked) is an alias for C(enabled).
    type: str
    choices: [ present, absent, enabled, disabled, locked, unlocked ]
    default: present
  poll_async:
    description:
      - Poll async jobs until job has finished.
    type: bool
    default: yes
extends_documentation_fragment:
- community.general.cloudstack

'''

EXAMPLES = '''
- name: create an account in domain 'CUSTOMERS'
  cs_account:
    name: customer_xy
    username: customer_xy
    password: S3Cur3
    last_name: Doe
    first_name: John
    email: john.doe@example.com
    domain: CUSTOMERS
    role: Domain Admin
  delegate_to: localhost

- name: Lock an existing account in domain 'CUSTOMERS'
  cs_account:
    name: customer_xy
    domain: CUSTOMERS
    state: locked
  delegate_to: localhost

- name: Disable an existing account in domain 'CUSTOMERS'
  cs_account:
    name: customer_xy
    domain: CUSTOMERS
    state: disabled
  delegate_to: localhost

- name: Enable an existing account in domain 'CUSTOMERS'
  cs_account:
    name: customer_xy
    domain: CUSTOMERS
    state: enabled
  delegate_to: localhost

- name: Remove an account in domain 'CUSTOMERS'
  cs_account:
    name: customer_xy
    domain: CUSTOMERS
    state: absent
  delegate_to: localhost

- name: Create a single user LDAP account in domain 'CUSTOMERS'
  cs_account:
    name: customer_xy
    username: customer_xy
    domain: CUSTOMERS
    ldap_domain: cn=customer_xy,cn=team_xy,ou=People,dc=domain,dc=local
  delegate_to: localhost

- name: Create a LDAP account in domain 'CUSTOMERS' and bind it to a LDAP group
  cs_account:
    name: team_xy
    username: customer_xy
    domain: CUSTOMERS
    ldap_domain: cn=team_xy,ou=People,dc=domain,dc=local
  delegate_to: localhost
'''

RETURN = '''
---
id:
  description: UUID of the account.
  returned: success
  type: str
  sample: 87b1e0ce-4e01-11e4-bb66-0050569e64b8
name:
  description: Name of the account.
  returned: success
  type: str
  sample: linus@example.com
account_type:
  description: Type of the account.
  returned: success
  type: str
  sample: user
state:
  description: State of the account.
  returned: success
  type: str
  sample: enabled
network_domain:
  description: Network domain of the account.
  returned: success
  type: str
  sample: example.local
domain:
  description: Domain the account is related.
  returned: success
  type: str
  sample: ROOT
role:
  description: The role name of the account
  returned: success
  type: str
  sample: Domain Admin
'''

# import cloudstack common
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.cloudstack import (
    AnsibleCloudStack,
    cs_argument_spec,
    cs_required_together
)


class AnsibleCloudStackAccount(AnsibleCloudStack):

    def __init__(self, module):
        super(AnsibleCloudStackAccount, self).__init__(module)
        self.returns = {
            'networkdomain': 'network_domain',
            'rolename': 'role',
        }
        self.account = None
        self.account_types = {
            'user': 0,
            'root_admin': 1,
            'domain_admin': 2,
        }

    def get_role_id(self):
        role_param = self.module.params.get('role')
        role_id = None

        if role_param:
            role_list = self.query_api('listRoles')
            for role in role_list['role']:
                if role_param in [role['name'], role['id']]:
                    role_id = role['id']

            if not role_id:
                self.module.fail_json(msg="Role not found: %s" % role_param)

        return role_id

    def get_account_type(self):
        account_type = self.module.params.get('account_type')
        return self.account_types[account_type]

    def get_account(self):
        if not self.account:
            args = {
                'listall': True,
                'domainid': self.get_domain(key='id'),
                'fetch_list': True,
            }
            accounts = self.query_api('listAccounts', **args)
            if accounts:
                account_name = self.module.params.get('name')
                for a in accounts:
                    if account_name == a['name']:
                        self.account = a
                        break

        return self.account

    def enable_account(self):
        account = self.get_account()
        if not account:
            account = self.present_account()

        if account['state'].lower() != 'enabled':
            self.result['changed'] = True
            args = {
                'id': account['id'],
                'account': self.module.params.get('name'),
                'domainid': self.get_domain(key='id')
            }
            if not self.module.check_mode:
                res = self.query_api('enableAccount', **args)
                account = res['account']
        return account

    def lock_account(self):
        return self.lock_or_disable_account(lock=True)

    def disable_account(self):
        return self.lock_or_disable_account()

    def lock_or_disable_account(self, lock=False):
        account = self.get_account()
        if not account:
            account = self.present_account()

        # we need to enable the account to lock it.
        if lock and account['state'].lower() == 'disabled':
            account = self.enable_account()

        if (lock and account['state'].lower() != 'locked' or
                not lock and account['state'].lower() != 'disabled'):
            self.result['changed'] = True
            args = {
                'id': account['id'],
                'account': self.module.params.get('name'),
                'domainid': self.get_domain(key='id'),
                'lock': lock,
            }
            if not self.module.check_mode:
                account = self.query_api('disableAccount', **args)

                poll_async = self.module.params.get('poll_async')
                if poll_async:
                    account = self.poll_job(account, 'account')
        return account

    def present_account(self):
        account = self.get_account()

        if not account:
            self.result['changed'] = True

            if self.module.params.get('ldap_domain'):
                required_params = [
                    'domain',
                    'username',
                ]
                self.module.fail_on_missing_params(required_params=required_params)

                account = self.create_ldap_account(account)

            else:
                required_params = [
                    'email',
                    'username',
                    'password',
                    'first_name',
                    'last_name',
                ]
                self.module.fail_on_missing_params(required_params=required_params)

                account = self.create_account(account)

        return account

    def create_ldap_account(self, account):
        args = {
            'account': self.module.params.get('name'),
            'domainid': self.get_domain(key='id'),
            'accounttype': self.get_account_type(),
            'networkdomain': self.module.params.get('network_domain'),
            'username': self.module.params.get('username'),
            'timezone': self.module.params.get('timezone'),
            'roleid': self.get_role_id()
        }
        if not self.module.check_mode:
            res = self.query_api('ldapCreateAccount', **args)
            account = res['account']

            args = {
                'account': self.module.params.get('name'),
                'domainid': self.get_domain(key='id'),
                'accounttype': self.get_account_type(),
                'ldapdomain': self.module.params.get('ldap_domain'),
                'type': self.module.params.get('ldap_type')
            }

            self.query_api('linkAccountToLdap', **args)

        return account

    def create_account(self, account):
        args = {
            'account': self.module.params.get('name'),
            'domainid': self.get_domain(key='id'),
            'accounttype': self.get_account_type(),
            'networkdomain': self.module.params.get('network_domain'),
            'username': self.module.params.get('username'),
            'password': self.module.params.get('password'),
            'firstname': self.module.params.get('first_name'),
            'lastname': self.module.params.get('last_name'),
            'email': self.module.params.get('email'),
            'timezone': self.module.params.get('timezone'),
            'roleid': self.get_role_id()
        }
        if not self.module.check_mode:
            res = self.query_api('createAccount', **args)
            account = res['account']

        return account

    def absent_account(self):
        account = self.get_account()
        if account:
            self.result['changed'] = True

            if not self.module.check_mode:
                res = self.query_api('deleteAccount', id=account['id'])

                poll_async = self.module.params.get('poll_async')
                if poll_async:
                    self.poll_job(res, 'account')
        return account

    def get_result(self, account):
        super(AnsibleCloudStackAccount, self).get_result(account)
        if account:
            if 'accounttype' in account:
                for key, value in self.account_types.items():
                    if value == account['accounttype']:
                        self.result['account_type'] = key
                        break
        return self.result


def main():
    argument_spec = cs_argument_spec()
    argument_spec.update(dict(
        name=dict(required=True),
        state=dict(choices=['present', 'absent', 'enabled', 'disabled', 'locked', 'unlocked'], default='present'),
        account_type=dict(choices=['user', 'root_admin', 'domain_admin'], default='user'),
        network_domain=dict(),
        domain=dict(default='ROOT'),
        email=dict(),
        first_name=dict(),
        last_name=dict(),
        username=dict(),
        password=dict(no_log=True),
        timezone=dict(),
        role=dict(),
        ldap_domain=dict(),
        ldap_type=dict(choices=['GROUP', 'OU'], default='GROUP'),
        poll_async=dict(type='bool', default=True),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_together=cs_required_together(),
        supports_check_mode=True
    )

    acs_acc = AnsibleCloudStackAccount(module)

    state = module.params.get('state')

    if state in ['absent']:
        account = acs_acc.absent_account()

    elif state in ['enabled', 'unlocked']:
        account = acs_acc.enable_account()

    elif state in ['disabled']:
        account = acs_acc.disable_account()

    elif state in ['locked']:
        account = acs_acc.lock_account()

    else:
        account = acs_acc.present_account()

    result = acs_acc.get_result(account)

    module.exit_json(**result)


if __name__ == '__main__':
    main()

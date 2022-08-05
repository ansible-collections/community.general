#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013, Peter Sprygada <sprygada@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: ejabberd_user
author: "Peter Sprygada (@privateip)"
short_description: Manages users for ejabberd servers
requirements:
    - ejabberd with mod_admin_extra
description:
    - This module provides user management for ejabberd servers
options:
    username:
        type: str
        description:
            - the name of the user to manage
        required: true
    host:
        type: str
        description:
            - the ejabberd host associated with this username
        required: true
    password:
        type: str
        description:
            - the password to assign to the username
        required: false
    logging:
        description:
            - enables or disables the local syslog facility for this module
        required: false
        default: false
        type: bool
    state:
        type: str
        description:
            - describe the desired state of the user to be managed
        required: false
        default: 'present'
        choices: [ 'present', 'absent' ]
notes:
    - Password parameter is required for state == present only
    - Passwords must be stored in clear text for this release
    - The ejabberd configuration file must include mod_admin_extra as a module.
'''
EXAMPLES = '''
# Example playbook entries using the ejabberd_user module to manage users state.

- name: Create a user if it does not exist
  community.general.ejabberd_user:
    username: test
    host: server
    password: password

- name: Delete a user if it exists
  community.general.ejabberd_user:
    username: test
    host: server
    state: absent
'''

import syslog

from ansible.module_utils.basic import AnsibleModule


class EjabberdUser(object):
    """ This object represents a user resource for an ejabberd server.   The
    object manages user creation and deletion using ejabberdctl.  The following
    commands are currently supported:
        * ejabberdctl register
        * ejabberdctl deregister
    """

    def __init__(self, module):
        self.module = module
        self.logging = module.params.get('logging')
        self.state = module.params.get('state')
        self.host = module.params.get('host')
        self.user = module.params.get('username')
        self.pwd = module.params.get('password')

    @property
    def changed(self):
        """ This method will check the current user and see if the password has
        changed.   It will return True if the user does not match the supplied
        credentials and False if it does not
        """
        return self.run_command('check_password', [self.user, self.host, self.pwd])

    @property
    def exists(self):
        """ This method will check to see if the supplied username exists for
        host specified.  If the user exists True is returned, otherwise False
        is returned
        """
        return self.run_command('check_account', [self.user, self.host])

    def log(self, entry):
        """ This method will log information to the local syslog facility """
        if self.logging:
            syslog.openlog('ansible-%s' % self.module._name)
            syslog.syslog(syslog.LOG_NOTICE, entry)

    def run_command(self, cmd, options):
        """ This method will run the any command specified and return the
        returns using the Ansible common module
        """
        cmd = [self.module.get_bin_path('ejabberdctl'), cmd] + options
        self.log('command: %s' % " ".join(cmd))
        return self.module.run_command(cmd)

    def update(self):
        """ The update method will update the credentials for the user provided
        """
        return self.run_command('change_password', [self.user, self.host, self.pwd])

    def create(self):
        """ The create method will create a new user on the host with the
        password provided
        """
        return self.run_command('register', [self.user, self.host, self.pwd])

    def delete(self):
        """ The delete method will delete the user from the host
        """
        return self.run_command('unregister', [self.user, self.host])


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True, type='str'),
            username=dict(required=True, type='str'),
            password=dict(type='str', no_log=True),
            state=dict(default='present', choices=['present', 'absent']),
            logging=dict(default=False, type='bool')  # deprecate in favour of c.g.syslogger?
        ),
        required_if=[
            ('state', 'present', ['password']),
        ],
        supports_check_mode=True,
    )

    obj = EjabberdUser(module)

    rc = None
    result = dict(changed=False)

    if obj.state == 'absent':
        if obj.exists:
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = obj.delete()
            if rc != 0:
                module.fail_json(msg=err, rc=rc)

    elif obj.state == 'present':
        if not obj.exists:
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = obj.create()
        elif obj.changed:
            if module.check_mode:
                module.exit_json(changed=True)
            (rc, out, err) = obj.update()
        if rc is not None and rc != 0:
            module.fail_json(msg=err, rc=rc)

    if rc is None:
        result['changed'] = False
    else:
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()

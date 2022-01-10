#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2022, James Livulpi
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
module: homectl
short_description: Manage user accounts with systemd-homed
author:
    - James Livulpi
description:
    - Manages a user's home directory managed by systemd-homed
options:
    name:
        description:
            - The user name to create, remove, or modify.
        type: str
        required: true
        aliases: [ user, username ]
    password:
        description:
            - Set the user's password to this.
            - Homed requires this value has to be cleartext on account creation. Beware of security issues.
            - See here https://systemd.io/USER_RECORD/
            - password → an array of strings, each containing a plain text password.
        type: str
    state:
        description:
            - Whether the account should exist or not, taking action if the state is different from what is stated.
        type: str
        choices: [ absent, present ]
        default: present
    storage:
         description:
            - Indicates the storage mechanism for the user’s home directory.
        choices: [ 'classic', 'luks', 'directory', 'subvolume', 'fscrypt', 'cifs']
        default: classic
        type: str
    disksize:
        description:
            - The intended home directory disk space.
            - Human readable value such as 10G, 10M, 10B, etc
        type: str
    realname:
        description:
            - The user’s real (“human”) name.
        type: str
    realm:
        description:
            - The “realm” a user is defined in.
        type: str
    email:
        description:
            - The email address of the user.
        type: str
    location:
        description:
            -  A free-form location string describing the location of the user.
        type: str
    iconname:
        description:
            - The name of an icon picked by the user, for example for the purpose of an avatar.
            - Should follow the semantics defined in the Icon Naming Specification.
            - https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
    homedir:
        description:
            - Absolute file system path to the home directory.
        type: path
    uid:
        description:
            -  Sets the I(UID) of the user.
        type: int
    gid:
        description:
            - Sets the I(GID) of the user.
        type: int
    umask:
        description:
            - Sets the umask for the user’s login sessions.
            - ex: 0000..0777
        type: int
    member:
        description:
            - String separated by comma each indicating a UNIX group this user shall be a member of.
        type: list
        elements: str
    shell:
        description:
            - Shell binary to use for terminal logins of given user.
        type: str
        default: /bin/bash
    environment:
        description:
            - String separated by comma each containing an environment variable and its value to set for the user’s login session, in a format compatible with I(putenv()).
            - Any environment variable listed here is automatically set by pam_systemd for all login sessions of the user.
    timezone:
        description:
            - Preferred timezone to use for the user.
            - Should be a tzdata compatible location string,
            - ex: America/New_York

    #TODO
'''

EXAMPLES = r'''#TODO'''

RETURN = r'''#TODO'''

import crypt
from dateutil import tz


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import jsonify
from ansible.module_utils.common.text.formatters import human_to_bytes


class Homectl(object):
    '''#TODO DOC STRINGS'''

    def __init__(self, module):
        self.module = module
        self.state = module.params['state']
        self.name = module.params['name']
        self.password = module.params['password']
        self.storage = module.params['storage']
        self.disksize = module.params['disksize']
        self.realname = module.params['realname']
        self.realm = module.params['realm']
        self.email = module.params['email']
        self.location = module.params['location']
        self.iconname = module.params['iconname']
        self.homedir = module.params['homedir']
        self.uid = module.params['uid']
        self.gid = module.params['gid']
        self.umask = module.params['umask']
        self.member = module.params['member']
        self.shell = module.params['shell']
        self.environment = module.params['environment']
        self.timezone = module.params['timezone']

    # Cannot run homectl commands if service is not active
    def homed_service_active(self):
        active = True
        cmd = "systemctl show systemd-homed.service -p ActiveState"
        rc, show_service_stdout, stderr = self.module.run_command(cmd, use_unsafe_shell=True)
        if rc == 0:
            state = show_service_stdout.rsplit("=")[1]
            if state != "active":
                active = False
        return active

    def user_exists(self):
        # Get user properties if they exist in json
        # TODO can be used to query later on in a dict for updating record.
        exists = False
        cmd = "homectl inspect %s -j" % self.name
        rc, stdout, stderr = self.module.run_command(cmd, use_unsafe_shell=True)
        if rc == 0:
            exists = True
        return exists

    # Build up dictionary to jsonify for homectl commands.
    def create_json_record(self):
        record = {}
        record["userName"] = self.name
        record['secret'] = {'password': [self.password]}
        password_hash = self._hash_password(self.password)
        record['privileged'] = {'hashedPassword': [password_hash]}

        if self.uid:
            record['uid'] = self.uid

        if self.gid:
            record['gid'] = self.gid
        if self.member:
            record['memberOf'] = [s for s in self.member.split(",")]

        if self.realname:
            record['realName'] = self.realname

        if self.storage:
            record['storage'] = self.storage

        if self.homedir:
            record['homeDirectory'] = self.homedir

        if self.disksize:
            # convert humand readble to bytes
            record['diskSize'] = human_to_bytes(self.disksize)

        if self.realm:
            record['realm'] = self.realm

        if self.email:
            record['emailAddress'] = self.email

        if self.location:
            record['location'] = self.location

        if self.iconname:
            record['iconName'] = self.iconname

        if self.shell:
            record['shell'] = self.shell

        if self.umask:
            record['umask'] = self.umask

        if self.environment:
            record['environment'] = [s for s in self.environment.split(",")]

        if self.timezone:
            # Verify its in proper TZ format e.g., America/New_York, Europe/Amsterdam, etc.
            if tz.gettz(self.timezone):
                record['timeZone'] = self.timezone
            else:
                self.module.fail_json(msg="timezone is not fomatted correctly!")

        return jsonify(record)

    def create_user(self):
        record = self.create_json_record()
        cmd = [self.module.get_bin_path('homectl', True)]
        cmd.append("create")
        cmd.append("--identity=-") #read the user record from standard input.
        return(self.module.run_command(cmd, data=record, use_unsafe_shell=True))

    def _hash_password(self, password):
        #TODO handle errors etc.
        return(crypt.crypt(password))

    def remove_user(self):
        cmd = [self.module.get_bin_path('homectl', True)]
        cmd.append('remove')
        cmd.append(self.name)
        return(self.module.run_command(cmd, use_unsafe_shell=True))

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['absent', 'present']),
            name=dict(type='str', required=True, aliases=['user', 'username']),
            password=dict(type='str', no_log=True, required=True),
            storage=dict(type='str'),
            disksize=dict(type='str'),
            realname=dict(type='str', aliases=['real_name']),
            realm=dict(type='str'),
            email=dict(type='str'),
            location=dict(type='str'),
            iconname=dict(type='str'),
            homedir=dict(type='path'),
            uid=dict(type='int'),
            gid=dict(type='int'),
            umask=dict(type='int'),
            environment=dict(type='list', elements='str'),
            timezone=dict(type='str'),
            member=dict(type='str'),
            shell=dict(type='str'),
        ),
        supports_check_mode=True,
    )

    homectl = Homectl(module)
    rc = None
    result = {}
    result['name'] = homectl.name
    result['state'] = homectl.state

    # First we need to make sure homed service is active
    if not homectl.homed_service_active():
        module.fail_json(msg="systemd-homed.service is not active")

    # handle removing user
    if homectl.state == 'absent':
        if homectl.user_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            rc, stdout, stderr = homectl.remove_user()
            if rc != 0:
                module.fail_json(name=homectl.name, msg=stderr, rc=rc)
            result['changed'] = True
            result['msg'] = "User %s removed!" % homectl.name
        else:
            result['msg'] = "User Doesn't Exist!"
            result['changed'] = False

    # Handle adding a user
    if homectl.state == 'present':
        if not homectl.user_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            rc, stdout, stderr = homectl.create_user()
            if rc != 0:
                module.fail_json(name=homectl.name, msg=stderr, rc=rc)
            result['changed'] = True
            result['msg'] = "User %s created!" % homectl.name
        else:
            result['msg'] = "User already Exists!"
            result['changed'] = False

    module.exit_json(**result)

if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2022, James Livulpi
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: homectl
author:
    - "James Livulpi (@jameslivulpi)"
short_description: Manage user accounts with systemd-homed
version_added: 4.4.0
description:
    - Manages a user's home directory managed by systemd-homed.
options:
    name:
        description:
            - The user name to create, remove, or modify.
        required: true
        aliases: [ 'user', 'username' ]
        type: str
    password:
        description:
            - Set the user's password to this.
            - Homed requires this value to be in cleartext on user creation and updating a user.
            - The module takes the password and generates a password hash in SHA-512 with 10000 rounds of salt generation using crypt.
            - See U(https://systemd.io/USER_RECORD/).
            - This is required for I(state=present) and I(state=modify).
        type: str
    state:
        description:
            - The operation to take on the user such as remove, add user, and modify user.
        choices: [ 'absent', 'present', 'modify' ]
        default: present
        type: str
    storage:
        description:
            - Indicates the storage mechanism for the user's home directory.
            - If the storage type is not specified, ``homed.conf(5)`` defines which default storage to use.
        choices: [ 'classic', 'luks', 'directory', 'subvolume', 'fscrypt', 'cifs' ]
        type: str
    disksize:
        description:
            - The intended home directory disk space.
            - Human readable value such as 10G, 10M, 10B, etc
        type: str
    resize:
        description:
            - When used with I(disksize) this will attempt to resize the home directory immediately.
        default: false
        type: bool
    realname:
        description:
            - The user's real ('human') name.
        aliases: [ 'real_name' ]
        type: str
    realm:
        description:
            - The 'realm' a user is defined in.
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
            - See U(https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html) for specifics.
        type: str
    homedir:
        description:
            - Path to use as home directory for the user.
            - This is the directory the user's home directory is mounted to while the user is logged in.
                - This is not where the user's data is actually stored, see I(imagepath) for that.
        type: path
    imagepath:
        description:
            - Path to place the user's home directory.
            - See U(https://www.freedesktop.org/software/systemd/man/homectl.html#--image-path=PATH) for more information.
        type: path
    uid:
        description:
            - Sets the uid of the user.
            - If using I(gid) homed requires the value to be the same
        type: int
    gid:
        description:
            - Sets the gid of the user.
            - If using I(uid) homed requires the value to be the same
        type: int
    umask:
        description:
            - Sets the umask for the user's login sessions
            - Value from C(0000) to C(0777).
        type: int
    member:
        description:
            - String separated by comma each indicating a UNIX group this user shall be a member of.
            - Groups the user should be a member of should be supplied as comma separated list.
        aliases: [ 'memberof' ]
        type: str
    shell:
        description:
            - Shell binary to use for terminal logins of given user.
            - If not specified homed by default uses ``/bin/bash``
        type: str
    environment:
        description:
            - String separated by comma each containing an environment variable and its value to
              set for the user's login session, in a format compatible with ``putenv()``.
            - Any environment variable listed here is automatically set by pam_systemd for all
              login sessions of the user.
        type: str
    timezone:
        description:
            - Preferred timezone to use for the user.
            - Should be a tzdata compatible location string such as C(America/New_York).
        type: str
    locked:
        description:
            - Whether the user account should be locked or not.
        type: bool
'''

EXAMPLES = '''
- name: Add the user 'james'
  community.general.homectl:
    name: johnd
    password: myreallysecurepassword1!
    state: present

- name: Add the user 'tom' with a zsh shell, uid of 1000, and gid of 2000
  community.general.homectl:
    name: tom
    password: myreallysecurepassword1!
    state: present
    shell: /bin/zsh
    uid: 1000
    gid: 1000

- name: Modify an existing user 'frank' to have 10G of diskspace and resize usage now
  community.general.homectl:
    name: frank
    password: myreallysecurepassword1!
    state: modify
    disksize: 10G
    resize: yes

- name: Remove an existing user 'tom'
  community.general.homectl:
    name: frank
    state: absent
'''

RETURN = '''
data:
    description: A json dictionary returned from C(homectl inspect -j)
    returned: success
    type: dict
    sample: {
        "data": {
            "binding": {
                "e9ed2a5b0033427286b228e97c1e8343": {
                    "fileSystemType": "btrfs",
                    "fileSystemUuid": "7bd59491-2812-4642-a492-220c3f0c6c0b",
                    "gid": 60268,
                    "imagePath": "/home/james.home",
                    "luksCipher": "aes",
                    "luksCipherMode": "xts-plain64",
                    "luksUuid": "7f05825a-2c38-47b4-90e1-f21540a35a81",
                    "luksVolumeKeySize": 32,
                    "partitionUuid": "5a906126-d3c8-4234-b230-8f6e9b427b2f",
                    "storage": "luks",
                    "uid": 60268
                }
            },
            "diskSize": 3221225472,
            "disposition": "regular",
            "lastChangeUSec": 1641941238208691,
            "lastPasswordChangeUSec": 1641941238208691,
            "privileged": {
                "hashedPassword": [
                    "$6$ov9AKni.trf76inT$tTtfSyHgbPTdUsG0CvSSQZXGqFGdHKQ9Pb6e0BTZhDmlgrL/vA5BxrXduBi8u/PCBiYUffGLIkGhApjKMK3bV."
                ]
            },
            "signature": [
                {
                    "data": "o6zVFbymcmk4YTVaY6KPQK23YCp+VkXdGEeniZeV1pzIbFzoaZBvVLPkNKMoPAQbodY5BYfBtuy41prNL78qAg==",
                    "key": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAbs7ELeiEYBxkUQhxZ+5NGyu6J7gTtZtZ5vmIw3jowcY=\n-----END PUBLIC KEY-----\n"
                }
            ],
            "status": {
                "e9ed2a5b0033427286b228e97c1e8343": {
                    "diskCeiling": 21845405696,
                    "diskFloor": 268435456,
                    "diskSize": 3221225472,
                    "service": "io.systemd.Home",
                    "signedLocally": true,
                    "state": "inactive"
                }
             },
            "userName": "james",
        }
    }
'''

import crypt
import json
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
        self.resize = module.params['resize']
        self.realname = module.params['realname']
        self.realm = module.params['realm']
        self.email = module.params['email']
        self.location = module.params['location']
        self.iconname = module.params['iconname']
        self.homedir = module.params['homedir']
        self.imagepath = module.params['imagepath']
        self.uid = module.params['uid']
        self.gid = module.params['gid']
        self.umask = module.params['umask']
        self.member = module.params['member']
        self.shell = module.params['shell']
        self.environment = module.params['environment']
        self.timezone = module.params['timezone']
        self.locked = module.params['locked']

    # Cannot run homectl commands if service is not active
    def homed_service_active(self):
        is_active = True
        cmd = ["systemctl", "show", "systemd-homed.service", "-p", "ActiveState"]
        rc, show_service_stdout, stderr = self.module.run_command(cmd)
        if rc == 0:
            state = show_service_stdout.rsplit("=")[1]
            if state.strip() != "active":
                is_active = False
        return is_active

    def user_exists(self):
        # Get user properties if they exist in json
        # TODO can be used to query later on in a dict for updating record.
        exists = False
        cmd = [self.module.get_bin_path('homectl', True)]
        cmd.append("inspect")
        cmd.append(self.name)
        cmd.append("-j")
        rc, stdout, stderr = self.module.run_command(cmd, use_unsafe_shell=True)
        if rc == 0:
            exists = True
        return exists

    def create_user(self):
        record = self.create_json_record()
        cmd = [self.module.get_bin_path('homectl', True)]
        cmd.append("create")
        cmd.append("--identity=-")  # Read the user record from standard input.
        return(self.module.run_command(cmd, data=record, use_unsafe_shell=True))

    def _hash_password(self, password):
        method = crypt.METHOD_SHA512
        salt = crypt.mksalt(method, rounds=10000)
        pw_hash = crypt.crypt(password, salt)
        return pw_hash

    def remove_user(self):
        cmd = [self.module.get_bin_path('homectl', True)]
        cmd.append('remove')
        cmd.append(self.name)
        return(self.module.run_command(cmd, use_unsafe_shell=True))

    def modify_user(self):
        record = self.create_json_record()
        cmd = [self.module.get_bin_path('homectl', True)]
        cmd.append('update')
        cmd.append(self.name)
        cmd.append('--identity=-')  # Read the user record from standard input.
        # Resize disksize now resize = true
        # This is not valid in user record (json) and requires it to be passed on command.
        if self.disksize and self.resize:
            cmd.append('--and-resize')
            cmd.append('true')
        return(self.module.run_command(cmd, data=record, use_unsafe_shell=True))

    def get_user_metadata(self):
        cmd = [self.module.get_bin_path('homectl', True)]
        cmd.append("inspect")
        cmd.append(self.name)
        cmd.append("-j")
        cmd.append("--no-pager")
        rc, stdout, stderr = self.module.run_command(cmd)
        return stdout

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
            record['memberOf'] = list(self.member.split(','))

        if self.realname:
            record['realName'] = self.realname

        if self.storage:
            record['storage'] = self.storage

        if self.homedir:
            record['homeDirectory'] = self.homedir

        if self.imagepath:
            record['imagePath'] = self.imagepath

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
            record['environment'] = list(self.environment.split(','))

        if self.timezone:
            record['timeZone'] = self.timezone

        if self.locked:
            record['locked'] = self.locked

        return jsonify(record)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['absent', 'present', 'modify']),
            name=dict(type='str', required=True, aliases=['user', 'username']),
            password=dict(type='str', no_log=True),
            storage=dict(type='str', choices=['classic', 'luks', 'directory', 'subvolume', 'fscrypt', 'cifs']),
            disksize=dict(type='str'),
            resize=dict(type='bool', default=False),
            realname=dict(type='str', aliases=['real_name']),
            realm=dict(type='str'),
            email=dict(type='str'),
            location=dict(type='str'),
            iconname=dict(type='str'),
            homedir=dict(type='path'),
            imagepath=dict(type='path'),
            uid=dict(type='int'),
            gid=dict(type='int'),
            umask=dict(type='int'),
            environment=dict(type='str'),
            timezone=dict(type='str'),
            member=dict(type='str', aliases=['memberof']),
            shell=dict(type='str'),
            locked=dict(type='bool')
        ),
        supports_check_mode=True,

        required_if=[
            ('state', 'modify', ['password']),
            ('state', 'present', ['password']),
            ('resize', True, ['disksize']),
        ]
    )

    homectl = Homectl(module)
    rc = None
    result = {}
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
            result['rc'] = rc
            result['msg'] = "User %s removed!" % homectl.name
        else:
            result['changed'] = False
            result['rc'] = rc
            result['msg'] = "User Doesn't Exist!"

    # Handle adding a user
    if homectl.state == 'present':
        if not homectl.user_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            rc, stdout, stderr = homectl.create_user()
            if rc != 0:
                module.fail_json(name=homectl.name, msg=stderr, rc=rc)
            user_metadata = json.loads(homectl.get_user_metadata())
            result['data'] = user_metadata
            result['rc'] = rc
            result['changed'] = True
            result['msg'] = "User %s created!" % homectl.name
        else:
            user_metadata = json.loads(homectl.get_user_metadata())
            result['data'] = user_metadata
            result['changed'] = False
            result['msg'] = "User already Exists!"

    # Modifying a user if exists
    if homectl.state == 'modify':
        if homectl.user_exists():
            if module.check_mode:
                module.exit_json(changed=True)
            rc, stdout, stderr = homectl.modify_user()
            if rc != 0:
                module.fail_json(name=homectl.name, msg=stderr, rc=rc)
            user_metadata = json.loads(homectl.get_user_metadata())
            result['data'] = user_metadata
            result['changed'] = True
            result['rc'] = rc
            result['msg'] = "User %s modified" % homectl.name
        else:
            result['changed'] = False
            result['rc'] = rc
            result['msg'] = "User doesn't exist!"

    module.exit_json(**result)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022, James Livulpi
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

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
notes:
    - This module does B(not) work with Python 3.13 or newer. It uses the deprecated L(crypt Python module,
      https://docs.python.org/3.12/library/crypt.html) from the Python standard library, which was removed
      from Python 3.13.
requirements:
    - Python 3.12 or earlier
extends_documentation_fragment:
    - community.general.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    name:
        description:
            - The user name to create, remove, or update.
        required: true
        aliases: [ 'user', 'username' ]
        type: str
    password:
        description:
            - Set the user's password to this.
            - Homed requires this value to be in cleartext on user creation and updating a user.
            - The module takes the password and generates a password hash in SHA-512 with 10000 rounds of salt generation using crypt.
            - See U(https://systemd.io/USER_RECORD/).
            - This is required for O(state=present). When an existing user is updated this is checked against the stored hash in homed.
        type: str
    state:
        description:
            - The operation to take on the user.
        choices: [ 'absent', 'present' ]
        default: present
        type: str
    storage:
        description:
            - Indicates the storage mechanism for the user's home directory.
            - If the storage type is not specified, ``homed.conf(5)`` defines which default storage to use.
            - Only used when a user is first created.
        choices: [ 'classic', 'luks', 'directory', 'subvolume', 'fscrypt', 'cifs' ]
        type: str
    disksize:
        description:
            - The intended home directory disk space.
            - Human readable value such as V(10G), V(10M), or V(10B).
        type: str
    resize:
        description:
            - When used with O(disksize) this will attempt to resize the home directory immediately.
        default: false
        type: bool
    realname:
        description:
            - The user's real ('human') name.
            - This can also be used to add a comment to maintain compatibility with C(useradd).
        aliases: [ 'comment' ]
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
            - This is not where the user's data is actually stored, see O(imagepath) for that.
            - Only used when a user is first created.
        type: path
    imagepath:
        description:
            - Path to place the user's home directory.
            - See U(https://www.freedesktop.org/software/systemd/man/homectl.html#--image-path=PATH) for more information.
            - Only used when a user is first created.
        type: path
    uid:
        description:
            - Sets the UID of the user.
            - If using O(gid) homed requires the value to be the same.
            - Only used when a user is first created.
        type: int
    gid:
        description:
            - Sets the gid of the user.
            - If using O(uid) homed requires the value to be the same.
            - Only used when a user is first created.
        type: int
    mountopts:
        description:
            - String separated by comma each indicating mount options for a users home directory.
            - Valid options are V(nosuid), V(nodev) or V(noexec).
            - Homed by default uses V(nodev) and V(nosuid) while V(noexec) is off.
        type: str
    umask:
        description:
            - Sets the umask for the user's login sessions
            - Value from V(0000) to V(0777).
        type: int
    memberof:
        description:
            - String separated by comma each indicating a UNIX group this user shall be a member of.
            - Groups the user should be a member of should be supplied as comma separated list.
        aliases: [ 'groups' ]
        type: str
    skeleton:
        description:
            - The absolute path to the skeleton directory to populate a new home directory from.
            - This is only used when a home directory is first created.
            - If not specified homed by default uses V(/etc/skel).
        aliases: [ 'skel' ]
        type: path
    shell:
        description:
            - Shell binary to use for terminal logins of given user.
            - If not specified homed by default uses V(/bin/bash).
        type: str
    environment:
        description:
            - String separated by comma each containing an environment variable and its value to
              set for the user's login session, in a format compatible with ``putenv()``.
            - Any environment variable listed here is automatically set by pam_systemd for all
              login sessions of the user.
        aliases: [ 'setenv' ]
        type: str
    timezone:
        description:
            - Preferred timezone to use for the user.
            - Should be a tzdata compatible location string such as V(America/New_York).
        type: str
    locked:
        description:
            - Whether the user account should be locked or not.
        type: bool
    language:
        description:
            - The preferred language/locale for the user.
            - This should be in a format compatible with the E(LANG) environment variable.
        type: str
    passwordhint:
        description:
            - Password hint for the given user.
        type: str
    sshkeys:
        description:
            - String separated by comma each listing a SSH public key that is authorized to access the account.
            - The keys should follow the same format as the lines in a traditional C(~/.ssh/authorized_key) file.
        type: str
    notbefore:
        description:
            - A time since the UNIX epoch before which the record should be considered invalid for the purpose of logging in.
        type: int
    notafter:
        description:
            - A time since the UNIX epoch after which the record should be considered invalid for the purpose of logging in.
        type: int
'''

EXAMPLES = '''
- name: Add the user 'james'
  community.general.homectl:
    name: johnd
    password: myreallysecurepassword1!
    state: present

- name: Add the user 'alice' with a zsh shell, uid of 1000, and gid of 2000
  community.general.homectl:
    name: alice
    password: myreallysecurepassword1!
    state: present
    shell: /bin/zsh
    uid: 1000
    gid: 1000

- name: Modify an existing user 'frank' to have 10G of diskspace and resize usage now
  community.general.homectl:
    name: frank
    password: myreallysecurepassword1!
    state: present
    disksize: 10G
    resize: true

- name: Remove an existing user 'janet'
  community.general.homectl:
    name: janet
    state: absent
'''

RETURN = '''
data:
    description: A json dictionary returned from C(homectl inspect -j).
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

import json
import traceback
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.basic import jsonify
from ansible.module_utils.common.text.formatters import human_to_bytes

try:
    import crypt
except ImportError:
    HAS_CRYPT = False
    CRYPT_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_CRYPT = True
    CRYPT_IMPORT_ERROR = None


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
        self.memberof = module.params['memberof']
        self.skeleton = module.params['skeleton']
        self.shell = module.params['shell']
        self.environment = module.params['environment']
        self.timezone = module.params['timezone']
        self.locked = module.params['locked']
        self.passwordhint = module.params['passwordhint']
        self.sshkeys = module.params['sshkeys']
        self.language = module.params['language']
        self.notbefore = module.params['notbefore']
        self.notafter = module.params['notafter']
        self.mountopts = module.params['mountopts']

        self.result = {}

    # Cannot run homectl commands if service is not active
    def homed_service_active(self):
        is_active = True
        cmd = ['systemctl', 'show', 'systemd-homed.service', '-p', 'ActiveState']
        rc, show_service_stdout, stderr = self.module.run_command(cmd)
        if rc == 0:
            state = show_service_stdout.rsplit('=')[1]
            if state.strip() != 'active':
                is_active = False
        return is_active

    def user_exists(self):
        exists = False
        valid_pw = False
        # Get user properties if they exist in json
        rc, stdout, stderr = self.get_user_metadata()
        if rc == 0:
            exists = True
            # User exists now compare password given with current hashed password stored in the user metadata.
            if self.state != 'absent':  # Don't need checking on remove user
                stored_pwhash = json.loads(stdout)['privileged']['hashedPassword'][0]
                if self._check_password(stored_pwhash):
                    valid_pw = True
        return exists, valid_pw

    def create_user(self):
        record = self.create_json_record(create=True)
        cmd = [self.module.get_bin_path('homectl', True)]
        cmd.append('create')
        cmd.append('--identity=-')  # Read the user record from standard input.
        return self.module.run_command(cmd, data=record)

    def _hash_password(self, password):
        method = crypt.METHOD_SHA512
        salt = crypt.mksalt(method, rounds=10000)
        pw_hash = crypt.crypt(password, salt)
        return pw_hash

    def _check_password(self, pwhash):
        hash = crypt.crypt(self.password, pwhash)
        return pwhash == hash

    def remove_user(self):
        cmd = [self.module.get_bin_path('homectl', True)]
        cmd.append('remove')
        cmd.append(self.name)
        return self.module.run_command(cmd)

    def prepare_modify_user_command(self):
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
            self.result['changed'] = True
        return cmd, record

    def get_user_metadata(self):
        cmd = [self.module.get_bin_path('homectl', True)]
        cmd.append('inspect')
        cmd.append(self.name)
        cmd.append('-j')
        cmd.append('--no-pager')
        rc, stdout, stderr = self.module.run_command(cmd)
        return rc, stdout, stderr

    # Build up dictionary to jsonify for homectl commands.
    def create_json_record(self, create=False):
        record = {}
        user_metadata = {}
        self.result['changed'] = False
        # Get the current user record if not creating a new user record.
        if not create:
            rc, user_metadata, stderr = self.get_user_metadata()
            user_metadata = json.loads(user_metadata)
            # Remove elements that are not meant to be updated from record.
            # These are always part of the record when a user exists.
            user_metadata.pop('signature', None)
            user_metadata.pop('binding', None)
            user_metadata.pop('status', None)
            # Let last change Usec be updated by homed when command runs.
            user_metadata.pop('lastChangeUSec', None)
            # Now only change fields that are called on leaving what's currently in the record intact.
            record = user_metadata

        record['userName'] = self.name
        record['secret'] = {'password': [self.password]}

        if create:
            password_hash = self._hash_password(self.password)
            record['privileged'] = {'hashedPassword': [password_hash]}
            self.result['changed'] = True

        if self.uid and self.gid and create:
            record['uid'] = self.uid
            record['gid'] = self.gid
            self.result['changed'] = True

        if self.memberof:
            member_list = list(self.memberof.split(','))
            if member_list != record.get('memberOf', [None]):
                record['memberOf'] = member_list
                self.result['changed'] = True

        if self.realname:
            if self.realname != record.get('realName'):
                record['realName'] = self.realname
                self.result['changed'] = True

        # Cannot update storage unless were creating a new user.
        # See 'Fields in the binding section' at https://systemd.io/USER_RECORD/
        if self.storage and create:
            record['storage'] = self.storage
            self.result['changed'] = True

        # Cannot update homedir unless were creating a new user.
        # See 'Fields in the binding section' at https://systemd.io/USER_RECORD/
        if self.homedir and create:
            record['homeDirectory'] = self.homedir
            self.result['changed'] = True

        # Cannot update imagepath unless were creating a new user.
        # See 'Fields in the binding section' at https://systemd.io/USER_RECORD/
        if self.imagepath and create:
            record['imagePath'] = self.imagepath
            self.result['changed'] = True

        if self.disksize:
            # convert human readable to bytes
            if self.disksize != record.get('diskSize'):
                record['diskSize'] = human_to_bytes(self.disksize)
                self.result['changed'] = True

        if self.realm:
            if self.realm != record.get('realm'):
                record['realm'] = self.realm
                self.result['changed'] = True

        if self.email:
            if self.email != record.get('emailAddress'):
                record['emailAddress'] = self.email
                self.result['changed'] = True

        if self.location:
            if self.location != record.get('location'):
                record['location'] = self.location
                self.result['changed'] = True

        if self.iconname:
            if self.iconname != record.get('iconName'):
                record['iconName'] = self.iconname
                self.result['changed'] = True

        if self.skeleton:
            if self.skeleton != record.get('skeletonDirectory'):
                record['skeletonDirectory'] = self.skeleton
                self.result['changed'] = True

        if self.shell:
            if self.shell != record.get('shell'):
                record['shell'] = self.shell
                self.result['changed'] = True

        if self.umask:
            if self.umask != record.get('umask'):
                record['umask'] = self.umask
                self.result['changed'] = True

        if self.environment:
            if self.environment != record.get('environment', [None]):
                record['environment'] = list(self.environment.split(','))
                self.result['changed'] = True

        if self.timezone:
            if self.timezone != record.get('timeZone'):
                record['timeZone'] = self.timezone
                self.result['changed'] = True

        if self.locked:
            if self.locked != record.get('locked'):
                record['locked'] = self.locked
                self.result['changed'] = True

        if self.passwordhint:
            if self.passwordhint != record.get('privileged', {}).get('passwordHint'):
                record['privileged']['passwordHint'] = self.passwordhint
                self.result['changed'] = True

        if self.sshkeys:
            if self.sshkeys != record.get('privileged', {}).get('sshAuthorizedKeys'):
                record['privileged']['sshAuthorizedKeys'] = list(self.sshkeys.split(','))
                self.result['changed'] = True

        if self.language:
            if self.locked != record.get('preferredLanguage'):
                record['preferredLanguage'] = self.language
                self.result['changed'] = True

        if self.notbefore:
            if self.locked != record.get('notBeforeUSec'):
                record['notBeforeUSec'] = self.notbefore
                self.result['changed'] = True

        if self.notafter:
            if self.locked != record.get('notAfterUSec'):
                record['notAfterUSec'] = self.notafter
                self.result['changed'] = True

        if self.mountopts:
            opts = list(self.mountopts.split(','))
            if 'nosuid' in opts:
                if record.get('mountNoSuid') is not True:
                    record['mountNoSuid'] = True
                    self.result['changed'] = True
            else:
                if record.get('mountNoSuid') is not False:
                    record['mountNoSuid'] = False
                    self.result['changed'] = True

            if 'nodev' in opts:
                if record.get('mountNoDevices') is not True:
                    record['mountNoDevices'] = True
                    self.result['changed'] = True
            else:
                if record.get('mountNoDevices') is not False:
                    record['mountNoDevices'] = False
                    self.result['changed'] = True

            if 'noexec' in opts:
                if record.get('mountNoExecute') is not True:
                    record['mountNoExecute'] = True
                    self.result['changed'] = True
            else:
                if record.get('mountNoExecute') is not False:
                    record['mountNoExecute'] = False
                    self.result['changed'] = True

        return jsonify(record)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['absent', 'present']),
            name=dict(type='str', required=True, aliases=['user', 'username']),
            password=dict(type='str', no_log=True),
            storage=dict(type='str', choices=['classic', 'luks', 'directory', 'subvolume', 'fscrypt', 'cifs']),
            disksize=dict(type='str'),
            resize=dict(type='bool', default=False),
            realname=dict(type='str', aliases=['comment']),
            realm=dict(type='str'),
            email=dict(type='str'),
            location=dict(type='str'),
            iconname=dict(type='str'),
            homedir=dict(type='path'),
            imagepath=dict(type='path'),
            uid=dict(type='int'),
            gid=dict(type='int'),
            umask=dict(type='int'),
            environment=dict(type='str', aliases=['setenv']),
            timezone=dict(type='str'),
            memberof=dict(type='str', aliases=['groups']),
            skeleton=dict(type='path', aliases=['skel']),
            shell=dict(type='str'),
            locked=dict(type='bool'),
            passwordhint=dict(type='str', no_log=True),
            sshkeys=dict(type='str', no_log=True),
            language=dict(type='str'),
            notbefore=dict(type='int'),
            notafter=dict(type='int'),
            mountopts=dict(type='str'),
        ),
        supports_check_mode=True,

        required_if=[
            ('state', 'present', ['password']),
            ('resize', True, ['disksize']),
        ]
    )

    if not HAS_CRYPT:
        module.fail_json(
            msg=missing_required_lib('crypt (part of Python 3.13 standard library)'),
            exception=CRYPT_IMPORT_ERROR,
        )

    homectl = Homectl(module)
    homectl.result['state'] = homectl.state

    # First we need to make sure homed service is active
    if not homectl.homed_service_active():
        module.fail_json(msg='systemd-homed.service is not active')

    # handle removing user
    if homectl.state == 'absent':
        user_exists, valid_pwhash = homectl.user_exists()
        if user_exists:
            if module.check_mode:
                module.exit_json(changed=True)
            rc, stdout, stderr = homectl.remove_user()
            if rc != 0:
                module.fail_json(name=homectl.name, msg=stderr, rc=rc)
            homectl.result['changed'] = True
            homectl.result['rc'] = rc
            homectl.result['msg'] = 'User %s removed!' % homectl.name
        else:
            homectl.result['changed'] = False
            homectl.result['msg'] = 'User does not exist!'

    # Handle adding a user
    if homectl.state == 'present':
        user_exists, valid_pwhash = homectl.user_exists()
        if not user_exists:
            if module.check_mode:
                module.exit_json(changed=True)
            rc, stdout, stderr = homectl.create_user()
            if rc != 0:
                module.fail_json(name=homectl.name, msg=stderr, rc=rc)
            rc, user_metadata, stderr = homectl.get_user_metadata()
            homectl.result['data'] = json.loads(user_metadata)
            homectl.result['rc'] = rc
            homectl.result['msg'] = 'User %s created!' % homectl.name
        else:
            if valid_pwhash:
                # Run this to see if changed would be True or False which is useful for check_mode
                cmd, record = homectl.prepare_modify_user_command()
            else:
                # User gave wrong password fail with message
                homectl.result['changed'] = False
                homectl.result['msg'] = 'User exists but password is incorrect!'
                module.fail_json(**homectl.result)

            if module.check_mode:
                module.exit_json(**homectl.result)

            # Now actually modify the user if changed was set to true at any point.
            if homectl.result['changed']:
                rc, stdout, stderr = module.run_command(cmd, data=record)
                if rc != 0:
                    module.fail_json(name=homectl.name, msg=stderr, rc=rc, changed=False)
            rc, user_metadata, stderr = homectl.get_user_metadata()
            homectl.result['data'] = json.loads(user_metadata)
            homectl.result['rc'] = rc
            if homectl.result['changed']:
                homectl.result['msg'] = 'User %s modified' % homectl.name

    module.exit_json(**homectl.result)


if __name__ == '__main__':
    main()

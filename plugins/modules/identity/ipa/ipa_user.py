#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ipa_user
author: Thomas Krahn (@Nosmoht)
short_description: Manage FreeIPA users
description:
- Add, modify and delete user within IPA server.
options:
  displayname:
    description: Display name.
    type: str
  update_password:
    description:
    - Set password for a user.
    type: str
    default: 'always'
    choices: [ always, on_create ]
  givenname:
    description: First name.
    type: str
  krbpasswordexpiration:
    description:
    - Date at which the user password will expire.
    - In the format YYYYMMddHHmmss.
    - e.g. 20180121182022 will expire on 21 January 2018 at 18:20:22.
    type: str
  loginshell:
    description: Login shell.
    type: str
  mail:
    description:
    - List of mail addresses assigned to the user.
    - If an empty list is passed all assigned email addresses will be deleted.
    - If None is passed email addresses will not be checked or changed.
    type: list
    elements: str
  password:
    description:
    - Password for a user.
    - Will not be set for an existing user unless I(update_password=always), which is the default.
    type: str
  sn:
    description: Surname.
    type: str
  sshpubkey:
    description:
    - List of public SSH key.
    - If an empty list is passed all assigned public keys will be deleted.
    - If None is passed SSH public keys will not be checked or changed.
    type: list
    elements: str
  state:
    description: State to ensure.
    default: "present"
    choices: ["absent", "disabled", "enabled", "present"]
    type: str
  telephonenumber:
    description:
    - List of telephone numbers assigned to the user.
    - If an empty list is passed all assigned telephone numbers will be deleted.
    - If None is passed telephone numbers will not be checked or changed.
    type: list
    elements: str
  title:
    description: Title.
    type: str
  uid:
    description: uid of the user.
    required: true
    aliases: ["name"]
    type: str
  uidnumber:
    description:
    - Account Settings UID/Posix User ID number.
    type: str
  gidnumber:
    description:
    - Posix Group ID.
    type: str
  homedirectory:
    description:
    - Default home directory of the user.
    type: str
    version_added: '0.2.0'
  userauthtype:
    description:
    - The authentication type to use for the user.
    choices: ["password", "radius", "otp", "pkinit", "hardened"]
    type: list
    elements: str
    version_added: '1.2.0'
extends_documentation_fragment:
- community.general.ipa.documentation

requirements:
- base64
- hashlib
'''

EXAMPLES = r'''
- name: Ensure pinky is present and always reset password
  community.general.ipa_user:
    name: pinky
    state: present
    krbpasswordexpiration: 20200119235959
    givenname: Pinky
    sn: Acme
    mail:
    - pinky@acme.com
    telephonenumber:
    - '+555123456'
    sshpubkey:
    - ssh-rsa ....
    - ssh-dsa ....
    uidnumber: '1001'
    gidnumber: '100'
    homedirectory: /home/pinky
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret

- name: Ensure brain is absent
  community.general.ipa_user:
    name: brain
    state: absent
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret

- name: Ensure pinky is present but don't reset password if already exists
  community.general.ipa_user:
    name: pinky
    state: present
    givenname: Pinky
    sn: Acme
    password: zounds
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret
    update_password: on_create

- name: Ensure pinky is present and using one time password and RADIUS authentication
  community.general.ipa_user:
    name: pinky
    state: present
    userauthtype:
      - otp
      - radius
    ipa_host: ipa.example.com
    ipa_user: admin
    ipa_pass: topsecret
'''

RETURN = r'''
user:
  description: User as returned by IPA API
  returned: always
  type: dict
'''

import base64
import hashlib
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ipa import IPAClient, ipa_argument_spec
from ansible.module_utils.common.text.converters import to_native


class UserIPAClient(IPAClient):
    def __init__(self, module, host, port, protocol):
        super(UserIPAClient, self).__init__(module, host, port, protocol)

    def user_find(self, name):
        return self._post_json(method='user_find', name=None, item={'all': True, 'uid': name})

    def user_add(self, name, item):
        return self._post_json(method='user_add', name=name, item=item)

    def user_mod(self, name, item):
        return self._post_json(method='user_mod', name=name, item=item)

    def user_del(self, name):
        return self._post_json(method='user_del', name=name)

    def user_disable(self, name):
        return self._post_json(method='user_disable', name=name)

    def user_enable(self, name):
        return self._post_json(method='user_enable', name=name)


def get_user_dict(displayname=None, givenname=None, krbpasswordexpiration=None, loginshell=None,
                  mail=None, nsaccountlock=False, sn=None, sshpubkey=None, telephonenumber=None,
                  title=None, userpassword=None, gidnumber=None, uidnumber=None, homedirectory=None,
                  userauthtype=None):
    user = {}
    if displayname is not None:
        user['displayname'] = displayname
    if krbpasswordexpiration is not None:
        user['krbpasswordexpiration'] = krbpasswordexpiration + "Z"
    if givenname is not None:
        user['givenname'] = givenname
    if loginshell is not None:
        user['loginshell'] = loginshell
    if mail is not None:
        user['mail'] = mail
    user['nsaccountlock'] = nsaccountlock
    if sn is not None:
        user['sn'] = sn
    if sshpubkey is not None:
        user['ipasshpubkey'] = sshpubkey
    if telephonenumber is not None:
        user['telephonenumber'] = telephonenumber
    if title is not None:
        user['title'] = title
    if userpassword is not None:
        user['userpassword'] = userpassword
    if gidnumber is not None:
        user['gidnumber'] = gidnumber
    if uidnumber is not None:
        user['uidnumber'] = uidnumber
    if homedirectory is not None:
        user['homedirectory'] = homedirectory
    if userauthtype is not None:
        user['ipauserauthtype'] = userauthtype

    return user


def get_user_diff(client, ipa_user, module_user):
    """
        Return the keys of each dict whereas values are different. Unfortunately the IPA
        API returns everything as a list even if only a single value is possible.
        Therefore some more complexity is needed.
        The method will check if the value type of module_user.attr is not a list and
        create a list with that element if the same attribute in ipa_user is list. In this way I hope that the method
        must not be changed if the returned API dict is changed.
    :param ipa_user:
    :param module_user:
    :return:
    """
    # sshpubkeyfp is the list of ssh key fingerprints. IPA doesn't return the keys itself but instead the fingerprints.
    # These are used for comparison.
    sshpubkey = None
    if 'ipasshpubkey' in module_user:
        hash_algo = 'md5'
        if 'sshpubkeyfp' in ipa_user and ipa_user['sshpubkeyfp'][0][:7].upper() == 'SHA256:':
            hash_algo = 'sha256'
        module_user['sshpubkeyfp'] = [get_ssh_key_fingerprint(pubkey, hash_algo) for pubkey in module_user['ipasshpubkey']]
        # Remove the ipasshpubkey element as it is not returned from IPA but save it's value to be used later on
        sshpubkey = module_user['ipasshpubkey']
        del module_user['ipasshpubkey']

    result = client.get_diff(ipa_data=ipa_user, module_data=module_user)

    # If there are public keys, remove the fingerprints and add them back to the dict
    if sshpubkey is not None:
        del module_user['sshpubkeyfp']
        module_user['ipasshpubkey'] = sshpubkey
    return result


def get_ssh_key_fingerprint(ssh_key, hash_algo='sha256'):
    """
    Return the public key fingerprint of a given public SSH key
    in format "[fp] [comment] (ssh-rsa)" where fp is of the format:
    FB:0C:AC:0A:07:94:5B:CE:75:6E:63:32:13:AD:AD:D7
    for md5 or
    SHA256:[base64]
    for sha256
    Comments are assumed to be all characters past the second
    whitespace character in the sshpubkey string.
    :param ssh_key:
    :param hash_algo:
    :return:
    """
    parts = ssh_key.strip().split(None, 2)
    if len(parts) == 0:
        return None
    key_type = parts[0]
    key = base64.b64decode(parts[1].encode('ascii'))

    if hash_algo == 'md5':
        fp_plain = hashlib.md5(key).hexdigest()
        key_fp = ':'.join(a + b for a, b in zip(fp_plain[::2], fp_plain[1::2])).upper()
    elif hash_algo == 'sha256':
        fp_plain = base64.b64encode(hashlib.sha256(key).digest()).decode('ascii').rstrip('=')
        key_fp = 'SHA256:{fp}'.format(fp=fp_plain)
    if len(parts) < 3:
        return "%s (%s)" % (key_fp, key_type)
    else:
        comment = parts[2]
        return "%s %s (%s)" % (key_fp, comment, key_type)


def ensure(module, client):
    state = module.params['state']
    name = module.params['uid']
    nsaccountlock = state == 'disabled'

    module_user = get_user_dict(displayname=module.params.get('displayname'),
                                krbpasswordexpiration=module.params.get('krbpasswordexpiration'),
                                givenname=module.params.get('givenname'),
                                loginshell=module.params['loginshell'],
                                mail=module.params['mail'], sn=module.params['sn'],
                                sshpubkey=module.params['sshpubkey'], nsaccountlock=nsaccountlock,
                                telephonenumber=module.params['telephonenumber'], title=module.params['title'],
                                userpassword=module.params['password'],
                                gidnumber=module.params.get('gidnumber'), uidnumber=module.params.get('uidnumber'),
                                homedirectory=module.params.get('homedirectory'),
                                userauthtype=module.params.get('userauthtype'))

    update_password = module.params.get('update_password')
    ipa_user = client.user_find(name=name)

    changed = False
    if state in ['present', 'enabled', 'disabled']:
        if not ipa_user:
            changed = True
            if not module.check_mode:
                ipa_user = client.user_add(name=name, item=module_user)
        else:
            if update_password == 'on_create':
                module_user.pop('userpassword', None)
            diff = get_user_diff(client, ipa_user, module_user)
            if len(diff) > 0:
                changed = True
                if not module.check_mode:
                    ipa_user = client.user_mod(name=name, item=module_user)
    else:
        if ipa_user:
            changed = True
            if not module.check_mode:
                client.user_del(name)

    return changed, ipa_user


def main():
    argument_spec = ipa_argument_spec()
    argument_spec.update(displayname=dict(type='str'),
                         givenname=dict(type='str'),
                         update_password=dict(type='str', default="always",
                                              choices=['always', 'on_create'],
                                              no_log=False),
                         krbpasswordexpiration=dict(type='str', no_log=False),
                         loginshell=dict(type='str'),
                         mail=dict(type='list', elements='str'),
                         sn=dict(type='str'),
                         uid=dict(type='str', required=True, aliases=['name']),
                         gidnumber=dict(type='str'),
                         uidnumber=dict(type='str'),
                         password=dict(type='str', no_log=True),
                         sshpubkey=dict(type='list', elements='str'),
                         state=dict(type='str', default='present',
                                    choices=['present', 'absent', 'enabled', 'disabled']),
                         telephonenumber=dict(type='list', elements='str'),
                         title=dict(type='str'),
                         homedirectory=dict(type='str'),
                         userauthtype=dict(type='list', elements='str',
                                           choices=['password', 'radius', 'otp', 'pkinit', 'hardened']))

    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True)

    client = UserIPAClient(module=module,
                           host=module.params['ipa_host'],
                           port=module.params['ipa_port'],
                           protocol=module.params['ipa_prot'])

    # If sshpubkey is defined as None than module.params['sshpubkey'] is [None]. IPA itself returns None (not a list).
    # Therefore a small check here to replace list(None) by None. Otherwise get_user_diff() would return sshpubkey
    # as different which should be avoided.
    if module.params['sshpubkey'] is not None:
        if len(module.params['sshpubkey']) == 1 and module.params['sshpubkey'][0] == "":
            module.params['sshpubkey'] = None

    try:
        client.login(username=module.params['ipa_user'],
                     password=module.params['ipa_pass'])
        changed, user = ensure(module, client)
        module.exit_json(changed=changed, user=user)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()

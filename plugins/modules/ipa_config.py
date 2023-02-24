#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2018, Fran Fitzpatrick <francis.x.fitzpatrick@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: ipa_config
author: Fran Fitzpatrick (@fxfitz)
short_description: Manage Global FreeIPA Configuration Settings
description:
  - Modify global configuration settings of a FreeIPA Server.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  ipaconfigstring:
    description: Extra hashes to generate in password plug-in.
    aliases: ["configstring"]
    type: list
    elements: str
    choices: ["AllowNThash", "KDC:Disable Last Success", "KDC:Disable Lockout", "KDC:Disable Default Preauth for SPNs"]
    version_added: '2.5.0'
  ipadefaultloginshell:
    description: Default shell for new users.
    aliases: ["loginshell"]
    type: str
  ipadefaultemaildomain:
    description: Default e-mail domain for new users.
    aliases: ["emaildomain"]
    type: str
  ipadefaultprimarygroup:
    description: Default group for new users.
    aliases: ["primarygroup"]
    type: str
    version_added: '2.5.0'
  ipagroupsearchfields:
    description: A list of fields to search in when searching for groups.
    aliases: ["groupsearchfields"]
    type: list
    elements: str
    version_added: '2.5.0'
  ipahomesrootdir:
    description: Default location of home directories.
    aliases: ["homesrootdir"]
    type: str
    version_added: '2.5.0'
  ipakrbauthzdata:
    description: Default types of PAC supported for services.
    aliases: ["krbauthzdata"]
    type: list
    elements: str
    choices: ["MS-PAC", "PAD", "nfs:NONE"]
    version_added: '2.5.0'
  ipamaxusernamelength:
    description: Maximum length of usernames.
    aliases: ["maxusernamelength"]
    type: int
    version_added: '2.5.0'
  ipapwdexpadvnotify:
    description: Notice of impending password expiration, in days.
    aliases: ["pwdexpadvnotify"]
    type: int
    version_added: '2.5.0'
  ipasearchrecordslimit:
    description: Maximum number of records to search (-1 or 0 is unlimited).
    aliases: ["searchrecordslimit"]
    type: int
    version_added: '2.5.0'
  ipasearchtimelimit:
    description: Maximum amount of time (seconds) for a search (-1 or 0 is unlimited).
    aliases: ["searchtimelimit"]
    type: int
    version_added: '2.5.0'
  ipaselinuxusermaporder:
    description: The SELinux user map order (order in increasing priority of SELinux users).
    aliases: ["selinuxusermaporder"]
    type: list
    elements: str
    version_added: '3.7.0'
  ipauserauthtype:
    description: The authentication type to use by default.
    aliases: ["userauthtype"]
    choices: ["password", "radius", "otp", "pkinit", "hardened", "disabled"]
    type: list
    elements: str
    version_added: '2.5.0'
  ipausersearchfields:
    description: A list of fields to search in when searching for users.
    aliases: ["usersearchfields"]
    type: list
    elements: str
    version_added: '2.5.0'
extends_documentation_fragment:
  - community.general.ipa.documentation
  - community.general.attributes

'''

EXAMPLES = r'''
- name: Ensure password plugin features DC:Disable Last Success and KDC:Disable Lockout are enabled
  community.general.ipa_config:
    ipaconfigstring: ["KDC:Disable Last Success", "KDC:Disable Lockout"]
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the default login shell is bash
  community.general.ipa_config:
    ipadefaultloginshell: /bin/bash
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the default e-mail domain is ansible.com
  community.general.ipa_config:
    ipadefaultemaildomain: ansible.com
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the default primary group is set to ipausers
  community.general.ipa_config:
    ipadefaultprimarygroup: ipausers
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the group search fields are set to 'cn,description'
  community.general.ipa_config:
    ipagroupsearchfields: ['cn', 'description']
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the home directory location is set to /home
  community.general.ipa_config:
    ipahomesrootdir: /home
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the default types of PAC supported for services is set to MS-PAC and PAD
  community.general.ipa_config:
    ipakrbauthzdata: ["MS-PAC", "PAD"]
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the maximum user name length is set to 32
  community.general.ipa_config:
    ipamaxusernamelength: 32
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the password expiration notice is set to 4 days
  community.general.ipa_config:
    ipapwdexpadvnotify: 4
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the search record limit is set to 100
  community.general.ipa_config:
    ipasearchrecordslimit: 100
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the search time limit is set to 2 seconds
  community.general.ipa_config:
    ipasearchtimelimit: 2
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the default user auth type is password
  community.general.ipa_config:
    ipauserauthtype: ['password']
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the user search fields is set to 'uid,givenname,sn,ou,title'
  community.general.ipa_config:
    ipausersearchfields: ['uid', 'givenname', 'sn', 'ou', 'title']
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the SELinux user map order is set
  community.general.ipa_config:
    ipaselinuxusermaporder:
      - "guest_u:s0"
      - "xguest_u:s0"
      - "user_u:s0"
      - "staff_u:s0-s0:c0.c1023"
      - "unconfined_u:s0-s0:c0.c1023"
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret
'''

RETURN = r'''
config:
  description: Configuration as returned by IPA API.
  returned: always
  type: dict
'''

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ipa import IPAClient, ipa_argument_spec
from ansible.module_utils.common.text.converters import to_native


class ConfigIPAClient(IPAClient):
    def __init__(self, module, host, port, protocol):
        super(ConfigIPAClient, self).__init__(module, host, port, protocol)

    def config_show(self):
        return self._post_json(method='config_show', name=None)

    def config_mod(self, name, item):
        return self._post_json(method='config_mod', name=name, item=item)


def get_config_dict(ipaconfigstring=None, ipadefaultloginshell=None,
                    ipadefaultemaildomain=None, ipadefaultprimarygroup=None,
                    ipagroupsearchfields=None, ipahomesrootdir=None,
                    ipakrbauthzdata=None, ipamaxusernamelength=None,
                    ipapwdexpadvnotify=None, ipasearchrecordslimit=None,
                    ipasearchtimelimit=None, ipaselinuxusermaporder=None,
                    ipauserauthtype=None, ipausersearchfields=None):
    config = {}
    if ipaconfigstring is not None:
        config['ipaconfigstring'] = ipaconfigstring
    if ipadefaultloginshell is not None:
        config['ipadefaultloginshell'] = ipadefaultloginshell
    if ipadefaultemaildomain is not None:
        config['ipadefaultemaildomain'] = ipadefaultemaildomain
    if ipadefaultprimarygroup is not None:
        config['ipadefaultprimarygroup'] = ipadefaultprimarygroup
    if ipagroupsearchfields is not None:
        config['ipagroupsearchfields'] = ','.join(ipagroupsearchfields)
    if ipahomesrootdir is not None:
        config['ipahomesrootdir'] = ipahomesrootdir
    if ipakrbauthzdata is not None:
        config['ipakrbauthzdata'] = ipakrbauthzdata
    if ipamaxusernamelength is not None:
        config['ipamaxusernamelength'] = str(ipamaxusernamelength)
    if ipapwdexpadvnotify is not None:
        config['ipapwdexpadvnotify'] = str(ipapwdexpadvnotify)
    if ipasearchrecordslimit is not None:
        config['ipasearchrecordslimit'] = str(ipasearchrecordslimit)
    if ipasearchtimelimit is not None:
        config['ipasearchtimelimit'] = str(ipasearchtimelimit)
    if ipaselinuxusermaporder is not None:
        config['ipaselinuxusermaporder'] = '$'.join(ipaselinuxusermaporder)
    if ipauserauthtype is not None:
        config['ipauserauthtype'] = ipauserauthtype
    if ipausersearchfields is not None:
        config['ipausersearchfields'] = ','.join(ipausersearchfields)

    return config


def get_config_diff(client, ipa_config, module_config):
    return client.get_diff(ipa_data=ipa_config, module_data=module_config)


def ensure(module, client):
    module_config = get_config_dict(
        ipaconfigstring=module.params.get('ipaconfigstring'),
        ipadefaultloginshell=module.params.get('ipadefaultloginshell'),
        ipadefaultemaildomain=module.params.get('ipadefaultemaildomain'),
        ipadefaultprimarygroup=module.params.get('ipadefaultprimarygroup'),
        ipagroupsearchfields=module.params.get('ipagroupsearchfields'),
        ipahomesrootdir=module.params.get('ipahomesrootdir'),
        ipakrbauthzdata=module.params.get('ipakrbauthzdata'),
        ipamaxusernamelength=module.params.get('ipamaxusernamelength'),
        ipapwdexpadvnotify=module.params.get('ipapwdexpadvnotify'),
        ipasearchrecordslimit=module.params.get('ipasearchrecordslimit'),
        ipasearchtimelimit=module.params.get('ipasearchtimelimit'),
        ipaselinuxusermaporder=module.params.get('ipaselinuxusermaporder'),
        ipauserauthtype=module.params.get('ipauserauthtype'),
        ipausersearchfields=module.params.get('ipausersearchfields'),
    )
    ipa_config = client.config_show()
    diff = get_config_diff(client, ipa_config, module_config)

    changed = False
    new_config = {}
    for module_key in diff:
        if module_config.get(module_key) != ipa_config.get(module_key, None):
            changed = True
            new_config.update({module_key: module_config.get(module_key)})

    if changed and not module.check_mode:
        client.config_mod(name=None, item=new_config)

    return changed, client.config_show()


def main():
    argument_spec = ipa_argument_spec()
    argument_spec.update(
        ipaconfigstring=dict(type='list', elements='str',
                             choices=['AllowNThash',
                                      'KDC:Disable Last Success',
                                      'KDC:Disable Lockout',
                                      'KDC:Disable Default Preauth for SPNs'],
                             aliases=['configstring']),
        ipadefaultloginshell=dict(type='str', aliases=['loginshell']),
        ipadefaultemaildomain=dict(type='str', aliases=['emaildomain']),
        ipadefaultprimarygroup=dict(type='str', aliases=['primarygroup']),
        ipagroupsearchfields=dict(type='list', elements='str',
                                  aliases=['groupsearchfields']),
        ipahomesrootdir=dict(type='str', aliases=['homesrootdir']),
        ipakrbauthzdata=dict(type='list', elements='str',
                             choices=['MS-PAC', 'PAD', 'nfs:NONE'],
                             aliases=['krbauthzdata']),
        ipamaxusernamelength=dict(type='int', aliases=['maxusernamelength']),
        ipapwdexpadvnotify=dict(type='int', aliases=['pwdexpadvnotify']),
        ipasearchrecordslimit=dict(type='int', aliases=['searchrecordslimit']),
        ipasearchtimelimit=dict(type='int', aliases=['searchtimelimit']),
        ipaselinuxusermaporder=dict(type='list', elements='str',
                                    aliases=['selinuxusermaporder']),
        ipauserauthtype=dict(type='list', elements='str',
                             aliases=['userauthtype'],
                             choices=["password", "radius", "otp", "pkinit",
                                      "hardened", "disabled"]),
        ipausersearchfields=dict(type='list', elements='str',
                                 aliases=['usersearchfields']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    client = ConfigIPAClient(
        module=module,
        host=module.params['ipa_host'],
        port=module.params['ipa_port'],
        protocol=module.params['ipa_prot']
    )

    try:
        client.login(
            username=module.params['ipa_user'],
            password=module.params['ipa_pass']
        )
        changed, user = ensure(module, client)
        module.exit_json(changed=changed, user=user)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()

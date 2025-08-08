#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Ansible Project
# Heavily influenced from Fran Fitzpatrick <francis.x.fitzpatrick@gmail.com> ipa_config module
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
module: ipa_otpconfig
author: justchris1 (@justchris1)
short_description: Manage FreeIPA OTP Configuration Settings
version_added: 2.5.0
description:
  - Modify global configuration settings of a FreeIPA Server with respect to OTP (One Time Passwords).
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  ipatokentotpauthwindow:
    description: TOTP authentication window in seconds.
    aliases: ["totpauthwindow"]
    type: int
  ipatokentotpsyncwindow:
    description: TOTP synchronization window in seconds.
    aliases: ["totpsyncwindow"]
    type: int
  ipatokenhotpauthwindow:
    description: HOTP authentication window in number of hops.
    aliases: ["hotpauthwindow"]
    type: int
  ipatokenhotpsyncwindow:
    description: HOTP synchronization window in hops.
    aliases: ["hotpsyncwindow"]
    type: int
extends_documentation_fragment:
  - community.general.ipa.documentation
  - community.general.ipa.connection_notes
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Ensure the TOTP authentication window is set to 300 seconds
  community.general.ipa_otpconfig:
    ipatokentotpauthwindow: '300'
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the TOTP synchronization window is set to 86400 seconds
  community.general.ipa_otpconfig:
    ipatokentotpsyncwindow: '86400'
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the HOTP authentication window is set to 10 hops
  community.general.ipa_otpconfig:
    ipatokenhotpauthwindow: '10'
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret

- name: Ensure the HOTP synchronization window is set to 100 hops
  community.general.ipa_otpconfig:
    ipatokenhotpsyncwindow: '100'
    ipa_host: localhost
    ipa_user: admin
    ipa_pass: supersecret
"""

RETURN = r"""
otpconfig:
  description: OTP configuration as returned by IPA API.
  returned: always
  type: dict
"""

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.ipa import IPAClient, ipa_argument_spec
from ansible.module_utils.common.text.converters import to_native


class OTPConfigIPAClient(IPAClient):
    def __init__(self, module, host, port, protocol):
        super(OTPConfigIPAClient, self).__init__(module, host, port, protocol)

    def otpconfig_show(self):
        return self._post_json(method='otpconfig_show', name=None)

    def otpconfig_mod(self, name, item):
        return self._post_json(method='otpconfig_mod', name=name, item=item)


def get_otpconfig_dict(ipatokentotpauthwindow=None, ipatokentotpsyncwindow=None,
                       ipatokenhotpauthwindow=None, ipatokenhotpsyncwindow=None):

    config = {}
    if ipatokentotpauthwindow is not None:
        config['ipatokentotpauthwindow'] = str(ipatokentotpauthwindow)
    if ipatokentotpsyncwindow is not None:
        config['ipatokentotpsyncwindow'] = str(ipatokentotpsyncwindow)
    if ipatokenhotpauthwindow is not None:
        config['ipatokenhotpauthwindow'] = str(ipatokenhotpauthwindow)
    if ipatokenhotpsyncwindow is not None:
        config['ipatokenhotpsyncwindow'] = str(ipatokenhotpsyncwindow)

    return config


def get_otpconfig_diff(client, ipa_config, module_config):
    return client.get_diff(ipa_data=ipa_config, module_data=module_config)


def ensure(module, client):
    module_otpconfig = get_otpconfig_dict(
        ipatokentotpauthwindow=module.params.get('ipatokentotpauthwindow'),
        ipatokentotpsyncwindow=module.params.get('ipatokentotpsyncwindow'),
        ipatokenhotpauthwindow=module.params.get('ipatokenhotpauthwindow'),
        ipatokenhotpsyncwindow=module.params.get('ipatokenhotpsyncwindow'),
    )
    ipa_otpconfig = client.otpconfig_show()
    diff = get_otpconfig_diff(client, ipa_otpconfig, module_otpconfig)

    changed = False
    new_otpconfig = {}
    for module_key in diff:
        if module_otpconfig.get(module_key) != ipa_otpconfig.get(module_key, None):
            changed = True
            new_otpconfig.update({module_key: module_otpconfig.get(module_key)})

    if changed and not module.check_mode:
        client.otpconfig_mod(name=None, item=new_otpconfig)

    return changed, client.otpconfig_show()


def main():
    argument_spec = ipa_argument_spec()
    argument_spec.update(
        ipatokentotpauthwindow=dict(type='int', aliases=['totpauthwindow'], no_log=False),
        ipatokentotpsyncwindow=dict(type='int', aliases=['totpsyncwindow'], no_log=False),
        ipatokenhotpauthwindow=dict(type='int', aliases=['hotpauthwindow'], no_log=False),
        ipatokenhotpsyncwindow=dict(type='int', aliases=['hotpsyncwindow'], no_log=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    client = OTPConfigIPAClient(
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
        changed, otpconfig = ensure(module, client)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=traceback.format_exc())

    module.exit_json(changed=changed, otpconfig=otpconfig)


if __name__ == '__main__':
    main()

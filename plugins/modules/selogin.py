#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2017, Petr Lautrbach <plautrba@redhat.com>
# Based on seport.py module (c) 2014, Dan Keder <dan.keder@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: selogin
short_description: Manages linux user to SELinux user mapping
description:
  - Manages linux user to SELinux user mapping
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  login:
    type: str
    description:
      - a Linux user
    required: true
  seuser:
    type: str
    description:
      - SELinux user name
  selevel:
    type: str
    aliases: [ serange ]
    description:
      - MLS/MCS Security Range (MLS/MCS Systems only) SELinux Range for SELinux login mapping defaults to the SELinux user record range.
    default: s0
  state:
    type: str
    description:
      - Desired mapping value.
    default: present
    choices: [ 'present', 'absent' ]
  reload:
    description:
      - Reload SELinux policy after commit.
    type: bool
    default: true
  ignore_selinux_state:
    description:
    - Run independent of selinux runtime state
    type: bool
    default: false
notes:
   - The changes are persistent across reboots
   - Not tested on any debian based system
requirements: [ 'libselinux', 'policycoreutils' ]
author:
- Dan Keder (@dankeder)
- Petr Lautrbach (@bachradsusi)
- James Cassell (@jamescassell)
'''

EXAMPLES = '''
- name: Modify the default user on the system to the guest_u user
  community.general.selogin:
    login: __default__
    seuser: guest_u
    state: present

- name: Assign gijoe user on an MLS machine a range and to the staff_u user
  community.general.selogin:
    login: gijoe
    seuser: staff_u
    serange: SystemLow-Secret
    state: present

- name: Assign all users in the engineering group to the staff_u user
  community.general.selogin:
    login: '%engineering'
    seuser: staff_u
    state: present
'''

RETURN = r'''
# Default return values
'''


import traceback

SELINUX_IMP_ERR = None
try:
    import selinux
    HAVE_SELINUX = True
except ImportError:
    SELINUX_IMP_ERR = traceback.format_exc()
    HAVE_SELINUX = False

SEOBJECT_IMP_ERR = None
try:
    import seobject
    HAVE_SEOBJECT = True
except ImportError:
    SEOBJECT_IMP_ERR = traceback.format_exc()
    HAVE_SEOBJECT = False


from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native


def semanage_login_add(module, login, seuser, do_reload, serange='s0', sestore=''):
    """ Add linux user to SELinux user mapping

    :type module: AnsibleModule
    :param module: Ansible module

    :type login: str
    :param login: a Linux User or a Linux group if it begins with %

    :type seuser: str
    :param proto: An SELinux user ('__default__', 'unconfined_u', 'staff_u', ...), see 'semanage login -l'

    :type serange: str
    :param serange: SELinux MLS/MCS range (defaults to 's0')

    :type do_reload: bool
    :param do_reload: Whether to reload SELinux policy after commit

    :type sestore: str
    :param sestore: SELinux store

    :rtype: bool
    :return: True if the policy was changed, otherwise False
    """
    try:
        selogin = seobject.loginRecords(sestore)
        selogin.set_reload(do_reload)
        change = False
        all_logins = selogin.get_all()
        # module.fail_json(msg="%s: %s %s" % (all_logins, login, sestore))
        # for local_login in all_logins:
        if login not in all_logins.keys():
            change = True
            if not module.check_mode:
                selogin.add(login, seuser, serange)
        else:
            if all_logins[login][0] != seuser or all_logins[login][1] != serange:
                change = True
                if not module.check_mode:
                    selogin.modify(login, seuser, serange)

    except (ValueError, KeyError, OSError, RuntimeError) as e:
        module.fail_json(msg="%s: %s\n" % (e.__class__.__name__, to_native(e)), exception=traceback.format_exc())

    return change


def semanage_login_del(module, login, seuser, do_reload, sestore=''):
    """ Delete linux user to SELinux user mapping

    :type module: AnsibleModule
    :param module: Ansible module

    :type login: str
    :param login: a Linux User or a Linux group if it begins with %

    :type seuser: str
    :param proto: An SELinux user ('__default__', 'unconfined_u', 'staff_u', ...), see 'semanage login -l'

    :type do_reload: bool
    :param do_reload: Whether to reload SELinux policy after commit

    :type sestore: str
    :param sestore: SELinux store

    :rtype: bool
    :return: True if the policy was changed, otherwise False
    """
    try:
        selogin = seobject.loginRecords(sestore)
        selogin.set_reload(do_reload)
        change = False
        all_logins = selogin.get_all()
        # module.fail_json(msg="%s: %s %s" % (all_logins, login, sestore))
        if login in all_logins.keys():
            change = True
            if not module.check_mode:
                selogin.delete(login)

    except (ValueError, KeyError, OSError, RuntimeError) as e:
        module.fail_json(msg="%s: %s\n" % (e.__class__.__name__, to_native(e)), exception=traceback.format_exc())

    return change


def get_runtime_status(ignore_selinux_state=False):
    return True if ignore_selinux_state is True else selinux.is_selinux_enabled()


def main():
    module = AnsibleModule(
        argument_spec=dict(
            ignore_selinux_state=dict(type='bool', default=False),
            login=dict(type='str', required=True),
            seuser=dict(type='str'),
            selevel=dict(type='str', aliases=['serange'], default='s0'),
            state=dict(type='str', default='present', choices=['absent', 'present']),
            reload=dict(type='bool', default=True),
        ),
        required_if=[
            ["state", "present", ["seuser"]]
        ],
        supports_check_mode=True
    )
    if not HAVE_SELINUX:
        module.fail_json(msg=missing_required_lib("libselinux"), exception=SELINUX_IMP_ERR)

    if not HAVE_SEOBJECT:
        module.fail_json(msg=missing_required_lib("seobject from policycoreutils"), exception=SEOBJECT_IMP_ERR)

    ignore_selinux_state = module.params['ignore_selinux_state']

    if not get_runtime_status(ignore_selinux_state):
        module.fail_json(msg="SELinux is disabled on this host.")

    login = module.params['login']
    seuser = module.params['seuser']
    serange = module.params['selevel']
    state = module.params['state']
    do_reload = module.params['reload']

    result = {
        'login': login,
        'seuser': seuser,
        'serange': serange,
        'state': state,
    }

    if state == 'present':
        result['changed'] = semanage_login_add(module, login, seuser, do_reload, serange)
    elif state == 'absent':
        result['changed'] = semanage_login_del(module, login, seuser, do_reload)
    else:
        module.fail_json(msg='Invalid value of argument "state": {0}'.format(state))

    module.exit_json(**result)


if __name__ == '__main__':
    main()

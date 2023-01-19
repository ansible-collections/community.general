#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sefcontext
short_description: Manages SELinux file context mapping definitions
description:
  - Manages SELinux file context mapping definitions.
  - Similar to the C(semanage fcontext) command.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
  platform:
    platforms: rhel
options:
  target:
    description:
    - Target path (expression).
    type: str
    required: true
    aliases: [ path ]
  ftype:
    description:
    - The file type that should have SELinux contexts applied.
    - "The following file type options are available:"
    - C(a) for all files,
    - C(b) for block devices,
    - C(c) for character devices,
    - C(d) for directories,
    - C(f) for regular files,
    - C(l) for symbolic links,
    - C(p) for named pipes,
    - C(s) for socket files.
    type: str
    choices: [ a, b, c, d, f, l, p, s ]
    default: a
  setype:
    description:
    - SELinux type for the specified I(target).
    type: str
  equal:
    description:
    - Path to use for substituting the I(target). The context labeling for the I(target) subtree is made equivalent to this path.
    version_added: 6.3.0
    type: str
  seuser:
    description:
    - SELinux user for the specified I(target).
    - Defaults to C(system_u) for new file contexts and to existing value when modifying file contexts.
    type: str
  selevel:
    description:
    - SELinux range for the specified I(target).
    - Defaults to C(s0) for new file contexts and to existing value when modifying file contexts.
    type: str
    aliases: [ serange ]
  state:
    description:
    - Whether the SELinux file context must be C(absent) or C(present).
    - Specifying C(absent) without either I(setype) or I(equal) deletes both SELinux type or path substitution mappings that match I(target).
    type: str
    choices: [ absent, present ]
    default: present
  reload:
    description:
    - Reload SELinux policy after commit.
    - Note that this does not apply SELinux file contexts to existing files.
    type: bool
    default: true
  ignore_selinux_state:
    description:
    - Useful for scenarios (chrooted environment) that you can't get the real SELinux state.
    type: bool
    default: false
notes:
- The changes are persistent across reboots.
- I(setype) and I(equal) are mutually exclusive.
- If I(state=present) then one of I(setype) or I(equal) is mandatory.
- The M(community.general.sefcontext) module does not modify existing files to the new
  SELinux context(s), so it is advisable to first create the SELinux
  file contexts before creating files, or run C(restorecon) manually
  for the existing files that require the new SELinux file contexts.
- Not applying SELinux fcontexts to existing files is a deliberate
  decision as it would be unclear what reported changes would entail
  to, and there's no guarantee that applying SELinux fcontext does
  not pick up other unrelated prior changes.
requirements:
- libselinux-python
- policycoreutils-python
author:
- Dag Wieers (@dagwieers)
'''

EXAMPLES = r'''
- name: Allow apache to modify files in /srv/git_repos
  community.general.sefcontext:
    target: '/srv/git_repos(/.*)?'
    setype: httpd_git_rw_content_t
    state: present

- name: Substitute file contexts for path /srv/containers with /var/lib/containers
  community.general.sefcontext:
    target: /srv/containers
    equal: /var/lib/containers
    state: present

- name: Delete file context path substitution for /srv/containers
  community.general.sefcontext:
    target: /srv/containers
    equal: /var/lib/containers
    state: absent

- name: Delete any file context mappings for path /srv/git
  community.general.sefcontext:
    target: /srv/git
    state: absent

- name: Apply new SELinux file context to filesystem
  ansible.builtin.command: restorecon -irv /srv/git_repos
'''

RETURN = r'''
# Default return values
'''

import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

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

# Add missing entries (backward compatible)
if HAVE_SEOBJECT:
    seobject.file_types.update(
        a=seobject.SEMANAGE_FCONTEXT_ALL,
        b=seobject.SEMANAGE_FCONTEXT_BLOCK,
        c=seobject.SEMANAGE_FCONTEXT_CHAR,
        d=seobject.SEMANAGE_FCONTEXT_DIR,
        f=seobject.SEMANAGE_FCONTEXT_REG,
        l=seobject.SEMANAGE_FCONTEXT_LINK,
        p=seobject.SEMANAGE_FCONTEXT_PIPE,
        s=seobject.SEMANAGE_FCONTEXT_SOCK,
    )

# Make backward compatible
option_to_file_type_str = dict(
    a='all files',
    b='block device',
    c='character device',
    d='directory',
    f='regular file',
    l='symbolic link',
    p='named pipe',
    s='socket',
)


def get_runtime_status(ignore_selinux_state=False):
    return True if ignore_selinux_state is True else selinux.is_selinux_enabled()


def semanage_fcontext_exists(sefcontext, target, ftype):
    ''' Get the SELinux file context mapping definition from policy. Return None if it does not exist. '''

    # Beware that records comprise of a string representation of the file_type
    record = (target, option_to_file_type_str[ftype])
    records = sefcontext.get_all()
    try:
        return records[record]
    except KeyError:
        return None


def semanage_fcontext_equal_exists(sefcontext, target):
    ''' Get the SELinux file context path substitution definition from policy. Return None if it does not exist. '''

    return sefcontext.equiv_dist.get(target, sefcontext.equiv.get(target))


def semanage_fcontext_modify(module, result, target, ftype, setype, equal, do_reload, serange, seuser, sestore=''):
    ''' Add or modify SELinux file context mapping definition to the policy. '''

    changed = False
    prepared_diff = ''

    try:
        sefcontext = seobject.fcontextRecords(sestore)
        sefcontext.set_reload(do_reload)
        if equal is None:
            exists = semanage_fcontext_exists(sefcontext, target, ftype)
            if exists:
                # Modify existing entry
                orig_seuser, orig_serole, orig_setype, orig_serange = exists

                if seuser is None:
                    seuser = orig_seuser
                if serange is None:
                    serange = orig_serange

                if setype != orig_setype or seuser != orig_seuser or serange != orig_serange:
                    if not module.check_mode:
                        sefcontext.modify(target, setype, ftype, serange, seuser)
                    changed = True

                    if module._diff:
                        prepared_diff += '# Change to semanage file context mappings\n'
                        prepared_diff += '-%s      %s      %s:%s:%s:%s\n' % (target, ftype, orig_seuser, orig_serole, orig_setype, orig_serange)
                        prepared_diff += '+%s      %s      %s:%s:%s:%s\n' % (target, ftype, seuser, orig_serole, setype, serange)
            else:
                # Add missing entry
                if seuser is None:
                    seuser = 'system_u'
                if serange is None:
                    serange = 's0'

                if not module.check_mode:
                    sefcontext.add(target, setype, ftype, serange, seuser)
                changed = True

                if module._diff:
                    prepared_diff += '# Addition to semanage file context mappings\n'
                    prepared_diff += '+%s      %s      %s:%s:%s:%s\n' % (target, ftype, seuser, 'object_r', setype, serange)
        else:
            exists = semanage_fcontext_equal_exists(sefcontext, target)
            if exists:
                # Modify existing path substitution entry
                orig_equal = exists

                if equal != orig_equal:
                    if not module.check_mode:
                        sefcontext.modify_equal(target, equal)
                    changed = True

                    if module._diff:
                        prepared_diff += '# Change to semanage file context path substitutions\n'
                        prepared_diff += '-%s = %s\n' % (orig_equal, target)
                        prepared_diff += '+%s = %s\n' % (equal, target)
            else:
                # Add missing path substitution entry
                if not module.check_mode:
                    sefcontext.add_equal(target, equal)
                changed = True
                if module._diff:
                    prepared_diff += '# Addition to semanage file context path substitutions\n'
                    prepared_diff += '+%s = %s\n' % (equal, target)

    except Exception as e:
        module.fail_json(msg="%s: %s\n" % (e.__class__.__name__, to_native(e)))

    if module._diff and prepared_diff:
        result['diff'] = dict(prepared=prepared_diff)

    module.exit_json(changed=changed, seuser=seuser, serange=serange, **result)


def semanage_fcontext_delete(module, result, target, ftype, setype, equal, do_reload, sestore=''):
    ''' Delete SELinux file context mapping definition from the policy. '''

    changed = False
    prepared_diff = ''

    try:
        sefcontext = seobject.fcontextRecords(sestore)
        sefcontext.set_reload(do_reload)
        exists = semanage_fcontext_exists(sefcontext, target, ftype)
        equal_exists = semanage_fcontext_equal_exists(sefcontext, target)
        if exists and equal is None and ((setype is not None and exists[2] == setype) or setype is None):
            # Remove existing entry
            orig_seuser, orig_serole, orig_setype, orig_serange = exists

            if not module.check_mode:
                sefcontext.delete(target, ftype)
            changed = True

            if module._diff:
                prepared_diff += '# Deletion to semanage file context mappings\n'
                prepared_diff += '-%s      %s      %s:%s:%s:%s\n' % (target, ftype, exists[0], exists[1], exists[2], exists[3])
        if equal_exists and setype is None and ((equal is not None and equal_exists == equal) or equal is None):
            # Remove existing path substitution entry
            orig_equal = equal_exists

            if not module.check_mode:
                sefcontext.delete(target, orig_equal)
            changed = True

            if module._diff:
                prepared_diff += '# Deletion to semanage file context path substitutions\n'
                prepared_diff += '-%s = %s\n' % (orig_equal, target)

    except Exception as e:
        module.fail_json(msg="%s: %s\n" % (e.__class__.__name__, to_native(e)))

    if module._diff and prepared_diff:
        result['diff'] = dict(prepared=prepared_diff)

    module.exit_json(changed=changed, **result)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            ignore_selinux_state=dict(type='bool', default=False),
            target=dict(type='str', required=True, aliases=['path']),
            ftype=dict(type='str', default='a', choices=list(option_to_file_type_str.keys())),
            setype=dict(type='str'),
            equal=dict(type='str'),
            seuser=dict(type='str'),
            selevel=dict(type='str', aliases=['serange']),
            state=dict(type='str', default='present', choices=['absent', 'present']),
            reload=dict(type='bool', default=True),
        ),
        mutually_exclusive=[
            ('setype', 'equal'),
            ('equal', 'ftype'),
            ('equal', 'seuser'),
            ('equal', 'selevel'),
        ],
        required_if=[
            ('state', 'present', ('setype', 'equal'), True),
        ],

        supports_check_mode=True,
    )
    if not HAVE_SELINUX:
        module.fail_json(msg=missing_required_lib("libselinux-python"), exception=SELINUX_IMP_ERR)

    if not HAVE_SEOBJECT:
        module.fail_json(msg=missing_required_lib("policycoreutils-python"), exception=SEOBJECT_IMP_ERR)

    ignore_selinux_state = module.params['ignore_selinux_state']

    if not get_runtime_status(ignore_selinux_state):
        module.fail_json(msg="SELinux is disabled on this host.")

    target = module.params['target']
    ftype = module.params['ftype']
    setype = module.params['setype']
    equal = module.params['equal']
    seuser = module.params['seuser']
    serange = module.params['selevel']
    state = module.params['state']
    do_reload = module.params['reload']

    result = dict(target=target, ftype=ftype, setype=setype, equal=equal, state=state)

    if state == 'present':
        semanage_fcontext_modify(module, result, target, ftype, setype, equal, do_reload, serange, seuser)
    elif state == 'absent':
        semanage_fcontext_delete(module, result, target, ftype, setype, equal, do_reload)
    else:
        module.fail_json(msg='Invalid value of argument "state": {0}'.format(state))


if __name__ == '__main__':
    main()

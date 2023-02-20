#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, Sebastien Rohaut <sebastien.rohaut@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: pam_limits
author:
- "Sebastien Rohaut (@usawa)"
short_description: Modify Linux PAM limits
description:
  - The C(pam_limits) module modifies PAM limits.
  - The default file is C(/etc/security/limits.conf).
  - For the full documentation, see C(man 5 limits.conf).
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
    version_added: 2.0.0
  diff_mode:
    support: full
    version_added: 2.0.0
options:
  domain:
    type: str
    description:
      - A username, @groupname, wildcard, UID/GID range.
    required: true
  limit_type:
    type: str
    description:
      - Limit type, see C(man 5 limits.conf) for an explanation.
    required: true
    choices: [ "hard", "soft", "-" ]
  limit_item:
    type: str
    description:
      - The limit to be set.
    required: true
    choices:
        - "core"
        - "data"
        - "fsize"
        - "memlock"
        - "nofile"
        - "rss"
        - "stack"
        - "cpu"
        - "nproc"
        - "as"
        - "maxlogins"
        - "maxsyslogins"
        - "priority"
        - "locks"
        - "sigpending"
        - "msgqueue"
        - "nice"
        - "rtprio"
        - "chroot"
  value:
    type: str
    description:
      - The value of the limit.
      - Value must either be C(unlimited), C(infinity) or C(-1), all of which indicate no limit, or a limit of 0 or larger.
      - Value must be a number in the range -20 to 19 inclusive, if I(limit_item) is set to C(nice) or C(priority).
      - Refer to the C(man 5 limits.conf) manual pages for more details.
    required: true
  backup:
    description:
      - Create a backup file including the timestamp information so you can get
        the original file back if you somehow clobbered it incorrectly.
    required: false
    type: bool
    default: false
  use_min:
    description:
      - If set to C(true), the minimal value will be used or conserved.
      - If the specified value is inferior to the value in the file,
        file content is replaced with the new value, else content is not modified.
    required: false
    type: bool
    default: false
  use_max:
    description:
      - If set to C(true), the maximal value will be used or conserved.
      - If the specified value is superior to the value in the file,
        file content is replaced with the new value, else content is not modified.
    required: false
    type: bool
    default: false
  dest:
    type: str
    description:
      - Modify the limits.conf path.
    required: false
    default: "/etc/security/limits.conf"
  comment:
    type: str
    description:
      - Comment associated with the limit.
    required: false
    default: ''
notes:
  - If I(dest) file does not exist, it is created.
'''

EXAMPLES = r'''
- name: Add or modify nofile soft limit for the user joe
  community.general.pam_limits:
    domain: joe
    limit_type: soft
    limit_item: nofile
    value: 64000

- name: Add or modify fsize hard limit for the user smith. Keep or set the maximal value
  community.general.pam_limits:
    domain: smith
    limit_type: hard
    limit_item: fsize
    value: 1000000
    use_max: true

- name: Add or modify memlock, both soft and hard, limit for the user james with a comment
  community.general.pam_limits:
    domain: james
    limit_type: '-'
    limit_item: memlock
    value: unlimited
    comment: unlimited memory lock for james

- name: Add or modify hard nofile limits for wildcard domain
  community.general.pam_limits:
    domain: '*'
    limit_type: hard
    limit_item: nofile
    value: 39693561
'''

import os
import re
import tempfile

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


def _assert_is_valid_value(module, item, value, prefix=''):
    if item in ['nice', 'priority']:
        try:
            valid = -20 <= int(value) <= 19
        except ValueError:
            valid = False
        if not valid:
            module.fail_json(msg="%s Value of %r for item %r is invalid. Value must be a number in the range -20 to 19 inclusive. "
                                 "Refer to the limits.conf(5) manual pages for more details." % (prefix, value, item))
    elif not (value in ['unlimited', 'infinity', '-1'] or value.isdigit()):
        module.fail_json(msg="%s Value of %r for item %r is invalid. Value must either be 'unlimited', 'infinity' or -1, all of "
                             "which indicate no limit, or a limit of 0 or larger. Refer to the limits.conf(5) manual pages for "
                             "more details." % (prefix, value, item))


def main():
    pam_items = ['core', 'data', 'fsize', 'memlock', 'nofile', 'rss', 'stack', 'cpu', 'nproc', 'as', 'maxlogins', 'maxsyslogins', 'priority', 'locks',
                 'sigpending', 'msgqueue', 'nice', 'rtprio', 'chroot']

    pam_types = ['soft', 'hard', '-']

    limits_conf = '/etc/security/limits.conf'

    module = AnsibleModule(
        # not checking because of daisy chain to file module
        argument_spec=dict(
            domain=dict(required=True, type='str'),
            limit_type=dict(required=True, type='str', choices=pam_types),
            limit_item=dict(required=True, type='str', choices=pam_items),
            value=dict(required=True, type='str'),
            use_max=dict(default=False, type='bool'),
            use_min=dict(default=False, type='bool'),
            backup=dict(default=False, type='bool'),
            dest=dict(default=limits_conf, type='str'),
            comment=dict(required=False, default='', type='str')
        ),
        supports_check_mode=True,
    )

    domain = module.params['domain']
    limit_type = module.params['limit_type']
    limit_item = module.params['limit_item']
    value = module.params['value']
    use_max = module.params['use_max']
    use_min = module.params['use_min']
    backup = module.params['backup']
    limits_conf = module.params['dest']
    new_comment = module.params['comment']

    changed = False

    if os.path.isfile(limits_conf):
        if not os.access(limits_conf, os.W_OK):
            module.fail_json(msg="%s is not writable. Use sudo" % limits_conf)
    else:
        limits_conf_dir = os.path.dirname(limits_conf)
        if os.path.isdir(limits_conf_dir) and os.access(limits_conf_dir, os.W_OK):
            open(limits_conf, 'a').close()
            changed = True
        else:
            module.fail_json(msg="directory %s is not writable (check presence, access rights, use sudo)" % limits_conf_dir)

    if use_max and use_min:
        module.fail_json(msg="Cannot use use_min and use_max at the same time.")

    _assert_is_valid_value(module, limit_item, value)

    # Backup
    if backup:
        backup_file = module.backup_local(limits_conf)

    space_pattern = re.compile(r'\s+')

    message = ''
    f = open(limits_conf, 'rb')
    # Tempfile
    nf = tempfile.NamedTemporaryFile(mode='w+')

    found = False
    new_value = value

    for line in f:
        line = to_native(line, errors='surrogate_or_strict')
        if line.startswith('#'):
            nf.write(line)
            continue

        newline = re.sub(space_pattern, ' ', line).strip()
        if not newline:
            nf.write(line)
            continue

        # Remove comment in line
        newline = newline.split('#', 1)[0]
        try:
            old_comment = line.split('#', 1)[1]
        except Exception:
            old_comment = ''

        newline = newline.rstrip()

        if not new_comment:
            new_comment = old_comment

        line_fields = newline.split(' ')

        if len(line_fields) != 4:
            nf.write(line)
            continue

        line_domain = line_fields[0]
        line_type = line_fields[1]
        line_item = line_fields[2]
        actual_value = line_fields[3]

        _assert_is_valid_value(module, line_item, actual_value,
                               prefix="Invalid configuration found in '%s'." % limits_conf)

        # Found the line
        if line_domain == domain and line_type == limit_type and line_item == limit_item:
            found = True
            if value == actual_value:
                message = line
                nf.write(line)
                continue

            if line_type not in ['nice', 'priority']:
                actual_value_unlimited = actual_value in ['unlimited', 'infinity', '-1']
                value_unlimited = value in ['unlimited', 'infinity', '-1']
            else:
                actual_value_unlimited = value_unlimited = False

            if use_max:
                if actual_value_unlimited:
                    new_value = actual_value
                elif value_unlimited:
                    new_value = value
                else:
                    new_value = str(max(int(value), int(actual_value)))

            if use_min:
                if actual_value_unlimited and value_unlimited:
                    new_value = actual_value
                elif actual_value_unlimited:
                    new_value = value
                elif value_unlimited:
                    new_value = actual_value
                else:
                    new_value = str(min(int(value), int(actual_value)))

            # Change line only if value has changed
            if new_value != actual_value:
                changed = True
                if new_comment:
                    new_comment = "\t#" + new_comment
                new_limit = domain + "\t" + limit_type + "\t" + limit_item + "\t" + new_value + new_comment + "\n"
                message = new_limit
                nf.write(new_limit)
            else:
                message = line
                nf.write(line)
        else:
            nf.write(line)

    if not found:
        changed = True
        if new_comment:
            new_comment = "\t#" + new_comment
        new_limit = domain + "\t" + limit_type + "\t" + limit_item + "\t" + new_value + new_comment + "\n"
        message = new_limit
        nf.write(new_limit)

    f.close()
    nf.flush()

    with open(limits_conf, 'r') as content:
        content_current = content.read()

    with open(nf.name, 'r') as content:
        content_new = content.read()

    if not module.check_mode:
        # Copy tempfile to newfile
        module.atomic_move(nf.name, limits_conf)

    try:
        nf.close()
    except Exception:
        pass

    res_args = dict(
        changed=changed,
        msg=message,
        diff=dict(before=content_current, after=content_new),
    )

    if backup:
        res_args['backup_file'] = backup_file

    module.exit_json(**res_args)


if __name__ == '__main__':
    main()

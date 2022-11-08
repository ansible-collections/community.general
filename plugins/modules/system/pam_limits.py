#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2014, Sebastien Rohaut <sebastien.rohaut@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: pam_limits
author:
    - "Sebastien Rohaut (@usawa)"
short_description: Modify Linux PAM limits
description:
     - The C(pam_limits) module modifies PAM limits. The default file is
       C(/etc/security/limits.conf). For the full documentation, see C(man 5
       limits.conf).
options:
  domain:
    description:
      - A username, @groupname, wildcard, uid/gid range.
    required: true
  limit_type:
    description:
      - Limit type, see C(man 5 limits.conf) for an explanation
    required: true
    choices: [ "hard", "soft", "-" ]
  limit_item:
    description:
      - The limit to be set
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
    description:
      - The value of the limit.
    required: true
  backup:
    description:
      - Create a backup file including the timestamp information so you can get
        the original file back if you somehow clobbered it incorrectly.
    required: false
    type: bool
    default: "no"
  use_min:
    description:
      - If set to C(yes), the minimal value will be used or conserved.
        If the specified value is inferior to the value in the file, file content is replaced with the new value,
        else content is not modified.
    required: false
    type: bool
    default: "no"
  use_max:
    description:
      - If set to C(yes), the maximal value will be used or conserved.
        If the specified value is superior to the value in the file, file content is replaced with the new value,
        else content is not modified.
    required: false
    type: bool
    default: "no"
  dest:
    description:
      - Modify the limits.conf path.
    required: false
    default: "/etc/security/limits.conf"
  comment:
    description:
      - Comment associated with the limit.
    required: false
    default: ''
notes:
  - If C(dest) file doesn't exist, it is created.
'''

EXAMPLES = '''
- name: Add or modify nofile soft limit for the user joe
  community.general.pam_limits:
    domain: joe
    limit_type: soft
    limit_item: nofile
    value: 64000

- name: Add or modify fsize hard limit for the user smith. Keep or set the maximal value.
  community.general.pam_limits:
    domain: smith
    limit_type: hard
    limit_item: fsize
    value: 1000000
    use_max: yes

- name: Add or modify memlock, both soft and hard, limit for the user james with a comment.
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
import os.path
import tempfile
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native


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
        )
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

    if not (value in ['unlimited', 'infinity', '-1'] or value.isdigit()):
        module.fail_json(msg="Argument 'value' can be one of 'unlimited', 'infinity', '-1' or positive number. Refer to manual pages for more details.")

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

        if not (actual_value in ['unlimited', 'infinity', '-1'] or actual_value.isdigit()):
            module.fail_json(msg="Invalid configuration of '%s'. Current value of %s is unsupported." % (limits_conf, line_item))

        # Found the line
        if line_domain == domain and line_type == limit_type and line_item == limit_item:
            found = True
            if value == actual_value:
                message = line
                nf.write(line)
                continue

            actual_value_unlimited = actual_value in ['unlimited', 'infinity', '-1']
            value_unlimited = value in ['unlimited', 'infinity', '-1']

            if use_max:
                if value.isdigit() and actual_value.isdigit():
                    new_value = str(max(int(value), int(actual_value)))
                elif actual_value_unlimited:
                    new_value = actual_value
                else:
                    new_value = value

            if use_min:
                if value.isdigit() and actual_value.isdigit():
                    new_value = str(min(int(value), int(actual_value)))
                elif value_unlimited:
                    new_value = actual_value
                else:
                    new_value = value

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

    # Copy tempfile to newfile
    module.atomic_move(nf.name, f.name)

    try:
        nf.close()
    except Exception:
        pass

    res_args = dict(
        changed=changed, msg=message
    )

    if backup:
        res_args['backup_file'] = backup_file

    module.exit_json(**res_args)


if __name__ == '__main__':
    main()

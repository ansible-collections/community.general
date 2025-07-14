#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, Jan-Piet Mens <jpmens () gmail.com>
# Copyright (c) 2015, Ales Nosek <anosek.nosek () gmail.com>
# Copyright (c) 2017, Ansible Project
# Copyright (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: ini_file
short_description: Tweak settings in INI files
extends_documentation_fragment:
  - files
  - community.general.attributes
description:
  - Manage (add, remove, change) individual settings in an INI-style file without having to manage the file as a whole with,
    say, M(ansible.builtin.template) or M(ansible.builtin.assemble).
  - Adds missing sections if they do not exist.
  - This module adds missing ending newlines to files to keep in line with the POSIX standard, even when no other modifications
    need to be applied.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  path:
    description:
      - Path to the INI-style file; this file is created if required.
    type: path
    required: true
    aliases: [dest]
  section:
    description:
      - Section name in INI file. This is added if O(state=present) automatically when a single value is being set.
      - If being omitted, the O(option) is placed before the first O(section).
      - Omitting O(section) is also required if the config format does not support sections.
    type: str
  section_has_values:
    type: list
    elements: dict
    required: false
    suboptions:
      option:
        type: str
        description: Matching O(section) must contain this option.
        required: true
      value:
        type: str
        description: Matching O(section_has_values[].option) must have this specific value.
      values:
        description:
          - The string value to be associated with an O(section_has_values[].option).
          - Mutually exclusive with O(section_has_values[].value).
          - O(section_has_values[].value=v) is equivalent to O(section_has_values[].values=[v]).
        type: list
        elements: str
    description:
      - Among possibly multiple sections of the same name, select the first one that contains matching options and values.
      - With O(state=present), if a suitable section is not found, a new section is added, including the required options.
      - With O(state=absent), at most one O(section) is removed if it contains the values.
    version_added: 8.6.0
  option:
    description:
      - If set (required for changing a O(value)), this is the name of the option.
      - May be omitted if adding/removing a whole O(section).
    type: str
  value:
    description:
      - The string value to be associated with an O(option).
      - May be omitted when removing an O(option).
      - Mutually exclusive with O(values).
      - O(value=v) is equivalent to O(values=[v]).
    type: str
  values:
    description:
      - The string value to be associated with an O(option).
      - May be omitted when removing an O(option).
      - Mutually exclusive with O(value).
      - O(value=v) is equivalent to O(values=[v]).
    type: list
    elements: str
    version_added: 3.6.0
  backup:
    description:
      - Create a backup file including the timestamp information so you can get the original file back if you somehow clobbered
        it incorrectly.
    type: bool
    default: false
  state:
    description:
      - If set to V(absent) and O(exclusive) set to V(true) all matching O(option) lines are removed.
      - If set to V(absent) and O(exclusive) set to V(false) the specified O(option=value) lines are removed, but the other
        O(option)s with the same name are not touched.
      - If set to V(present) and O(exclusive) set to V(false) the specified O(option=values) lines are added, but the other
        O(option)s with the same name are not touched.
      - If set to V(present) and O(exclusive) set to V(true) all given O(option=values) lines are added and the other O(option)s
        with the same name are removed.
    type: str
    choices: [absent, present]
    default: present
  exclusive:
    description:
      - If set to V(true) (default), all matching O(option) lines are removed when O(state=absent), or replaced when O(state=present).
      - If set to V(false), only the specified O(value)/O(values) are added when O(state=present), or removed when O(state=absent),
        and existing ones are not modified.
    type: bool
    default: true
    version_added: 3.6.0
  no_extra_spaces:
    description:
      - Do not insert spaces before and after '=' symbol.
    type: bool
    default: false
  ignore_spaces:
    description:
      - Do not change a line if doing so would only add or remove spaces before or after the V(=) symbol.
    type: bool
    default: false
    version_added: 7.5.0
  create:
    description:
      - If set to V(false), the module fails if the file does not already exist.
      - By default it creates the file if it is missing.
    type: bool
    default: true
  allow_no_value:
    description:
      - Allow option without value and without '=' symbol.
    type: bool
    default: false
  modify_inactive_option:
    description:
      - By default the module replaces a commented line that matches the given option.
      - Set this option to V(false) to avoid this. This is useful when you want to keep commented example C(key=value) pairs
        for documentation purposes.
    type: bool
    default: true
    version_added: 8.0.0
  follow:
    description:
      - This flag indicates that filesystem links, if they exist, should be followed.
      - O(follow=true) can modify O(path) when combined with parameters such as O(mode).
    type: bool
    default: false
    version_added: 7.1.0
notes:
  - While it is possible to add an O(option) without specifying a O(value), this makes no sense.
  - As of community.general 3.2.0, UTF-8 BOM markers are discarded when reading files.
author:
  - Jan-Piet Mens (@jpmens)
  - Ales Nosek (@noseka1)
"""

EXAMPLES = r"""
- name: Ensure "fav=lemonade is in section "[drinks]" in specified file
  community.general.ini_file:
    path: /etc/conf
    section: drinks
    option: fav
    value: lemonade
    mode: '0600'
    backup: true

- name: Ensure "temperature=cold is in section "[drinks]" in specified file
  community.general.ini_file:
    path: /etc/anotherconf
    section: drinks
    option: temperature
    value: cold
    backup: true

- name: Add "beverage=lemon juice" is in section "[drinks]" in specified file
  community.general.ini_file:
    path: /etc/conf
    section: drinks
    option: beverage
    value: lemon juice
    mode: '0600'
    state: present
    exclusive: false

- name: Ensure multiple values "beverage=coke" and "beverage=pepsi" are in section "[drinks]" in specified file
  community.general.ini_file:
    path: /etc/conf
    section: drinks
    option: beverage
    values:
      - coke
      - pepsi
    mode: '0600'
    state: present

- name: Add "beverage=lemon juice" outside a section in specified file
  community.general.ini_file:
    path: /etc/conf
    option: beverage
    value: lemon juice
    state: present

- name: Remove the peer configuration for 10.128.0.11/32
  community.general.ini_file:
    path: /etc/wireguard/wg0.conf
    section: Peer
    section_has_values:
      - option: AllowedIps
        value: 10.128.0.11/32
    mode: '0600'
    state: absent

- name: Add "beverage=lemon juice" outside a section in specified file
  community.general.ini_file:
    path: /etc/conf
    option: beverage
    value: lemon juice
    state: present

- name: Update the public key for peer 10.128.0.12/32
  community.general.ini_file:
    path: /etc/wireguard/wg0.conf
    section: Peer
    section_has_values:
      - option: AllowedIps
        value: 10.128.0.12/32
    option: PublicKey
    value: xxxxxxxxxxxxxxxxxxxx
    mode: '0600'
    state: present

- name: Remove the peer configuration for 10.128.0.11/32
  community.general.ini_file:
    path: /etc/wireguard/wg0.conf
    section: Peer
    section_has_values:
      - option: AllowedIps
        value: 10.4.0.11/32
    mode: '0600'
    state: absent

- name: Update the public key for peer 10.128.0.12/32
  community.general.ini_file:
    path: /etc/wireguard/wg0.conf
    section: Peer
    section_has_values:
      - option: AllowedIps
        value: 10.4.0.12/32
    option: PublicKey
    value: xxxxxxxxxxxxxxxxxxxx
    mode: '0600'
    state: present
"""

import io
import os
import re
import tempfile
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_bytes, to_text


def match_opt(option, line):
    option = re.escape(option)
    return re.match('( |\t)*([#;]?)( |\t)*(%s)( |\t)*(=|$)( |\t)*(.*)' % option, line)


def match_active_opt(option, line):
    option = re.escape(option)
    return re.match('()()( |\t)*(%s)( |\t)*(=|$)( |\t)*(.*)' % option, line)


def update_section_line(option, changed, section_lines, index, changed_lines, ignore_spaces, newline, msg):
    option_changed = None
    if ignore_spaces:
        old_match = match_opt(option, section_lines[index])
        if not old_match.group(2):
            new_match = match_opt(option, newline)
            option_changed = old_match.group(8) != new_match.group(8)
    if option_changed is None:
        option_changed = section_lines[index] != newline
    if option_changed:
        section_lines[index] = newline
    changed = changed or option_changed
    if option_changed:
        msg = 'option changed'
    changed_lines[index] = 1
    return (changed, msg)


def check_section_has_values(section_has_values, section_lines):
    if section_has_values is not None:
        for condition in section_has_values:
            for line in section_lines:
                match = match_opt(condition["option"], line)
                if match and (len(condition["values"]) == 0 or match.group(8) in condition["values"]):
                    break
            else:
                return False
    return True


def do_ini(module, filename, section=None, section_has_values=None, option=None, values=None,
           state='present', exclusive=True, backup=False, no_extra_spaces=False,
           ignore_spaces=False, create=True, allow_no_value=False, modify_inactive_option=True, follow=False):

    if section is not None:
        section = to_text(section)
    if option is not None:
        option = to_text(option)

    # deduplicate entries in values
    values_unique = []
    [values_unique.append(to_text(value)) for value in values if value not in values_unique and value is not None]
    values = values_unique

    diff = dict(
        before='',
        after='',
        before_header='%s (content)' % filename,
        after_header='%s (content)' % filename,
    )

    if follow and os.path.islink(filename):
        target_filename = os.path.realpath(filename)
    else:
        target_filename = filename

    if not os.path.exists(target_filename):
        if not create:
            module.fail_json(rc=257, msg='Destination %s does not exist!' % target_filename)
        destpath = os.path.dirname(target_filename)
        if not os.path.exists(destpath) and not module.check_mode:
            os.makedirs(destpath)
        ini_lines = []
    else:
        with io.open(target_filename, 'r', encoding="utf-8-sig") as ini_file:
            ini_lines = [to_text(line) for line in ini_file.readlines()]

    if module._diff:
        diff['before'] = u''.join(ini_lines)

    changed = False

    # ini file could be empty
    if not ini_lines:
        ini_lines.append(u'\n')

    # last line of file may not contain a trailing newline
    if ini_lines[-1] == u"" or ini_lines[-1][-1] != u'\n':
        ini_lines[-1] += u'\n'
        changed = True

    # append fake section lines to simplify the logic
    # At top:
    # Fake random section to do not match any other in the file
    # Using commit hash as fake section name
    fake_section_name = u"ad01e11446efb704fcdbdb21f2c43757423d91c5"

    # Insert it at the beginning
    ini_lines.insert(0, u'[%s]' % fake_section_name)

    # At bottom:
    ini_lines.append(u'[')

    # If no section is defined, fake section is used
    if not section:
        section = fake_section_name

    within_section = not section
    section_start = section_end = 0
    msg = 'OK'
    if no_extra_spaces:
        assignment_format = u'%s=%s\n'
    else:
        assignment_format = u'%s = %s\n'

    option_no_value_present = False

    non_blank_non_comment_pattern = re.compile(to_text(r'^[ \t]*([#;].*)?$'))

    before = after = []
    section_lines = []

    section_pattern = re.compile(to_text(r'^\[\s*%s\s*]' % re.escape(section.strip())))

    for index, line in enumerate(ini_lines):
        # end of section:
        if within_section and line.startswith(u'['):
            if check_section_has_values(
                section_has_values, ini_lines[section_start:index]
            ):
                section_end = index
                break
            else:
                # look for another section
                within_section = False
                section_start = section_end = 0

        # find start and end of section
        if section_pattern.match(line):
            within_section = True
            section_start = index

    before = ini_lines[0:section_start]
    section_lines = ini_lines[section_start:section_end]
    after = ini_lines[section_end:len(ini_lines)]

    # Keep track of changed section_lines
    changed_lines = [0] * len(section_lines)

    # Determine whether to consider using commented out/inactive options or only active ones
    if modify_inactive_option:
        match_function = match_opt
    else:
        match_function = match_active_opt

    # handling multiple instances of option=value when state is 'present' with/without exclusive is a bit complex
    #
    # 1. edit all lines where we have a option=value pair with a matching value in values[]
    # 2. edit all the remaining lines where we have a matching option
    # 3. delete remaining lines where we have a matching option
    # 4. insert missing option line(s) at the end of the section

    if state == 'present' and option:
        for index, line in enumerate(section_lines):
            if match_function(option, line):
                match = match_function(option, line)
                if values and match.group(8) in values:
                    matched_value = match.group(8)
                    if not matched_value and allow_no_value:
                        # replace existing option with no value line(s)
                        newline = u'%s\n' % option
                        option_no_value_present = True
                    else:
                        # replace existing option=value line(s)
                        newline = assignment_format % (option, matched_value)
                    (changed, msg) = update_section_line(option, changed, section_lines, index, changed_lines, ignore_spaces, newline, msg)
                    values.remove(matched_value)
                elif not values and allow_no_value:
                    # replace existing option with no value line(s)
                    newline = u'%s\n' % option
                    (changed, msg) = update_section_line(option, changed, section_lines, index, changed_lines, ignore_spaces, newline, msg)
                    option_no_value_present = True
                    break

    if state == 'present' and exclusive and not allow_no_value:
        # override option with no value to option with value if not allow_no_value
        if len(values) > 0:
            for index, line in enumerate(section_lines):
                if not changed_lines[index] and match_function(option, line):
                    newline = assignment_format % (option, values.pop(0))
                    (changed, msg) = update_section_line(option, changed, section_lines, index, changed_lines, ignore_spaces, newline, msg)
                    if len(values) == 0:
                        break
        # remove all remaining option occurrences from the rest of the section
        for index in range(len(section_lines) - 1, 0, -1):
            if not changed_lines[index] and match_function(option, section_lines[index]):
                del section_lines[index]
                del changed_lines[index]
                changed = True
                msg = 'option changed'

    if state == 'present':
        # insert missing option line(s) at the end of the section
        for index in range(len(section_lines), 0, -1):
            # search backwards for previous non-blank or non-comment line
            if not non_blank_non_comment_pattern.match(section_lines[index - 1]):
                if option and values:
                    # insert option line(s)
                    for element in values[::-1]:
                        # items are added backwards, so traverse the list backwards to not confuse the user
                        # otherwise some of their options might appear in reverse order for whatever fancy reason ¯\_(ツ)_/¯
                        if element is not None:
                            # insert option=value line
                            section_lines.insert(index, assignment_format % (option, element))
                            msg = 'option added'
                            changed = True
                        elif element is None and allow_no_value:
                            # insert option with no value line
                            section_lines.insert(index, u'%s\n' % option)
                            msg = 'option added'
                            changed = True
                elif option and not values and allow_no_value and not option_no_value_present:
                    # insert option with no value line(s)
                    section_lines.insert(index, u'%s\n' % option)
                    msg = 'option added'
                    changed = True
                break

    if state == 'absent':
        if option:
            if exclusive:
                # delete all option line(s) with given option and ignore value
                new_section_lines = [line for line in section_lines if not (match_active_opt(option, line))]
                if section_lines != new_section_lines:
                    changed = True
                    msg = 'option changed'
                    section_lines = new_section_lines
            elif not exclusive and len(values) > 0:
                # delete specified option=value line(s)
                new_section_lines = [i for i in section_lines if not (match_active_opt(option, i) and match_active_opt(option, i).group(8) in values)]
                if section_lines != new_section_lines:
                    changed = True
                    msg = 'option changed'
                    section_lines = new_section_lines
        else:
            # drop the entire section
            if section_lines:
                section_lines = []
                msg = 'section removed'
                changed = True

    # reassemble the ini_lines after manipulation
    ini_lines = before + section_lines + after

    # remove the fake section line
    del ini_lines[0]
    del ini_lines[-1:]

    if not within_section and state == 'present':
        ini_lines.append(u'[%s]\n' % section)
        msg = 'section and option added'
        if section_has_values:
            for condition in section_has_values:
                if condition['option'] != option:
                    if len(condition['values']) > 0:
                        for value in condition['values']:
                            ini_lines.append(assignment_format % (condition['option'], value))
                    elif allow_no_value:
                        ini_lines.append(u'%s\n' % condition['option'])
                elif not exclusive:
                    for value in condition['values']:
                        if value not in values:
                            values.append(value)
        if option and values:
            for value in values:
                ini_lines.append(assignment_format % (option, value))
        elif option and not values and allow_no_value:
            ini_lines.append(u'%s\n' % option)
        else:
            msg = 'only section added'
        changed = True

    if module._diff:
        diff['after'] = u''.join(ini_lines)

    backup_file = None
    if changed and not module.check_mode:
        if backup:
            backup_file = module.backup_local(target_filename)

        encoded_ini_lines = [to_bytes(line) for line in ini_lines]
        try:
            tmpfd, tmpfile = tempfile.mkstemp(dir=module.tmpdir)
            f = os.fdopen(tmpfd, 'wb')
            f.writelines(encoded_ini_lines)
            f.close()
        except IOError:
            module.fail_json(msg="Unable to create temporary file %s", traceback=traceback.format_exc())

        try:
            module.atomic_move(tmpfile, os.path.abspath(target_filename))
        except IOError:
            module.ansible.fail_json(msg='Unable to move temporary \
                                   file %s to %s, IOError' % (tmpfile, target_filename), traceback=traceback.format_exc())

    return (changed, backup_file, diff, msg)


def main():

    module = AnsibleModule(
        argument_spec=dict(
            path=dict(type='path', required=True, aliases=['dest']),
            section=dict(type='str'),
            section_has_values=dict(type='list', elements='dict', options=dict(
                option=dict(type='str', required=True),
                value=dict(type='str'),
                values=dict(type='list', elements='str')
            ), default=None, mutually_exclusive=[['value', 'values']]),
            option=dict(type='str'),
            value=dict(type='str'),
            values=dict(type='list', elements='str'),
            backup=dict(type='bool', default=False),
            state=dict(type='str', default='present', choices=['absent', 'present']),
            exclusive=dict(type='bool', default=True),
            no_extra_spaces=dict(type='bool', default=False),
            ignore_spaces=dict(type='bool', default=False),
            allow_no_value=dict(type='bool', default=False),
            modify_inactive_option=dict(type='bool', default=True),
            create=dict(type='bool', default=True),
            follow=dict(type='bool', default=False)
        ),
        mutually_exclusive=[
            ['value', 'values']
        ],
        add_file_common_args=True,
        supports_check_mode=True,
    )

    path = module.params['path']
    section = module.params['section']
    section_has_values = module.params['section_has_values']
    option = module.params['option']
    value = module.params['value']
    values = module.params['values']
    state = module.params['state']
    exclusive = module.params['exclusive']
    backup = module.params['backup']
    no_extra_spaces = module.params['no_extra_spaces']
    ignore_spaces = module.params['ignore_spaces']
    allow_no_value = module.params['allow_no_value']
    modify_inactive_option = module.params['modify_inactive_option']
    create = module.params['create']
    follow = module.params['follow']

    if state == 'present' and not allow_no_value and value is None and not values:
        module.fail_json(msg="Parameter 'value(s)' must be defined if state=present and allow_no_value=False.")

    if value is not None:
        values = [value]
    elif values is None:
        values = []

    if section_has_values:
        for condition in section_has_values:
            if condition['value'] is not None:
                condition['values'] = [condition['value']]
            elif condition['values'] is None:
                condition['values'] = []
#        raise Exception("section_has_values: {}".format(section_has_values))

    (changed, backup_file, diff, msg) = do_ini(
        module, path, section, section_has_values, option, values, state, exclusive, backup,
        no_extra_spaces, ignore_spaces, create, allow_no_value, modify_inactive_option, follow)

    if not module.check_mode and os.path.exists(path):
        file_args = module.load_file_common_arguments(module.params)
        changed = module.set_fs_attributes_if_different(file_args, changed)

    results = dict(
        changed=changed,
        diff=diff,
        msg=msg,
        path=path,
    )
    if backup_file is not None:
        results['backup_file'] = backup_file

    # Mission complete
    module.exit_json(**results)


if __name__ == '__main__':
    main()

#!/usr/bin/python

# SPDX-FileCopyrightText: 2022, David Peng <dpeng1@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: greppy

short_description: Scan logs for certain patterns within a given timeframe

description: 
    - >
        Grep logs for a list of patterns within a given timeframe. If given, also excludes 
        a list of patterns from the file. Returns a list of matching strings, along with 
        a count of both matched and excluded patterns.

options:
    path:
        description: The file to grep.
        required: true
        type: path
    search:
        description: The literal string to look for in every line of the file. This does not have to match the entire line.
        required: true
        type: list
        elements: str
    exclude:
        description: The literal string to exclude from the file. This does not have to match the entire line.
        required: false
        type: list
        elements: str
    timeout:
        description: The number of seconds to wait on file that is continually being written to.
        required: false
        default: 60
        type: int
    ignore_case:
        description: Case insensitive regex search.
        required: false
        type: bool
    find_only_first:
        description: Exit right after finding the first occurrence.
        required: false
        default: false
        type: bool

author:
    - David Peng (@dpengftw)
'''

EXAMPLES = '''
- name: Grep for strings in given list but also exclude certain strings
  community.general.greppy:
    path: example.txt
    search:
      - first string
      - second string
    exclude:
      - third
      - fourth

- name: Grep for strings and wait for 120 seconds
  community.general.greppy:
    path: example.txt
    search:
      - first string
    timeout: 120

- name: Grep for first occurrence then exit
  community.general.greppy:
    path: example.txt
    search:
      - first occurrence
    find_only_first: true

'''

RETURN = '''
output:
    description: List of lines that matched given search.
    type: list
    returned: always
    sample: [
            "Ex eorum enim scriptis et institutis cum omnis doctrina liberalis, omnis historia.\n",
            "Esse enim quam vellet iniquus iustus poterat inpune.\n"
        ]

matches:
    description: Number of lines that matched.
    type: int
    returned: always
    sample: 2

exclude_matches:
    description: Number of lines that matched the exclusion strings.
    type: int
    sample: 1
'''

import re
import os
import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native
from ansible.module_utils.common.text.converters import to_text

def run_checks(module):
    """Do baseline checks before proceeding."""
    params = module.params
    path = params['path']

    b_dest = to_bytes(path, errors='surrogate_or_strict')
    if os.path.isdir(b_dest):
        module.fail_json(rc=256, msg='Destination %s is a directory!' % path)

    time_to_wait = 3
    time_counter = 0
    while not os.path.exists(path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            module.fail_json(rc=256, msg='Destination %s does not exist!' % path)

def search_line(pattern, string):
    """Find pattern match in string."""
    if type(string) is bytes:
        pc = re.compile(bytes(pattern, "utf-8"))
    else:
        pc = re.compile(to_text(pattern))

    if re.search(pc, string):
        return string
    else:
        return None

def grep_file(filename, patterns, excludes, ignore_case, timeout, find_only_first):
    """Search a single file."""
    file = open(filename, 'rb')
    result = {
        'output': [],
        'exclude_matches': 0,
        'matches': 0
    }

    timeout_start = time.time()

    while time.time() < timeout_start + timeout:
        line = file.readline()
        continue_while = False

        # skip on exclude patterns
        for e in (excludes or []):
            if ignore_case:
                e = e.lower()
                lower_case_line = line.lower()
            if search_line(e, lower_case_line):
                continue_while = True
                result['exclude_matches'] += 1
                break

        if continue_while:
            continue

        for p in patterns:
            if ignore_case:
                p = p.lower()
                lower_case_line = line.lower()
            found_line = search_line(p, lower_case_line)
            if found_line:
                result['output'].append(line)
                result['matches'] += 1
                if find_only_first:
                    return result

    result['matches'] = len(result['output'])
    file.close()
    return result


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        path=dict(type='path', aliases=['src'], required=True),
        search=dict(type='list', required=True),
        exclude=dict(type='list', required=False),
        ignore_case=dict(type='bool', required=False, default=False),
        find_only_first=dict(type='bool', required=False, default=False),
        timeout=dict(type='int', required=False, default=60)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        output=[],
        matches=0,
        exclude_matches=0
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    run_checks(module)
    result = grep_file(module.params['path'], 
        module.params['search'],
        module.params['exclude'],
        module.params['ignore_case'],
        module.params['timeout'],
        module.params['find_only_first'])

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()

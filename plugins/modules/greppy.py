#!/usr/bin/python

# Copyright: (c) 2022, David Peng <dpeng1@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: greppy

short_description: Scan logs for certain patterns within a given timeframe.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: Grep logs for a list of patterns within a given timeframe.

options:
    path:
        description: The file to grep.
        required: true
        type: path
    search:
        description: The literal string to look for in every line of the file. This does not have to match the entire line.
        required: true
        type: list
    exclude:
        description: The literal string to exclude from the file. This does not have to match the entire line.
        required: false
        type: list
    timeout:
        description: The number of seconds to wait.
        required: false
        type: int
    ignore_case:
        description: Case insensitive regex search.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - David Peng (@dpengftw)
'''

EXAMPLES = r'''
- name: Grep for strings in given list but also exclude certain strings
  my_namespace.my_collection.greppy:
    path: example.txt
    search:
      - first string
      - second string
    exclude:
      - third

- name: Grep for strings and wait for 120 seconds
  my_namespace.my_collection.greppy:
    path: example.txt
    search:
      - first string
    timeout: 120

'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
output:
    description: List of lines that matched given search
    type: list
    returned: always
    sample:
        "output": [
            "Ex eorum enim scriptis et institutis cum omnis doctrina liberalis, omnis historia.\n",
            "Esse enim quam vellet iniquus iustus poterat inpune.\n"
        ]

matches:
    description: Number of lines that matched
    type: int
    returned: always
    sample: "matches": 2

'''

import re
import os
import time

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes, to_native

def run_checks(module):
    params = module.params
    path = params['path']

    b_dest = to_bytes(path, errors='surrogate_or_strict')
    if os.path.isdir(b_dest):
        module.fail_json(rc=256, msg='Destination %s is a directory !' % path)


def search_line(pattern, string, ignore_case):
    """Find pattern match in string."""
    if ignore_case:
        pattern = pattern.lower()
        string = string.lower()

    mo = re.search(pattern, string)
    if mo:
        return string
    else:
        return None

def grep_file(filename, patterns, excludes, ignore_case, timeout, findexit):
    """Search a single file or standard input."""
    file = open(filename, 'r')
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
            if search_line(re.compile(e), line, ignore_case):
                continue_while = True
                result['exclude_matches'] += 1
                break

        if continue_while:
            continue

        for p in patterns:
            found_line = search_line(re.compile(p), line, ignore_case)
            if found_line != None:
                result['output'].append(found_line)
                result['matches'] += 1
                if findexit:
                    return result

    result['matches'] = len(result['output'])
    return result


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        path=dict(type='path', aliases=['src'], required=True),
        search=dict(type='list', required=True),
        exclude=dict(type='list', required=False),
        ignore_case=dict(type='bool', required=False, default=False),
        findexit=dict(type='bool', required=False, default=False),
        timeout=dict(type='int', required=False, default=60)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
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
    result = grep_file(module.params['path'], module.params['search'], 
        module.params['exclude'], module.params['ignore_case'], 
        module.params['timeout'], module.params['findexit'])
    result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    #if module.params['name'] == 'fail me':
    #    module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
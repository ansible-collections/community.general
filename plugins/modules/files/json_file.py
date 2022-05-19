#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import os

from ansible_collections.community.general.plugins.module_utils.common.validation import check_type_dict_or_list
from ansible_collections.community.general.plugins.module_utils.mh.module_helper_dest_file import (
    DestFileModuleHelper,
    ModuleHelperException,
)
from ansible_collections.community.general.plugins.module_utils.data_merge_utils import (
    DataMergeUtils,
)


DOCUMENTATION = r'''
---
module: json_file
short_description: Managage (add, remove, update) elements in a JSON file.
description:
  - This module ensures that a set of values is present or absent in a JSON
    file.
  - The check can be done in all childrens of an object.
  - It also makes sure a value is present or absent in a list or in a
    specific index of the list.
  - In background, this module use the python JSON lib
    U(https://docs.python.org/3/library/json.html).
notes:
  - Take note of the following warning before using this module, B(if you have
    some comments in your JSON file, this module will not preserve them !) So
    don't use it if it's important for you to keep these comments.
  - This module supports C(--check) and C(--diff) flags.
options:
  path:
    description:
      - Absolute path of the JSON file.
    type: path
    required: true
    alias: [ dest ]
  state:
    description:
      - If set to C(present), that ensure the values are present in the JSON
        file. If the JSON file contain datas that are not present in the
        expected values, they will not be modified (this only ensure
        that the expected datas are presents).
      - If set to C(absent), that ensure the values are absent in the JSON
        file.
      - If set to C(identic), that ensure the values in the JSON are identic to
        those provided in arguments. If the JSON file contain datas that are
        not present in the expected values they will be removed (this ensure
        that the datas in the file are exactly the same as the expected datas).
    type: str
    choices: [ present, absent, identic ]
    default: present
  list_diff_type:
    description:
      - This describes how the list are compared.
      - If set to C(value), it checks if a value is present in the list
        elements.  With this, you can't check a list element in another list
        element.  Only the first level of a list can be checked.
      - If set to C(index), the value in a list are compared by their index.
        With this, you can check an element in another list, but you make sure
        that the expected value is at this position in the list.
    type: str
    choices: [ value, index ]
    default: value
  value:
    description:
      - The values that you want to compare with the one present in the JSON
        file.
    type: dict
    required: true
  create:
    description:
      - If set to C(no), the module will fail if the JSON file not exists.
        Else, the JSON file will be created.
    type: bool
    default: false
  diff_on_value:
    description:
      - This describes how check the if it has a difference between the datas
        present in the JSON file and the expected values. This will also
        impact the output in diff mode (in a case you get indents or lines
        breaks in the diff will in the other you only gets values).
      - If set to C(true), it checks the difference by only comparing the
        values of elements in the JSON file and in the expected datas. In this
        case, change indentation or sort keys will not be considered as a
        change on the file will the values are the sames (just like any other
        difference in JSON file unrelated to values of elements like line
        breaks or comments).
      - If set to C(false), it checks the difference by comparing the lines
        output with the actual lines in the JSON file. In this case, all the
        change on the indentation or on the sort keys will be considered as a
        change on the file even if it has no difference on the values (if a
        comment, or an empty line break is present in the file, a change will
        be detected).
    type: bool
    default: true
  backup:
    description:
      - Create a backup file including the timestamp information so you can get
        the original file back if you somehow clobbered it incorrectly.
    type: bool
    default: no
  indent:
    description:
      - Set the indentation for elements in the JSON file.
        See U(https://docs.python.org/3/library/json.html#basic-usage).
    type: int
    default: 4
  sort_keys:
    description:
      - If set to C(true), the values in the will sorted by their keys.
        See U(https://docs.python.org/3/library/json.html#basic-usage).
    type: bool
    default: false
author:
    - DEMAREST Maxime (@indelog) <maxime@indelog.fr>
'''

EXAMPLES = r'''
# We consider the following content in /my/dest/file.json on the remote host :
# {
#    "A": 1,
#    "B": 2,
#    "C": {
#        "D": 3,
#        "E": [
#            4,
#            5,
#            6
#        ]
#    }
# }
# The values are kept in all samples.

- name: "Ensure values are present in the JSON."
  community.general.json_file:
    path: "/my/dest/file.json"
    value:
      B: 3
      C:
       F: 8
    state: "present"
# {'B': 3} and {'C':{'F': 8}} are not present in the original values, they will
# be added.
# There is no change.
# Get the following content in /my/dest/file.json :
# {
#    "A": 1,
#    "B": 3,
#    "C": {
#        "D": 3,
#        "E": [
#            4,
#            5,
#            6
#        ],
#        "F": 8
#    }
# }

- name: "Ensure values are absent in the JSON file files."
  community.general.json_file:
    path: "/my/dest/file.json"
    value:
      B: 3
      C:
       F: 8
    state: "absent"
# {'B': 3} and {'C':{'F': 8}} are not present in the original values, so there
# is no change.
# There is no change.
# Get the following content in /my/dest/file.json :
# {
#   "A": 1,
#   "B": 2,
#   "C": {
#       "D": 3,
#       "E": [
#           4,
#           5,
#           6
#       ]
#   }
# }

- name: "Ensure values are absent in the JSON file files."
  community.general.json_file:
    path: "/my/dest/file.json"
    value:
      B: 2
      C:
       D: 3
    state: "absent"
# {'B': 2} and {'C':{'D': 3}} are present in the original values, so it will
# be removed.
# There is no change.
# Get the following content in /my/dest/file.json :
# {
#   "A": 1,
#   "C": {
#       "E": [
#           4,
#           5,
#           6
#       ]
#   }
# }

- name: "Ensure values are identic in the JSON file files."
  community.general.json_file:
    path: "/my/dest/file.json"
    value:
      B: 4
      C:
       D: 6
      Z: 8
    state: "identic"
# In the original values, 5 is already present in C.D.
# There is a change..
# Get the following content in /my/dest/file.json :
# {
#    "B": 4,
#    "C": {
#        "D": 6
#    },
#    "Z": 8
# }

- name: "Ensure values are present in a list."
  community.general.json_file:
    path: "/my/dest/file.json"
    value:
      C:
       E:
        - 5
    state: "present"
# In the original values, 5 is already present in C.D.
# There is no change.
# Get the following content in /my/dest/file.json :
# {
#    "A": 1,
#    "B": 3,
#    "C": {
#        "D": 3,
#        "E": [
#            4,
#            5,
#            6
#        ],
#        "F": 7
#    }
# }

- name: "Ensure values are present in a list."
  community.general.json_file:
    path: "/my/dest/file.json"
    value:
      C:
       E:
        - 7
    state: "present"
# In the original values, 7 is not present in C.D, it will be added.
# There is a change.
# Get the following content in /my/dest/file.json :
# {
#    "A": 1,
#    "B": 3,
#    "C": {
#        "D": 3,
#        "E": [
#            4,
#            5,
#            6,
#            7
#        ],
#        "F": 7
#    }
# }

- name: "Ensure values are absent in a list."
  community.general.json_file:
    path: "/my/dest/file.json"
    value:
      C:
       E:
        - 6
    state: "absent"
# In the orginal values, 6 is present in C.D, it will be removed.
# There is a change.
# Get the following content in /my/dest/file.json :
# {
#    "A": 1,
#    "B": 3,
#    "C": {
#        "D": 3,
#        "E": [
#            4,
#            5
#        ],
#        "F": 7
#    }
# }

- name: "Ensure values are present depending their index in a list."
  community.general.json_file:
    path: "/my/dest/file.json"
    list_diff_type: index
    value:
      C:
       E:
        -
        - 7
    state: "present"
# In the original value, the second index for C.E list is not 7, values will
# be updated.
# Note, if you do not want to change the value in on some check you can set it
# to none like the first index of C.E in the previous sample.
# There is a change.
# Get the following content in /my/dest/file.json :
# {
#    "A": 1,
#    "B": 2,
#    "C": {
#        "D": 3,
#        "E": [
#            4,
#            7,
#            6
#        ]
#    }
# }

- name: "Ensure values are absent depending their index in a list."
  community.general.json_file:
    path: "/my/dest/file.json"
    list_diff_type: index
    value:
      C:
       E:
        -
        - 7
        - 6
    state: "absent"
# In the original datas, the second value of C.E list is not 7 so it will be
# keept, but the third value is 6, so it will be removed.
# Note, if you do not want to change the value in on some check you can set it
# to none like the first index of C.E in the previous sample.
# There is a change.
# Get the following content in /my/dest/file.json :
# {
#    "A": 1,
#    "B": 2,
#    "C": {
#        "D": 3,
#        "E": [
#            4,
#            5
#        ]
#    }
# }

- name: "Ensure values are present in the JSON diff, check only on values."
  community.general.json_file:
    path: "/my/dest/file.json"
    indent: 2
    value:
      A: 1
    state: "present"
# We will change the indent but when the change are only detected on the values
# the JSON file will not be update ("A": 1 is already in the originals values).
# There is no change.
# Get the following content in /my/dest/file.json :
# {
#    "A": 1,
#    "B": 3,
#    "C": {
#        "D": 3,
#        "E": [
#            4,
#            5,
#            6
#        ],
#        "F": 7
#    }
# }

- name: "Ensure values are present in the JSON diff, also check file format."
  community.general.json_file:
    path: "/my/dest/file.json"
    indent: 2
    diff_on_value: false
    value:
      A: 1
    state: "present"
# There is not diff in the values but the file format is changed (intent 4
# There is a change.
# Get the following content in /my/dest/file.json :
to 2).
#{
#  "A": 1,
#  "B": 2,
#  "C": {
#    "D": 3,
#    "E": [
#      4,
#      5,
#      6
#    ]
#  }
#}
'''

RETURN = r'''
  changed:
    description:
      - Indicate whether the JSON file is changed or not.
    returned: always
    type: bool
  created:
    description:
      - Indicate if the file JSON is created or not.
    returned: success
    type: bool
  diff:
    description:
      - Contain a dict with two elements, C(after) contain the value after
        the change and C(before) contain values before the change.
    returned: changed
    type: dict
  failed:
    description:
      - Indicate if the module has failed or not.
    returned: always
    type: bool
  result:
    description:
      - Contain the values that are finally present in the JSON file.
    returned: success
    type: dict
'''


class JsonFile(DestFileModuleHelper):

    module = dict(
        argument_spec=dict(
            path=dict(type='path', required=True, aliases=['dest']),
            state=dict(
                type='str',
                default='present',
                choices=[
                        'present',
                        'absent',
                        'identic',
                ]
            ),
            list_diff_type=dict(
                type='str',
                default='value',
                choices=[
                        'value',
                        'index',
                ],
            ),
            value=dict(type=check_type_dict_or_list, required=True),
            create=dict(type='bool', default=False),
            diff_on_value=dict(type='bool', default=True),
            backup=dict(type='bool', default=False),
            indent=dict(type='int', default=4),
            sort_keys=dict(type='bool', default=False),
        ),
        supports_check_mode=True,
    )

    def __load_result_data__(self):
        # type: () -> dict
        content = []
        try:
            with open(self.vars.path, 'r') as file:
                content = file.readlines()
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            raise ModuleHelperException(
                'Failed to decode JSON in {}'.format(self.vars["path"]))
        if ''.join(content).strip() == '':
            content = ['{}']
        if self.vars['diff_on_value']:
            self.vars.set(self.var_result_data,
                          json.loads(''.join(content)), diff=True)
        else:
            self.vars.set(self.var_result_data, content, diff=True)

    def __run__(self):
        # type: () -> None
        merge_util = DataMergeUtils(self.vars['state'],
                                    self.vars['list_diff_type'])
        self._set_result(merge_util.get_new_merged_data(
            self._get_current(), self.vars.value))

    def _get_current(self):
        # type: () -> None
        if self.vars['diff_on_value']:
            return self.vars[self.var_result_data]
        else:
            return json.loads(''.join(self.vars[self.var_result_data]))

    def _set_result(self, result):
        # type: (dict) -> None
        if self.vars['diff_on_value']:
            self.vars.set(self.var_result_data, result)
        else:
            self.vars.set(self.var_result_data,
                          self._json_dumps(result).splitlines(keepends=True))

    @DestFileModuleHelper.write_tempfile    # provide kwargs['fd']
    def __write_temp__(self, *args, **kwargs):
        # type: () -> None
        if self.vars['diff_on_value']:
            json_string = self._json_dumps(self.vars[self.var_result_data])
        else:
            json_string = ''.join(self.vars[self.var_result_data])
        os.write(kwargs['fd'], bytes(json_string, 'utf-8'))

    def _json_dumps(self, json_str):
        # type: (str) -> dict
        indent = None if self.vars['indent'] == 0 else self.vars['indent']
        return json.dumps(json_str,
                          indent=indent,
                          sort_keys=self.vars['sort_keys'])


def main():
    # type: () -> None
    JsonFile().execute()


if __name__ == '__main__':
    main()

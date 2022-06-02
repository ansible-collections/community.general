#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2022, DEMAREST Maxime <maxime@indelog.fr>
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: yaml_file
short_description: Managage (add, remove, update) elements in a YAML file
extends_documentation_fragment: files
description:
  - This module ensures that a set of values is present or absent in a yaml
    file.
  - The check can be done in all childrens of an object.
  - It also makes sure a value is present or absent in a list or in a
    specific index of the list.
  - In background, this module use the python YAML lib
    U(https://pyyaml.org/wiki/PyYAMLDocumentation).
notes:
  - Take note of the following warning before using this module, B(if you have
    some comments in your YAML file, this module will not preserve them!) So
    do not use it if it is important for you to keep these comments.
  - This module supports C(--check) and C(--diff) flags.
options:
  path:
    description:
      - Absolute path of the YAML file.
    type: path
    required: true
    aliases: [ dest ]
  state:
    description:
      - If set to C(present), that ensure the values are present in the YAML
        file. If the YAML file contain datas that are not present in the
        expected values, they will not be modified (this only ensure
        that the expected datas are presents).
      - If set to C(absent), that ensure the values are absent in the YAML
        file.
      - If set to C(identic), that ensure the values in the YAML are identic to
        those provided in arguments. If the YAML file contain datas that are
        not present in the expected values they will be removed (this ensure
        that the datas in the file are exactly the same as the expected datas).
    type: str
    choices: [ present, absent, identic ]
    default: present
  list_diff_type:
    description:
      - This describes how the list are compared.
      - If set to C(value), it checks if a value is present in the list
        elements. With this, you cannot check a list element in another list
        element. Only the first level of a list can be checked.
      - If set to C(index), the value in a list are compared by their index.
        With this, you can check an element in another list, but you make sure
        that the expected value is at this position in the list.
    type: str
    choices: [ value, index ]
    default: value
  value:
    description:
      - The values that you want to compare with the one present in the YAML
        file. Can be a dict or a list.
    type: raw
    required: true
  allow_creation:
    description:
      - If set to C(no), the module will fail if the YAML file does not exist.
        Else, the YAML file will be created.
    type: bool
    default: false
  diff_on_value:
    description:
      - This describes how check if it has a difference between the datas
        present in the YAML file and the expected values. This will also
        impact the output in diff mode (in a case you get indents or lines
        breaks in the diff will in the other you only gets values).
      - If set to C(true), it checks the difference by only comparing the
        values of elements in the YAML file and in the expected datas. In this
        case, change indentation or sort keys will not be considered as a
        change on the file will the values are the sames (just like any other
        difference in YAML file unrelated to values of elements like line
        breaks or comments).
      - If set to C(false), it checks the difference by comparing the lines
        output with the actual lines in the YAML file. In this case, all the
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
    default: false
  indent:
    description:
      - Set the indentation for elements in the YAML file.
    type: int
    default: 2
  sort_keys:
    description:
      - If set to C(true), the values in the will sorted by their keys.
    type: bool
    default: false
  explicit_start:
    description:
      - If C(true) then add C(---) at the document begin.
    type: bool
    default: true
  explicit_end:
    description:
      - If C(true) then add C(...) at the document ending.
    type: bool
    default: false
  default_flow_style:
    description:
      - If C(null) Mappings blocks will be separated by lines breaks and indents
        and sequences blocks will be wrapped by square brackets and separated by
        commas.
      - If C(true) Mappings blocks and sequences blocks will be separated by lines
        breaks and indents.
      - If C(false) Mappings blocks will be wrapped by curly braces and separated
        by commas and sequences blocks will be wrapped by square brackets and
        separated by commas.
      - This option is mutually exclusive with C(canonical).
    type: bool
    default: null
  canonical:
    description:
      - If C(true) then the YAML will be in canonical form.
      - This option is mutually exclusive with C(default_flow_style).
    type: bool
    default: false
  width:
    description:
      - Set the maximum line width.
      - C(0) mean there is not max line width.
    type: int
    default: 0
  add_ansible_managed:
    description:
      - If C(true) the mention C(# Ansible managed, do not edit this file manually !)
        will be added in the top the the file when it be modified.
    type: bool
    default: true
requirements:
  - python3-yaml
version_added: 5.1.0
author:
    - DEMAREST Maxime (@indelog) <maxime@indelog.fr>
'''

EXAMPLES = r'''
# We consider the following content in /my/dest/file.yaml on the remote host :
# ---
# A: 1
# B: 2
# C:
#   D: 3
#   E: [4, 5, 6]
# The values are kept in all samples.

- name: "Ensure values are present in the YAML."
  community.general.yaml_file:
    path: "/my/dest/file.yaml"
    value:
      B: 3
      C:
       F: 8
    state: "present"
# {'B': 3} and {'C':{'F': 8}} are not present in the original values, they will
# be added.
# There is a change.
# Get the following content in /my/dest/file.yaml :
# ---
# A: 1
# B: 3
# C:
#   D: 3
#   E: [4, 5, 6]
#   F: 8

- name: "Ensure values are absent in the YAML file files."
  community.general.yaml_file:
    path: "/my/dest/file.yaml"
    value:
      B: 3
      C:
       F: 8
    state: "absent"
# {'B': 3} and {'C':{'F': 8}} are not present in the original values, so there
# is no change.
# There is no change.
# Get the following content in /my/dest/file.yaml :
# ---
# A: 1
# B: 2
# C:
#   D: 3
#   E: [4, 5, 6]
- name: "Ensure values are absent in the YAML file files."
  community.general.yaml_file:
    path: "/my/dest/file.yaml"
    value:
      B: 2
      C:
       D: 3
    state: "absent"
# {'B': 2} and {'C':{'D': 3}} are present in the original values, so it will
# be removed.
# There is a change.
# Get the following content in /my/dest/file.yaml :
# ---
# A: 1
# C:
#   E: [4, 5, 6]
- name: "Ensure values are identic in the YAML file files."
  community.general.yaml_file:
    path: "/my/dest/file.yaml"
    value:
      B: 4
      C:
       D: 6
      Z: 8
    state: "identic"
# The values in the file will be set to identical that expected values.
# There is a change.
# Get the following content in /my/dest/file.yaml :
# ---
# B: 4
# C:
#   D: 6
# Z: 8

- name: "Ensure values are present in a list."
  community.general.yaml_file:
    path: "/my/dest/file.yaml"
    value:
      C:
       E: [5]
    state: "present"
# In the original values, 5 is already present in C.D.
# There is no change.
# Get the following content in /my/dest/file.yaml :
# ---
# A: 1
# B: 2
# C:
#   D: 3
#   E: [4, 5, 6]

- name: "Ensure values are present in a list."
  community.general.yaml_file:
    path: "/my/dest/file.yaml"
    value:
      C:
       E:
        - 7
    state: "present"
# In the original values, 7 is not present in C.D, it will be added.
# There is a change.
# Get the following content in /my/dest/file.yaml :
# ---
# A: 1
# B: 2
# C:
#   D: 3
#   E: [4, 5, 6, 7]

- name: "Ensure values are absent in a list."
  community.general.yaml_file:
    path: "/my/dest/file.yaml"
    value:
      C:
       E:
        - 5
    state: "absent"
# In the orginal values, 5 is present in C.D, it will be removed.
# There is a change.
# Get the following content in /my/dest/file.yaml :
# ---
# A: 1
# B: 2
# C:
#   D: 3
#   E: [4, 6]

- name: "Ensure values are present depending their index in a list."
  community.general.yaml_file:
    path: "/my/dest/file.yaml"
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
# There is no change.
# Get the following content in /my/dest/file.yaml :
# ---
# A: 1
# B: 2
# C:
#   D: 3
#   E: [4, 7, 6]

- name: "Ensure values are absent depending their index in a list."
  community.general.yaml_file:
    path: "/my/dest/file.yaml"
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
# Get the following content in /my/dest/file.yaml :
# ---
# A: 1
# B: 2
# C:
#   D: 3
#   E: [4, 5]

- name: "Ensure values are present in the YAML diff, check only on values."
  community.general.yaml_file:
    path: "/my/dest/file.yaml"
    indent: 4
    value:
      A: 1
    state: "present"
# We will change the indent but when the change are only detected on the values
# the YAML file will not be update ("A": 1 is already in the originals values).
# There is no change.
# Get the following content in /my/dest/file.json :
# ---
# A: 1
# B: 2
# C:
#   D: 3
#   E: [4, 5, 6]

- name: "Ensure values are present in the YAML diff, also check file format."
  community.general.yaml_file:
    path: "/my/dest/file.yaml"
    indent: 2
    diff_on_value: false
    value:
      A: 1
    state: "present"
# There is not diff in the values but the file format is changed (intent 4
# to 2).
# There is a change.
# Get the following content in /my/dest/file.yaml :
# ---
# A: 1
# B: 2
# C:
#     D: 3
#     E: [4, 5, 6]
'''

RETURN = r'''
  changed:
    description:
      - Indicate whether the YAML file is changed or not.
    returned: always
    type: bool
  created:
    description:
      - Indicate if the file YAML is created or not.
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
      - Contain the values that are finally present in the YAML file.
    returned: success
    type: dict
'''

import traceback

try:
    import yaml
except ImportError:
    HAS_YAML = False
    YAML_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_YAML = True


from ansible.module_utils.basic import missing_required_lib
from ansible_collections.community.general.plugins.module_utils.mh.module_helper_dest_file import (
    DestFileModuleHelper,
    ModuleHelperException,
)
from ansible_collections.community.general.plugins.module_utils.data_merge_utils import DataMergeUtils
from ansible_collections.community.general.plugins.module_utils.common.validation import check_type_dict_or_list


class YamlFile(DestFileModuleHelper):

    ANSIBLE_MANAGED_LINE = '# Ansible managed, do not edit this file manually !\n'

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
            value=dict(type='raw', required=True),
            allow_creation=dict(type='bool', default=False),
            backup=dict(type='bool', default=False),
            diff_on_value=dict(type='bool', default=True),
            indent=dict(type='int', default=2),
            explicit_start=dict(type='bool', default=True),
            explicit_end=dict(type='bool', default=False),
            sort_keys=dict(type='bool', default=False),
            default_flow_style=dict(type='bool'),
            canonical=dict(type='bool', default=False),
            width=dict(type='int', default=0),
            add_ansible_managed=dict(type='bool', default=True),
        ),
        mutually_exclusive=[
            ['canonical', 'default_flow_style'],
        ],
        supports_check_mode=True,
        add_file_common_args=True,
    )

    def __init_module__(self):
        # type: () -> None
        self.vars.set('value', check_type_dict_or_list(self.vars['value']))
        super().__init_module__()

    def __load_result_data__(self):
        # type: () -> dict
        content = []
        try:
            with open(self.vars.path, 'r') as file:
                content = file.readlines()
        except FileNotFoundError:
            pass
        if ''.join(content).strip() == '':
            content = ['{}']
        if self.vars['diff_on_value']:
            self.vars.set(self.var_result_data, self._yaml_loads(content), diff=True)
        else:
            self.vars.set(self.var_result_data, content, diff=True)

    def __run__(self):
        # type: () -> None
        merge_util = DataMergeUtils(self.vars['state'], self.vars['list_diff_type'])
        self._set_result(merge_util.get_new_merged_data(self._get_current(), self.vars.value))

    def _get_current(self):
        # type: () -> None
        if self.vars['diff_on_value']:
            return self.vars[self.var_result_data]
        else:
            return self._yaml_loads(self.vars[self.var_result_data])

    def _yaml_loads(self, yaml_str):
        # type: (str) -> str
        try:
            return yaml.safe_load(''.join(yaml_str))
        except yaml.scanner.ScannerError:
            raise ModuleHelperException(msg='Failed to decode YAML in {0}'.format(self.vars["path"]))

    def _set_result(self, result):
        # type: (dict) -> None
        if self.vars['diff_on_value']:
            self.vars.set(self.var_result_data, result)
        else:
            self.vars.set(self.var_result_data,
                          self._yaml_dumps(result).splitlines(keepends=True))

    def __write_temp__(self, *args, **kwargs):
        # type: () -> None
        if self.vars['add_ansible_managed']:
            yaml_string = self.ANSIBLE_MANAGED_LINE
        else:
            yaml_string = ''
        if self.vars['diff_on_value']:
            yaml_string += self._yaml_dumps(self.vars[self.var_result_data])
        else:
            yaml_string += ''.join(self.vars[self.var_result_data])
        self._tmpfile = self._write_in_tempfile(yaml_string)

    def _yaml_dumps(self, yaml_str):
        # type: (str) -> dict
        return yaml.safe_dump(
            yaml_str,
            explicit_start=self.vars['explicit_start'],
            explicit_end=self.vars['explicit_end'],
            sort_keys=self.vars['sort_keys'],
            default_flow_style=self.vars['default_flow_style'],
            canonical=self.vars['canonical'],
            indent=self.vars['indent'],
            width=self.vars['width'])


def main():
    # type: () -> None
    module = YamlFile()
    if not HAS_YAML:
        module.module.fail_json(msg=missing_required_lib('yaml'), exception=YAML_IMPORT_ERROR)
    else:
        module.execute()


if __name__ == '__main__':
    main()

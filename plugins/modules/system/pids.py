#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Saranya Sridharan
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
module: pids
description: "Retrieves a list of PIDs of given process name in Ansible controller/controlled machines.Returns an empty list if no process in that name exists."
short_description: "Retrieves process IDs list if the process is running otherwise return empty list"
author:
  - Saranya Sridharan (@saranyasridharan)
requirements:
  - psutil(python module)
options:
  name:
    description: The name of the process(es) you want to get PID(s) for.
    type: str
  pattern:
    description: The pattern (regular expression) to match the process(es) you want to get PID(s) for.
    type: str
    version_added: 3.0.0
  ignore_case:
    description: Ignore case in pattern if using the I(pattern) option.
    type: bool
    default: false
    version_added: 3.0.0
'''

EXAMPLES = r'''
# Pass the process name
- name: Getting process IDs of the process
  community.general.pids:
      name: python
  register: pids_of_python

- name: Printing the process IDs obtained
  ansible.builtin.debug:
    msg: "PIDS of python:{{pids_of_python.pids|join(',')}}"

- name: Getting process IDs of processes matching pattern
  community.general.pids:
    pattern: python(2(\.7)?|3(\.6)?)?\s+myapp\.py
  register: myapp_pids
'''

RETURN = '''
pids:
  description: Process IDs of the given process
  returned: list of none, one, or more process IDs
  type: list
  sample: [100,200]
'''

import abc
import re
from distutils.version import LooseVersion
from os.path import basename

from ansible.module_utils import six
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class PSAdapterError(Exception):
    pass


@six.add_metaclass(abc.ABCMeta)
class PSAdapter(object):
    GET_PIDS_ATTRS = ('name', 'cmdline')
    GET_MATCHING_PIDS_ATTRS = ('name', 'exe', 'cmdline')

    def __init__(self, psutil):
        self._psutil = psutil

    @staticmethod
    def from_package(psutil):
        version = LooseVersion(psutil.__version__)
        if version < LooseVersion('2.0.0'):
            return PSAdapter100(psutil)
        elif version < LooseVersion('5.3.0'):
            return PSAdapter200(psutil)
        else:
            return PSAdapter530(psutil)

    def get_pids_by_name(self, name):
        return [p.pid for p in self._process_iter(*self.GET_PIDS_ATTRS) if self._has_name(p, name)]

    def _process_iter(self, *attrs):
        return self._psutil.process_iter()

    def _has_name(self, proc, name):
        proc_name, proc_cmd = self._get_proc_attributes(proc, *self.GET_PIDS_ATTRS)
        return compare_lower(proc_name, name) or (proc_cmd and compare_lower(proc_cmd[0], name))

    @staticmethod
    @abc.abstractmethod
    def _get_proc_attributes(proc, *attributes):
        pass

    def get_pids_by_pattern(self, pattern, ignore_case):
        return [p.pid for p in self._process_iter(*self.GET_MATCHING_PIDS_ATTRS)
                if self._matches_pattern(p, pattern, ignore_case)]

    def _matches_pattern(self, proc, pattern, ignore_case):
        flags = 0
        if ignore_case:
            flags |= re.I

        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            raise PSAdapterError("'%s' is not a valid regular expression: %s" % (self._pattern, to_native(e)))

        # See https://psutil.readthedocs.io/en/latest/#find-process-by-name for more information
        proc_name, proc_exe, proc_cmd = self._get_proc_attributes(proc, *self.GET_MATCHING_PIDS_ATTRS)
        matches_name = regex.search(to_native(proc_name))
        matches_exe = proc_exe and regex.search(basename(to_native(proc_exe)))
        matches_cmd = proc_cmd and regex.search(to_native(' '.join(proc_cmd)))

        return any([matches_name, matches_exe, matches_cmd])


class PSAdapter100(PSAdapter):
    def __init__(self, psutil):
        super(PSAdapter100, self).__init__(psutil)

    @staticmethod
    def _get_proc_attributes(proc, *attributes):
        return [getattr(proc, attribute) for attribute in attributes]


class PSAdapter200(PSAdapter):
    def __init__(self, psutil):
        super(PSAdapter200, self).__init__(psutil)

    @staticmethod
    def _get_proc_attributes(proc, *attributes):
        proc_methods = [getattr(proc, attribute) for attribute in attributes]
        return [method() for method in proc_methods]


class PSAdapter530(PSAdapter):
    def __init__(self, psutil):
        super(PSAdapter530, self).__init__(psutil)

    def _process_iter(self, *attrs):
        return self._psutil.process_iter(attrs=attrs)

    @staticmethod
    def _get_proc_attributes(proc, *attributes):
        return [proc.info[attribute] for attribute in attributes]


def compare_lower(a, b):
    if a is None or b is None:
        # this could just be "return False" but would lead to surprising behavior if both a and b are None
        return a == b

    return a.lower() == b.lower()


class Pids(object):
    def __init__(self, module):
        if not HAS_PSUTIL:
            module.fail_json(msg=missing_required_lib('psutil'))

        self._ps = PSAdapter.from_package(psutil)

        self._module = module
        self._name = module.params['name']
        self._pattern = module.params['pattern']
        self._ignore_case = module.params['ignore_case']

        self._pids = []

    def execute(self):
        if self._name:
            self._pids = self._ps.get_pids_by_name(self._name)
        else:
            try:
                self._pids = self._ps.get_pids_by_pattern(self._pattern, self._ignore_case)
            except PSAdapterError as e:
                self._module.fail_json(msg=to_native(e))

        return self._module.exit_json(**self.result)

    @property
    def result(self):
        return {
            'pids': self._pids,
        }


def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str"),
            pattern=dict(type="str"),
            ignore_case=dict(type="bool", default=False),
        ),
        required_one_of=[
            ('name', 'pattern')
        ],
        mutually_exclusive=[
            ('name', 'pattern')
        ],
        supports_check_mode=True,
    )

    Pids(module).execute()


if __name__ == '__main__':
    main()

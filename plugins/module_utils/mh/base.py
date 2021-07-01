# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.mh.exceptions import ModuleHelperException as _MHE
from ansible_collections.community.general.plugins.module_utils.mh.deco import module_fails_on_exception


class ModuleHelperBase(object):
    module = None
    ModuleHelperException = _MHE

    def __init__(self, module=None):
        self._changed = False

        if module:
            self.module = module

        if not isinstance(self.module, AnsibleModule):
            self.module = AnsibleModule(**self.module)

    def __init_module__(self):
        pass

    def __run__(self):
        raise NotImplementedError()

    def __quit_module__(self):
        pass

    def __changed__(self):
        raise NotImplementedError()

    @property
    def changed(self):
        try:
            return self.__changed__()
        except NotImplementedError:
            return self._changed

    @changed.setter
    def changed(self, value):
        self._changed = value

    def has_changed(self):
        raise NotImplementedError()

    @property
    def output(self):
        raise NotImplementedError()

    @module_fails_on_exception
    def run(self):
        self.__init_module__()
        self.__run__()
        self.__quit_module__()
        output = self.output
        if 'failed' not in output:
            output['failed'] = False
        self.module.exit_json(changed=self.has_changed(), **output)

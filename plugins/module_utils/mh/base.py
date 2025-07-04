# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.mh.exceptions import ModuleHelperException as _MHE
from ansible_collections.community.general.plugins.module_utils.mh.deco import module_fails_on_exception


class ModuleHelperBase(object):
    module = None
    ModuleHelperException = _MHE
    # in 12.0.0 add 'debug' to the tuple
    _delegated_to_module = (
        'check_mode', 'get_bin_path', 'warn', 'deprecate',
    )

    def __init__(self, module=None):
        self._changed = False

        if module:
            self.module = module

        if not isinstance(self.module, AnsibleModule):
            self.module = AnsibleModule(**self.module)

        # in 12.0.0 remove this if statement entirely
        if hasattr(self, 'debug'):
            msg = (
                "This class ({cls}) has an attribute 'debug' defined and that is deprecated. "
                "Method 'debug' will be an integral part of ModuleHelper in community.general "
                "12.0.0, delegated to the underlying AnsibleModule object. "
                "Please rename the existing attribute to prevent this message from showing.".format(cls=self.__class__.__name__)
            )
            self.deprecate(msg, version="12.0.0", collection_name="community.general")
        else:
            self._delegated_to_module = self._delegated_to_module + ('debug',)

    @property
    def diff_mode(self):
        return self.module._diff

    @property
    def verbosity(self):
        return self.module._verbosity

    def do_raise(self, *args, **kwargs):
        raise _MHE(*args, **kwargs)

    def __getattr__(self, attr):
        if attr in self._delegated_to_module:
            return getattr(self.module, attr)
        raise AttributeError("ModuleHelperBase has no attribute '%s'" % (attr, ))

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

    @classmethod
    def execute(cls, module=None):
        cls(module).run()

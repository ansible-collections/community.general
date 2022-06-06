# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils.common.text.converters import to_native


class ModuleHelperException(Exception):
    def __init__(self, msg, update_output=None, *args, **kwargs):
        self.msg = to_native(msg or "Module failed with exception: {0}".format(self))
        if update_output is None:
            update_output = {}
        self.update_output = update_output
        super(ModuleHelperException, self).__init__(*args)

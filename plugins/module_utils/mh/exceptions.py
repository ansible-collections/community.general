# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class ModuleHelperException(Exception):
    @staticmethod
    def _get_remove(key, kwargs):
        if key in kwargs:
            result = kwargs[key]
            del kwargs[key]
            return result
        return None

    def __init__(self, *args, **kwargs):
        self.msg = self._get_remove('msg', kwargs) or "Module failed with exception: {0}".format(self)
        self.update_output = self._get_remove('update_output', kwargs) or {}
        super(ModuleHelperException, self).__init__(*args)

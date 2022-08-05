# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function
__metaclass__ = type


from ansible.module_utils.basic import AnsibleModule


class DeprecateAttrsMixin(object):

    def _deprecate_setup(self, attr, target, module):
        if target is None:
            target = self
        if not hasattr(target, attr):
            raise ValueError("Target {0} has no attribute {1}".format(target, attr))
        if module is None:
            if isinstance(target, AnsibleModule):
                module = target
            elif hasattr(target, "module") and isinstance(target.module, AnsibleModule):
                module = target.module
            else:
                raise ValueError("Failed to automatically discover the AnsibleModule instance. Pass 'module' parameter explicitly.")

        # setup internal state dicts
        value_attr = "__deprecated_attr_value"
        trigger_attr = "__deprecated_attr_trigger"
        if not hasattr(target, value_attr):
            setattr(target, value_attr, {})
        if not hasattr(target, trigger_attr):
            setattr(target, trigger_attr, {})
        value_dict = getattr(target, value_attr)
        trigger_dict = getattr(target, trigger_attr)
        return target, module, value_dict, trigger_dict

    def _deprecate_attr(self, attr, msg, version=None, date=None, collection_name=None, target=None, value=None, module=None):
        target, module, value_dict, trigger_dict = self._deprecate_setup(attr, target, module)

        value_dict[attr] = getattr(target, attr, value)
        trigger_dict[attr] = False

        def _trigger():
            if not trigger_dict[attr]:
                module.deprecate(msg, version=version, date=date, collection_name=collection_name)
                trigger_dict[attr] = True

        def _getter(_self):
            _trigger()
            return value_dict[attr]

        def _setter(_self, new_value):
            _trigger()
            value_dict[attr] = new_value

        # override attribute
        prop = property(_getter)
        setattr(target, attr, prop)
        setattr(target, "_{0}_setter".format(attr), prop.setter(_setter))

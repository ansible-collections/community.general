# -*- coding: utf-8 -*-
# (c) 2020-2024, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020-2024, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function
__metaclass__ = type


from ansible.module_utils.common.dict_transformations import dict_merge

from ansible_collections.community.general.plugins.module_utils.vardict import VarDict as _NewVarDict  # remove "as NewVarDict" in 11.0.0
# (TODO: remove AnsibleModule!) pylint: disable-next=unused-import
from ansible_collections.community.general.plugins.module_utils.mh.base import AnsibleModule  # noqa: F401 DEPRECATED, remove in 11.0.0
from ansible_collections.community.general.plugins.module_utils.mh.base import ModuleHelperBase
from ansible_collections.community.general.plugins.module_utils.mh.mixins.state import StateMixin
# (TODO: remove mh.mixins.vars!) pylint: disable-next=unused-import
from ansible_collections.community.general.plugins.module_utils.mh.mixins.vars import VarsMixin, VarDict as _OldVarDict  # noqa: F401 remove in 11.0.0
from ansible_collections.community.general.plugins.module_utils.mh.mixins.deprecate_attrs import DeprecateAttrsMixin


class ModuleHelper(DeprecateAttrsMixin, ModuleHelperBase):
    facts_name = None
    output_params = ()
    diff_params = ()
    change_params = ()
    facts_params = ()
    use_old_vardict = True      # remove in 11.0.0
    mute_vardict_deprecation = False

    def __init__(self, module=None):
        if self.use_old_vardict:  # remove first half of the if in 11.0.0
            self.vars = _OldVarDict()
            super(ModuleHelper, self).__init__(module)
            if not self.mute_vardict_deprecation:
                self.module.deprecate(
                    "This class is using the old VarDict from ModuleHelper, which is deprecated. "
                    "Set the class variable use_old_vardict to False and make the necessary adjustments."
                    "The old VarDict class will be removed in community.general 11.0.0",
                    version="11.0.0", collection_name="community.general"
                )
        else:
            self.vars = _NewVarDict()
            super(ModuleHelper, self).__init__(module)

        for name, value in self.module.params.items():
            self.vars.set(
                name, value,
                diff=name in self.diff_params,
                output=name in self.output_params,
                change=None if not self.change_params else name in self.change_params,
                fact=name in self.facts_params,
            )

    def update_vars(self, meta=None, **kwargs):
        if meta is None:
            meta = {}
        for k, v in kwargs.items():
            self.vars.set(k, v, **meta)

    def update_output(self, **kwargs):
        self.update_vars(meta={"output": True}, **kwargs)

    def update_facts(self, **kwargs):
        self.update_vars(meta={"fact": True}, **kwargs)

    def _vars_changed(self):
        if self.use_old_vardict:
            return any(self.vars.has_changed(v) for v in self.vars.change_vars())

        return self.vars.has_changed

    def has_changed(self):
        return self.changed or self._vars_changed()

    @property
    def output(self):
        result = dict(self.vars.output())
        if self.facts_name:
            facts = self.vars.facts()
            if facts is not None:
                result['ansible_facts'] = {self.facts_name: facts}
        if self.diff_mode:
            diff = result.get('diff', {})
            vars_diff = self.vars.diff() or {}
            result['diff'] = dict_merge(dict(diff), vars_diff)

        return result


class StateModuleHelper(StateMixin, ModuleHelper):
    pass

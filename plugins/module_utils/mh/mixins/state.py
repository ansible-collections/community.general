# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class StateMixin(object):
    state_param = None
    default_state = None
    default_state_param = 'state'

    @property
    def _state_param_name(self):
        param_name = self.state_param or self.default_state_param
        if param_name in self.module.params:
            return param_name

        aliased_args = [arg for arg, spec in self.module.argument_spec.items() if 'aliases' in spec]
        if param_name not in aliased_args:
            return param_name

        return [param for param in self.module.params if param in aliased_args[param_name]['aliases']][0]

    @property
    def _state_value(self):
        state = self.vars.get(self._state_param_name)
        return self.default_state if state is None else state

    def _method(self, state):
        return "{0}_{1}".format(self.state_param or self.default_state_param, state)

    def __run__(self):
        method = self._method(self._state_value)
        try:
            func = getattr(self, method)
        except AttributeError:
            func = self.__state_fallback__
        return func()

    def __state_fallback__(self):
        raise ValueError("Cannot find method: {0}".format(self._method(self._state_value)))

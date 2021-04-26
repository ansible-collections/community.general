# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class StateMixin(object):
    state_param = 'state'
    default_state = None

    def _state(self):
        state = self.module.params.get(self.state_param)
        return self.default_state if state is None else state

    def _method(self, state):
        return "{0}_{1}".format(self.state_param, state)

    def __run__(self):
        state = self._state()
        self.vars.state = state

        # resolve aliases
        if state not in self.module.params:
            aliased = [name for name, param in self.module.argument_spec.items() if state in param.get('aliases', [])]
            if aliased:
                state = aliased[0]
                self.vars.effective_state = state

        method = self._method(state)
        if not hasattr(self, method):
            return self.__state_fallback__()
        func = getattr(self, method)
        return func()

    def __state_fallback__(self):
        raise ValueError("Cannot find method: {0}".format(self._method(self._state())))

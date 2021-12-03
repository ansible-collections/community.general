# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class StateMixin(object):
    state_param = 'state'
    default_state = None

    @property
    def _state_value(self):
        state = self.vars.get(self.state_param)
        return self.default_state if state is None else state

    def _method(self, state):
        return "{0}_{1}".format(self.state_param, state)

    def __run__(self):
        method = self._method(self._state_value)
        try:
            func = getattr(self, method)
        except AttributeError:
            func = self.__state_fallback__
        return func()

    def __state_fallback__(self):
        raise ValueError("Cannot find method: {0}".format(self._method(self._state_value)))

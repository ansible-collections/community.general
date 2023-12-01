# Copyright 2012, Dag Wieers <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleError
from ansible.playbook.conditional import Conditional
from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    ''' Fail with custom message '''

    _requires_connection = False

    _VALID_ARGS = frozenset(('msg', 'that'))

    def _make_safe(self, text):
        # A simple str(text) won't do it since AnsibleUnsafeText is clever :-)
        return ''.join(chr(ord(x)) for x in text)

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        if 'that' not in self._task.args:
            raise AnsibleError('conditional required in "that" string')

        fail_msg = 'Assertion failed'
        success_msg = 'All assertions passed'

        thats = self._task.args['that']

        cond = Conditional(loader=self._loader)
        result['_ansible_verbose_always'] = True

        for that in thats:
            cond.when = [str(self._make_safe(that))]
            test_result = cond.evaluate_conditional(templar=self._templar, all_vars=task_vars)
            if not test_result:
                result['failed'] = True
                result['evaluated_to'] = test_result
                result['assertion'] = that

                result['msg'] = fail_msg

                return result

        result['changed'] = False
        result['msg'] = success_msg
        return result

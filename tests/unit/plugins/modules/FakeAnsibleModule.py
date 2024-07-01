# -*- coding: utf-8 -*-
#
# Copyright (c) 2019, Bojan Vitnik <bvitnik@mainstream.rs>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from collections import defaultdict

from ansible.module_utils.six import binary_type, text_type


class AnsibleModuleException(Exception):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class ExitJsonException(AnsibleModuleException):
    pass


class FailJsonException(AnsibleModuleException):
    pass


class CommandNotRegisteredException(Exception):
    pass


class FakeAnsibleModule:
    def __init__(self, params=None, check_mode=False):
        self.params = params
        self.check_mode = check_mode
        self.commands = defaultdict(list)
        self._keep_last_command = False

    def register_command(self, args, rc=0, stdout='', stderr=''):
        """Register a command which will be 'executed' later with run_command.

        Each command you register is only used once, so you can register the
        same command multiple times with different results. If you call
        `keep_last_command(True)` than the last instance of any particular
        command will be preserved and used as the result of any subsequent
        invocations."""
        if not isinstance(rc, int):
            raise TypeError('rc must be int, not "%s"' % (rc,))
        self.commands[tuple(args)].append((rc, stdout, stderr))

    def keep_last_command(self, value):
        """Specify whether to use the last instance of a command for multiple invocations."""
        self._keep_last_command = value

    # Note: Most of these arguments don't do anything yet in this stub; they're
    # they're just here for call signature compatibility with the real
    # function. If you need any of this functionality in your tests feel free
    # to add it!
    def run_command(self, args, check_rc=False, close_fds=True,
                    executable=None, data=None, binary_data=False,
                    path_prefix=None, cwd=None, use_unsafe_shell=False,
                    prompt_regex=None, environ_update=None, umask=None,
                    encoding='utf-8', errors='surrogate_or_strict',
                    expand_user_and_vars=True, pass_fds=None,
                    before_communicate_callback=None, ignore_invalid_cwd=True,
                    handle_exceptions=True):
        if not isinstance(args, (list, binary_type, text_type)):
            raise TypeError(
                "Argument 'args' to run_command must be list or string")
        args = tuple(args)
        if not self.commands[args]:
            raise CommandNotRegisteredException(str(args))
        if len(self.commands[args]) > 1 or not self._keep_last_command:
            return self.commands[args].pop(0)
        else:
            return self.commands[args][0]

    def exit_json(self, *args, **kwargs):
        raise ExitJsonException(*args, **kwargs)

    def fail_json(self, *args, **kwargs):
        raise FailJsonException(*args, **kwargs)

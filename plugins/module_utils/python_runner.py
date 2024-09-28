# -*- coding: utf-8 -*-
# Copyright (c) 2024, Alexei Znamensky <russoz@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import os

from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, _ensure_list


class PythonRunner(CmdRunner):
    def __init__(self, module, command, arg_formats=None, default_args_order=(),
                 check_rc=False, force_lang="C", path_prefix=None, environ_update=None,
                 python="python", venv=None):
        self.python = python
        self.venv = venv
        self.has_venv = venv is not None

        if (os.path.isabs(python) or '/' in python):
            self.python = python
        elif self.has_venv:
            if path_prefix is None:
                path_prefix = []
            path_prefix.append(os.path.join(venv, "bin"))
            if environ_update is None:
                environ_update = {}
            environ_update["PATH"] = "%s:%s" % (":".join(path_prefix), os.environ["PATH"])
            environ_update["VIRTUAL_ENV"] = venv

        python_cmd = [self.python] + _ensure_list(command)

        super(PythonRunner, self).__init__(module, python_cmd, arg_formats, default_args_order,
                                           check_rc, force_lang, path_prefix, environ_update)

# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function
__metaclass__ = type


class DependencyCtxMgr(object):
    """
    DEPRECATION WARNING

    This class is deprecated and will be removed in community.general 11.0.0
    Modules should use plugins/module_utils/deps.py instead.
    """
    def __init__(self, name, msg=None):
        self.name = name
        self.msg = msg
        self.has_it = False
        self.exc_type = None
        self.exc_val = None
        self.exc_tb = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.has_it = exc_type is None
        self.exc_type = exc_type
        self.exc_val = exc_val
        self.exc_tb = exc_tb
        return not self.has_it

    @property
    def text(self):
        return self.msg or str(self.exc_val)

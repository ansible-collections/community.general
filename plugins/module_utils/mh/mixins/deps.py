# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2020, Ansible Project
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import traceback

from ansible_collections.community.general.plugins.module_utils.mh.base import ModuleHelperBase
from ansible_collections.community.general.plugins.module_utils.mh.deco import module_fails_on_exception


class DependencyCtxMgr(object):
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


class DependencyMixin(ModuleHelperBase):
    """
    THIS CLASS IS BEING DEPRECATED.
    See the deprecation notice in ``DependencyMixin.fail_on_missing_deps()`` below.

    Mixin for mapping module options to running a CLI command with its arguments.
    """
    _dependencies = []

    @classmethod
    def dependency(cls, name, msg):
        cls._dependencies.append(DependencyCtxMgr(name, msg))
        return cls._dependencies[-1]

    def fail_on_missing_deps(self):
        if not self._dependencies:
            return
        self.module.deprecate(
            'The DependencyMixin is being deprecated. '
            'Modules should use community.general.plugins.module_utils.deps instead.',
            version='9.0.0',
            collection_name='community.general',
        )
        for d in self._dependencies:
            if not d.has_it:
                self.module.fail_json(changed=False,
                                      exception="\n".join(traceback.format_exception(d.exc_type, d.exc_val, d.exc_tb)),
                                      msg=d.text,
                                      **self.output)

    @module_fails_on_exception
    def run(self):
        self.fail_on_missing_deps()
        super(DependencyMixin, self).run()

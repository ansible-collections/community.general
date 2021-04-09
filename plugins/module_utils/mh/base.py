# -*- coding: utf-8 -*-
# (c) 2020, Alexei Znamensky <russoz@gmail.com>
# Copyright: (c) 2020, Ansible Project
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import abc

from ansible_collections.community.general.plugins.module_utils.mh.exceptions import ModuleHelperException as _MHE


class ModuleHelperBase(abc.ABC):
    module = None
    ModuleHelperException = _MHE

    def __init_module__(self):
        pass

    def __run__(self):
        raise NotImplementedError()

    def __quit_module__(self):
        pass

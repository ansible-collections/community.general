#!/usr/bin/python
# -*- coding: utf-8 -*-
# (c) 2021, Alexei Znamensky <russoz@gmail.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import collections
__metaclass__ = type

DOCUMENTATION = '''
module: msimpleda
author: "Alexei Znamensky (@russoz)"
short_description: Simple module for testing DeprecationAttrsMixin
description:
  - Simple module test description.
options:
  a:
    description: aaaa
    type: int
'''

EXAMPLES = ""

RETURN = ""

from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper
from ansible_collections.community.general.plugins.module_utils.mh.mixins.deprecate_attrs import DeprecateAttrsMixin


class MSimpleDA(ModuleHelper):
    output_params = ('a',)
    module = dict(
        argument_spec=dict(
            a=dict(type='int'),
        ),
    )

    attr1 = "abc"
    attr2 = "def"

    def __init_module__(self):
        self._deprecate_attr(
            "attr2",
            msg="Attribute attr2 is deprecated",
            version="9.9.9",
            collection_name="community.general",
            target=self.__class__,
            module=self.module,
        )

    def __run__(self):
        if self.vars.a == 1:
            self.vars.attr1 = self.attr1
        if self.vars.a == 2:
            self.vars.attr2 = self.attr2


def main():
    MSimpleDA.execute()


if __name__ == '__main__':
    main()

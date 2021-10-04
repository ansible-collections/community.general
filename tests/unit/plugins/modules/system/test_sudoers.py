# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Jon Ellis <ellis.jp@gmail.com>

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import pytest
import json

from ansible_collections.community.general.plugins.modules.system import sudoers
from ansible_collections.community.general.tests.unit.plugins.modules.utils import set_module_args

class TestUFW(unittest.TestCase):

    def test_tests(capfd):
        self.assertTrue(False)

# def test_suders_without_arguments(capfd):
#     set_module_args({})
#     with pytest.raises(SystemExit) as results:
#         sudoers.main()
#     out, err = capfd.readouterr()
#     assert not err
#     assert json.loads(out)['failed']

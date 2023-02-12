# Copyright (c) 2014, Toshio Kuratomi <tkuratomi@ansible.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

'''
Compat module for Python2.7's unittest module
'''

import sys

# Allow wildcard import because we really do want to import all of
# unittests's symbols into this compat shim
# pylint: disable=wildcard-import,unused-wildcard-import
if sys.version_info < (2, 7):
    try:
        # Need unittest2 on python2.6
        from unittest2 import *  # noqa: F401, pylint: disable=unused-import
    except ImportError:
        print('You need unittest2 installed on python2.6.x to run tests')
else:
    from unittest import *  # noqa: F401, pylint: disable=unused-import

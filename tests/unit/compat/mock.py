# Copyright (c) 2014, Toshio Kuratomi <tkuratomi@ansible.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

'''
Compat module for Python3.x's unittest.mock module
'''
# Python 2.7

# Note: Could use the pypi mock library on python3.x as well as python2.x.  It
# is the same as the python3 stdlib mock library

try:
    # Allow wildcard import because we really do want to import all of mock's
    # symbols into this compat shim
    # pylint: disable=wildcard-import,unused-wildcard-import
    from unittest.mock import *  # noqa: F401, pylint: disable=unused-import
except ImportError:
    # Python 2
    # pylint: disable=wildcard-import,unused-wildcard-import
    try:
        from mock import *  # noqa: F401, pylint: disable=unused-import
    except ImportError:
        print('You need the mock library installed on python2.x to run tests')

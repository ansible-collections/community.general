# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Common parameters for Redis modules
    DOCUMENTATION = r'''
options:
  tls:
    description:
      - Specify whether or not to use TLS for the connection.
    type: bool
    default: true
'''

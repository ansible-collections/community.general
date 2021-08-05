# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andreas Botzner <andreas at botzner dot com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Common parameters for Redis modules
    DOCUMENTATION = r'''
options:
  login_host:
    description:
      - Specify the target host running the database.
    default: localhost
    type: str
  login_port:
    description:
      - Specify the port to connect to.
    default: 6379
    type: int
  login_user:
    description:
      - Specify the user to authenticate with.
    type: str
  login_password:
    description:
      - Specify the password to authenticate with.
      - Usually not used when target is localhost.
    type: str
  validate_certs:
    description:
      - Specify whether or not to validate SSL certificates.
      - This should only be turned off for personally controlled sites or with
      - localhost as target.
    type: bool
    default: True
  ssl_ca_certs:
    description:
      - Path to root certificates file. If not set and C(validate_certs) is
      - set to I(True), certifi ca-certificates will be used.
    type: str
requirements: [ "redis", "certifi" ]
'''

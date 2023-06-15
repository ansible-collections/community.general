# -*- coding: utf-8 -*-

# Copyright (c) 2018, www.privaz.io Valletech AB
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # OpenNebula common documentation
    DOCUMENTATION = r'''
options:
    api_url:
        description:
            - The ENDPOINT URL of the XMLRPC server.
            - If not specified then the value of the E(ONE_URL) environment variable, if any, is used.
        type: str
        aliases:
            - api_endpoint
    api_username:
        description:
            - The name of the user for XMLRPC authentication.
            - If not specified then the value of the E(ONE_USERNAME) environment variable, if any, is used.
        type: str
    api_password:
        description:
            - The password or token for XMLRPC authentication.
            - If not specified then the value of the E(ONE_PASSWORD) environment variable, if any, is used.
        type: str
        aliases:
            - api_token
    validate_certs:
        description:
            - Whether to validate the TLS/SSL certificates or not.
            - This parameter is ignored if E(PYTHONHTTPSVERIFY) environment variable is used.
        type: bool
        default: true
    wait_timeout:
        description:
            - Time to wait for the desired state to be reached before timeout, in seconds.
        type: int
        default: 300
'''

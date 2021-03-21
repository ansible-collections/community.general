# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Florian Dambrine <android.florian@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r"""
options:
    pritunl_url:
        type: str
        required: true
        description:
        - URL and port of the Pritunl server on which the API is enabled.

    pritunl_api_token:
        type: str
        required: true
        description:
        - API Token of a Pritunl admin user.
        - It needs to be enabled in Administrators > USERNAME > Enable Token Authentication.

    pritunl_api_secret:
        type: str
        required: true
        description:
        - API Secret found in Administrators > USERNAME > API Secret.

    validate_certs:
        type: bool
        required: false
        default: true
        description:
        - If certificates should be validated or not.
        - This should never be set to C(false), except if you are very sure that
          your connection to the server can not be subject to a Man In The Middle
          attack.
"""

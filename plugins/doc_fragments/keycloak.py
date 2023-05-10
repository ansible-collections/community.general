# -*- coding: utf-8 -*-

# Copyright (c) 2017, Eike Frost <ei@kefro.st>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard documentation fragment
    DOCUMENTATION = r'''
options:
    auth_keycloak_url:
        description:
            - URL to the Keycloak instance.
        type: str
        required: true
        aliases:
          - url

    auth_client_id:
        description:
            - OpenID Connect I(client_id) to authenticate to the API with.
        type: str
        default: admin-cli

    auth_realm:
        description:
            - Keycloak realm name to authenticate to for API access.
        type: str

    auth_client_secret:
        description:
            - Client Secret to use in conjunction with I(auth_client_id) (if required).
        type: str

    auth_username:
        description:
            - Username to authenticate for API access with.
        type: str
        aliases:
          - username

    auth_password:
        description:
            - Password to authenticate for API access with.
        type: str
        aliases:
          - password

    token:
        description:
            - Authentication token for Keycloak API.
        type: str
        version_added: 3.0.0

    validate_certs:
        description:
            - Verify TLS certificates (do not disable this in production).
        type: bool
        default: true

    connection_timeout:
        description:
            - Controls the HTTP connections timeout period (in seconds) to Keycloak API.
        type: int
        default: 10
        version_added: 4.5.0
    http_agent:
        description:
            - Configures the HTTP User-Agent header.
        type: str
        default: Ansible
        version_added: 5.4.0
'''

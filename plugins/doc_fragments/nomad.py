# -*- coding: utf-8 -*-

# Copyright: (c) 2020 FERREIRA Christophe <christophe.ferreira@cnaf.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard files documentation fragment
    DOCUMENTATION = r'''
options:
    host:
      description:
        - FQDN of Nomad server.
      required: true
      type: str
    use_ssl:
      description:
        - Use TLS/SSL connection.
      type: bool
      default: true
    timeout:
      description:
        - Timeout (in seconds) for the request to Nomad.
      type: int
      default: 5
    validate_certs:
      description:
        - Enable TLS/SSL certificate validation.
      type: bool
      default: true
    client_cert:
      description:
        - Path of certificate for TLS/SSL.
      type: path
    client_key:
      description:
        - Path of certificate's private key for TLS/SSL.
      type: path
    namespace:
      description:
        - Namespace for Nomad.
      type: str
    token:
      description:
        - ACL token for authentification.
      type: str
'''

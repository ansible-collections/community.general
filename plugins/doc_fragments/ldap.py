# -*- coding: utf-8 -*-

# Copyright (c) 2016, Peter Sagerson <psagers@ignorare.net>
# Copyright (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
# Copyright (c) 2017-2018 Keller Fuchs (@KellerFuchs) <kellerfuchs@hashbang.sh>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Standard LDAP documentation fragment
    DOCUMENTATION = r"""
notes:
  - The default authentication settings attempts to use a SASL EXTERNAL bind over a UNIX domain socket. This works well with
    the default Ubuntu install for example, which includes a C(cn=peercred,cn=external,cn=auth) ACL rule allowing root to
    modify the server configuration. If you need to use a simple bind to access your server, pass the credentials in O(bind_dn)
    and O(bind_pw).
options:
  bind_dn:
    description:
      - A DN to bind with. Try to use a SASL bind with the EXTERNAL mechanism as default when this parameter is omitted.
      - Use an anonymous bind if the parameter is blank.
    type: str
  bind_pw:
    description:
      - The password to use with O(bind_dn).
    type: str
    default: ''
  ca_path:
    description:
      - Set the path to PEM file with CA certs.
    type: path
    version_added: "6.5.0"
  client_cert:
    type: path
    description:
      - PEM formatted certificate chain file to be used for SSL client authentication.
      - Required if O(client_key) is defined.
    version_added: "7.1.0"
  client_key:
    type: path
    description:
      - PEM formatted file that contains your private key to be used for SSL client authentication.
      - Required if O(client_cert) is defined.
    version_added: "7.1.0"
  dn:
    required: true
    description:
      - The DN of the entry to add or remove.
    type: str
  referrals_chasing:
    choices: [disabled, anonymous]
    default: anonymous
    type: str
    description:
      - Set the referrals chasing behavior.
      - V(anonymous) follow referrals anonymously. This is the default behavior.
      - V(disabled) disable referrals chasing. This sets C(OPT_REFERRALS) to off.
    version_added: 2.0.0
  server_uri:
    description:
      - The O(server_uri) parameter may be a comma- or whitespace-separated list of URIs containing only the schema, the host,
        and the port fields.
      - The default value lets the underlying LDAP client library look for a UNIX domain socket in its default location.
      - Note that when using multiple URIs you cannot determine to which URI your client gets connected.
      - For URIs containing additional fields, particularly when using commas, behavior is undefined.
    type: str
    default: ldapi:///
  start_tls:
    description:
      - Use the START_TLS LDAP extension if set to V(true).
    type: bool
    default: false
  validate_certs:
    description:
      - If set to V(false), SSL certificates are not validated.
      - This should only be used on sites using self-signed certificates.
    type: bool
    default: true
  sasl_class:
    description:
      - The class to use for SASL authentication.
    type: str
    choices: ['external', 'gssapi']
    default: external
    version_added: "2.0.0"
  xorder_discovery:
    description:
      - Set the behavior on how to process Xordered DNs.
      - V(enable) performs a C(ONELEVEL) search below the superior RDN to find the matching DN.
      - V(disable) always uses the DN unmodified (as passed by the O(dn) parameter).
      - V(auto) only performs a search if the first RDN does not contain an index number (C({x})).
    type: str
    choices: ['enable', 'auto', 'disable']
    default: auto
    version_added: "6.4.0"
"""

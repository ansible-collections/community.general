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
    DOCUMENTATION = r'''
options:
  bind_dn:
    description:
      - A DN to bind with. If this is omitted, we'll try a SASL bind with the EXTERNAL mechanism as default.
      - If this is blank, we'll use an anonymous bind.
    type: str
  bind_pw:
    description:
      - The password to use with I(bind_dn).
    type: str
    default: ''
  ca_path:
    description:
      - Set the path to PEM file with CA certs.
    type: path
    version_added: "6.5.0"
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
      - C(anonymous) follow referrals anonymously. This is the default behavior.
      - C(disabled) disable referrals chasing. This sets C(OPT_REFERRALS) to off.
    version_added: 2.0.0
  server_uri:
    description:
      - The I(server_uri) parameter may be a comma- or whitespace-separated list of URIs containing only the schema, the host, and the port fields.
      - The default value lets the underlying LDAP client library look for a UNIX domain socket in its default location.
      - Note that when using multiple URIs you cannot determine to which URI your client gets connected.
      - For URIs containing additional fields, particularly when using commas, behavior is undefined.
    type: str
    default: ldapi:///
  start_tls:
    description:
      - If true, we'll use the START_TLS LDAP extension.
    type: bool
    default: false
  validate_certs:
    description:
      - If set to C(false), SSL certificates will not be validated.
      - This should only be used on sites using self-signed certificates.
    type: bool
    default: true
  sasl_class:
    description:
      - The class to use for SASL authentication.
      - Possible choices are C(external), C(gssapi).
    type: str
    choices: ['external', 'gssapi']
    default: external
    version_added: "2.0.0"
  xorder_discovery:
    description:
      - Set the behavior on how to process Xordered DNs.
      - C(enable) will perform a C(ONELEVEL) search below the superior RDN to find the matching DN.
      - C(disable) will always use the DN unmodified (as passed by the I(dn) parameter).
      - C(auto) will only perform a search if the first RDN does not contain an index number (C({x})).
      - Possible choices are C(enable), C(auto), C(disable).
    type: str
    choices: ['enable', 'auto', 'disable']
    default: auto
    version_added: "6.4.0"
'''

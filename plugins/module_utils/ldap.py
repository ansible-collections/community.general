# Copyright (c) 2016, Peter Sagerson <psagers@ignorare.net>
# Copyright (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
# Copyright (c) 2017-2018 Keller Fuchs (@KellerFuchs) <kellerfuchs@hashbang.sh>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import re
import traceback
from ansible.module_utils.common.text.converters import to_native

try:
    import ldap
    import ldap.dn
    import ldap.filter
    import ldap.sasl

    HAS_LDAP = True

    SASCL_CLASS = {
        "gssapi": ldap.sasl.gssapi,
        "external": ldap.sasl.external,
    }
except ImportError:
    HAS_LDAP = False


def gen_specs(**specs):
    specs.update(
        {
            "bind_dn": dict(),
            "bind_pw": dict(default="", no_log=True),
            "ca_path": dict(type="path"),
            "dn": dict(required=True),
            "referrals_chasing": dict(type="str", default="anonymous", choices=["disabled", "anonymous"]),
            "server_uri": dict(default="ldapi:///"),
            "start_tls": dict(default=False, type="bool"),
            "validate_certs": dict(default=True, type="bool"),
            "sasl_class": dict(choices=["external", "gssapi"], default="external", type="str"),
            "xorder_discovery": dict(choices=["enable", "auto", "disable"], default="auto", type="str"),
            "client_cert": dict(default=None, type="path"),
            "client_key": dict(default=None, type="path"),
        }
    )

    return specs


def ldap_required_together():
    return [["client_cert", "client_key"]]


class LdapGeneric:
    def __init__(self, module):
        # Shortcuts
        self.module = module
        self.bind_dn = self.module.params["bind_dn"]
        self.bind_pw = self.module.params["bind_pw"]
        self.ca_path = self.module.params["ca_path"]
        self.referrals_chasing = self.module.params["referrals_chasing"]
        self.server_uri = self.module.params["server_uri"]
        self.start_tls = self.module.params["start_tls"]
        self.verify_cert = self.module.params["validate_certs"]
        self.sasl_class = self.module.params["sasl_class"]
        self.xorder_discovery = self.module.params["xorder_discovery"]
        self.client_cert = self.module.params["client_cert"]
        self.client_key = self.module.params["client_key"]

        # Establish connection
        self.connection = self._connect_to_ldap()

        if self.xorder_discovery == "enable" or (self.xorder_discovery == "auto" and not self._xorder_dn()):
            # Try to find the X_ORDERed version of the DN
            self.dn = self._find_dn()
        else:
            self.dn = self.module.params["dn"]

    def fail(self, msg, exn):
        self.module.fail_json(msg=msg, details=to_native(exn), exception=traceback.format_exc())

    def _find_dn(self):
        dn = self.module.params["dn"]

        explode_dn = ldap.dn.explode_dn(dn)

        if len(explode_dn) > 1:
            try:
                escaped_value = ldap.filter.escape_filter_chars(explode_dn[0])
                filterstr = f"({escaped_value})"
                dns = self.connection.search_s(",".join(explode_dn[1:]), ldap.SCOPE_ONELEVEL, filterstr)
                if len(dns) == 1:
                    dn, dummy = dns[0]
            except Exception:
                pass

        return dn

    def _connect_to_ldap(self):
        if not self.verify_cert:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        if self.ca_path:
            ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, self.ca_path)

        if self.client_cert and self.client_key:
            ldap.set_option(ldap.OPT_X_TLS_CERTFILE, self.client_cert)
            ldap.set_option(ldap.OPT_X_TLS_KEYFILE, self.client_key)

        connection = ldap.initialize(self.server_uri)

        if self.referrals_chasing == "disabled":
            # Switch off chasing of referrals (https://github.com/ansible-collections/community.general/issues/1067)
            connection.set_option(ldap.OPT_REFERRALS, 0)

        if self.start_tls:
            try:
                connection.start_tls_s()
            except ldap.LDAPError as e:
                self.fail("Cannot start TLS.", e)

        try:
            if self.bind_dn is not None:
                connection.simple_bind_s(self.bind_dn, self.bind_pw)
            else:
                klass = SASCL_CLASS.get(self.sasl_class, ldap.sasl.external)
                connection.sasl_interactive_bind_s("", klass())
        except ldap.LDAPError as e:
            self.fail("Cannot bind to the server.", e)

        return connection

    def _xorder_dn(self):
        # match X_ORDERed DNs
        regex = r".+\{\d+\}.+"
        explode_dn = ldap.dn.explode_dn(self.module.params["dn"])

        return re.match(regex, explode_dn[0]) is not None

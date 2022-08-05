# -*- coding: utf-8 -*-

# Copyright (c) 2016, Peter Sagerson <psagers@ignorare.net>
# Copyright (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
# Copyright (c) 2017-2018 Keller Fuchs (@KellerFuchs) <kellerfuchs@hashbang.sh>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import traceback
from ansible.module_utils.common.text.converters import to_native

try:
    import ldap
    import ldap.sasl

    HAS_LDAP = True

    SASCL_CLASS = {
        'gssapi': ldap.sasl.gssapi,
        'external': ldap.sasl.external,
    }
except ImportError:
    HAS_LDAP = False


def gen_specs(**specs):
    specs.update({
        'bind_dn': dict(),
        'bind_pw': dict(default='', no_log=True),
        'dn': dict(required=True),
        'referrals_chasing': dict(type='str', default='anonymous', choices=['disabled', 'anonymous']),
        'server_uri': dict(default='ldapi:///'),
        'start_tls': dict(default=False, type='bool'),
        'validate_certs': dict(default=True, type='bool'),
        'sasl_class': dict(choices=['external', 'gssapi'], default='external', type='str'),
    })

    return specs


class LdapGeneric(object):
    def __init__(self, module):
        # Shortcuts
        self.module = module
        self.bind_dn = self.module.params['bind_dn']
        self.bind_pw = self.module.params['bind_pw']
        self.dn = self.module.params['dn']
        self.referrals_chasing = self.module.params['referrals_chasing']
        self.server_uri = self.module.params['server_uri']
        self.start_tls = self.module.params['start_tls']
        self.verify_cert = self.module.params['validate_certs']
        self.sasl_class = self.module.params['sasl_class']

        # Establish connection
        self.connection = self._connect_to_ldap()

    def fail(self, msg, exn):
        self.module.fail_json(
            msg=msg,
            details=to_native(exn),
            exception=traceback.format_exc()
        )

    def _connect_to_ldap(self):
        if not self.verify_cert:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        connection = ldap.initialize(self.server_uri)

        if self.referrals_chasing == 'disabled':
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
                connection.sasl_interactive_bind_s('', klass())
        except ldap.LDAPError as e:
            self.fail("Cannot bind to the server.", e)

        return connection

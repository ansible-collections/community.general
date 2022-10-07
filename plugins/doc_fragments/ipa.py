# -*- coding: utf-8 -*-

# Copyright (c) 2017-18, Ansible Project
# Copyright (c) 2017-18, Abhijeet Kasurde (akasurde@redhat.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):
    # Parameters for FreeIPA/IPA modules
    DOCUMENTATION = r'''
options:
  ipa_port:
    description:
    - Port of FreeIPA / IPA server.
    - If the value is not specified in the task, the value of environment variable C(IPA_PORT) will be used instead.
    - If both the environment variable C(IPA_PORT) and the value are not specified in the task, then default value is set.
    - Environment variable fallback mechanism is added in Ansible 2.5.
    type: int
    default: 443
  ipa_host:
    description:
    - IP or hostname of IPA server.
    - If the value is not specified in the task, the value of environment variable C(IPA_HOST) will be used instead.
    - If both the environment variable C(IPA_HOST) and the value are not specified in the task, then DNS will be used to try to discover the FreeIPA server.
    - The relevant entry needed in FreeIPA is the 'ipa-ca' entry.
    - If neither the DNS entry, nor the environment C(IPA_HOST), nor the value are available in the task, then the default value will be used.
    - Environment variable fallback mechanism is added in Ansible 2.5.
    type: str
    default: ipa.example.com
  ipa_user:
    description:
    - Administrative account used on IPA server.
    - If the value is not specified in the task, the value of environment variable C(IPA_USER) will be used instead.
    - If both the environment variable C(IPA_USER) and the value are not specified in the task, then default value is set.
    - Environment variable fallback mechanism is added in Ansible 2.5.
    type: str
    default: admin
  ipa_pass:
    description:
    - Password of administrative user.
    - If the value is not specified in the task, the value of environment variable C(IPA_PASS) will be used instead.
    - Note that if the 'urllib_gssapi' library is available, it is possible to use GSSAPI to authenticate to FreeIPA.
    - If the environment variable C(KRB5CCNAME) is available, the module will use this kerberos credentials cache to authenticate to the FreeIPA server.
    - If the environment variable C(KRB5_CLIENT_KTNAME) is available, and C(KRB5CCNAME) is not; the module will use this kerberos keytab to authenticate.
    - If GSSAPI is not available, the usage of 'ipa_pass' is required.
    - Environment variable fallback mechanism is added in Ansible 2.5.
    type: str
  ipa_prot:
    description:
    - Protocol used by IPA server.
    - If the value is not specified in the task, the value of environment variable C(IPA_PROT) will be used instead.
    - If both the environment variable C(IPA_PROT) and the value are not specified in the task, then default value is set.
    - Environment variable fallback mechanism is added in Ansible 2.5.
    type: str
    choices: [ http, https ]
    default: https
  validate_certs:
    description:
    - This only applies if C(ipa_prot) is I(https).
    - If set to C(false), the SSL certificates will not be validated.
    - This should only set to C(false) used on personally controlled sites using self-signed certificates.
    type: bool
    default: true
  ipa_timeout:
    description:
    - Specifies idle timeout (in seconds) for the connection.
    - For bulk operations, you may want to increase this in order to avoid timeout from IPA server.
    - If the value is not specified in the task, the value of environment variable C(IPA_TIMEOUT) will be used instead.
    - If both the environment variable C(IPA_TIMEOUT) and the value are not specified in the task, then default value is set.
    type: int
    default: 10
'''

# Copyright (c) 2017-18, Ansible Project
# Copyright (c) 2017-18, Abhijeet Kasurde (akasurde@redhat.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


class ModuleDocFragment:
    # Parameters for FreeIPA/IPA modules
    DOCUMENTATION = r"""
options:
  ipa_port:
    description:
      - Port of FreeIPA / IPA server.
      - If the value is not specified in the task, the value of environment variable E(IPA_PORT) is used instead.
      - If both the environment variable E(IPA_PORT) and the value are not specified in the task, then default value is set.
    type: int
    default: 443
  ipa_host:
    description:
      - IP or hostname of IPA server.
      - If the value is not specified in the task, the value of environment variable E(IPA_HOST) is used instead.
      - If both the environment variable E(IPA_HOST) and the value are not specified in the task, then DNS is used to try
        to discover the FreeIPA server.
      - The relevant entry needed in FreeIPA is the C(ipa-ca) entry.
      - If neither the DNS entry, nor the environment E(IPA_HOST), nor the value are available in the task, then the default
        value is used.
    type: str
    default: ipa.example.com
  ipa_user:
    description:
      - Administrative account used on IPA server.
      - If the value is not specified in the task, the value of environment variable E(IPA_USER) is used instead.
      - If both the environment variable E(IPA_USER) and the value are not specified in the task, then default value is set.
    type: str
    default: admin
  ipa_pass:
    description:
      - Password of administrative user.
      - If the value is not specified in the task, the value of environment variable E(IPA_PASS) is used instead.
      - Note that if the C(urllib_gssapi) library is available, it is possible to use GSSAPI to authenticate to FreeIPA.
      - If the environment variable E(KRB5CCNAME) is available, the module uses this Kerberos credentials cache to authenticate
        to the FreeIPA server.
      - If the environment variable E(KRB5_CLIENT_KTNAME) is available, and E(KRB5CCNAME) is not; the module uses this Kerberos
        keytab to authenticate.
      - If GSSAPI is not available, the usage of O(ipa_pass) is required.
    type: str
  ipa_prot:
    description:
      - Protocol used by IPA server.
      - If the value is not specified in the task, the value of environment variable E(IPA_PROT) is used instead.
      - If both the environment variable E(IPA_PROT) and the value are not specified in the task, then default value is set.
    type: str
    choices: [http, https]
    default: https
  validate_certs:
    description:
      - This only applies if O(ipa_prot) is V(https).
      - If set to V(false), the SSL certificates are not validated.
      - This should only set to V(false) used on personally controlled sites using self-signed certificates.
    type: bool
    default: true
  ipa_timeout:
    description:
      - Specifies idle timeout (in seconds) for the connection.
      - For bulk operations, you may want to increase this in order to avoid timeout from IPA server.
      - If the value is not specified in the task, the value of environment variable E(IPA_TIMEOUT) is used instead.
      - If both the environment variable E(IPA_TIMEOUT) and the value are not specified in the task, then default value is
        set.
    type: int
    default: 10
"""

    CONNECTION_NOTES = r"""
options: {}
notes:
  - This module uses JSON-RPC over HTTP(S) to communicate with the FreeIPA server.
    If you need to enroll the managed node into FreeIPA realm, you might want to consider using the collection
    L(freeipa.ansible_freeipa, https://galaxy.ansible.com/ui/repo/published/freeipa/ansible_freeipa/), but shell access to one
    node from the realm is required to manage the deployment.
"""

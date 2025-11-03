#!/usr/bin/python
# Copyright (c) 2024 Alexander Bakanovskii <skottttt228@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: ipa_getkeytab
short_description: Manage keytab file in FreeIPA
version_added: 9.5.0
description:
  - Manage keytab file with C(ipa-getkeytab) utility.
  - See U(https://manpages.ubuntu.com/manpages/jammy/man1/ipa-getkeytab.1.html) for reference.
author: "Alexander Bakanovskii (@abakanovskii)"
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  path:
    description:
      - The base path where to put generated keytab file.
    type: path
    aliases: ["keytab"]
    required: true
  principal:
    description:
      - The non-realm part of the full principal name.
    type: str
    required: true
  ipa_host:
    description:
      - The IPA server to retrieve the keytab from (FQDN).
    type: str
  ldap_uri:
    description:
      - LDAP URI. If V(ldap://) is specified, STARTTLS is initiated by default.
      - Can not be used with the O(ipa_host) option.
    type: str
  bind_dn:
    description:
      - The LDAP DN to bind as when retrieving a keytab without Kerberos credentials.
      - Generally used with the O(bind_pw) option.
    type: str
  bind_pw:
    description:
      - The LDAP password to use when not binding with Kerberos.
    type: str
  password:
    description:
      - Use this password for the key instead of one randomly generated.
    type: str
  ca_cert:
    description:
      - The path to the IPA CA certificate used to validate LDAPS/STARTTLS connections.
    type: path
  sasl_mech:
    description:
      - SASL mechanism to use if O(bind_dn) and O(bind_pw) are not specified.
    choices: ["GSSAPI", "EXTERNAL"]
    type: str
  retrieve_mode:
    description:
      - Retrieve an existing key from the server instead of generating a new one.
      - This is incompatible with the O(password), and works only against a IPA server more recent than version 3.3.
      - The user requesting the keytab must have access to the keys for this operation to succeed.
      - Be aware that if set V(true), a new keytab is generated.
      - This invalidates all previously retrieved keytabs for this service principal.
    type: bool
  encryption_types:
    description:
      - The list of encryption types to use to generate keys.
      - It uses local client defaults if not provided.
      - Valid values depend on the Kerberos library version and configuration.
    type: str
  state:
    description:
      - The state of the keytab file.
      - V(present) only check for existence of a file, if you want to recreate keytab with other parameters you should set
        O(force=true).
    type: str
    default: present
    choices: ["present", "absent"]
  force:
    description:
      - Force recreation if exists already.
    type: bool
requirements:
  - freeipa-client
  - Managed host is FreeIPA client
extends_documentation_fragment:
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Get Kerberos ticket using default principal
  community.general.krb_ticket:
    password: "{{ aldpro_admin_password }}"

- name: Create keytab
  community.general.ipa_getkeytab:
    path: /etc/ipa/test.keytab
    principal: HTTP/freeipa-dc02.ipa.test
    ipa_host: freeipa-dc01.ipa.test

- name: Retrieve already existing keytab
  community.general.ipa_getkeytab:
    path: /etc/ipa/test.keytab
    principal: HTTP/freeipa-dc02.ipa.test
    ipa_host: freeipa-dc01.ipa.test
    retrieve_mode: true

- name: Force keytab recreation
  community.general.ipa_getkeytab:
    path: /etc/ipa/test.keytab
    principal: HTTP/freeipa-dc02.ipa.test
    ipa_host: freeipa-dc01.ipa.test
    force: true
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt


class IPAKeytab:
    def __init__(self, module, **kwargs):
        self.module = module
        self.path = kwargs["path"]
        self.state = kwargs["state"]
        self.principal = kwargs["principal"]
        self.ipa_host = kwargs["ipa_host"]
        self.ldap_uri = kwargs["ldap_uri"]
        self.bind_dn = kwargs["bind_dn"]
        self.bind_pw = kwargs["bind_pw"]
        self.password = kwargs["password"]
        self.ca_cert = kwargs["ca_cert"]
        self.sasl_mech = kwargs["sasl_mech"]
        self.retrieve_mode = kwargs["retrieve_mode"]
        self.encryption_types = kwargs["encryption_types"]

        self.runner = CmdRunner(
            module,
            command="ipa-getkeytab",
            arg_formats=dict(
                retrieve_mode=cmd_runner_fmt.as_bool("--retrieve"),
                path=cmd_runner_fmt.as_opt_val("--keytab"),
                ipa_host=cmd_runner_fmt.as_opt_val("--server"),
                principal=cmd_runner_fmt.as_opt_val("--principal"),
                ldap_uri=cmd_runner_fmt.as_opt_val("--ldapuri"),
                bind_dn=cmd_runner_fmt.as_opt_val("--binddn"),
                bind_pw=cmd_runner_fmt.as_opt_val("--bindpw"),
                password=cmd_runner_fmt.as_opt_val("--password"),
                ca_cert=cmd_runner_fmt.as_opt_val("--cacert"),
                sasl_mech=cmd_runner_fmt.as_opt_val("--mech"),
                encryption_types=cmd_runner_fmt.as_opt_val("--enctypes"),
            ),
        )

    def _exec(self, check_rc=True):
        with self.runner(
            "retrieve_mode path ipa_host principal ldap_uri bind_dn bind_pw password ca_cert sasl_mech encryption_types",
            check_rc=check_rc,
        ) as ctx:
            rc, out, err = ctx.run()
        return out


def main():
    arg_spec = dict(
        path=dict(type="path", required=True, aliases=["keytab"]),
        state=dict(default="present", choices=["present", "absent"]),
        principal=dict(type="str", required=True),
        ipa_host=dict(type="str"),
        ldap_uri=dict(type="str"),
        bind_dn=dict(type="str"),
        bind_pw=dict(type="str"),
        password=dict(type="str", no_log=True),
        ca_cert=dict(type="path"),
        sasl_mech=dict(type="str", choices=["GSSAPI", "EXTERNAL"]),
        retrieve_mode=dict(type="bool"),
        encryption_types=dict(type="str"),
        force=dict(type="bool"),
    )
    module = AnsibleModule(
        argument_spec=arg_spec,
        mutually_exclusive=[("ipa_host", "ldap_uri"), ("retrieve_mode", "password")],
        supports_check_mode=True,
    )

    path = module.params["path"]
    state = module.params["state"]
    force = module.params["force"]

    keytab = IPAKeytab(
        module,
        path=path,
        state=state,
        principal=module.params["principal"],
        ipa_host=module.params["ipa_host"],
        ldap_uri=module.params["ldap_uri"],
        bind_dn=module.params["bind_dn"],
        bind_pw=module.params["bind_pw"],
        password=module.params["password"],
        ca_cert=module.params["ca_cert"],
        sasl_mech=module.params["sasl_mech"],
        retrieve_mode=module.params["retrieve_mode"],
        encryption_types=module.params["encryption_types"],
    )

    changed = False
    if state == "present":
        if os.path.exists(path):
            if force and not module.check_mode:
                try:
                    os.remove(path)
                except OSError as e:
                    module.fail_json(msg=f"Error deleting: {e.filename} - {e.strerror}.")
                keytab._exec()
                changed = True
            if force and module.check_mode:
                changed = True
        else:
            changed = True
            keytab._exec()

    if state == "absent":
        if os.path.exists(path):
            changed = True
            if not module.check_mode:
                try:
                    os.remove(path)
                except OSError as e:
                    module.fail_json(msg=f"Error deleting: {e.filename} - {e.strerror}.")

    module.exit_json(changed=changed)


if __name__ == "__main__":
    main()

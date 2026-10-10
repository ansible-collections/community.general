# Copyright (c) 2018, Scott Buchanan <scott@buchanan.works>
# Copyright (c) 2016, Andrew Zenk <azenk@umn.edu> (lastpass.py used as starting point)
# Copyright (c) 2018, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: onepassword
author:
  - Scott Buchanan (@scottsb)
  - Andrew Zenk (@azenk)
  - Sam Doran (@samdoran)
short_description: Fetch field values from 1Password
description:
  - P(community.general.onepassword#lookup) wraps the C(op) command line utility to fetch specific field values from 1Password.
options:
  _terms:
    description:
      - Identifier(s) (case-insensitive UUID or name or secret reference) of item(s) to retrieve.
      - Secret references start with V(op://) and are supported since community.general 13.0.0.
    required: true
    type: list
    elements: string
  account_id:
    version_added: 7.5.0
  domain:
    version_added: 3.2.0
  field:
    description:
      - Field to return from each matching item (case-insensitive).
      - Ignored when using a secret reference, as the field is included in the secret reference.
    default: 'password'
    type: str
  service_account_token:
    version_added: 7.1.0
extends_documentation_fragment:
  - community.general._onepassword
  - community.general._onepassword.lookup
"""

EXAMPLES = r"""
# These examples only work when already signed in to 1Password
- name: Retrieve password for KITT when already signed in to 1Password
  ansible.builtin.debug:
    var: lookup('community.general.onepassword', 'KITT')

- name: Retrieve password for Wintermute when already signed in to 1Password
  ansible.builtin.debug:
    var: lookup('community.general.onepassword', 'Tessier-Ashpool', section='Wintermute')

- name: Retrieve username for HAL when already signed in to 1Password
  ansible.builtin.debug:
    var: lookup('community.general.onepassword', 'HAL 9000', field='username', vault='Discovery')

- name: Retrieve password for HAL when not signed in to 1Password
  ansible.builtin.debug:
    var: lookup('community.general.onepassword', 'HAL 9000', subdomain='Discovery', master_password=vault_master_password)

- name: Retrieve password for HAL when never signed in to 1Password
  ansible.builtin.debug:
    var: >-
      lookup('community.general.onepassword', 'HAL 9000', subdomain='Discovery', master_password=vault_master_password,
             username='tweety@acme.com', secret_key=vault_secret_key)

- name: Retrieve password from specific account
  ansible.builtin.debug:
    var: lookup('community.general.onepassword', 'HAL 9000', account_id='abc123')
"""

RETURN = r"""
_raw:
  description: Field data requested.
  type: list
  elements: str
"""

import os
import subprocess
from contextlib import contextmanager

from ansible.errors import AnsibleLookupError, AnsibleOptionsError
from ansible.plugins.lookup import LookupBase

from ansible_collections.community.general.plugins.module_utils._onepassword_cli import (
    OnePass,
    OnePasswordError,
    OnePasswordOptionsError,
)
from ansible_collections.community.general.plugins.plugin_utils._lookup import check_for_wrong_terms


@contextmanager
def onepassword_errors():
    try:
        yield
    except OnePasswordOptionsError as e:
        raise AnsibleOptionsError(str(e)) from None
    except OnePasswordError as e:
        raise AnsibleLookupError(str(e)) from None


def run_command(command, command_input=None, environment_update=None):
    call_kwargs = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "stdin": subprocess.PIPE,
    }

    if environment_update:
        env = os.environ.copy()
        env.update(environment_update)
        call_kwargs["env"] = env

    p = subprocess.Popen(command, **call_kwargs)
    out, err = p.communicate(input=command_input)
    rc = p.wait()

    return rc, out, err


class LookupModule(LookupBase):
    @onepassword_errors()
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        check_for_wrong_terms(self, direct=kwargs)

        field = self.get_option("field")
        section = self.get_option("section")
        vault = self.get_option("vault")
        subdomain = self.get_option("subdomain")
        domain = self.get_option("domain")
        username = self.get_option("username")
        secret_key = self.get_option("secret_key")
        master_password = self.get_option("master_password")
        service_account_token = self.get_option("service_account_token")
        account_id = self.get_option("account_id")
        connect_host = self.get_option("connect_host")
        connect_token = self.get_option("connect_token")

        op = OnePass(
            subdomain=subdomain,
            domain=domain,
            username=username,
            secret_key=secret_key,
            master_password=master_password,
            service_account_token=service_account_token,
            account_id=account_id,
            connect_host=connect_host,
            connect_token=connect_token,
            run_command=run_command,
        )
        op.assert_logged_in()

        values = []
        for term in terms:
            if term.startswith("op://"):
                values.append(op.get_secret_reference(term))
            else:
                values.append(op.get_field(term, field, section, vault))

        return values

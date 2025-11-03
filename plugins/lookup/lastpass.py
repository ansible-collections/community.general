# Copyright (c) 2016, Andrew Zenk <azenk@umn.edu>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
name: lastpass
author:
  - Andrew Zenk (!UNKNOWN) <azenk@umn.edu>
requirements:
  - lpass (command line utility)
  - must have already logged into LastPass
short_description: Fetch data from LastPass
description:
  - Use the lpass command line utility to fetch specific fields from LastPass.
options:
  _terms:
    description: Key from which you want to retrieve the field.
    required: true
    type: list
    elements: str
  field:
    description: Field to return from LastPass.
    default: 'password'
    type: str
"""

EXAMPLES = r"""
- name: get 'custom_field' from LastPass entry 'entry-name'
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.lastpass', 'entry-name', field='custom_field') }}"
"""

RETURN = r"""
_raw:
  description: Secrets stored.
  type: list
  elements: str
"""

from subprocess import Popen, PIPE

from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import to_bytes, to_text
from ansible.plugins.lookup import LookupBase


class LPassException(AnsibleError):
    pass


class LPass:
    def __init__(self, path="lpass"):
        self._cli_path = path

    @property
    def cli_path(self):
        return self._cli_path

    @property
    def logged_in(self):
        out, err = self._run(self._build_args("logout"), stdin="n\n", expected_rc=1)
        return err.startswith("Are you sure you would like to log out?")

    def _run(self, args, stdin=None, expected_rc=0):
        p = Popen([self.cli_path] + args, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        out, err = p.communicate(to_bytes(stdin))
        rc = p.wait()
        if rc != expected_rc:
            raise LPassException(err)
        return to_text(out, errors="surrogate_or_strict"), to_text(err, errors="surrogate_or_strict")

    def _build_args(self, command, args=None):
        if args is None:
            args = []
        args = [command] + args
        args += ["--color=never"]
        return args

    def get_field(self, key, field):
        if field in ["username", "password", "url", "notes", "id", "name"]:
            out, err = self._run(self._build_args("show", [f"--{field}", key]))
        else:
            out, err = self._run(self._build_args("show", [f"--field={field}", key]))
        return out.strip()


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        field = self.get_option("field")

        lp = LPass()

        if not lp.logged_in:
            raise AnsibleError("Not logged into LastPass: please run 'lpass login' first")

        values = []
        for term in terms:
            values.append(lp.get_field(term, field))
        return values

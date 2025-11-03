# Copyright (c) 2017-2018, Jan-Piet Mens <jpmens(at)gmail.com>
# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

DOCUMENTATION = r"""
name: lmdb_kv
author:
  - Jan-Piet Mens (@jpmens)
version_added: '0.2.0'
short_description: Fetch data from LMDB
description:
  - This lookup returns a list of results from an LMDB DB corresponding to a list of items given to it.
requirements:
  - lmdb (Python library U(https://lmdb.readthedocs.io/en/release/))
options:
  _terms:
    description: List of keys to query.
    type: list
    elements: str
  db:
    description: Path to LMDB database.
    type: str
    default: 'ansible.mdb'
    vars:
      - name: lmdb_kv_db
"""

EXAMPLES = r"""
- name: query LMDB for a list of country codes
  ansible.builtin.debug:
    msg: "{{ query('community.general.lmdb_kv', 'nl', 'be', 'lu', db='jp.mdb') }}"

- name: use list of values in a loop by key wildcard
  ansible.builtin.debug:
    msg: "Hello from {{ item.0 }} a.k.a. {{ item.1 }}"
  vars:
    - lmdb_kv_db: jp.mdb
  with_community.general.lmdb_kv:
    - "n*"

- name: get an item by key
  ansible.builtin.assert:
    that:
      - item == 'Belgium'
    vars:
      - lmdb_kv_db: jp.mdb
  with_community.general.lmdb_kv:
    - be
"""

RETURN = r"""
_raw:
  description: Value(s) stored in LMDB.
  type: list
  elements: raw
"""


from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_native, to_text

HAVE_LMDB = True
try:
    import lmdb
except ImportError:
    HAVE_LMDB = False


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        """
        terms contain any number of keys to be retrieved.
        If terms is None, all keys from the database are returned
        with their values, and if term ends in an asterisk, we
        start searching there

        The LMDB database defaults to 'ansible.mdb' if Ansible's
        variable 'lmdb_kv_db' is not set:

              vars:
                - lmdb_kv_db: "jp.mdb"
        """
        if HAVE_LMDB is False:
            raise AnsibleError("Can't LOOKUP(lmdb_kv): this module requires lmdb to be installed")

        self.set_options(var_options=variables, direct=kwargs)

        db = self.get_option("db")

        try:
            env = lmdb.open(str(db), readonly=True)
        except Exception as e:
            raise AnsibleError(f"LMDB cannot open database {db}: {e}")

        ret = []
        if len(terms) == 0:
            with env.begin() as txn:
                cursor = txn.cursor()
                cursor.first()
                for key, value in cursor:
                    ret.append((to_text(key), to_native(value)))

        else:
            for term in terms:
                with env.begin() as txn:
                    if term.endswith("*"):
                        cursor = txn.cursor()
                        prefix = term[:-1]  # strip asterisk
                        cursor.set_range(to_text(term).encode())
                        while cursor.key().startswith(to_text(prefix).encode()):
                            for key, value in cursor:
                                ret.append((to_text(key), to_native(value)))
                            cursor.next()
                    else:
                        value = txn.get(to_text(term).encode())
                        if value is not None:
                            ret.append(to_native(value))

        return ret

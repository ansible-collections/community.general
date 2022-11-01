# -*- coding: utf-8 -*-
# Copyright (c) 2012, Jan-Piet Mens <jpmens(at)gmail.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: dnstxt
    author: Jan-Piet Mens (@jpmens) <jpmens(at)gmail.com>
    short_description: query a domain(s)'s DNS txt fields
    requirements:
      - dns/dns.resolver (python library)
    description:
      - Uses a python library to return the DNS TXT record for a domain.
    options:
      _terms:
        description: domain or list of domains to query TXT records from
        required: true
        type: list
        elements: string
      real_empty:
        description:
          - Return empty result without empty strings, and return empty list instead of C(NXDOMAIN).
          - The default for this option will likely change to C(true) in the future.
        default: false
        type: bool
        version_added: 6.0.0
'''

EXAMPLES = """
- name: show txt entry
  ansible.builtin.debug:
    msg: "{{lookup('community.general.dnstxt', ['test.example.com'])}}"

- name: iterate over txt entries
  ansible.builtin.debug:
    msg: "{{item}}"
  with_community.general.dnstxt:
    - 'test.example.com'
    - 'other.example.com'
    - 'last.example.com'

- name: iterate of a comma delimited DNS TXT entry
  ansible.builtin.debug:
    msg: "{{item}}"
  with_community.general.dnstxt: "{{lookup('community.general.dnstxt', ['test.example.com']).split(',')}}"
"""

RETURN = """
  _list:
    description:
      - values returned by the DNS TXT record.
    type: list
"""

HAVE_DNS = False
try:
    import dns.resolver
    from dns.exception import DNSException
    HAVE_DNS = True
except ImportError:
    pass

from ansible.errors import AnsibleError
from ansible.module_utils.common.text.converters import to_native
from ansible.plugins.lookup import LookupBase

# ==============================================================
# DNSTXT: DNS TXT records
#
#       key=domainname
# TODO: configurable resolver IPs
# --------------------------------------------------------------


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        if HAVE_DNS is False:
            raise AnsibleError("Can't LOOKUP(dnstxt): module dns.resolver is not installed")

        real_empty = self.get_option('real_empty')

        ret = []
        for term in terms:
            domain = term.split()[0]
            string = []
            try:
                answers = dns.resolver.query(domain, 'TXT')
                for rdata in answers:
                    s = rdata.to_text()
                    string.append(s[1:-1])  # Strip outside quotes on TXT rdata

            except dns.resolver.NXDOMAIN:
                if real_empty:
                    continue
                string = 'NXDOMAIN'
            except dns.resolver.Timeout:
                if real_empty:
                    continue
                string = ''
            except dns.resolver.NoAnswer:
                if real_empty:
                    continue
                string = ''
            except DNSException as e:
                raise AnsibleError("dns.resolver unhandled exception %s" % to_native(e))

            ret.append(''.join(string))

        return ret

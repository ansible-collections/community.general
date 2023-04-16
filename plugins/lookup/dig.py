# -*- coding: utf-8 -*-
# Copyright (c) 2015, Jan-Piet Mens <jpmens(at)gmail.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: dig
    author: Jan-Piet Mens (@jpmens) <jpmens(at)gmail.com>
    short_description: query DNS using the dnspython library
    requirements:
      - dnspython (python library, http://www.dnspython.org/)
    description:
      - The dig lookup runs queries against DNS servers to retrieve DNS records for a specific name (FQDN - fully qualified domain name).
        It is possible to lookup any DNS record in this manner.
      - There is a couple of different syntaxes that can be used to specify what record should be retrieved, and for which name.
         It is also possible to explicitly specify the DNS server(s) to use for lookups.
      - In its simplest form, the dig lookup plugin can be used to retrieve an IPv4 address (DNS A record) associated with FQDN
      - In addition to (default) A record, it is also possible to specify a different record type that should be queried.
        This can be done by either passing-in additional parameter of format qtype=TYPE to the dig lookup, or by appending /TYPE to the FQDN being queried.
      - If multiple values are associated with the requested record, the results will be returned as a comma-separated list.
        In such cases you may want to pass option I(wantlist=true) to the lookup call, or alternatively use C(query) instead of C(lookup),
        which will result in the record values being returned as a list over which you can iterate later on.
      - By default, the lookup will rely on system-wide configured DNS servers for performing the query.
        It is also possible to explicitly specify DNS servers to query using the @DNS_SERVER_1,DNS_SERVER_2,...,DNS_SERVER_N notation.
        This needs to be passed-in as an additional parameter to the lookup
    options:
      _terms:
        description: Domain(s) to query.
        type: list
        elements: str
      qtype:
        description:
            - Record type to query.
            - C(DLV) has been removed in community.general 6.0.0.
            - C(CAA) has been added in community.general 6.3.0.
        type: str
        default: 'A'
        choices: [A, ALL, AAAA, CAA, CNAME, DNAME, DNSKEY, DS, HINFO, LOC, MX, NAPTR, NS, NSEC3PARAM, PTR, RP, RRSIG, SOA, SPF, SRV, SSHFP, TLSA, TXT]
      flat:
        description: If 0 each record is returned as a dictionary, otherwise a string.
        type: int
        default: 1
      retry_servfail:
        description: Retry a nameserver if it returns SERVFAIL.
        default: false
        type: bool
        version_added: 3.6.0
      fail_on_error:
        description:
          - Abort execution on lookup errors.
          - The default for this option will likely change to C(true) in the future.
            The current default, C(false), is used for backwards compatibility, and will result in empty strings
            or the string C(NXDOMAIN) in the result in case of errors.
        default: false
        type: bool
        version_added: 5.4.0
      real_empty:
        description:
          - Return empty result without empty strings, and return empty list instead of C(NXDOMAIN).
          - The default for this option will likely change to C(true) in the future.
          - This option will be forced to C(true) if multiple domains to be queried are specified.
        default: false
        type: bool
        version_added: 6.0.0
      class:
        description:
          - "Class."
        type: str
        default: 'IN'
    notes:
      - ALL is not a record per-se, merely the listed fields are available for any record results you retrieve in the form of a dictionary.
      - While the 'dig' lookup plugin supports anything which dnspython supports out of the box, only a subset can be converted into a dictionary.
      - If you need to obtain the AAAA record (IPv6 address), you must specify the record type explicitly.
        Syntax for specifying the record type is shown in the examples below.
      - The trailing dot in most of the examples listed is purely optional, but is specified for completeness/correctness sake.
'''

EXAMPLES = """
- name: Simple A record (IPV4 address) lookup for example.com
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.dig', 'example.com.')}}"

- name: "The TXT record for example.org."
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.dig', 'example.org.', qtype='TXT') }}"

- name: "The TXT record for example.org, alternative syntax."
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.dig', 'example.org./TXT') }}"

- name: use in a loop
  ansible.builtin.debug:
    msg: "MX record for gmail.com {{ item }}"
  with_items: "{{ lookup('community.general.dig', 'gmail.com./MX', wantlist=true) }}"

- name: Lookup multiple names at once
  ansible.builtin.debug:
    msg: "A record found {{ item }}"
  loop: "{{ query('community.general.dig', 'example.org.', 'example.com.', 'gmail.com.') }}"

- name: Lookup multiple names at once (from list variable)
  ansible.builtin.debug:
    msg: "A record found {{ item }}"
  loop: "{{ query('community.general.dig', *hosts) }}"
  vars:
    hosts:
      - example.org.
      - example.com.
      - gmail.com.

- ansible.builtin.debug:
    msg: "Reverse DNS for 192.0.2.5 is {{ lookup('community.general.dig', '192.0.2.5/PTR') }}"
- ansible.builtin.debug:
    msg: "Reverse DNS for 192.0.2.5 is {{ lookup('community.general.dig', '5.2.0.192.in-addr.arpa./PTR') }}"
- ansible.builtin.debug:
    msg: "Reverse DNS for 192.0.2.5 is {{ lookup('community.general.dig', '5.2.0.192.in-addr.arpa.', qtype='PTR') }}"
- ansible.builtin.debug:
    msg: "Querying 198.51.100.23 for IPv4 address for example.com. produces {{ lookup('dig', 'example.com', '@198.51.100.23') }}"

- ansible.builtin.debug:
    msg: "XMPP service for gmail.com. is available at {{ item.target }} on port {{ item.port }}"
  with_items: "{{ lookup('community.general.dig', '_xmpp-server._tcp.gmail.com./SRV', flat=0, wantlist=true) }}"

- name: Retry nameservers that return SERVFAIL
  ansible.builtin.debug:
    msg: "{{ lookup('community.general.dig', 'example.org./A', retry_servfail=true) }}"
"""

RETURN = """
  _list:
    description:
      - List of composed strings or dictionaries with key and value
        If a dictionary, fields shows the keys returned depending on query type
    type: list
    elements: raw
    contains:
       ALL:
           description:
               - owner, ttl, type
       A:
           description:
               - address
       AAAA:
           description:
               - address
       CAA:
           description:
               - flags
               - tag
               - value
           version_added: 6.3.0
       CNAME:
           description:
               - target
       DNAME:
           description:
               - target
       DNSKEY:
            description:
                - flags, algorithm, protocol, key
       DS:
            description:
                - algorithm, digest_type, key_tag, digest
       HINFO:
            description:
                -  cpu, os
       LOC:
            description:
                - latitude, longitude, altitude, size, horizontal_precision, vertical_precision
       MX:
            description:
                - preference, exchange
       NAPTR:
            description:
                - order, preference, flags, service, regexp, replacement
       NS:
            description:
                - target
       NSEC3PARAM:
            description:
                - algorithm, flags, iterations, salt
       PTR:
            description:
                - target
       RP:
            description:
                - mbox, txt
       SOA:
            description:
                - mname, rname, serial, refresh, retry, expire, minimum
       SPF:
            description:
                - strings
       SRV:
            description:
                - priority, weight, port, target
       SSHFP:
            description:
                - algorithm, fp_type, fingerprint
       TLSA:
            description:
                - usage, selector, mtype, cert
       TXT:
            description:
                - strings
"""

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.utils.display import Display
import socket

try:
    import dns.exception
    import dns.name
    import dns.resolver
    import dns.reversename
    import dns.rdataclass
    from dns.rdatatype import (A, AAAA, CAA, CNAME, DNAME, DNSKEY, DS, HINFO, LOC,
                               MX, NAPTR, NS, NSEC3PARAM, PTR, RP, SOA, SPF, SRV, SSHFP, TLSA, TXT)
    HAVE_DNS = True
except ImportError:
    HAVE_DNS = False


display = Display()


def make_rdata_dict(rdata):
    ''' While the 'dig' lookup plugin supports anything which dnspython supports
        out of the box, the following supported_types list describes which
        DNS query types we can convert to a dict.

        Note: adding support for RRSIG is hard work. :)
    '''
    supported_types = {
        A: ['address'],
        AAAA: ['address'],
        CAA: ['flags', 'tag', 'value'],
        CNAME: ['target'],
        DNAME: ['target'],
        DNSKEY: ['flags', 'algorithm', 'protocol', 'key'],
        DS: ['algorithm', 'digest_type', 'key_tag', 'digest'],
        HINFO: ['cpu', 'os'],
        LOC: ['latitude', 'longitude', 'altitude', 'size', 'horizontal_precision', 'vertical_precision'],
        MX: ['preference', 'exchange'],
        NAPTR: ['order', 'preference', 'flags', 'service', 'regexp', 'replacement'],
        NS: ['target'],
        NSEC3PARAM: ['algorithm', 'flags', 'iterations', 'salt'],
        PTR: ['target'],
        RP: ['mbox', 'txt'],
        # RRSIG: ['type_covered', 'algorithm', 'labels', 'original_ttl', 'expiration', 'inception', 'key_tag', 'signer', 'signature'],
        SOA: ['mname', 'rname', 'serial', 'refresh', 'retry', 'expire', 'minimum'],
        SPF: ['strings'],
        SRV: ['priority', 'weight', 'port', 'target'],
        SSHFP: ['algorithm', 'fp_type', 'fingerprint'],
        TLSA: ['usage', 'selector', 'mtype', 'cert'],
        TXT: ['strings'],
    }

    rd = {}

    if rdata.rdtype in supported_types:
        fields = supported_types[rdata.rdtype]
        for f in fields:
            val = rdata.__getattribute__(f)

            if isinstance(val, dns.name.Name):
                val = dns.name.Name.to_text(val)

            if rdata.rdtype == DS and f == 'digest':
                val = dns.rdata._hexify(rdata.digest).replace(' ', '')
            if rdata.rdtype == DNSKEY and f == 'algorithm':
                val = int(val)
            if rdata.rdtype == DNSKEY and f == 'key':
                val = dns.rdata._base64ify(rdata.key).replace(' ', '')
            if rdata.rdtype == NSEC3PARAM and f == 'salt':
                val = dns.rdata._hexify(rdata.salt).replace(' ', '')
            if rdata.rdtype == SSHFP and f == 'fingerprint':
                val = dns.rdata._hexify(rdata.fingerprint).replace(' ', '')
            if rdata.rdtype == TLSA and f == 'cert':
                val = dns.rdata._hexify(rdata.cert).replace(' ', '')

            rd[f] = val

    return rd


# ==============================================================
# dig: Lookup DNS records
#
# --------------------------------------------------------------

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        '''
        terms contains a string with things to `dig' for. We support the
        following formats:
            example.com                                     # A record
            example.com  qtype=A                            # same
            example.com/TXT                                 # specific qtype
            example.com  qtype=txt                          # same
            192.0.2.23/PTR                                 # reverse PTR
              ^^ shortcut for 23.2.0.192.in-addr.arpa/PTR
            example.net/AAAA  @nameserver                   # query specified server
                               ^^^ can be comma-sep list of names/addresses

            ... flat=0                                      # returns a dict; default is 1 == string
        '''
        if HAVE_DNS is False:
            raise AnsibleError("The dig lookup requires the python 'dnspython' library and it is not installed")

        self.set_options(var_options=variables, direct=kwargs)

        # Create Resolver object so that we can set NS if necessary
        myres = dns.resolver.Resolver(configure=True)
        edns_size = 4096
        myres.use_edns(0, ednsflags=dns.flags.DO, payload=edns_size)

        domains = []
        qtype = self.get_option('qtype')
        flat = self.get_option('flat')
        fail_on_error = self.get_option('fail_on_error')
        real_empty = self.get_option('real_empty')
        try:
            rdclass = dns.rdataclass.from_text(self.get_option('class'))
        except Exception as e:
            raise AnsibleError("dns lookup illegal CLASS: %s" % to_native(e))
        myres.retry_servfail = self.get_option('retry_servfail')

        for t in terms:
            if t.startswith('@'):       # e.g. "@10.0.1.2,192.0.2.1" is ok.
                nsset = t[1:].split(',')
                for ns in nsset:
                    nameservers = []
                    # Check if we have a valid IP address. If so, use that, otherwise
                    # try to resolve name to address using system's resolver. If that
                    # fails we bail out.
                    try:
                        socket.inet_aton(ns)
                        nameservers.append(ns)
                    except Exception:
                        try:
                            nsaddr = dns.resolver.query(ns)[0].address
                            nameservers.append(nsaddr)
                        except Exception as e:
                            raise AnsibleError("dns lookup NS: %s" % to_native(e))
                    myres.nameservers = nameservers
                continue
            if '=' in t:
                try:
                    opt, arg = t.split('=', 1)
                except Exception:
                    pass

                if opt == 'qtype':
                    qtype = arg.upper()
                elif opt == 'flat':
                    flat = int(arg)
                elif opt == 'class':
                    try:
                        rdclass = dns.rdataclass.from_text(arg)
                    except Exception as e:
                        raise AnsibleError("dns lookup illegal CLASS: %s" % to_native(e))
                elif opt == 'retry_servfail':
                    myres.retry_servfail = boolean(arg)
                elif opt == 'fail_on_error':
                    fail_on_error = boolean(arg)
                elif opt == 'real_empty':
                    real_empty = boolean(arg)

                continue

            if '/' in t:
                try:
                    domain, qtype = t.split('/')
                    domains.append(domain)
                except Exception:
                    domains.append(t)
            else:
                domains.append(t)

        # print "--- domain = {0} qtype={1} rdclass={2}".format(domain, qtype, rdclass)

        if qtype.upper() == 'PTR':
            reversed_domains = []
            for domain in domains:
                try:
                    n = dns.reversename.from_address(domain)
                    reversed_domains.append(n.to_text())
                except dns.exception.SyntaxError:
                    pass
                except Exception as e:
                    raise AnsibleError("dns.reversename unhandled exception %s" % to_native(e))
            domains = reversed_domains

        if len(domains) > 1:
            real_empty = True

        ret = []

        for domain in domains:
            try:
                answers = myres.query(domain, qtype, rdclass=rdclass)
                for rdata in answers:
                    s = rdata.to_text()
                    if qtype.upper() == 'TXT':
                        s = s[1:-1]  # Strip outside quotes on TXT rdata

                    if flat:
                        ret.append(s)
                    else:
                        try:
                            rd = make_rdata_dict(rdata)
                            rd['owner'] = answers.canonical_name.to_text()
                            rd['type'] = dns.rdatatype.to_text(rdata.rdtype)
                            rd['ttl'] = answers.rrset.ttl
                            rd['class'] = dns.rdataclass.to_text(rdata.rdclass)

                            ret.append(rd)
                        except Exception as err:
                            if fail_on_error:
                                raise AnsibleError("Lookup failed: %s" % str(err))
                            ret.append(str(err))

            except dns.resolver.NXDOMAIN as err:
                if fail_on_error:
                    raise AnsibleError("Lookup failed: %s" % str(err))
                if not real_empty:
                    ret.append('NXDOMAIN')
            except dns.resolver.NoAnswer as err:
                if fail_on_error:
                    raise AnsibleError("Lookup failed: %s" % str(err))
                if not real_empty:
                    ret.append("")
            except dns.resolver.Timeout as err:
                if fail_on_error:
                    raise AnsibleError("Lookup failed: %s" % str(err))
                if not real_empty:
                    ret.append("")
            except dns.exception.DNSException as err:
                raise AnsibleError("dns.resolver unhandled exception %s" % to_native(err))

        return ret

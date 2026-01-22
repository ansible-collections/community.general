#!/usr/bin/python

# Copyright (c) 2016, Marcin Skarbek <github@skarbek.name>
# Copyright (c) 2016, Andreas Olsson <andreas@arrakis.se>
# Copyright (c) 2017, Loic Blot <loic.blot@unix-experience.fr>
#
# This module was ported from https://github.com/mskarbek/ansible-nsupdate
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: nsupdate

short_description: Manage DNS records
description:
  - Create, update and remove DNS records using DDNS updates.
requirements:
  - dnspython
  - gssapi (when using GSS-TSIG authentication)
author: "Loic Blot (@nerzhul)"
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  state:
    description:
      - Manage DNS record.
    choices: ['present', 'absent']
    default: 'present'
    type: str
  server:
    description:
      - Apply DNS modification on this server, specified by IPv4/IPv6 address or FQDN.
      - FQDNs are supported since community.general 12.3.0.
    required: true
    type: str
  port:
    description:
      - Use this TCP port when connecting to O(server).
    default: 53
    type: int
  key_name:
    description:
      - Use TSIG key name to authenticate against DNS O(server).
      - Not required when using O(key_algorithm=gss-tsig).
    type: str
  key_secret:
    description:
      - Use TSIG key secret, associated with O(key_name), to authenticate against O(server).
      - Not required when using O(key_algorithm=gss-tsig).
    type: str
  key_algorithm:
    description:
      - Specify key algorithm used by O(key_secret).
      - Use V(gss-tsig) for GSS-TSIG authentication (requires the gssapi library and Kerberos credentials).
      - V(gss-tsig) was added in community.general 12.3.0.
    choices: ['HMAC-MD5.SIG-ALG.REG.INT', 'hmac-md5', 'hmac-sha1', 'hmac-sha224', 'hmac-sha256', 'hmac-sha384', 'hmac-sha512', 'gss-tsig']
    default: 'hmac-md5'
    type: str
  zone:
    description:
      - DNS record is modified on this O(zone).
      - When omitted, DNS is queried to attempt finding the correct zone.
    type: str
  record:
    description:
      - Sets the DNS record to modify. When zone is omitted this has to be absolute (ending with a dot).
    required: true
    type: str
  type:
    description:
      - Sets the record type.
    default: 'A'
    type: str
  ttl:
    description:
      - Sets the record TTL.
    default: 3600
    type: int
  value:
    description:
      - Sets the record value.
    type: list
    elements: str
  protocol:
    description:
      - Sets the transport protocol (TCP or UDP). TCP is the recommended and a more robust option.
    default: 'tcp'
    choices: ['tcp', 'udp']
    type: str
"""

EXAMPLES = r"""
- name: Add or modify ansible.example.org A to 192.168.1.1"
  community.general.nsupdate:
    key_name: "nsupdate"
    key_secret: "+bFQtBCta7j2vWkjPkAFtgA=="
    server: "10.1.1.1"
    zone: "example.org"
    record: "ansible"
    value: "192.168.1.1"

- name: Add or modify ansible.example.org A to 192.168.1.1, 192.168.1.2 and 192.168.1.3"
  community.general.nsupdate:
    key_name: "nsupdate"
    key_secret: "+bFQtBCta7j2vWkjPkAFtgA=="
    server: "10.1.1.1"
    zone: "example.org"
    record: "ansible"
    value: ["192.168.1.1", "192.168.1.2", "192.168.1.3"]

- name: Remove puppet.example.org CNAME
  community.general.nsupdate:
    key_name: "nsupdate"
    key_secret: "+bFQtBCta7j2vWkjPkAFtgA=="
    server: "10.1.1.1"
    zone: "example.org"
    record: "puppet"
    type: "CNAME"
    state: absent

- name: Add 1.1.168.192.in-addr.arpa. PTR for ansible.example.org
  community.general.nsupdate:
    key_name: "nsupdate"
    key_secret: "+bFQtBCta7j2vWkjPkAFtgA=="
    server: "10.1.1.1"
    record: "1.1.168.192.in-addr.arpa."
    type: "PTR"
    value: "ansible.example.org."
    state: present

- name: Remove 1.1.168.192.in-addr.arpa. PTR
  community.general.nsupdate:
    key_name: "nsupdate"
    key_secret: "+bFQtBCta7j2vWkjPkAFtgA=="
    server: "10.1.1.1"
    record: "1.1.168.192.in-addr.arpa."
    type: "PTR"
    state: absent

- name: Use FQDN for server instead of IP address
  community.general.nsupdate:
    key_name: "nsupdate"
    key_secret: "+bFQtBCta7j2vWkjPkAFtgA=="
    server: "ns1.example.org"
    zone: "example.org"
    record: "ansible"
    value: "192.168.1.1"

- name: Use GSS-TSIG authentication (requires Kerberos credentials)
  community.general.nsupdate:
    key_algorithm: "gss-tsig"
    server: "ns1.example.org"
    zone: "example.org"
    record: "ansible"
    value: "192.168.1.1"
"""

RETURN = r"""
record:
  description: DNS record.
  returned: success
  type: str
  sample: 'ansible'
ttl:
  description: DNS record TTL.
  returned: success
  type: int
  sample: 86400
type:
  description: DNS record type.
  returned: success
  type: str
  sample: 'CNAME'
value:
  description: DNS record value(s).
  returned: success
  type: list
  sample: '192.168.1.1'
zone:
  description: DNS record zone.
  returned: success
  type: str
  sample: 'example.org.'
dns_rc:
  description: C(dnspython) return code.
  returned: always
  type: int
  sample: 4
dns_rc_str:
  description: C(dnspython) return code (string representation).
  returned: always
  type: str
  sample: 'REFUSED'
"""

import ipaddress
import time
import uuid
from binascii import Error as binascii_error
from contextlib import suppress

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils import deps

with deps.declare("dnspython", url="https://github.com/rthalley/dnspython"):
    import dns.message
    import dns.query
    import dns.rdtypes.ANY.TKEY
    import dns.resolver
    import dns.tsigkeyring
    import dns.update

with deps.declare("gssapi", reason="for gss-tsig keys", url="https://github.com/pythongssapi/python-gssapi"):
    import gssapi


class RecordManager:
    def __init__(self, module):
        self.module = module

        self.server_fqdn = None
        self.server_ips = self.resolve_server()

        if module.params["key_algorithm"] == "hmac-md5":
            self.algorithm = "HMAC-MD5.SIG-ALG.REG.INT"
        elif module.params["key_algorithm"] == "gss-tsig":
            if module.params["key_name"]:
                self.module.fail_json(msg="key_name cannot be used with GSS-TSIG")
            self.algorithm = dns.tsig.GSS_TSIG
            self.keyring, self.keyname = self.init_gssapi()
        else:
            self.algorithm = module.params["key_algorithm"]

        if module.params["key_name"]:
            try:
                self.keyring = dns.tsigkeyring.from_text({module.params["key_name"]: module.params["key_secret"]})
                self.keyname = module.params["key_name"]
            except TypeError:
                module.fail_json(msg="Missing key_secret")
            except binascii_error as e:
                module.fail_json(msg=f"TSIG key error: {e}")

        if module.params["zone"] is None:
            if module.params["record"][-1] != ".":
                self.module.fail_json(msg="record must be absolute when omitting zone parameter")
            self.zone = self.lookup_zone()
        else:
            self.zone = module.params["zone"]

            if self.zone[-1] != ".":
                self.zone += "."

        if module.params["record"][-1] != ".":
            self.fqdn = f"{module.params['record']}.{self.zone}"
        else:
            self.fqdn = module.params["record"]

        if self.module.params["type"].lower() == "txt" and self.module.params["value"] is not None:
            self.value = list(map(self.txt_helper, self.module.params["value"]))
        else:
            self.value = self.module.params["value"]

        self.dns_rc = 0

    def resolve_server(self):
        """Resolve server parameter to a list of IP addresses if it's a FQDN."""
        server = self.module.params["server"]

        # Check if it's already an IPv4/IPv6 address
        try:
            ipaddress.ip_address(server)
            return [server]
        except ValueError:
            pass

        # Try to resolve the FQDN
        try:
            resolver = dns.resolver.Resolver()
            name = dns.name.from_text(server)
            ip_list = []

            with suppress(dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                answers = resolver.resolve(name, dns.rdatatype.AAAA)
                self.server_fqdn = server
                ip_list.extend([str(answer) for answer in answers])

            with suppress(dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                answers = resolver.resolve(name, dns.rdatatype.A)
                self.server_fqdn = server
                ip_list.extend([str(answer) for answer in answers])

            if not ip_list:
                self.module.fail_json(msg=f"Failed to resolve server '{server}' to an IP address")

            return ip_list

        except dns.exception.DNSException as e:
            self.module.fail_json(msg=f"DNS resolution error for server '{server}': {e}")

    def query(self, query, timeout=10):
        last_exception = None
        for server_ip in self.server_ips:
            try:
                if self.module.params["protocol"] == "tcp":
                    return dns.query.tcp(query, server_ip, timeout=timeout, port=self.module.params["port"])
                else:
                    return dns.query.udp(query, server_ip, timeout=timeout, port=self.module.params["port"])
            except (OSError, dns.exception.Timeout) as e:
                last_exception = e
                continue

        # If all servers failed, raise the last exception
        if last_exception:
            raise last_exception

    def build_tkey_query(self, token, key_ring, key_name):
        inception_time = int(time.time())
        tkey = dns.rdtypes.ANY.TKEY.TKEY(
            dns.rdataclass.ANY,
            dns.rdatatype.TKEY,
            dns.tsig.GSS_TSIG,
            inception_time,
            inception_time,
            3,
            dns.rcode.NOERROR,
            token,
            b"",
        )

        query = dns.message.make_query(key_name, dns.rdatatype.TKEY, dns.rdataclass.ANY)
        query.keyring = key_ring
        query.find_rrset(dns.message.ADDITIONAL, key_name, dns.rdataclass.ANY, dns.rdatatype.TKEY, create=True).add(
            tkey
        )
        return query

    def init_gssapi(self):
        deps.validate(self.module, "gssapi")
        if not self.server_fqdn:
            self.module.fail_json(msg="server must be a FQDN")

        # Acquire GSSAPI credentials
        gss_name = gssapi.Name(f"DNS@{self.server_fqdn}", gssapi.NameType.hostbased_service)
        try:
            gss_ctx = gssapi.SecurityContext(name=gss_name, usage="initiate")
        except gssapi.exceptions.GSSError as e:
            self.module.fail_json(msg=f"GSSAPI context initialization error: {e}")

        # Generate unique key name
        keyname = dns.name.from_text(f"{uuid.uuid4()}.{self.server_fqdn}")
        tsig_key = dns.tsig.Key(keyname, gss_ctx, dns.tsig.GSS_TSIG)
        keyring = dns.tsig.GSSTSigAdapter({keyname: tsig_key})

        # Perform GSS-TSIG negotiation
        token = gss_ctx.step()
        while not gss_ctx.complete:
            tkey_query = self.build_tkey_query(token, keyring, keyname)
            try:
                response = self.query(tkey_query)
            except (OSError, dns.exception.Timeout) as e:
                self.module.fail_json(msg=f"GSS-TSIG negotiation error: ({e.__class__.__name__}): {e}")
            if not gss_ctx.complete:
                token = gss_ctx.step(response.answer[0][0].key)

        return (keyring, keyname)

    def txt_helper(self, entry):
        if entry[0] == '"' and entry[-1] == '"':
            return entry
        return f'"{entry}"'

    def lookup_zone(self):
        name = dns.name.from_text(self.module.params["record"])
        while True:
            query = dns.message.make_query(name, dns.rdatatype.SOA)
            if self.keyring:
                query.use_tsig(keyring=self.keyring, keyname=self.keyname, algorithm=self.algorithm)
            try:
                lookup = self.query(query)
            except (dns.tsig.PeerBadKey, dns.tsig.PeerBadSignature) as e:
                self.module.fail_json(msg=f"TSIG update error ({e.__class__.__name__}): {e}")
            except (OSError, dns.exception.Timeout) as e:
                self.module.fail_json(msg=f"DNS server error: ({e.__class__.__name__}): {e}")
            if lookup.rcode() in [dns.rcode.SERVFAIL, dns.rcode.REFUSED]:
                self.module.fail_json(
                    msg=f"Zone lookup failure: '{self.module.params['server']}' will not "
                    f"respond to queries regarding '{self.module.params['record']}'."
                )
            # If the response contains an Answer SOA RR whose name matches the queried name,
            # this is the name of the zone in which the record needs to be inserted.
            for rr in lookup.answer:
                if rr.rdtype == dns.rdatatype.SOA and rr.name == name:
                    return rr.name.to_text()
            # If the response contains an Authority SOA RR whose name is a subdomain of the queried name,
            # this SOA name is the zone in which the record needs to be inserted.
            for rr in lookup.authority:
                if rr.rdtype == dns.rdatatype.SOA and name.fullcompare(rr.name)[0] == dns.name.NAMERELN_SUBDOMAIN:
                    return rr.name.to_text()
            try:
                name = name.parent()
            except dns.name.NoParent:
                self.module.fail_json(msg=f"Zone lookup of '{self.module.params['record']}' failed for unknown reason.")

    def __do_update(self, update):
        response = None
        try:
            response = self.query(update)
        except (dns.tsig.PeerBadKey, dns.tsig.PeerBadSignature) as e:
            self.module.fail_json(msg=f"TSIG update error ({e.__class__.__name__}): {e}")
        except (OSError, dns.exception.Timeout) as e:
            self.module.fail_json(msg=f"DNS server error: ({e.__class__.__name__}): {e}")
        return response

    def create_or_update_record(self):
        result = {"changed": False, "failed": False}

        exists = self.record_exists()
        if exists in [0, 2]:
            if self.module.check_mode:
                self.module.exit_json(changed=True)

            if exists == 0:
                self.dns_rc = self.create_record()
                if self.dns_rc != 0:
                    result["msg"] = f"Failed to create DNS record (rc: {int(self.dns_rc)})"

            elif exists == 2:
                self.dns_rc = self.modify_record()
                if self.dns_rc != 0:
                    result["msg"] = f"Failed to update DNS record (rc: {int(self.dns_rc)})"

            if self.dns_rc != 0:
                result["failed"] = True
            else:
                result["changed"] = True

        else:
            result["changed"] = False

        return result

    def create_record(self):
        update = dns.update.Update(self.zone, keyring=self.keyring, keyname=self.keyname, keyalgorithm=self.algorithm)
        for entry in self.value:
            try:
                update.add(self.module.params["record"], self.module.params["ttl"], self.module.params["type"], entry)
            except AttributeError:
                self.module.fail_json(msg="value needed when state=present")
            except dns.exception.SyntaxError:
                self.module.fail_json(msg="Invalid/malformed value")

        response = self.__do_update(update)
        return dns.message.Message.rcode(response)

    def modify_record(self):
        update = dns.update.Update(self.zone, keyring=self.keyring, keyname=self.keyname, keyalgorithm=self.algorithm)

        if self.module.params["type"].upper() == "NS":
            # When modifying a NS record, Bind9 silently refuses to delete all the NS entries for a zone:
            # > 09-May-2022 18:00:50.352 client @0x7fe7dd1f9568 192.168.1.3#45458/key rndc_ddns_ansible:
            # > updating zone 'lab/IN': attempt to delete all SOA or NS records ignored
            # https://gitlab.isc.org/isc-projects/bind9/-/blob/v9_18/lib/ns/update.c#L3304
            # Let's perform dns inserts and updates first, deletes after.
            query = dns.message.make_query(self.module.params["record"], self.module.params["type"])
            if self.keyring:
                query.use_tsig(keyring=self.keyring, keyname=self.keyname, algorithm=self.algorithm)

            try:
                lookup = self.query(query)
            except (dns.tsig.PeerBadKey, dns.tsig.PeerBadSignature) as e:
                self.module.fail_json(msg=f"TSIG update error ({e.__class__.__name__}): {e}")
            except (OSError, dns.exception.Timeout) as e:
                self.module.fail_json(msg=f"DNS server error: ({e.__class__.__name__}): {e}")

            lookup_result = lookup.answer[0] if lookup.answer else lookup.authority[0]
            entries_to_remove = [n.to_text() for n in lookup_result.items if n.to_text() not in self.value]
        else:
            update.delete(self.module.params["record"], self.module.params["type"])

        for entry in self.value:
            try:
                update.add(self.module.params["record"], self.module.params["ttl"], self.module.params["type"], entry)
            except AttributeError:
                self.module.fail_json(msg="value needed when state=present")
            except dns.exception.SyntaxError:
                self.module.fail_json(msg="Invalid/malformed value")

        if self.module.params["type"].upper() == "NS":
            for entry in entries_to_remove:
                update.delete(self.module.params["record"], self.module.params["type"], entry)

        response = self.__do_update(update)

        return dns.message.Message.rcode(response)

    def remove_record(self):
        result = {"changed": False, "failed": False}

        if self.record_exists() == 0:
            return result

        # Check mode and record exists, declared fake change.
        if self.module.check_mode:
            self.module.exit_json(changed=True)

        update = dns.update.Update(self.zone, keyring=self.keyring, keyname=self.keyname, keyalgorithm=self.algorithm)
        update.delete(self.module.params["record"], self.module.params["type"])

        response = self.__do_update(update)
        self.dns_rc = dns.message.Message.rcode(response)

        if self.dns_rc != 0:
            result["failed"] = True
            result["msg"] = f"Failed to delete record (rc: {int(self.dns_rc)})"
        else:
            result["changed"] = True

        return result

    def record_exists(self):
        update = dns.update.Update(self.zone, keyring=self.keyring, keyname=self.keyname, keyalgorithm=self.algorithm)
        try:
            update.present(self.module.params["record"], self.module.params["type"])
        except dns.rdatatype.UnknownRdatatype as e:
            self.module.fail_json(msg=f"Record error: {e}")

        response = self.__do_update(update)
        self.dns_rc = dns.message.Message.rcode(response)
        if self.dns_rc == 0:
            if self.module.params["state"] == "absent":
                return 1
            for entry in self.value:
                try:
                    update.present(self.module.params["record"], self.module.params["type"], entry)
                except AttributeError:
                    self.module.fail_json(msg="value needed when state=present")
                except dns.exception.SyntaxError:
                    self.module.fail_json(msg="Invalid/malformed value")
            response = self.__do_update(update)
            self.dns_rc = dns.message.Message.rcode(response)
            if self.dns_rc == 0:
                if self.ttl_changed():
                    return 2
                else:
                    return 1
            else:
                return 2
        else:
            return 0

    def ttl_changed(self):
        query = dns.message.make_query(self.fqdn, self.module.params["type"])
        if self.keyring:
            query.use_tsig(keyring=self.keyring, keyname=self.keyname, algorithm=self.algorithm)

        try:
            lookup = self.query(query)
        except (dns.tsig.PeerBadKey, dns.tsig.PeerBadSignature) as e:
            self.module.fail_json(msg=f"TSIG update error ({e.__class__.__name__}): {e}")
        except (OSError, dns.exception.Timeout) as e:
            self.module.fail_json(msg=f"DNS server error: ({e.__class__.__name__}): {e}")

        if lookup.rcode() != dns.rcode.NOERROR:
            self.module.fail_json(msg="Failed to lookup TTL of existing matching record.")

        current_ttl = lookup.answer[0].ttl if lookup.answer else lookup.authority[0].ttl

        return current_ttl != self.module.params["ttl"]


def main():
    tsig_algs = [
        "HMAC-MD5.SIG-ALG.REG.INT",
        "hmac-md5",
        "hmac-sha1",
        "hmac-sha224",
        "hmac-sha256",
        "hmac-sha384",
        "hmac-sha512",
        "gss-tsig",
    ]

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["present", "absent"], type="str"),
            server=dict(required=True, type="str"),
            port=dict(default=53, type="int"),
            key_name=dict(type="str"),
            key_secret=dict(type="str", no_log=True),
            key_algorithm=dict(default="hmac-md5", choices=tsig_algs, type="str"),
            zone=dict(type="str"),
            record=dict(required=True, type="str"),
            type=dict(default="A", type="str"),
            ttl=dict(default=3600, type="int"),
            value=dict(type="list", elements="str"),
            protocol=dict(default="tcp", choices=["tcp", "udp"], type="str"),
        ),
        supports_check_mode=True,
    )

    deps.validate(module, "dnspython")

    if len(module.params["record"]) == 0:
        module.fail_json(msg="record cannot be empty.")

    record = RecordManager(module)
    result = {}
    if module.params["state"] == "absent":
        result = record.remove_record()
    elif module.params["state"] == "present":
        result = record.create_or_update_record()

    result["dns_rc"] = record.dns_rc
    result["dns_rc_str"] = dns.rcode.to_text(record.dns_rc)
    if result["failed"]:
        module.fail_json(**result)
    else:
        result["record"] = dict(
            zone=record.zone,
            record=module.params["record"],
            type=module.params["type"],
            ttl=module.params["ttl"],
            value=record.value,
        )

        module.exit_json(**result)


if __name__ == "__main__":
    main()

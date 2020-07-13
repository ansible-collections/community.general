#!/usr/bin/python

# (c) 2016, Marcin Skarbek <github@skarbek.name>
# (c) 2016, Andreas Olsson <andreas@arrakis.se>
# (c) 2017, Loic Blot <loic.blot@unix-experience.fr>
#
# This module was ported from https://github.com/mskarbek/ansible-nsupdate
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: nsupdate

short_description: Manage DNS records.
description:
    - Create, update and remove DNS records using DDNS updates
requirements:
  - dnspython
author: "Loic Blot (@nerzhul)"
options:
    state:
        description:
            - Manage DNS record.
        choices: ['present', 'absent']
        default: 'present'
    server:
        description:
            - Apply DNS modification on this server, specified by IPv4 or IPv6 address.
        required: true
    port:
        description:
            - Use this TCP port when connecting to C(server).
        default: 53
    key_name:
        description:
            - Use TSIG key name to authenticate against DNS C(server)
    key_secret:
        description:
            - Use TSIG key secret, associated with C(key_name), to authenticate against C(server)
    key_algorithm:
        description:
            - Specify key algorithm used by C(key_secret).
        choices: ['HMAC-MD5.SIG-ALG.REG.INT', 'hmac-md5', 'hmac-sha1', 'hmac-sha224', 'hmac-sha256', 'hmac-sha384',
                  'hmac-sha512']
        default: 'hmac-md5'
    zone:
        description:
            - DNS record will be modified on this C(zone).
            - When omitted DNS will be queried to attempt finding the correct zone.
            - Starting with Ansible 2.7 this parameter is optional.
    record:
        description:
            - Sets the DNS record to modify. When zone is omitted this has to be absolute (ending with a dot).
        required: true
    type:
        description:
            - Sets the record type.
        default: 'A'
    ttl:
        description:
            - Sets the record TTL.
        default: 3600
    value:
        description:
            - Sets the record value.
    protocol:
        description:
            - Sets the transport protocol (TCP or UDP). TCP is the recommended and a more robust option.
        default: 'tcp'
        choices: ['tcp', 'udp']
'''

EXAMPLES = '''
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
'''

RETURN = '''
changed:
    description: If module has modified record
    returned: success
    type: str
record:
    description: DNS record
    returned: success
    type: str
    sample: 'ansible'
ttl:
    description: DNS record TTL
    returned: success
    type: int
    sample: 86400
type:
    description: DNS record type
    returned: success
    type: str
    sample: 'CNAME'
value:
    description: DNS record value(s)
    returned: success
    type: list
    sample: '192.168.1.1'
zone:
    description: DNS record zone
    returned: success
    type: str
    sample: 'example.org.'
dns_rc:
    description: dnspython return code
    returned: always
    type: int
    sample: 4
dns_rc_str:
    description: dnspython return code (string representation)
    returned: always
    type: str
    sample: 'REFUSED'
'''

import traceback

from binascii import Error as binascii_error
from socket import error as socket_error

DNSPYTHON_IMP_ERR = None
try:
    import dns.update
    import dns.query
    import dns.tsigkeyring
    import dns.message
    import dns.resolver

    HAVE_DNSPYTHON = True
except ImportError:
    DNSPYTHON_IMP_ERR = traceback.format_exc()
    HAVE_DNSPYTHON = False

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils._text import to_native


class RecordManager(object):
    def __init__(self, module):
        self.module = module

        if module.params['key_name']:
            try:
                self.keyring = dns.tsigkeyring.from_text({
                    module.params['key_name']: module.params['key_secret']
                })
            except TypeError:
                module.fail_json(msg='Missing key_secret')
            except binascii_error as e:
                module.fail_json(msg='TSIG key error: %s' % to_native(e))
        else:
            self.keyring = None

        if module.params['key_algorithm'] == 'hmac-md5':
            self.algorithm = 'HMAC-MD5.SIG-ALG.REG.INT'
        else:
            self.algorithm = module.params['key_algorithm']

        if module.params['zone'] is None:
            if module.params['record'][-1] != '.':
                self.module.fail_json(msg='record must be absolute when omitting zone parameter')
            self.zone = self.lookup_zone()
        else:
            self.zone = module.params['zone']

            if self.zone[-1] != '.':
                self.zone += '.'

        if module.params['record'][-1] != '.':
            self.fqdn = module.params['record'] + '.' + self.zone
        else:
            self.fqdn = module.params['record']

        if self.module.params['type'].lower() == 'txt' and self.module.params['value'] is not None:
            self.value = list(map(self.txt_helper, self.module.params['value']))
        else:
            self.value = self.module.params['value']

        self.dns_rc = 0

    def txt_helper(self, entry):
        if entry[0] == '"' and entry[-1] == '"':
            return entry
        return '"{text}"'.format(text=entry)

    def lookup_zone(self):
        name = dns.name.from_text(self.module.params['record'])
        while True:
            query = dns.message.make_query(name, dns.rdatatype.SOA)
            if self.keyring:
                query.use_tsig(keyring=self.keyring, algorithm=self.algorithm)
            try:
                if self.module.params['protocol'] == 'tcp':
                    lookup = dns.query.tcp(query, self.module.params['server'], timeout=10, port=self.module.params['port'])
                else:
                    lookup = dns.query.udp(query, self.module.params['server'], timeout=10, port=self.module.params['port'])
            except (dns.tsig.PeerBadKey, dns.tsig.PeerBadSignature) as e:
                self.module.fail_json(msg='TSIG update error (%s): %s' % (e.__class__.__name__, to_native(e)))
            except (socket_error, dns.exception.Timeout) as e:
                self.module.fail_json(msg='DNS server error: (%s): %s' % (e.__class__.__name__, to_native(e)))
            if lookup.rcode() in [dns.rcode.SERVFAIL, dns.rcode.REFUSED]:
                self.module.fail_json(msg='Zone lookup failure: \'%s\' will not respond to queries regarding \'%s\'.' % (
                    self.module.params['server'], self.module.params['record']))
            try:
                zone = lookup.authority[0].name
                if zone == name:
                    return zone.to_text()
            except IndexError:
                pass
            try:
                name = name.parent()
            except dns.name.NoParent:
                self.module.fail_json(msg='Zone lookup of \'%s\' failed for unknown reason.' % (self.module.params['record']))

    def __do_update(self, update):
        response = None
        try:
            if self.module.params['protocol'] == 'tcp':
                response = dns.query.tcp(update, self.module.params['server'], timeout=10, port=self.module.params['port'])
            else:
                response = dns.query.udp(update, self.module.params['server'], timeout=10, port=self.module.params['port'])
        except (dns.tsig.PeerBadKey, dns.tsig.PeerBadSignature) as e:
            self.module.fail_json(msg='TSIG update error (%s): %s' % (e.__class__.__name__, to_native(e)))
        except (socket_error, dns.exception.Timeout) as e:
            self.module.fail_json(msg='DNS server error: (%s): %s' % (e.__class__.__name__, to_native(e)))
        return response

    def create_or_update_record(self):
        result = {'changed': False, 'failed': False}

        exists = self.record_exists()
        if exists in [0, 2]:
            if self.module.check_mode:
                self.module.exit_json(changed=True)

            if exists == 0:
                self.dns_rc = self.create_record()
                if self.dns_rc != 0:
                    result['msg'] = "Failed to create DNS record (rc: %d)" % self.dns_rc

            elif exists == 2:
                self.dns_rc = self.modify_record()
                if self.dns_rc != 0:
                    result['msg'] = "Failed to update DNS record (rc: %d)" % self.dns_rc

            if self.dns_rc != 0:
                result['failed'] = True
            else:
                result['changed'] = True

        else:
            result['changed'] = False

        return result

    def create_record(self):
        update = dns.update.Update(self.zone, keyring=self.keyring, keyalgorithm=self.algorithm)
        for entry in self.value:
            try:
                update.add(self.module.params['record'],
                           self.module.params['ttl'],
                           self.module.params['type'],
                           entry)
            except AttributeError:
                self.module.fail_json(msg='value needed when state=present')
            except dns.exception.SyntaxError:
                self.module.fail_json(msg='Invalid/malformed value')

        response = self.__do_update(update)
        return dns.message.Message.rcode(response)

    def modify_record(self):
        update = dns.update.Update(self.zone, keyring=self.keyring, keyalgorithm=self.algorithm)
        update.delete(self.module.params['record'], self.module.params['type'])
        for entry in self.value:
            try:
                update.add(self.module.params['record'],
                           self.module.params['ttl'],
                           self.module.params['type'],
                           entry)
            except AttributeError:
                self.module.fail_json(msg='value needed when state=present')
            except dns.exception.SyntaxError:
                self.module.fail_json(msg='Invalid/malformed value')
        response = self.__do_update(update)

        return dns.message.Message.rcode(response)

    def remove_record(self):
        result = {'changed': False, 'failed': False}

        if self.record_exists() == 0:
            return result

        # Check mode and record exists, declared fake change.
        if self.module.check_mode:
            self.module.exit_json(changed=True)

        update = dns.update.Update(self.zone, keyring=self.keyring, keyalgorithm=self.algorithm)
        update.delete(self.module.params['record'], self.module.params['type'])

        response = self.__do_update(update)
        self.dns_rc = dns.message.Message.rcode(response)

        if self.dns_rc != 0:
            result['failed'] = True
            result['msg'] = "Failed to delete record (rc: %d)" % self.dns_rc
        else:
            result['changed'] = True

        return result

    def record_exists(self):
        update = dns.update.Update(self.zone, keyring=self.keyring, keyalgorithm=self.algorithm)
        try:
            update.present(self.module.params['record'], self.module.params['type'])
        except dns.rdatatype.UnknownRdatatype as e:
            self.module.fail_json(msg='Record error: {0}'.format(to_native(e)))

        response = self.__do_update(update)
        self.dns_rc = dns.message.Message.rcode(response)
        if self.dns_rc == 0:
            if self.module.params['state'] == 'absent':
                return 1
            for entry in self.value:
                try:
                    update.present(self.module.params['record'], self.module.params['type'], entry)
                except AttributeError:
                    self.module.fail_json(msg='value needed when state=present')
                except dns.exception.SyntaxError:
                    self.module.fail_json(msg='Invalid/malformed value')
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
        query = dns.message.make_query(self.fqdn, self.module.params['type'])
        if self.keyring:
            query.use_tsig(keyring=self.keyring, algorithm=self.algorithm)

        try:
            if self.module.params['protocol'] == 'tcp':
                lookup = dns.query.tcp(query, self.module.params['server'], timeout=10, port=self.module.params['port'])
            else:
                lookup = dns.query.udp(query, self.module.params['server'], timeout=10, port=self.module.params['port'])
        except (dns.tsig.PeerBadKey, dns.tsig.PeerBadSignature) as e:
            self.module.fail_json(msg='TSIG update error (%s): %s' % (e.__class__.__name__, to_native(e)))
        except (socket_error, dns.exception.Timeout) as e:
            self.module.fail_json(msg='DNS server error: (%s): %s' % (e.__class__.__name__, to_native(e)))

        if lookup.rcode() != dns.rcode.NOERROR:
            self.module.fail_json(msg='Failed to lookup TTL of existing matching record.')

        current_ttl = lookup.answer[0].ttl
        return current_ttl != self.module.params['ttl']


def main():
    tsig_algs = ['HMAC-MD5.SIG-ALG.REG.INT', 'hmac-md5', 'hmac-sha1', 'hmac-sha224',
                 'hmac-sha256', 'hmac-sha384', 'hmac-sha512']

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=False, default='present', choices=['present', 'absent'], type='str'),
            server=dict(required=True, type='str'),
            port=dict(required=False, default=53, type='int'),
            key_name=dict(required=False, type='str'),
            key_secret=dict(required=False, type='str', no_log=True),
            key_algorithm=dict(required=False, default='hmac-md5', choices=tsig_algs, type='str'),
            zone=dict(required=False, default=None, type='str'),
            record=dict(required=True, type='str'),
            type=dict(required=False, default='A', type='str'),
            ttl=dict(required=False, default=3600, type='int'),
            value=dict(required=False, default=None, type='list'),
            protocol=dict(required=False, default='tcp', choices=['tcp', 'udp'], type='str')
        ),
        supports_check_mode=True
    )

    if not HAVE_DNSPYTHON:
        module.fail_json(msg=missing_required_lib('dnspython'), exception=DNSPYTHON_IMP_ERR)

    if len(module.params["record"]) == 0:
        module.fail_json(msg='record cannot be empty.')

    record = RecordManager(module)
    result = {}
    if module.params["state"] == 'absent':
        result = record.remove_record()
    elif module.params["state"] == 'present':
        result = record.create_or_update_record()

    result['dns_rc'] = record.dns_rc
    result['dns_rc_str'] = dns.rcode.to_text(record.dns_rc)
    if result['failed']:
        module.fail_json(**result)
    else:
        result['record'] = dict(zone=record.zone,
                                record=module.params['record'],
                                type=module.params['type'],
                                ttl=module.params['ttl'],
                                value=record.value)

        module.exit_json(**result)


if __name__ == '__main__':
    main()

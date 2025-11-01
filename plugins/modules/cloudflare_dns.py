#!/usr/bin/python

# Copyright (c) 2016 Michael Gruener <michael.gruener@chaosmoon.net>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: cloudflare_dns
author:
  - Michael Gruener (@mgruener)
short_description: Manage Cloudflare DNS records
description:
  - 'Manages DNS records using the Cloudflare API, see the docs: U(https://api.cloudflare.com/).'
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  api_token:
    description:
      - API token.
      - Required for API token authentication.
      - "You can obtain your API token from the bottom of the Cloudflare 'My Account' page, found here: U(https://dash.cloudflare.com/)."
      - Can be specified in E(CLOUDFLARE_TOKEN) environment variable since community.general 2.0.0.
    type: str
    version_added: '0.2.0'
  account_api_key:
    description:
      - Account API key.
      - Required for API keys authentication.
      - "You can obtain your API key from the bottom of the Cloudflare 'My Account' page, found here: U(https://dash.cloudflare.com/)."
    type: str
    aliases: [account_api_token]
  account_email:
    description:
      - Account email. Required for API keys authentication.
    type: str
  algorithm:
    description:
      - Algorithm number.
      - Required for O(type=DS) and O(type=SSHFP) when O(state=present).
    type: int
  cert_usage:
    description:
      - Certificate usage number.
      - Required for O(type=TLSA) when O(state=present).
    type: int
    choices: [0, 1, 2, 3]
  comment:
    description:
      - Comments or notes about the DNS record.
    type: str
    version_added: 10.1.0
  flag:
    description:
      - Issuer Critical Flag.
      - Required for O(type=CAA) when O(state=present).
    type: int
    choices: [0, 1]
    version_added: 8.0.0
  tag:
    description:
      - CAA issue restriction.
      - Required for O(type=CAA) when O(state=present).
    type: str
    choices: [issue, issuewild, iodef]
    version_added: 8.0.0
  hash_type:
    description:
      - Hash type number.
      - Required for O(type=DS), O(type=SSHFP) and O(type=TLSA) when O(state=present).
    type: int
    choices: [1, 2]
  key_tag:
    description:
      - DNSSEC key tag.
      - Needed for O(type=DS) when O(state=present).
    type: int
  port:
    description:
      - Service port.
      - Required for O(type=SRV) and O(type=TLSA).
    type: int
  priority:
    description:
      - Record priority.
      - Required for O(type=MX) and O(type=SRV).
    default: 1
    type: int
  proto:
    description:
      - Service protocol. Required for O(type=SRV) and O(type=TLSA).
      - Common values are TCP and UDP.
    type: str
  proxied:
    description:
      - Proxy through Cloudflare network or just use DNS.
    type: bool
    default: false
  record:
    description:
      - Record to add.
      - Required if O(state=present).
      - Default is V(@) (that is, the zone name).
    type: str
    default: '@'
    aliases: [name]
  selector:
    description:
      - Selector number.
      - Required for O(type=TLSA) when O(state=present).
    choices: [0, 1]
    type: int
  service:
    description:
      - Record service.
      - Required for O(type=SRV).
    type: str
  solo:
    description:
      - Whether the record should be the only one for that record type and record name.
      - Only use with O(state=present).
      - This deletes all other records with the same record name and type.
    type: bool
  state:
    description:
      - Whether the record(s) should exist or not.
    type: str
    choices: [absent, present]
    default: present
  tags:
    description:
      - Custom tags for the DNS record.
    type: list
    elements: str
    version_added: 10.1.0
  timeout:
    description:
      - Timeout for Cloudflare API calls.
    type: int
    default: 30
  ttl:
    description:
      - The TTL to give the new record.
      - Must be between V(120) and V(2,147,483,647) seconds, or V(1) for automatic.
    type: int
    default: 1
  type:
    description:
      - The type of DNS record to create. Required if O(state=present).
      - Support for V(SPF) has been removed from community.general 9.0.0 since that record type is no longer supported by
        CloudFlare.
      - Support for V(PTR) has been added in community.general 11.1.0.
    type: str
    choices: [A, AAAA, CNAME, DS, MX, NS, SRV, SSHFP, TLSA, CAA, TXT, PTR]
  value:
    description:
      - The record value.
      - Required for O(state=present).
    type: str
    aliases: [content]
  weight:
    description:
      - Service weight.
      - Required for O(type=SRV).
    type: int
    default: 1
  zone:
    description:
      - The name of the Zone to work with (for example V(example.com)).
      - The Zone must already exist.
    type: str
    required: true
    aliases: [domain]
"""

EXAMPLES = r"""
- name: Create a test.example.net A record to point to 127.0.0.1
  community.general.cloudflare_dns:
    zone: example.net
    record: test
    type: A
    value: 127.0.0.1
    account_email: test@example.com
    account_api_key: dummyapitoken
  register: record

- name: Create a record using api token
  community.general.cloudflare_dns:
    zone: example.net
    record: test
    type: A
    value: 127.0.0.1
    api_token: dummyapitoken

- name: Create a record with comment and tags
  community.general.cloudflare_dns:
    zone: example.net
    record: test
    type: A
    value: 127.0.0.1
    comment: Local test website
    tags:
      - test
      - local
    api_token: dummyapitoken

- name: Create a example.net CNAME record to example.com
  community.general.cloudflare_dns:
    zone: example.net
    type: CNAME
    value: example.com
    account_email: test@example.com
    account_api_key: dummyapitoken
    state: present

- name: Change its TTL
  community.general.cloudflare_dns:
    zone: example.net
    type: CNAME
    value: example.com
    ttl: 600
    account_email: test@example.com
    account_api_key: dummyapitoken
    state: present

- name: Delete the record
  community.general.cloudflare_dns:
    zone: example.net
    type: CNAME
    value: example.com
    account_email: test@example.com
    account_api_key: dummyapitoken
    state: absent

- name: Create a example.net CNAME record to example.com and proxy through Cloudflare's network
  community.general.cloudflare_dns:
    zone: example.net
    type: CNAME
    value: example.com
    proxied: true
    account_email: test@example.com
    account_api_key: dummyapitoken
    state: present

# This deletes all other TXT records named "test.example.net"
- name: Create TXT record "test.example.net" with value "unique value"
  community.general.cloudflare_dns:
    domain: example.net
    record: test
    type: TXT
    value: unique value
    solo: true
    account_email: test@example.com
    account_api_key: dummyapitoken
    state: present

- name: Create an SRV record _foo._tcp.example.net
  community.general.cloudflare_dns:
    domain: example.net
    service: foo
    proto: tcp
    port: 3500
    priority: 10
    weight: 20
    type: SRV
    value: fooserver.example.net

- name: Create a SSHFP record login.example.com
  community.general.cloudflare_dns:
    zone: example.com
    record: login
    type: SSHFP
    algorithm: 4
    hash_type: 2
    value: 9dc1d6742696d2f51ca1f1a78b3d16a840f7d111eb9454239e70db31363f33e1

- name: Create a TLSA record _25._tcp.mail.example.com
  community.general.cloudflare_dns:
    zone: example.com
    record: mail
    port: 25
    proto: tcp
    type: TLSA
    cert_usage: 3
    selector: 1
    hash_type: 1
    value: 6b76d034492b493e15a7376fccd08e63befdad0edab8e442562f532338364bf3

- name: Create a CAA record subdomain.example.com
  community.general.cloudflare_dns:
    zone: example.com
    record: subdomain
    type: CAA
    flag: 0
    tag: issue
    value: ca.example.com

- name: Create a DS record for subdomain.example.com
  community.general.cloudflare_dns:
    zone: example.com
    record: subdomain
    type: DS
    key_tag: 5464
    algorithm: 8
    hash_type: 2
    value: B4EB5AC4467D2DFB3BAF9FB9961DC1B6FED54A58CDFAA3E465081EC86F89BFAB

- name: Create PTR record "1.2.0.192.in-addr.arpa" with value "test.example.com"
  community.general.cloudflare_dns:
    zone: 2.0.192.in-addr.arpa
    record: 1
    type: PTR
    value: test.example.com
    state: present
"""

RETURN = r"""
record:
  description: A dictionary containing the record data.
  returned: success, except on record deletion
  type: complex
  contains:
    comment:
      description: Comments or notes about the DNS record.
      returned: success
      type: str
      sample: Domain verification record
      version_added: 10.1.0
    comment_modified_on:
      description: When the record comment was last modified. Omitted if there is no comment.
      returned: success
      type: str
      sample: "2024-01-01T05:20:00.12345Z"
      version_added: 10.1.0
    content:
      description: The record content (details depend on record type).
      returned: success
      type: str
      sample: 192.0.2.91
    created_on:
      description: The record creation date.
      returned: success
      type: str
      sample: "2016-03-25T19:09:42.516553Z"
    data:
      description: Additional record data.
      returned: success, if type is SRV, DS, SSHFP TLSA or CAA
      type: dict
      sample:
        {
          "name": "jabber",
          "port": 8080,
          "priority": 10,
          "proto": "_tcp",
          "service": "_xmpp",
          "target": "jabberhost.sample.com",
          "weight": 5
        }
    id:
      description: The record ID.
      returned: success
      type: str
      sample: f9efb0549e96abcb750de63b38c9576e
    locked:
      description: No documentation available.
      returned: success
      type: bool
      sample: false
    meta:
      description: Extra Cloudflare-specific information about the record.
      returned: success
      type: dict
      sample: {"auto_added": false}
    modified_on:
      description: Record modification date.
      returned: success
      type: str
      sample: "2016-03-25T19:09:42.516553Z"
    name:
      description: The record name as FQDN (including _service and _proto for SRV).
      returned: success
      type: str
      sample: www.sample.com
    priority:
      description: Priority of the MX record.
      returned: success, if type is MX
      type: int
      sample: 10
    proxiable:
      description: Whether this record can be proxied through Cloudflare.
      returned: success
      type: bool
      sample: false
    proxied:
      description: Whether the record is proxied through Cloudflare.
      returned: success
      type: bool
      sample: false
    tags:
      description: Custom tags for the DNS record.
      returned: success
      type: list
      elements: str
      sample: ["production", "app"]
      version_added: 10.1.0
    tags_modified_on:
      description: When the record tags were last modified. Omitted if there are no tags.
      returned: success
      type: str
      sample: "2025-01-01T05:20:00.12345Z"
      version_added: 10.1.0
    ttl:
      description: The time-to-live for the record.
      returned: success
      type: int
      sample: 300
    type:
      description: The record type.
      returned: success
      type: str
      sample: A
    zone_id:
      description: The ID of the zone containing the record.
      returned: success
      type: str
      sample: abcede0bf9f0066f94029d2e6b73856a
    zone_name:
      description: The name of the zone containing the record.
      returned: success
      type: str
      sample: sample.com
"""

import json
from urllib.parse import urlencode

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.module_utils.urls import fetch_url


def lowercase_string(param):
    return param.lower() if isinstance(param, str) else param


def join_str(sep, *args):
    return sep.join([str(arg) for arg in args])


class CloudflareAPI:
    cf_api_endpoint = "https://api.cloudflare.com/client/v4"
    changed = False

    def __init__(self, module):
        self.module = module
        self.api_token = module.params["api_token"]
        self.account_api_key = module.params["account_api_key"]
        self.account_email = module.params["account_email"]
        self.algorithm = module.params["algorithm"]
        self.cert_usage = module.params["cert_usage"]
        self.comment = module.params["comment"]
        self.hash_type = module.params["hash_type"]
        self.flag = module.params["flag"]
        self.tag = module.params["tag"]
        self.tags = module.params["tags"]
        self.key_tag = module.params["key_tag"]
        self.port = module.params["port"]
        self.priority = module.params["priority"]
        self.proto = lowercase_string(module.params["proto"])
        self.proxied = module.params["proxied"]
        self.selector = module.params["selector"]
        self.record = lowercase_string(module.params["record"])
        self.service = lowercase_string(module.params["service"])
        self.is_solo = module.params["solo"]
        self.state = module.params["state"]
        self.timeout = module.params["timeout"]
        self.ttl = module.params["ttl"]
        self.type = module.params["type"]
        self.value = module.params["value"]
        self.weight = module.params["weight"]
        self.zone = lowercase_string(module.params["zone"])

        if self.record == "@":
            self.record = self.zone

        if (self.type in ["CNAME", "NS", "MX", "SRV"]) and (self.value is not None):
            self.value = self.value.rstrip(".").lower()

        if (self.type == "AAAA") and (self.value is not None):
            self.value = self.value.lower()

        if self.type == "SRV":
            if (self.proto is not None) and (not self.proto.startswith("_")):
                self.proto = f"_{self.proto}"
            if (self.service is not None) and (not self.service.startswith("_")):
                self.service = f"_{self.service}"

        if self.type == "TLSA":
            if (self.proto is not None) and (not self.proto.startswith("_")):
                self.proto = f"_{self.proto}"
            if self.port is not None:
                self.port = f"_{self.port}"

        if not self.record.endswith(self.zone):
            self.record = join_str(".", self.record, self.zone)

        if self.type == "DS":
            if self.record == self.zone:
                self.module.fail_json(msg="DS records only apply to subdomains.")

    def _cf_simple_api_call(self, api_call, method="GET", payload=None):
        if self.api_token:
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            }
        else:
            headers = {
                "X-Auth-Email": self.account_email,
                "X-Auth-Key": self.account_api_key,
                "Content-Type": "application/json",
            }
        data = None
        if payload:
            try:
                data = json.dumps(payload)
            except Exception as e:
                self.module.fail_json(msg=f"Failed to encode payload as JSON: {e} ")

        resp, info = fetch_url(
            self.module,
            self.cf_api_endpoint + api_call,
            headers=headers,
            data=data,
            method=method,
            timeout=self.timeout,
        )

        if info["status"] not in [200, 304, 400, 401, 403, 429, 405, 415]:
            self.module.fail_json(
                msg=f"Failed API call {api_call}; got unexpected HTTP code {info['status']}: {info.get('msg')}"
            )

        error_msg = ""
        if info["status"] == 401:
            # Unauthorized
            error_msg = (
                f"API user does not have permission; Status: {info['status']}; Method: {method}: Call: {api_call}"
            )
        elif info["status"] == 403:
            # Forbidden
            error_msg = f"API request not authenticated; Status: {info['status']}; Method: {method}: Call: {api_call}"
        elif info["status"] == 429:
            # Too many requests
            error_msg = f"API client is rate limited; Status: {info['status']}; Method: {method}: Call: {api_call}"
        elif info["status"] == 405:
            # Method not allowed
            error_msg = (
                f"API incorrect HTTP method provided; Status: {info['status']}; Method: {method}: Call: {api_call}"
            )
        elif info["status"] == 415:
            # Unsupported Media Type
            error_msg = f"API request is not valid JSON; Status: {info['status']}; Method: {method}: Call: {api_call}"
        elif info["status"] == 400:
            # Bad Request
            error_msg = f"API bad request; Status: {info['status']}; Method: {method}: Call: {api_call}"

        result = None
        try:
            content = resp.read()
        except AttributeError:
            content = None

        if not content:
            if info["body"]:
                content = info["body"]
            else:
                error_msg += "; The API response was empty"

        if content:
            try:
                result = json.loads(to_text(content, errors="surrogate_or_strict"))
            except getattr(json, "JSONDecodeError", ValueError) as e:
                error_msg += f"; Failed to parse API response with error {to_native(e)}: {content}"

        # Without a valid/parsed JSON response no more error processing can be done
        if result is None:
            self.module.fail_json(msg=error_msg)

        if "success" not in result:
            error_msg += f"; Unexpected error details: {result.get('error')}"
            self.module.fail_json(msg=error_msg)

        if not result["success"]:
            error_msg += "; Error details: "
            for error in result["errors"]:
                error_msg += f"code: {error['code']}, error: {error['message']}; "
                if "error_chain" in error:
                    for chain_error in error["error_chain"]:
                        error_msg += f"code: {chain_error['code']}, error: {chain_error['message']}; "
            self.module.fail_json(msg=error_msg)

        return result, info["status"]

    def _cf_api_call(self, api_call, method="GET", payload=None):
        result, status = self._cf_simple_api_call(api_call, method, payload)

        data = result["result"]

        if "result_info" in result:
            pagination = result["result_info"]
            if pagination["total_pages"] > 1:
                next_page = int(pagination["page"]) + 1
                parameters = [f"page={next_page}"]
                # strip "page" parameter from call parameters (if there are any)
                if "?" in api_call:
                    raw_api_call, query = api_call.split("?", 1)
                    parameters += [param for param in query.split("&") if not param.startswith("page")]
                else:
                    raw_api_call = api_call
                while next_page <= pagination["total_pages"]:
                    raw_api_call += f"?{'&'.join(parameters)}"
                    result, status = self._cf_simple_api_call(raw_api_call, method, payload)
                    data += result["result"]
                    next_page += 1

        return data, status

    def _get_zone_id(self, zone=None):
        if not zone:
            zone = self.zone

        zones = self.get_zones(zone)
        if len(zones) > 1:
            self.module.fail_json(msg=f"More than one zone matches {zone}")

        if len(zones) < 1:
            self.module.fail_json(msg=f"No zone found with name {zone}")

        return zones[0]["id"]

    def get_zones(self, name=None):
        if not name:
            name = self.zone
        param = ""
        if name:
            param = f"?{urlencode({'name': name})}"
        zones, status = self._cf_api_call(f"/zones{param}")
        return zones

    def get_dns_records(self, zone_name=None, type=None, record=None, value=""):
        if not zone_name:
            zone_name = self.zone
        if not type:
            type = self.type
        if not record:
            record = self.record
        # necessary because None as value means to override user
        # set module value
        if (not value) and (value is not None):
            value = self.value

        zone_id = self._get_zone_id()
        api_call = f"/zones/{zone_id}/dns_records"
        query = {}
        if type:
            query["type"] = type
        if record:
            query["name"] = record
        if value:
            query["content"] = value
        if query:
            api_call += f"?{urlencode(query)}"

        records, status = self._cf_api_call(api_call)
        return records

    def delete_dns_records(self, solo):
        records = []
        content = self.value
        search_record = self.record
        if self.type == "SRV":
            if not (self.value is None or self.value == ""):
                content = join_str("\t", self.weight, self.port, self.value)
            search_record = join_str(".", self.service, self.proto, self.record)
        elif self.type == "DS":
            if not (self.value is None or self.value == ""):
                content = join_str("\t", self.key_tag, self.algorithm, self.hash_type, self.value)
        elif self.type == "SSHFP":
            if not (self.value is None or self.value == ""):
                content = join_str(" ", self.algorithm, self.hash_type, self.value.upper())
        elif self.type == "TLSA":
            if not (self.value is None or self.value == ""):
                content = join_str("\t", self.cert_usage, self.selector, self.hash_type, self.value)
            search_record = join_str(".", self.port, self.proto, self.record)
        if solo:
            search_value = None
        else:
            search_value = content

        zone_id = self._get_zone_id(self.zone)
        records = self.get_dns_records(self.zone, self.type, search_record, search_value)

        for rr in records:
            if solo:
                if not ((rr["type"] == self.type) and (rr["name"] == search_record) and (rr["content"] == content)):
                    self.changed = True
                    if not self.module.check_mode:
                        result, info = self._cf_api_call(f"/zones/{zone_id}/dns_records/{rr['id']}", "DELETE")
            else:
                self.changed = True
                if not self.module.check_mode:
                    result, info = self._cf_api_call(f"/zones/{zone_id}/dns_records/{rr['id']}", "DELETE")
        return self.changed

    def ensure_dns_record(self):
        search_value = self.value
        search_record = self.record
        new_record = None

        if self.type in ["A", "AAAA", "CNAME", "TXT", "MX", "NS", "PTR"]:
            if not self.value:
                self.module.fail_json(msg="You must provide a non-empty value to create this record type")

            # there can only be one CNAME per record
            # ignoring the value when searching for existing
            # CNAME records allows us to update the value if it
            # changes
            if self.type == "CNAME":
                search_value = None

            new_record = {"type": self.type, "name": self.record, "content": self.value, "ttl": self.ttl}

        if self.type in ["A", "AAAA", "CNAME"]:
            new_record["proxied"] = self.proxied

        if self.type == "MX":
            for attr in [self.priority, self.value]:
                if (attr is None) or (attr == ""):
                    self.module.fail_json(msg="You must provide priority and a value to create this record type")
            new_record = {
                "type": self.type,
                "name": self.record,
                "content": self.value,
                "priority": self.priority,
                "ttl": self.ttl,
            }

        if self.type == "SRV":
            for attr in [self.port, self.priority, self.proto, self.service, self.weight, self.value]:
                if (attr is None) or (attr == ""):
                    self.module.fail_json(
                        msg="You must provide port, priority, proto, service, weight and a value to create this record type"
                    )
            srv_data = {
                "target": self.value,
                "port": self.port,
                "weight": self.weight,
                "priority": self.priority,
            }

            new_record = {
                "type": self.type,
                "name": join_str(".", self.service, self.proto, self.record),
                "ttl": self.ttl,
                "data": srv_data,
            }
            search_value = join_str("\t", self.weight, self.port, self.value)
            search_record = join_str(".", self.service, self.proto, self.record)

        if self.type == "DS":
            for attr in [self.key_tag, self.algorithm, self.hash_type, self.value]:
                if (attr is None) or (attr == ""):
                    self.module.fail_json(
                        msg="You must provide key_tag, algorithm, hash_type and a value to create this record type"
                    )
            ds_data = {
                "key_tag": self.key_tag,
                "algorithm": self.algorithm,
                "digest_type": self.hash_type,
                "digest": self.value,
            }
            new_record = {
                "type": self.type,
                "name": self.record,
                "data": ds_data,
                "ttl": self.ttl,
            }
            search_value = join_str("\t", self.key_tag, self.algorithm, self.hash_type, self.value)

        if self.type == "SSHFP":
            for attr in [self.algorithm, self.hash_type, self.value]:
                if (attr is None) or (attr == ""):
                    self.module.fail_json(
                        msg="You must provide algorithm, hash_type and a value to create this record type"
                    )
            sshfp_data = {
                "fingerprint": self.value.upper(),
                "type": self.hash_type,
                "algorithm": self.algorithm,
            }
            new_record = {
                "type": self.type,
                "name": self.record,
                "data": sshfp_data,
                "ttl": self.ttl,
            }
            search_value = join_str(" ", self.algorithm, self.hash_type, self.value)

        if self.type == "TLSA":
            for attr in [self.port, self.proto, self.cert_usage, self.selector, self.hash_type, self.value]:
                if (attr is None) or (attr == ""):
                    self.module.fail_json(
                        msg="You must provide port, proto, cert_usage, selector, hash_type and a value to create this record type"
                    )
            search_record = join_str(".", self.port, self.proto, self.record)
            tlsa_data = {
                "usage": self.cert_usage,
                "selector": self.selector,
                "matching_type": self.hash_type,
                "certificate": self.value,
            }
            new_record = {
                "type": self.type,
                "name": search_record,
                "data": tlsa_data,
                "ttl": self.ttl,
            }
            search_value = join_str("\t", self.cert_usage, self.selector, self.hash_type, self.value)

        if self.type == "CAA":
            for attr in [self.flag, self.tag, self.value]:
                if attr == "":
                    self.module.fail_json(msg="You must provide flag, tag and a value to create this record type")
            caa_data = {
                "flags": self.flag,
                "tag": self.tag,
                "value": self.value,
            }
            new_record = {
                "type": self.type,
                "name": self.record,
                "data": caa_data,
                "ttl": self.ttl,
            }
            search_value = None

        new_record["comment"] = self.comment or None
        new_record["tags"] = self.tags or []

        zone_id = self._get_zone_id(self.zone)
        records = self.get_dns_records(self.zone, self.type, search_record, search_value)
        # in theory this should be impossible as cloudflare does not allow
        # the creation of duplicate records but lets cover it anyways
        if len(records) > 1:
            # As Cloudflare API cannot filter record containing quotes
            # CAA records must be compared locally
            if self.type == "CAA":
                for rr in records:
                    if (
                        rr["data"]["flags"] == caa_data["flags"]
                        and rr["data"]["tag"] == caa_data["tag"]
                        and rr["data"]["value"] == caa_data["value"]
                    ):
                        return rr, self.changed
            else:
                self.module.fail_json(
                    msg="More than one record already exists for the given attributes. That should be impossible, please open an issue!"
                )
        # record already exists, check if it must be updated
        if len(records) == 1:
            cur_record = records[0]
            do_update = False
            if (self.ttl is not None) and (cur_record["ttl"] != self.ttl):
                do_update = True
            if (self.priority is not None) and ("priority" in cur_record) and (cur_record["priority"] != self.priority):
                do_update = True
            if ("proxied" in new_record) and ("proxied" in cur_record) and (cur_record["proxied"] != self.proxied):
                do_update = True
            if ("data" in new_record) and ("data" in cur_record):
                if cur_record["data"] != new_record["data"]:
                    do_update = True
            if (self.type == "CNAME") and (cur_record["content"] != new_record["content"]):
                do_update = True
            if cur_record["comment"] != new_record["comment"]:
                do_update = True
            if sorted(cur_record["tags"]) != sorted(new_record["tags"]):
                do_update = True
            if do_update:
                if self.module.check_mode:
                    result = new_record
                else:
                    result, info = self._cf_api_call(
                        f"/zones/{zone_id}/dns_records/{records[0]['id']}", "PUT", new_record
                    )
                self.changed = True
                return result, self.changed
            else:
                return records, self.changed
        if self.module.check_mode:
            result = new_record
        else:
            result, info = self._cf_api_call(f"/zones/{zone_id}/dns_records", "POST", new_record)
        self.changed = True
        return result, self.changed


def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_token=dict(type="str", no_log=True, fallback=(env_fallback, ["CLOUDFLARE_TOKEN"])),
            account_api_key=dict(type="str", no_log=True, aliases=["account_api_token"]),
            account_email=dict(type="str"),
            algorithm=dict(type="int"),
            cert_usage=dict(type="int", choices=[0, 1, 2, 3]),
            comment=dict(type="str"),
            hash_type=dict(type="int", choices=[1, 2]),
            key_tag=dict(type="int", no_log=False),
            port=dict(type="int"),
            flag=dict(type="int", choices=[0, 1]),
            tag=dict(type="str", choices=["issue", "issuewild", "iodef"]),
            tags=dict(type="list", elements="str"),
            priority=dict(type="int", default=1),
            proto=dict(type="str"),
            proxied=dict(type="bool", default=False),
            record=dict(type="str", default="@", aliases=["name"]),
            selector=dict(type="int", choices=[0, 1]),
            service=dict(type="str"),
            solo=dict(type="bool"),
            state=dict(type="str", default="present", choices=["absent", "present"]),
            timeout=dict(type="int", default=30),
            ttl=dict(type="int", default=1),
            type=dict(
                type="str",
                choices=["A", "AAAA", "CNAME", "DS", "MX", "NS", "SRV", "SSHFP", "TLSA", "CAA", "TXT", "PTR"],
            ),
            value=dict(type="str", aliases=["content"]),
            weight=dict(type="int", default=1),
            zone=dict(type="str", required=True, aliases=["domain"]),
        ),
        supports_check_mode=True,
        required_if=[
            ("state", "present", ["record", "type", "value"]),
            ("state", "absent", ["record"]),
            ("type", "SRV", ["proto", "service"]),
            ("type", "TLSA", ["proto", "port"]),
            ("type", "CAA", ["flag", "tag"]),
        ],
        required_together=[
            ("account_api_key", "account_email"),
        ],
        required_one_of=[
            ["api_token", "account_api_key"],
        ],
    )

    if module.params["type"] == "SRV":
        if not (
            (
                module.params["weight"] is not None
                and module.params["port"] is not None
                and not (module.params["value"] is None or module.params["value"] == "")
            )
            or (
                module.params["weight"] is None
                and module.params["port"] is None
                and (module.params["value"] is None or module.params["value"] == "")
            )
        ):
            module.fail_json(
                msg="For SRV records the params weight, port and value all need to be defined, or not at all."
            )

    if module.params["type"] == "SSHFP":
        if not (
            (
                module.params["algorithm"] is not None
                and module.params["hash_type"] is not None
                and not (module.params["value"] is None or module.params["value"] == "")
            )
            or (
                module.params["algorithm"] is None
                and module.params["hash_type"] is None
                and (module.params["value"] is None or module.params["value"] == "")
            )
        ):
            module.fail_json(
                msg="For SSHFP records the params algorithm, hash_type and value all need to be defined, or not at all."
            )

    if module.params["type"] == "TLSA":
        if not (
            (
                module.params["cert_usage"] is not None
                and module.params["selector"] is not None
                and module.params["hash_type"] is not None
                and not (module.params["value"] is None or module.params["value"] == "")
            )
            or (
                module.params["cert_usage"] is None
                and module.params["selector"] is None
                and module.params["hash_type"] is None
                and (module.params["value"] is None or module.params["value"] == "")
            )
        ):
            module.fail_json(
                msg="For TLSA records the params cert_usage, selector, hash_type and value all need to be defined, or not at all."
            )

    if module.params["type"] == "CAA":
        if not (
            (
                module.params["flag"] is not None
                and module.params["tag"] is not None
                and not (module.params["value"] is None or module.params["value"] == "")
            )
            or (
                module.params["flag"] is None
                and module.params["tag"] is None
                and (module.params["value"] is None or module.params["value"] == "")
            )
        ):
            module.fail_json(
                msg="For CAA records the params flag, tag and value all need to be defined, or not at all."
            )

    if module.params["type"] == "DS":
        if not (
            (
                module.params["key_tag"] is not None
                and module.params["algorithm"] is not None
                and module.params["hash_type"] is not None
                and not (module.params["value"] is None or module.params["value"] == "")
            )
            or (
                module.params["key_tag"] is None
                and module.params["algorithm"] is None
                and module.params["hash_type"] is None
                and (module.params["value"] is None or module.params["value"] == "")
            )
        ):
            module.fail_json(
                msg="For DS records the params key_tag, algorithm, hash_type and value all need to be defined, or not at all."
            )

    changed = False
    cf_api = CloudflareAPI(module)

    # sanity checks
    if cf_api.is_solo and cf_api.state == "absent":
        module.fail_json(msg="solo=true can only be used with state=present")

    # perform add, delete or update (only the TTL can be updated) of one or
    # more records
    if cf_api.state == "present":
        # delete all records matching record name + type
        if cf_api.is_solo:
            changed = cf_api.delete_dns_records(solo=cf_api.is_solo)
        result, changed = cf_api.ensure_dns_record()
        if isinstance(result, list):
            module.exit_json(changed=changed, result={"record": result[0]})

        module.exit_json(changed=changed, result={"record": result})
    else:
        # force solo to False, just to be sure
        changed = cf_api.delete_dns_records(solo=False)
        module.exit_json(changed=changed)


if __name__ == "__main__":
    main()

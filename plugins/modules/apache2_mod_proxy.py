#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2016, Olivier Boukili <boukili.olivier@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
module: apache2_mod_proxy
author: Olivier Boukili (@oboukili)
short_description: Set and/or get members' attributes of an Apache httpd 2.4 mod_proxy balancer pool
description:
  - Set and/or get members' attributes of an Apache httpd 2.4 mod_proxy balancer pool, using HTTP POST and GET requests. The
    httpd mod_proxy balancer-member status page has to be enabled and accessible, as this module relies on parsing this page.
extends_documentation_fragment:
  - community.general.attributes
requirements:
  - Python package C(BeautifulSoup) on Python 2, C(beautifulsoup4) on Python 3.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  balancer_url_suffix:
    type: str
    description:
      - Suffix of the balancer pool URL required to access the balancer pool status page (for example V(balancer_vhost[:port]/balancer_url_suffix)).
    default: /balancer-manager/
  balancer_vhost:
    type: str
    description:
      - (IPv4|IPv6|FQDN):port of the Apache httpd 2.4 mod_proxy balancer pool.
    required: true
  member_host:
    type: str
    description:
      - (IPv4|IPv6|FQDN) of the balancer member to get or to set attributes to. Port number is autodetected and should not
        be specified here.
      - If undefined, the M(community.general.apache2_mod_proxy) module will return a members list of dictionaries of all the current
        balancer pool members' attributes.
  state:
    type: list
    elements: str
    choices: [present, absent, enabled, disabled, drained, hot_standby, ignore_errors]
    description:
      - Desired state of the member host.
      - States can be simultaneously invoked by separating them with a comma (for example V(state=drained,ignore_errors)),
        but it is recommended to specify them as a proper YAML list.
      - States V(present) and V(absent) must be used without any other state.
  tls:
    description:
      - Use https to access balancer management page.
    type: bool
    default: false
  validate_certs:
    description:
      - Validate ssl/tls certificates.
    type: bool
    default: true
"""

EXAMPLES = r"""
- name: Get all current balancer pool members attributes
  community.general.apache2_mod_proxy:
    balancer_vhost: 10.0.0.2

- name: Get a specific member attributes
  community.general.apache2_mod_proxy:
    balancer_vhost: myws.mydomain.org
    balancer_suffix: /lb/
    member_host: node1.myws.mydomain.org

# Enable all balancer pool members:
- name: Get attributes
  community.general.apache2_mod_proxy:
    balancer_vhost: '{{ myloadbalancer_host }}'
  register: result

- name: Enable all balancer pool members
  community.general.apache2_mod_proxy:
    balancer_vhost: '{{ myloadbalancer_host }}'
    member_host: '{{ item.host }}'
    state: present
  with_items: '{{ result.members }}'

# Gracefully disable a member from a loadbalancer node:
- name: Step 1
  community.general.apache2_mod_proxy:
    balancer_vhost: '{{ vhost_host }}'
    member_host: '{{ member.host }}'
    state: drained
  delegate_to: myloadbalancernode

- name: Step 2
  ansible.builtin.wait_for:
    host: '{{ member.host }}'
    port: '{{ member.port }}'
    state: drained
  delegate_to: myloadbalancernode

- name: Step 3
  community.general.apache2_mod_proxy:
    balancer_vhost: '{{ vhost_host }}'
    member_host: '{{ member.host }}'
    state: absent
  delegate_to: myloadbalancernode
"""

RETURN = r"""
member:
  description: Specific balancer member information dictionary, returned when the module is invoked with O(member_host) parameter.
  type: dict
  returned: success
  sample:
    {"attributes":
          {"Busy": "0",
          "Elected": "42",
          "Factor": "1",
          "From": "136K",
          "Load": "0",
          "Route": null,
          "RouteRedir": null,
          "Set": "0",
          "Status": "Init Ok ",
          "To": " 47K",
          "Worker URL": null
      },
      "balancer_url": "http://10.10.0.2/balancer-manager/",
      "host": "10.10.0.20",
      "management_url": "http://10.10.0.2/lb/?b=mywsbalancer&w=http://10.10.0.20:8080/ws&nonce=8925436c-79c6-4841-8936-e7d13b79239b",
      "path": "/ws",
      "port": 8080,
      "protocol": "http",
      "status": {
          "disabled": false,
          "drained": false,
          "hot_standby": false,
          "ignore_errors": false
      }
    }
members:
  description: List of member (defined above) dictionaries, returned when the module is invoked with no O(member_host) and
    O(state) args.
  returned: success
  type: list
  sample:
    [{"attributes": {
          "Busy": "0",
          "Elected": "42",
          "Factor": "1",
          "From": "136K",
          "Load": "0",
          "Route": null,
          "RouteRedir": null,
          "Set": "0",
          "Status": "Init Ok ",
          "To": " 47K",
          "Worker URL": null
      },
      "balancer_url": "http://10.10.0.2/balancer-manager/",
      "host": "10.10.0.20",
      "management_url": "http://10.10.0.2/lb/?b=mywsbalancer&w=http://10.10.0.20:8080/ws&nonce=8925436c-79c6-4841-8936-e7d13b79239b",
      "path": "/ws",
      "port": 8080,
      "protocol": "http",
      "status": {
          "disabled": false,
          "drained": false,
          "hot_standby": false,
          "ignore_errors": false
      }
      },
      {"attributes": {
          "Busy": "0",
          "Elected": "42",
          "Factor": "1",
          "From": "136K",
          "Load": "0",
          "Route": null,
          "RouteRedir": null,
          "Set": "0",
          "Status": "Init Ok ",
          "To": " 47K",
          "Worker URL": null
      },
      "balancer_url": "http://10.10.0.2/balancer-manager/",
      "host": "10.10.0.21",
      "management_url": "http://10.10.0.2/lb/?b=mywsbalancer&w=http://10.10.0.21:8080/ws&nonce=8925436c-79c6-4841-8936-e7d13b79239b",
      "path": "/ws",
      "port": 8080,
      "protocol": "http",
      "status": {
          "disabled": false,
          "drained": false,
          "hot_standby": false,
          "ignore_errors": false}
      }
    ]
"""

import re

from ansible_collections.community.general.plugins.module_utils import deps
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six import iteritems, PY2

if PY2:
    with deps.declare("BeautifulSoup"):
        from BeautifulSoup import BeautifulSoup
else:
    with deps.declare("beautifulsoup4"):
        from bs4 import BeautifulSoup

# balancer member attributes extraction regexp:
EXPRESSION = re.compile(to_text(r"(b=([\w\.\-]+)&w=(https?|ajp|wss?|ftp|[sf]cgi)://([\w\.\-]+):?(\d*)([/\w\.\-]*)&?[\w\-\=]*)"))
# Apache2 server version extraction regexp:
APACHE_VERSION_EXPRESSION = re.compile(to_text(r"SERVER VERSION: APACHE/([\d.]+)"))


def find_all(where, what):
    if PY2:
        return where.findAll(what)
    return where.find_all(what)


def regexp_extraction(string, _regexp, groups=1):
    """ Returns the capture group (default=1) specified in the regexp, applied to the string """
    regexp_search = _regexp.search(string)
    if regexp_search:
        if regexp_search.group(groups) != '':
            return regexp_search.group(groups)
    return None


class BalancerMember(object):
    """ Apache 2.4 mod_proxy LB balancer member.
    attributes:
        read-only:
            host -> member host (string),
            management_url -> member management url (string),
            protocol -> member protocol (string)
            port -> member port (string),
            path -> member location (string),
            balancer_url -> url of this member's parent balancer (string),
            attributes -> whole member attributes (dictionary)
            module -> ansible module instance (AnsibleModule object).
        writable:
            status -> status of the member (dictionary)
    """

    def __init__(self, management_url, balancer_url, module):
        self.host = regexp_extraction(management_url, EXPRESSION, 4)
        self.management_url = management_url
        self.protocol = regexp_extraction(management_url, EXPRESSION, 3)
        self.port = regexp_extraction(management_url, EXPRESSION, 5)
        self.path = regexp_extraction(management_url, EXPRESSION, 6)
        self.balancer_url = balancer_url
        self.module = module

    def get_member_attributes(self):
        """ Returns a dictionary of a balancer member's attributes."""

        resp, info = fetch_url(self.module, self.management_url, headers={'Referer': self.management_url})

        if info['status'] != 200:
            self.module.fail_json(msg="Could not get balancer_member_page, check for connectivity! {0}".format(info))
        else:
            try:
                soup = BeautifulSoup(resp)
            except TypeError as exc:
                self.module.fail_json(msg="Cannot parse balancer_member_page HTML! {0}".format(exc))
            else:
                subsoup = find_all(find_all(soup, 'table')[1], 'tr')
                keys = find_all(subsoup[0], 'th')
                for valuesset in subsoup[1::1]:
                    if re.search(pattern=self.host, string=str(valuesset)):
                        values = find_all(valuesset, 'td')
                        return {keys[x].string: values[x].string for x in range(0, len(keys))}

    def get_member_status(self):
        """ Returns a dictionary of a balancer member's status attributes."""
        status_mapping = {'disabled': 'Dis',
                          'drained': 'Drn',
                          'hot_standby': 'Stby',
                          'ignore_errors': 'Ign'}
        actual_status = self.attributes['Status']
        status = {mode: patt in actual_status for mode, patt in iteritems(status_mapping)}
        return status

    def set_member_status(self, values):
        """ Sets a balancer member's status attributes amongst pre-mapped values."""
        values_mapping = {'disabled': '&w_status_D',
                          'drained': '&w_status_N',
                          'hot_standby': '&w_status_H',
                          'ignore_errors': '&w_status_I'}

        request_body = regexp_extraction(self.management_url, EXPRESSION, 1)
        values_url = "".join("{0}={1}".format(url_param, 1 if values[mode] else 0) for mode, url_param in values_mapping.items())
        request_body = "{0}{1}".format(request_body, values_url)

        response, info = fetch_url(self.module, self.management_url, data=request_body, headers={'Referer': self.management_url})
        if info['status'] != 200:
            self.module.fail_json(msg="Could not set the member status! {host} {status}".format(host=self.host, status=info['status']))

    attributes = property(get_member_attributes)
    status = property(get_member_status, set_member_status)

    def as_dict(self):
        return {
            "host": self.host,
            "status": self.status,
            "protocol": self.protocol,
            "port": self.port,
            "path": self.path,
            "attributes": self.attributes,
            "management_url": self.management_url,
            "balancer_url": self.balancer_url
        }


class Balancer(object):
    """ Apache httpd 2.4 mod_proxy balancer object"""

    def __init__(self, host, suffix, module, tls=False):
        if tls:
            self.base_url = 'https://{0}'.format(host)
            self.url = 'https://{0}{1}'.format(host, suffix)
        else:
            self.base_url = 'http://{0}'.format(host)
            self.url = 'http://{0}{1}'.format(host, suffix)
        self.module = module
        self.page = self.fetch_balancer_page()

    def fetch_balancer_page(self):
        """ Returns the balancer management html page as a string for later parsing."""
        resp, info = fetch_url(self.module, self.url)
        if info['status'] != 200:
            self.module.fail_json(msg="Could not get balancer page! HTTP status response: {0}".format(info['status']))
        else:
            content = to_text(resp.read())
            apache_version = regexp_extraction(content.upper(), APACHE_VERSION_EXPRESSION, 1)
            if apache_version:
                if not re.search(pattern=r"2\.4\.[\d]*", string=apache_version):
                    self.module.fail_json(
                        msg="This module only acts on an Apache2 2.4+ instance, current Apache2 version: {version}".format(
                            version=apache_version
                        )
                    )
                return content

            self.module.fail_json(msg="Could not get the Apache server version from the balancer-manager")

    def get_balancer_members(self):
        """ Returns members of the balancer as a generator object for later iteration."""
        try:
            soup = BeautifulSoup(self.page)
        except TypeError:
            self.module.fail_json(msg="Cannot parse balancer page HTML! {0}".format(self.page))
        else:
            elements = find_all(soup, 'a')
            for element in elements[1::1]:
                balancer_member_suffix = str(element.get('href'))
                if not balancer_member_suffix:
                    self.module.fail_json(msg="Argument 'balancer_member_suffix' is empty!")
                else:
                    yield BalancerMember(self.base_url + balancer_member_suffix, self.url, self.module)

    members = property(get_balancer_members)


def main():
    """ Initiates module."""
    module = AnsibleModule(
        argument_spec=dict(
            balancer_vhost=dict(required=True, type='str'),
            balancer_url_suffix=dict(default="/balancer-manager/", type='str'),
            member_host=dict(type='str'),
            state=dict(type='list', elements='str', choices=['present', 'absent', 'enabled', 'disabled', 'drained', 'hot_standby', 'ignore_errors']),
            tls=dict(default=False, type='bool'),
            validate_certs=dict(default=True, type='bool')
        ),
        supports_check_mode=True
    )

    deps.validate(module)

    if module.params['state'] is not None:
        states = module.params['state']
        if (len(states) > 1) and (("present" in states) or ("enabled" in states)):
            module.fail_json(msg="state present/enabled is mutually exclusive with other states!")
    else:
        states = ['None']

    mybalancer = Balancer(module.params['balancer_vhost'],
                          module.params['balancer_url_suffix'],
                          module=module,
                          tls=module.params['tls'])

    if module.params['member_host'] is None:
        json_output_list = []
        for member in mybalancer.members:
            json_output_list.append(member.as_dict())
        module.exit_json(
            changed=False,
            members=json_output_list
        )
    else:
        changed = False
        member_exists = False
        member_status = {'disabled': False, 'drained': False, 'hot_standby': False, 'ignore_errors': False}
        for mode in member_status:
            for state in states:
                if mode == state:
                    member_status[mode] = True
                elif mode == 'disabled' and state == 'absent':
                    member_status[mode] = True

        for member in mybalancer.members:
            if str(member.host) == module.params['member_host']:
                member_exists = True
                if module.params['state'] is not None:
                    member_status_before = member.status
                    if not module.check_mode:
                        member_status_after = member.status = member_status
                    else:
                        member_status_after = member_status
                    if member_status_before != member_status_after:
                        changed = True
                json_output = member.as_dict()
        if member_exists:
            module.exit_json(
                changed=changed,
                member=json_output
            )
        else:
            module.fail_json(
                msg='{member_host} is not a member of the balancer {balancer_vhost}!'.format(
                    member_host=module.params['member_host'],
                    balancer_vhost=module.params['balancer_vhost'],
                )
            )


if __name__ == '__main__':
    main()

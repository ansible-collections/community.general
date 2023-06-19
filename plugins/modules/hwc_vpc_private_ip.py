#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Huawei
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

###############################################################################
# Documentation
###############################################################################

DOCUMENTATION = '''
---
module: hwc_vpc_private_ip
description:
    - vpc private ip management.
short_description: Creates a resource of Vpc/PrivateIP in Huawei Cloud
notes:
    - If O(id) option is provided, it takes precedence over O(subnet_id), O(ip_address) for private ip selection.
    - O(subnet_id), O(ip_address) are used for private ip selection. If more than one private ip with this options exists, execution is aborted.
    - No parameter support updating. If one of option is changed, the module will create a new resource.
version_added: '0.2.0'
author: Huawei Inc. (@huaweicloud)
requirements:
    - keystoneauth1 >= 3.6.0
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    state:
        description:
            - Whether the given object should exist in Huawei Cloud.
        type: str
        choices: ['present', 'absent']
        default: 'present'
    subnet_id:
        description:
            - Specifies the ID of the subnet from which IP addresses are
              assigned. Cannot be changed after creating the private ip.
        type: str
        required: true
    ip_address:
        description:
            - Specifies the target IP address. The value can be an available IP
              address in the subnet. If it is not specified, the system
              automatically assigns an IP address. Cannot be changed after
              creating the private ip.
        type: str
        required: false
extends_documentation_fragment:
  - community.general.hwc
  - community.general.attributes

'''

EXAMPLES = '''
# create a private ip
- name: Create vpc
  hwc_network_vpc:
    cidr: "192.168.100.0/24"
    name: "ansible_network_vpc_test"
  register: vpc
- name: Create subnet
  hwc_vpc_subnet:
    gateway_ip: "192.168.100.32"
    name: "ansible_network_subnet_test"
    dhcp_enable: true
    vpc_id: "{{ vpc.id }}"
    cidr: "192.168.100.0/26"
  register: subnet
- name: Create a private ip
  community.general.hwc_vpc_private_ip:
    subnet_id: "{{ subnet.id }}"
    ip_address: "192.168.100.33"
'''

RETURN = '''
    subnet_id:
        description:
            - Specifies the ID of the subnet from which IP addresses are
              assigned.
        type: str
        returned: success
    ip_address:
        description:
            - Specifies the target IP address. The value can be an available IP
              address in the subnet. If it is not specified, the system
              automatically assigns an IP address.
        type: str
        returned: success
'''

from ansible_collections.community.general.plugins.module_utils.hwc_utils import (
    Config, HwcClientException, HwcModule, are_different_dicts, build_path,
    get_region, is_empty_value, navigate_value)


def build_module():
    return HwcModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent'],
                       type='str'),
            subnet_id=dict(type='str', required=True),
            ip_address=dict(type='str')
        ),
        supports_check_mode=True,
    )


def main():
    """Main function"""

    module = build_module()
    config = Config(module, "vpc")

    try:
        resource = None
        if module.params['id']:
            resource = True
        else:
            v = search_resource(config)
            if len(v) > 1:
                raise Exception("Found more than one resource(%s)" % ", ".join([
                                navigate_value(i, ["id"]) for i in v]))

            if len(v) == 1:
                resource = v[0]
                module.params['id'] = navigate_value(resource, ["id"])

        result = {}
        changed = False
        if module.params['state'] == 'present':
            if resource is None:
                if not module.check_mode:
                    create(config)
                changed = True

            current = read_resource(config, exclude_output=True)
            expect = user_input_parameters(module)
            if are_different_dicts(expect, current):
                raise Exception(
                    "Cannot change option from (%s) to (%s)of an"
                    " existing resource.(%s)" % (current, expect, module.params.get('id')))

            result = read_resource(config)
            result['id'] = module.params.get('id')
        else:
            if resource:
                if not module.check_mode:
                    delete(config)
                changed = True

    except Exception as ex:
        module.fail_json(msg=str(ex))

    else:
        result['changed'] = changed
        module.exit_json(**result)


def user_input_parameters(module):
    return {
        "ip_address": module.params.get("ip_address"),
        "subnet_id": module.params.get("subnet_id"),
    }


def create(config):
    module = config.module
    client = config.client(get_region(module), "vpc", "project")
    opts = user_input_parameters(module)

    params = build_create_parameters(opts)
    r = send_create_request(module, params, client)
    module.params['id'] = navigate_value(r, ["privateips", "id"],
                                         {"privateips": 0})


def delete(config):
    module = config.module
    client = config.client(get_region(module), "vpc", "project")

    send_delete_request(module, None, client)


def read_resource(config, exclude_output=False):
    module = config.module
    client = config.client(get_region(module), "vpc", "project")

    res = {}

    r = send_read_request(module, client)
    res["read"] = fill_read_resp_body(r)

    return update_properties(module, res, None, exclude_output)


def _build_query_link(opts):
    query_link = "?marker={marker}&limit=10"

    return query_link


def search_resource(config):
    module = config.module
    client = config.client(get_region(module), "vpc", "project")
    opts = user_input_parameters(module)
    identity_obj = _build_identity_object(opts)
    query_link = _build_query_link(opts)
    link = build_path(module, "subnets/{subnet_id}/privateips") + query_link

    result = []
    p = {'marker': ''}
    while True:
        url = link.format(**p)
        r = send_list_request(module, client, url)
        if not r:
            break

        for item in r:
            item = fill_list_resp_body(item)
            if not are_different_dicts(identity_obj, item):
                result.append(item)

        if len(result) > 1:
            break

        p['marker'] = r[-1].get('id')

    return result


def build_create_parameters(opts):
    params = dict()

    v = navigate_value(opts, ["ip_address"], None)
    if not is_empty_value(v):
        params["ip_address"] = v

    v = navigate_value(opts, ["subnet_id"], None)
    if not is_empty_value(v):
        params["subnet_id"] = v

    if not params:
        return params

    params = {"privateips": [params]}

    return params


def send_create_request(module, params, client):
    url = "privateips"
    try:
        r = client.post(url, params)
    except HwcClientException as ex:
        msg = ("module(hwc_vpc_private_ip): error running "
               "api(create), error: %s" % str(ex))
        module.fail_json(msg=msg)

    return r


def send_delete_request(module, params, client):
    url = build_path(module, "privateips/{id}")

    try:
        r = client.delete(url, params)
    except HwcClientException as ex:
        msg = ("module(hwc_vpc_private_ip): error running "
               "api(delete), error: %s" % str(ex))
        module.fail_json(msg=msg)

    return r


def send_read_request(module, client):
    url = build_path(module, "privateips/{id}")

    r = None
    try:
        r = client.get(url)
    except HwcClientException as ex:
        msg = ("module(hwc_vpc_private_ip): error running "
               "api(read), error: %s" % str(ex))
        module.fail_json(msg=msg)

    return navigate_value(r, ["privateip"], None)


def fill_read_resp_body(body):
    result = dict()

    result["id"] = body.get("id")

    result["ip_address"] = body.get("ip_address")

    result["subnet_id"] = body.get("subnet_id")

    return result


def update_properties(module, response, array_index, exclude_output=False):
    r = user_input_parameters(module)

    v = navigate_value(response, ["read", "ip_address"], array_index)
    r["ip_address"] = v

    v = navigate_value(response, ["read", "subnet_id"], array_index)
    r["subnet_id"] = v

    return r


def send_list_request(module, client, url):

    r = None
    try:
        r = client.get(url)
    except HwcClientException as ex:
        msg = ("module(hwc_vpc_private_ip): error running "
               "api(list), error: %s" % str(ex))
        module.fail_json(msg=msg)

    return navigate_value(r, ["privateips"], None)


def _build_identity_object(all_opts):
    result = dict()

    result["id"] = None

    v = navigate_value(all_opts, ["ip_address"], None)
    result["ip_address"] = v

    v = navigate_value(all_opts, ["subnet_id"], None)
    result["subnet_id"] = v

    return result


def fill_list_resp_body(body):
    result = dict()

    result["id"] = body.get("id")

    result["ip_address"] = body.get("ip_address")

    result["subnet_id"] = body.get("subnet_id")

    return result


if __name__ == '__main__':
    main()

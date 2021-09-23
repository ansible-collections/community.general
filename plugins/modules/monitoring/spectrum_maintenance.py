#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2021 Uwe Waechter <uwe.waechter@scok.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: spectrum_maintenance
short_description: put devices in/out maintenance or hibernating mode.
description:
   - Tested on CA Spectrum 10.4.3.x
version_added: 3.6.0
author: "Uwe Waechter (@UweW)"
options:
    device:
        aliases: [ host, name ]
        required: true
        description:
            - IP address of the device.
            - If a hostname is given, it will be resolved to the IP address.
        type: str
    state:
        description:
            - On C(inMaintenance) put device in maintenance mode.
            - On C(inHibernation) put device in hibernation mode.
            - On C(isManaged) put device in managed mode.
        choices: ['inMaintenance', 'inHibernation', 'isManaged']
        default: 'isManaged'
        type: str
    url:
        aliases: [ oneclick_url ]
        required: true
        description:
            - OneClick server URL in the form C((http|https)://host.domain[:port]).
        type: str
    url_username:
        aliases: [ oneclick_user ]
        required: true
        description:
            - Oneclick user name.
        type: str
    url_password:
        aliases: [ oneclick_password ]
        required: true
        description:
            - Oneclick user password.
        type: str
    use_proxy:
        required: false
        description:
            - if C(false), then a proxy will not be used even if one is defined in an environment
                variable on the target hosts.
        default: false
        type: bool
    validate_certs:
        required: false
        description:
            - If C(false), SSL certificates will not be validated. This should only be used
                on personally controlled sites using self-signed certificates.
        default: true
        type: bool
notes:
   -  expects IP address as inventory_hostname
'''

EXAMPLES = '''
- name: Put device in Maintenance mode
  spectrum_maintenance:
    device: '{{ inventory_hostname }}'
    oneclick_url: http://oneclick.example.com:8080
    url_username: username
    url_password: password
    state: 'inMaintenance'
  delegate_to: localhost

- name: Put device in Hibernating mode
  spectrum_maintenance:
    device: '{{ inventory_hostname }}'
    oneclick_url: http://oneclick.example.com:8080
    url_username: username
    url_password: password
    state: 'inHibernation'
  delegate_to: localhost

- name: Put device back in isManaged
  spectrum_maintenance:
    device: '{{ inventory_hostname }}'
    oneclick_url: http://oneclick.example.com:8080
    url_username: username
    url_password: password
    state: 'isManaged'
  delegate_to: localhost
'''


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from socket import gethostbyname, gaierror
import xml.etree.ElementTree as ET


def request(resource, xml=None, method=None):
    headers = {
        "Content-Type": "application/xml",
        "Accept": "application/xml"
    }
    url = module.params['oneclick_url'] + '/spectrum/restful/' + resource

    response, info = fetch_url(module, url, data=xml, method=method, headers=headers, timeout=45)

    if info['status'] == 401:
        module.fail_json(msg="failed to authenticate to Oneclick server")

    if info['status'] not in (200, 201, 204):
        module.fail_json(msg=info['msg'])

    return response.read()


def post(resource, xml=None):
    return request(resource, xml=xml, method='POST')


def put(resource):
    return request(resource, xml=None, method='PUT')


def get_ip():
    try:
        device_ip = gethostbyname(module.params.get('device'))
    except gaierror:
        module.fail_json(msg="failed to resolve device ip address for '%s'" % module.params.get('device'))

    return device_ip


def get_model_handle_by_ip(device_ip):
    """Query Spectrum for the model_handle of an IP Address"""
    resource = '/models'

    xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rs:model-request throttlesize="10000"
        xmlns:rs="http://www.ca.com/spectrum/restful/schema/request"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.ca.com/spectrum/restful/schema/request ../../../xsd/Request.xsd ">

        <rs:target-models>
            <rs:models-search>
            <rs:search-criteria xmlns="http://www.ca.com/spectrum/restful/schema/filter">
                <action-models>
                    <filtered-models>
                        <equals>
                            <model-type>SearchManager</model-type>
                        </equals>
                    </filtered-models>
                    <action>FIND_DEV_MODELS_BY_IP</action>
                        <attribute id="AttributeID.NETWORK_ADDRESS">
                            <value>{search_ip}</value>
                        </attribute>
                </action-models>
            </rs:search-criteria>
            </rs:models-search>
        </rs:target-models>
    <rs:requested-attribute id="0x1295d" />
    <rs:requested-attribute id="0x12aca" />
    <rs:requested-attribute id="0x12d8b" />
</rs:model-request> """.format(search_ip=device_ip)

    result = post(resource, xml=xml)

    root = ET.fromstring(result)

    if root.get('total-models') == '0':
        return None

    namespace = dict(ca='http://www.ca.com/spectrum/restful/schema/response')

    # get the first device
    model = root.find('ca:model-responses', namespace).find('ca:model', namespace)

    if model.get('error'):
        module.fail_json(msg="error checking device: %s" % model.get('error'))

    # get the attributes
    model_handle = model.get('mh')
    is_managed = model.find('./*[@id="0x1295d"]').text
    is_not_hibernating = model.find('./*[@id="0x12aca"]').text
    hibernating_after_maintenance = model.find('./*[@id="0x12d8b"]').text

    return model_handle, is_managed, is_not_hibernating, hibernating_after_maintenance, result


def put_maintenance(mh, resource):
    # model / 0x10041f?attr = 0x1295d & val = 0

    result = put(resource)
    return result


def main():
    global module
    module = AnsibleModule(
        argument_spec=dict(
            device=dict(type='str', required=True, aliases=['host', 'name']),
            state=dict(type='str', choices=['inMaintenance', 'inHibernation', 'isManaged'], default='isManaged'),
            url=dict(type='str', required=True, aliases=['oneclick_url']),
            url_username=dict(type='str', required=True, aliases=['oneclick_user']),
            url_password=dict(type='str', required=True, no_log=True, aliases=['oneclick_password']),
            use_proxy=dict(type='bool', default=False),
            validate_certs=dict(type='bool', default='no')
        ),
        supports_check_mode=True
    )
    module_state = module.params.get('state')
    mh, is_managed, is_not_hibernating, hibernating_after_maintenance, ergebnis = get_model_handle_by_ip(
        module.params.get('device'))

    if module_state == 'inMaintenance':
        if is_managed == 'false' and is_not_hibernating == 'true' and hibernating_after_maintenance == 'false':
            module.exit_json()

        resource = '/model/' + mh + '/?attr=0x1295d&val=0&attr=0x12aca&val=1'
        result = put_maintenance(mh, resource)
        module.exit_json(changed=True, msg=result)

    elif module_state == 'inHibernation':
        if is_managed == 'false' and is_not_hibernating == 'false' and hibernating_after_maintenance == 'false':
            module.exit_json()
        resource = '/model/' + mh + '/?attr=0x12aca&val=0'
        result = put_maintenance(mh, resource)
        module.exit_json(changed=True, msg=result)

    else:
        # isManaged
        if is_managed == 'true' and is_not_hibernating == 'true' and hibernating_after_maintenance == 'false':
            module.exit_json()
        resource = '/model/' + mh + '/?attr=0x1295d&val=1&attr=0x12aca&val=1'
        result = put_maintenance(mh, resource)
        module.exit_json(changed=True, result=result)


if __name__ == '__main__':
    main()

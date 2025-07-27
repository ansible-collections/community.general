#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021, Tyler Gates <tgates81@gmail.com>
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
module: spectrum_model_attrs
short_description: Enforce a model's attributes in CA Spectrum
description:
  - This module can be used to enforce a model's attributes in CA Spectrum.
version_added: 2.5.0
author:
  - Tyler Gates (@tgates81)
notes:
  - Tested on CA Spectrum version 10.4.2.0.189.
  - Model creation and deletion are not possible with this module. For that use M(community.general.spectrum_device) instead.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  url:
    description:
      - URL of OneClick server.
    type: str
    required: true
  url_username:
    description:
      - OneClick username.
    type: str
    required: true
    aliases: [username]
  url_password:
    description:
      - OneClick password.
    type: str
    required: true
    aliases: [password]
  use_proxy:
    description:
      - If V(false), it does not use a proxy, even if one is defined in an environment variable on the target hosts.
    default: true
    required: false
    type: bool
  name:
    description:
      - Model name.
    type: str
    required: true
  type:
    description:
      - Model type.
    type: str
    required: true
  validate_certs:
    description:
      - Validate SSL certificates. Only change this to V(false) if you can guarantee that you are talking to the correct endpoint
        and there is no man-in-the-middle attack happening.
    type: bool
    default: true
    required: false
  attributes:
    description:
      - A list of attribute names and values to enforce.
      - All values and parameters are case sensitive and must be provided as strings only.
    required: true
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Attribute name OR hex ID.
          - 'Currently defined names are:'
          - C(App_Manufacturer) (C(0x230683));
          - C(CollectionsModelNameString) (C(0x12adb));
          - C(Condition) (C(0x1000a));
          - C(Criticality) (C(0x1290c));
          - C(DeviceType) (C(0x23000e));
          - C(isManaged) (C(0x1295d));
          - C(Model_Class) (C(0x11ee8));
          - C(Model_Handle) (C(0x129fa));
          - C(Model_Name) (C(0x1006e));
          - C(Modeltype_Handle) (C(0x10001));
          - C(Modeltype_Name) (C(0x10000));
          - C(Network_Address) (C(0x12d7f));
          - C(Notes) (C(0x11564));
          - C(ServiceDesk_Asset_ID) (C(0x12db9));
          - C(TopologyModelNameString) (C(0x129e7));
          - C(sysDescr) (C(0x10052));
          - C(sysName) (C(0x10b5b));
          - C(Vendor_Name) (C(0x11570));
          - C(Description) (C(0x230017)).
          - Hex IDs are the direct identifiers in Spectrum and always work.
          - 'To lookup hex IDs go to the UI: Locator -> Devices -> By Model Name -> <enter any model> -> Attributes tab.'
        type: str
        required: true
      value:
        description:
          - Attribute value. Empty strings should be V("") or V(null).
        type: str
        required: true
"""

EXAMPLES = r"""
- name: Enforce maintenance mode for modelxyz01 with a note about why
  community.general.spectrum_model_attrs:
    url: "http://oneclick.url.com"
    username: "{{ oneclick_username }}"
    password: "{{ oneclick_password }}"
    name: "modelxyz01"
    type: "Host_Device"
    validate_certs: true
    attributes:
      - name: "isManaged"
        value: "false"
      - name: "Notes"
        value: >-
          MM set on {{ ansible_date_time.iso8601 }} via CO {{ CO }}
          by {{ tower_user_name | default(ansible_user_id) }}
  delegate_to: localhost
  register: spectrum_model_attrs_status
"""

RETURN = r"""
msg:
  description: Informational message on the job result.
  type: str
  returned: always
  sample: 'Success'
changed_attrs:
  description: Dictionary of changed name or hex IDs (whichever was specified) to their new corresponding values.
  type: dict
  returned: always
  sample: {"Notes": "MM set on 2021-02-03T22:04:02Z via CO CO9999 by tgates", "isManaged": "true"}
"""


from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.six.moves.urllib.parse import quote
import json
import re
import xml.etree.ElementTree as ET


class spectrum_model_attrs:
    def __init__(self, module):
        self.module = module
        self.url = module.params['url']
        # If the user did not define a full path to the restul space in url:
        # params, add what we believe it to be.
        if not re.search('\\/.+', self.url.split('://')[1]):
            self.url = "%s/spectrum/restful" % self.url.rstrip('/')
        # Align these with what is defined in OneClick's UI under:
        # Locator -> Devices -> By Model Name -> <enter any model> ->
        #    Attributes tab.
        self.attr_map = dict(App_Manufacturer=hex(0x230683),
                             CollectionsModelNameString=hex(0x12adb),
                             Condition=hex(0x1000a),
                             Criticality=hex(0x1290c),
                             DeviceType=hex(0x23000e),
                             isManaged=hex(0x1295d),
                             Model_Class=hex(0x11ee8),
                             Model_Handle=hex(0x129fa),
                             Model_Name=hex(0x1006e),
                             Modeltype_Handle=hex(0x10001),
                             Modeltype_Name=hex(0x10000),
                             Network_Address=hex(0x12d7f),
                             Notes=hex(0x11564),
                             ServiceDesk_Asset_ID=hex(0x12db9),
                             TopologyModelNameString=hex(0x129e7),
                             sysDescr=hex(0x10052),
                             sysName=hex(0x10b5b),
                             Vendor_Name=hex(0x11570),
                             Description=hex(0x230017))
        self.search_qualifiers = [
            "and", "or", "not", "greater-than", "greater-than-or-equals",
            "less-than", "less-than-or-equals", "equals", "equals-ignore-case",
            "does-not-equal", "does-not-equal-ignore-case", "has-prefix",
            "does-not-have-prefix", "has-prefix-ignore-case",
            "does-not-have-prefix-ignore-case", "has-substring",
            "does-not-have-substring", "has-substring-ignore-case",
            "does-not-have-substring-ignore-case", "has-suffix",
            "does-not-have-suffix", "has-suffix-ignore-case",
            "does-not-have-suffix-ignore-case", "has-pcre",
            "has-pcre-ignore-case", "has-wildcard", "has-wildcard-ignore-case",
            "is-derived-from", "not-is-derived-from"]

        self.resp_namespace = dict(ca="http://www.ca.com/spectrum/restful/schema/response")

        self.result = dict(msg="", changed_attrs=dict())
        self.success_msg = "Success"

    def build_url(self, path):
        """
        Build a sane Spectrum restful API URL
        :param path: The path to append to the restful base
        :type path: str
        :returns: Complete restful API URL
        :rtype: str
        """

        return "%s/%s" % (self.url.rstrip('/'), path.lstrip('/'))

    def attr_id(self, name):
        """
        Get attribute hex ID
        :param name: The name of the attribute to retrieve the hex ID for
        :type name: str
        :returns: Translated hex ID of name, or None if no translation found
        :rtype: str or None
        """

        try:
            return self.attr_map[name]
        except KeyError:
            return None

    def attr_name(self, _id):
        """
        Get attribute name from hex ID
        :param _id: The hex ID to lookup a name for
        :type _id: str
        :returns: Translated name of hex ID, or None if no translation found
        :rtype: str or None
        """

        for name, m_id in list(self.attr_map.items()):
            if _id == m_id:
                return name
        return None

    def urlencode(self, string):
        """
        URL Encode a string
        :param: string: The string to URL encode
        :type string: str
        :returns: URL encode version of supplied string
        :rtype: str
        """

        return quote(string, "<>%-_.!*'():?#/@&+,;=")

    def update_model(self, model_handle, attrs):
        """
        Update a model's attributes
        :param model_handle: The model's handle ID
        :type model_handle: str
        :param attrs: Model's attributes to update. {'<name/id>': '<attr>'}
        :type attrs: dict
        :returns: Nothing; exits on error or updates self.results
        :rtype: None
        """

        # Build the update URL
        update_url = self.build_url("/model/%s?" % model_handle)
        for name, val in list(attrs.items()):
            if val is None:
                # None values should be converted to empty strings
                val = ""
            val = self.urlencode(str(val))
            if not update_url.endswith('?'):
                update_url += "&"

            update_url += "attr=%s&val=%s" % (self.attr_id(name) or name, val)

        # POST to /model to update the attributes, or fail.
        resp, info = fetch_url(self.module, update_url, method="PUT",
                               headers={"Content-Type": "application/json",
                                        "Accept": "application/json"},
                               use_proxy=self.module.params['use_proxy'])
        status_code = info["status"]
        if status_code >= 400:
            body = info['body']
        else:
            body = "" if resp is None else resp.read()
        if status_code != 200:
            self.result['msg'] = "HTTP PUT error %s: %s: %s" % (status_code, update_url, body)
            self.module.fail_json(**self.result)

        # Load and parse the JSON response and either fail or set results.
        json_resp = json.loads(body)
        """
        Example success response:
        {'model-update-response-list':{'model-responses':{'model':{'@error':'Success','@mh':'0x1010e76','attribute':{'@error':'Success','@id':'0x1295d'}}}}}"
        Example failure response:
        {'model-update-response-list': {'model-responses': {'model': {'@error': 'PartialFailure', '@mh': '0x1010e76', 'attribute': {'@error-message': 'brn0vlappua001: You do not have permission to set attribute Network_Address for this model.', '@error': 'Error', '@id': '0x12d7f'}}}}}
        """  # noqa
        model_resp = json_resp['model-update-response-list']['model-responses']['model']
        if model_resp['@error'] != "Success":
            # I'm not 100% confident on the expected failure structure so just
            # dump all of ['attribute'].
            self.result['msg'] = str(model_resp['attribute'])
            self.module.fail_json(**self.result)

        # Should be OK if we get to here, set results.
        self.result['msg'] = self.success_msg
        self.result['changed_attrs'].update(attrs)
        self.result['changed'] = True

    def find_model(self, search_criteria, ret_attrs=None):
        """
        Search for a model in /models
        :param search_criteria: The XML <rs:search-criteria>
        :type search_criteria: str
        :param ret_attrs: List of attributes by name or ID to return back
            (default is Model_Handle)
        :type ret_attrs: list
        returns: Dictionary mapping of ret_attrs to values: {ret_attr: ret_val}
        rtype: dict
        """

        # If no return attributes were asked for, return Model_Handle.
        if ret_attrs is None:
            ret_attrs = ['Model_Handle']

        # Set the XML <rs:requested-attribute id=<id>> tags. If no hex ID
        # is found for the name, assume it is already in hex. {name: hex ID}
        rqstd_attrs = ""
        for ra in ret_attrs:
            _id = self.attr_id(ra) or ra
            rqstd_attrs += '<rs:requested-attribute id="%s" />' % (self.attr_id(ra) or ra)

        # Build the complete XML search query for HTTP POST.
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<rs:model-request throttlesize="5"
xmlns:rs="http://www.ca.com/spectrum/restful/schema/request"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://www.ca.com/spectrum/restful/schema/request ../../../xsd/Request.xsd">
    <rs:target-models>
        <rs:models-search>
            <rs:search-criteria xmlns="http://www.ca.com/spectrum/restful/schema/filter">
                {0}
            </rs:search-criteria>
        </rs:models-search>
    </rs:target-models>
 {1}
 </rs:model-request>
""".format(search_criteria, rqstd_attrs)

        # POST to /models and fail on errors.
        url = self.build_url("/models")
        resp, info = fetch_url(self.module, url, data=xml, method="POST",
                               use_proxy=self.module.params['use_proxy'],
                               headers={"Content-Type": "application/xml",
                                        "Accept": "application/xml"})
        status_code = info["status"]
        if status_code >= 400:
            body = info['body']
        else:
            body = "" if resp is None else resp.read()
        if status_code != 200:
            self.result['msg'] = "HTTP POST error %s: %s: %s" % (status_code, url, body)
            self.module.fail_json(**self.result)

        # Parse through the XML response and fail on any detected errors.
        root = ET.fromstring(body)
        total_models = int(root.attrib['total-models'])
        error = root.attrib['error']
        model_responses = root.find('ca:model-responses', self.resp_namespace)
        if total_models < 1:
            self.result['msg'] = "No models found matching search criteria `%s'" % search_criteria
            self.module.fail_json(**self.result)
        elif total_models > 1:
            self.result['msg'] = "More than one model found (%s): `%s'" % (total_models, ET.tostring(model_responses,
                                                                                                     encoding='unicode'))
            self.module.fail_json(**self.result)
        if error != "EndOfResults":
            self.result['msg'] = "Unexpected search response `%s': %s" % (error, ET.tostring(model_responses,
                                                                                             encoding='unicode'))
            self.module.fail_json(**self.result)
        model = model_responses.find('ca:model', self.resp_namespace)
        attrs = model.findall('ca:attribute', self.resp_namespace)
        if not attrs:
            self.result['msg'] = "No attributes returned."
            self.module.fail_json(**self.result)

        # XML response should be successful. Iterate and set each returned
        # attribute ID/name and value for return.
        ret = dict()
        for attr in attrs:
            attr_id = attr.get('id')
            attr_name = self.attr_name(attr_id)
            # Note: all values except empty strings (None) are strings only!
            attr_val = attr.text
            key = attr_name if attr_name in ret_attrs else attr_id
            ret[key] = attr_val
            ret_attrs.remove(key)
        return ret

    def find_model_by_name_type(self, mname, mtype, ret_attrs=None):
        """
        Find a model by name and type
        :param mname: Model name
        :type mname: str
        :param mtype: Model type
        :type mtype: str
        :param ret_attrs: List of attributes by name or ID to return back
            (default is Model_Handle)
        :type ret_attrs: list
        returns: find_model(): Dictionary mapping of ret_attrs to values:
            {ret_attr: ret_val}
        rtype: dict
        """

        # If no return attributes were asked for, return Model_Handle.
        if ret_attrs is None:
            ret_attrs = ['Model_Handle']

        """This is basically as follows:
        <filtered-models>
            <and>
                <equals>
                    <attribute id=...>
                        <value>...</value>
                    </attribute>
                </equals>
                <equals>
                    <attribute...>
                </equals>
            </and>
        </filtered-models>
        """

        # Parent filter tag
        filtered_models = ET.Element('filtered-models')
        # Logically and
        _and = ET.SubElement(filtered_models, 'and')

        # Model Name
        MN_equals = ET.SubElement(_and, 'equals')
        Model_Name = ET.SubElement(MN_equals, 'attribute',
                                   {'id': self.attr_map['Model_Name']})
        MN_value = ET.SubElement(Model_Name, 'value')
        MN_value.text = mname

        # Model Type Name
        MTN_equals = ET.SubElement(_and, 'equals')
        Modeltype_Name = ET.SubElement(MTN_equals, 'attribute',
                                       {'id': self.attr_map['Modeltype_Name']})
        MTN_value = ET.SubElement(Modeltype_Name, 'value')
        MTN_value.text = mtype

        return self.find_model(ET.tostring(filtered_models,
                                           encoding='unicode'),
                               ret_attrs)

    def ensure_model_attrs(self):

        # Get a list of all requested attribute names/IDs plus Model_Handle and
        # use them to query the values currently set. Store finding in a
        # dictionary.
        req_attrs = []
        for attr in self.module.params['attributes']:
            req_attrs.append(attr['name'])
        if 'Model_Handle' not in req_attrs:
            req_attrs.append('Model_Handle')

        # Survey attributes currently set and store in a dict.
        cur_attrs = self.find_model_by_name_type(self.module.params['name'],
                                                 self.module.params['type'],
                                                 req_attrs)

        # Iterate through the requested attributes names/IDs values pair and
        # compare with those currently set. If different, attempt to change.
        Model_Handle = cur_attrs.pop("Model_Handle")
        for attr in self.module.params['attributes']:
            req_name = attr['name']
            req_val = attr['value']
            if req_val == "":
                # The API will return None on empty string
                req_val = None
            if cur_attrs[req_name] != req_val:
                if self.module.check_mode:
                    self.result['changed_attrs'][req_name] = req_val
                    self.result['msg'] = self.success_msg
                    self.result['changed'] = True
                    continue
                resp = self.update_model(Model_Handle, {req_name: req_val})

        self.module.exit_json(**self.result)


def run_module():
    argument_spec = dict(
        url=dict(type='str', required=True),
        url_username=dict(type='str', required=True, aliases=['username']),
        url_password=dict(type='str', required=True, aliases=['password'],
                          no_log=True),
        validate_certs=dict(type='bool', default=True),
        use_proxy=dict(type='bool', default=True),
        name=dict(type='str', required=True),
        type=dict(type='str', required=True),
        attributes=dict(type='list',
                        required=True,
                        elements='dict',
                        options=dict(
                             name=dict(type='str', required=True),
                             value=dict(type='str', required=True)
                        )),
    )
    module = AnsibleModule(
        supports_check_mode=True,
        argument_spec=argument_spec,
    )

    try:
        sm = spectrum_model_attrs(module)
        sm.ensure_model_attrs()
    except Exception as e:
        module.fail_json(msg="Failed to ensure attribute(s) on `%s' with "
                             "exception: %s" % (module.params['name'],
                                                to_native(e)))


def main():
    run_module()


if __name__ == "__main__":
    main()

#!/usr/bin/python

# Copyright (c) 2014, Red Hat, Inc.
# Copyright (c) 2014, Tim Bielawa <tbielawa@redhat.com>
# Copyright (c) 2014, Magnus Hedemark <mhedemar@redhat.com>
# Copyright (c) 2017, Dag Wieers <dag@wieers.com>
# Copyright (c) 2026, Shreyash Bhosale <shreyashpb16@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: xml_info
short_description: Query XML files or strings
description:
  - A read-only interface to query XML files or strings using XPath expressions.
  - Supports counting matches, listing matched XPath paths, and retrieving element text or attributes.
version_added: "13.1.0"
extends_documentation_fragment:
  - community.general._attributes
  - community.general._attributes.info_module
  - community.general._xml
options:
  xpath:
    required: true
  count:
    description:
      - Search for a given O(xpath) and provide the count of any matches.
      - This parameter requires O(xpath) to be set.
    type: bool
    default: false
  print_match:
    description:
      - Search for a given O(xpath) and return the XPath paths of any matches.
      - This parameter requires O(xpath) to be set.
    type: bool
    default: false
  content:
    description:
      - Search for a given O(xpath) and get content.
      - If V(attribute), return the attributes of matched elements.
      - If V(text), return the text content of matched elements.
    type: str
    choices: [attribute, text]
seealso:
  - module: community.general.xml
    description: Manage bits and pieces of XML files or strings.
  - name: Introduction to XPath
    description: A brief tutorial on XPath (w3schools.com).
    link: https://www.w3schools.com/xml/xpath_intro.asp
  - name: XPath Reference document
    description: The reference documentation on XSLT/XPath (developer.mozilla.org).
    link: https://developer.mozilla.org/en-US/docs/Web/XPath
author:
  - Tim Bielawa (@tbielawa)
  - Magnus Hedemark (@magnus919)
  - Dag Wieers (@dagwieers)
  - Shreyash Bhosale (@Shreyashxredhat)
"""

EXAMPLES = r"""
# Consider the following XML file:
#
# <business type="bar">
#   <name>Tasty Beverage Co.</name>
#     <beers>
#       <beer>Rochefort 10</beer>
#       <beer>St. Bernardus Abbot 12</beer>
#       <beer>Schlitz</beer>
#    </beers>
#   <rating subjective="true">10</rating>
#   <website>
#     <mobilefriendly/>
#     <address>https://tastybeverageco.com</address>
#   </website>
# </business>

# Retrieve and display the number of nodes
- name: Get count of 'beers' nodes
  community.general.xml_info:
    path: /foo/bar.xml
    xpath: /business/beers/beer
    count: true
  register: hits

- ansible.builtin.debug:
    var: hits.count

# Retrieve and display the matching XPath paths
- name: Get matching paths for 'beer' nodes
  community.general.xml_info:
    path: /foo/bar.xml
    xpath: /business/beers/beer
    print_match: true
  register: hits

- ansible.builtin.debug:
    var: hits.matches

# How to read an attribute value and access it in Ansible
- name: Read an element's attribute values
  community.general.xml_info:
    path: /foo/bar.xml
    xpath: /business/rating
    content: attribute
  register: xmlresp

- name: Show an attribute value
  ansible.builtin.debug:
    var: xmlresp.matches[0].rating.subjective

# How to read text content
- name: Read an element's text content
  community.general.xml_info:
    path: /foo/bar.xml
    xpath: /business/rating
    content: text
  register: xmlresp

- name: Show text content
  ansible.builtin.debug:
    var: xmlresp.matches[0].rating

# Using an XML string instead of a file
- name: Count nodes in an XML string
  community.general.xml_info:
    xmlstring: "<config><item>1</item><item>2</item></config>"
    xpath: /config/item
    count: true
  register: hits

# Using namespaces
- name: Count nodes in a namespaced XML file
  community.general.xml_info:
    path: /foo/bar.xml
    xpath: /x:foo/x:bar/y:baz
    namespaces:
      x: http://x.test
      y: http://y.test
    count: true
  register: hits
"""

RETURN = r"""
count:
  description: The count of xpath matches.
  type: int
  returned: when parameter O(count) is set
  sample: 2
matches:
  description: The xpath matches found.
  type: list
  returned: when parameter O(print_match) or O(content) is set
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.community.general.plugins.module_utils._xml import (
    check_lxml,
    collect_element_attr,
    collect_element_text,
    count_matches,
    get_common_argument_spec,
    get_matches,
    parse_xml_doc,
    validate_xpath,
)


def main():
    argument_spec = get_common_argument_spec(xpath_required=True)
    argument_spec.update(
        count=dict(type="bool", default=False),
        print_match=dict(type="bool", default=False),
        content=dict(type="str", choices=["attribute", "text"]),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[
            ["path", "xmlstring"],
            ["count", "print_match", "content"],
        ],
        mutually_exclusive=[
            ["count", "print_match", "content"],
            ["path", "xmlstring"],
        ],
    )

    xml_file = module.params["path"]
    xml_string = module.params["xmlstring"]
    xpath = module.params["xpath"]
    namespaces = module.params["namespaces"]
    content = module.params["content"]
    print_match = module.params["print_match"]
    count = module.params["count"]
    strip_cdata_tags = module.params["strip_cdata_tags"]
    huge_tree = module.params["huge_tree"]

    check_lxml(module)
    validate_xpath(module, xpath)
    doc = parse_xml_doc(
        module,
        xml_file=xml_file,
        xml_string=xml_string,
        strip_cdata_tags=strip_cdata_tags,
        huge_tree=huge_tree,
        resolve_entities=False,
    )

    if print_match:
        result = get_matches(doc, xpath, namespaces)
        module.exit_json(**result)

    if count:
        result = count_matches(doc, xpath, namespaces)
        module.exit_json(**result)

    if content == "attribute":
        elements = collect_element_attr(doc, xpath, namespaces)
        if elements is None:
            module.fail_json(msg=f"Xpath {xpath} does not reference a node!")
        module.exit_json(count=len(elements), matches=elements)
    elif content == "text":
        elements = collect_element_text(doc, xpath, namespaces)
        if elements is None:
            module.fail_json(msg=f"Xpath {xpath} does not reference a node!")
        module.exit_json(count=len(elements), matches=elements)


if __name__ == "__main__":
    main()

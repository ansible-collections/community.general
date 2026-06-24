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
  what:
    description:
      - Select what kind of information to return for the given O(xpath).
    required: true
    type: str
    choices:
      count: Returns the number of matches as RV(count).
      paths: Return the XPath paths for all matched elements as RV(matches).
      content_text: Return the text content of the matched elements as RV(matches).
      content_attributes: Return the attributes of the matched elements as RV(matches).
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
    what: count
  register: hits

- name: Show count
  ansible.builtin.debug:
    var: hits.count

# Retrieve and display the matching XPath paths
- name: Get matching paths for 'beer' nodes
  community.general.xml_info:
    path: /foo/bar.xml
    xpath: /business/beers/beer
    what: paths
  register: hits

- name: Show matching paths
  ansible.builtin.debug:
    var: hits.matches

# How to read attribute values and access them in Ansible
- name: Read an element's attribute values
  community.general.xml_info:
    path: /foo/bar.xml
    xpath: /business/rating
    what: content_attributes
  register: xmlresp

- name: Show an attribute value
  ansible.builtin.debug:
    var: xmlresp.matches[0].attributes.subjective

# How to read text content
- name: Read an element's text content
  community.general.xml_info:
    path: /foo/bar.xml
    xpath: /business/rating
    what: content_text
  register: xmlresp

- name: Show text content
  ansible.builtin.debug:
    var: xmlresp.matches[0].text

# Using an XML string instead of a file
- name: Count nodes in an XML string
  community.general.xml_info:
    xmlstring: "<config><item>1</item><item>2</item></config>"
    xpath: /config/item
    what: count
  register: hits

# Using namespaces
- name: Count nodes in a namespaced XML file
  community.general.xml_info:
    path: /foo/bar.xml
    xpath: /x:foo/x:bar/y:baz
    namespaces:
      x: http://x.test
      y: http://y.test
    what: count
  register: hits
"""

RETURN = r"""
count:
  description: The count of xpath matches.
  type: int
  returned: always
  sample: 2
matches:
  description:
    - The xpath matches found.
    - When O(what=paths), each element is a string with the XPath path to the matched node.
    - When O(what=content_text) or O(what=content_attributes), each element is a dictionary
      with the fields documented below.
  type: list
  returned: when O(what) is V(paths), V(content_text), or V(content_attributes)
  sample:
    - tag: beer
      text: Rochefort 10
  contains:
    tag:
      description: The tag name of the matched element.
      type: str
      returned: when O(what=content_text) or O(what=content_attributes)
    text:
      description: The text content of the matched element.
      type: str
      returned: when O(what=content_text)
    attributes:
      description: The attributes of the matched element as key-value pairs.
      type: dict
      returned: when O(what=content_attributes)
"""

import typing as t

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


def main() -> None:
    argument_spec = get_common_argument_spec(xpath_required=True)
    argument_spec.update(
        what=dict(type="str", required=True, choices=["count", "paths", "content_text", "content_attributes"]),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[
            ["path", "xmlstring"],
        ],
        mutually_exclusive=[
            ["path", "xmlstring"],
        ],
    )

    xml_file = module.params["path"]
    xml_string = module.params["xmlstring"]
    xpath = module.params["xpath"]
    namespaces = module.params["namespaces"]
    what: t.Literal["count", "paths", "content_text", "content_attributes"] = module.params["what"]
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

    if what == "count":
        hits, _msg = count_matches(doc, xpath, namespaces)
        module.exit_json(count=hits)

    if what == "paths":
        match_xpaths, _msg = get_matches(doc, xpath, namespaces)
        module.exit_json(count=len(match_xpaths), matches=match_xpaths)

    if what == "content_text":
        raw = collect_element_text(doc, xpath, namespaces)
        if raw is None:
            module.fail_json(msg=f"Xpath {xpath} does not reference a node!")
        matches = [{"tag": tag, "text": text} for tag, text in raw]
        module.exit_json(count=len(matches), matches=matches)

    if what == "content_attributes":
        raw = collect_element_attr(doc, xpath, namespaces)
        if raw is None:
            module.fail_json(msg=f"Xpath {xpath} does not reference a node!")
        matches = [{"tag": tag, "attributes": attribs} for tag, attribs in raw]
        module.exit_json(count=len(matches), matches=matches)


if __name__ == "__main__":
    main()

# Copyright (c) 2014, Red Hat, Inc.
# Copyright (c) 2014, Tim Bielawa <tbielawa@redhat.com>
# Copyright (c) 2014, Magnus Hedemark <mhedemar@redhat.com>
# Copyright (c) 2017, Dag Wieers <dag@wieers.com>
# Copyright (c) 2026, Shreyash Bhosale <shreyashpb16@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Note that this module util is **PRIVATE** to the collection. It can have breaking changes at any time.
# Do not use this from other collections or standalone plugins/modules!

from __future__ import annotations

import json
import os
import typing as t
from io import BytesIO

from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.community.general.plugins.module_utils import _deps as deps
from ansible_collections.community.general.plugins.module_utils._version import LooseVersion

if t.TYPE_CHECKING:
    from ansible.module_utils.basic import AnsibleModule

with deps.declare("lxml"):
    from lxml import etree


def get_common_argument_spec(*, xpath_required: bool = False) -> dict[str, dict[str, t.Any]]:
    """Return the argument spec shared by xml and xml_info modules."""
    return dict(
        path=dict(type="path", aliases=["dest", "file"]),
        xmlstring=dict(type="str"),
        xpath=dict(type="str", required=xpath_required),
        namespaces=dict(type="dict", default={}),
        strip_cdata_tags=dict(type="bool", default=False),
        huge_tree=dict(type="bool", default=False),
    )


def check_lxml(module: AnsibleModule) -> None:
    deps.validate(module, "lxml")
    version_str = ".".join(str(f) for f in etree.LXML_VERSION)
    if LooseVersion(version_str) < LooseVersion("2.3.0"):
        module.fail_json(msg="The xml ansible module requires lxml 2.3.0 or newer installed on the managed machine")
    elif LooseVersion(version_str) < LooseVersion("3.0.0"):
        module.warn("Using lxml version lower than 3.0.0 does not guarantee predictable element attribute order.")


def validate_xpath(module: AnsibleModule, xpath: str) -> None:
    try:
        etree.XPath(xpath)
    except etree.XPathSyntaxError as e:
        module.fail_json(msg=f"Syntax error in xpath expression: {xpath} ({e})")
    except etree.XPathEvalError as e:
        module.fail_json(msg=f"Evaluation error in xpath expression: {xpath} ({e})")


def parse_xml_doc(
    module: AnsibleModule,
    xml_file: str | None = None,
    xml_string: str | None = None,
    strip_cdata_tags: bool = False,
    huge_tree: bool = False,
    remove_blank_text: bool = False,
    resolve_entities: bool = True,
) -> etree._ElementTree:
    infile: t.IO[bytes] | None = None
    try:
        if xml_string:
            infile = BytesIO(to_bytes(xml_string, errors="surrogate_or_strict"))
        elif xml_file:
            if not os.path.isfile(xml_file):
                module.fail_json(msg=f"The target XML source '{xml_file}' does not exist.")
            if not os.access(xml_file, os.R_OK):
                module.fail_json(msg=f"The target XML source '{xml_file}' is not readable.")
            infile = open(xml_file, "rb")  # noqa: SIM115
        else:
            module.fail_json(msg="No XML source provided; specify 'path' or 'xmlstring'.")

        parser = etree.XMLParser(
            remove_blank_text=remove_blank_text,
            strip_cdata=strip_cdata_tags,
            huge_tree=huge_tree,
            resolve_entities=resolve_entities,
        )
        doc = etree.parse(infile, parser)
    except etree.XMLSyntaxError as e:
        module.fail_json(msg=f"Error while parsing document: {xml_file or 'xml_string'} ({e})")
    except OSError as e:
        module.fail_json(msg=f"Error reading XML source: {xml_file or 'xml_string'} ({e})")
    finally:
        if infile:
            infile.close()

    return doc


def xpath_matches(tree: t.Any, xpath: str, namespaces: dict[str, str]) -> bool:
    """Test if a node exists."""
    return bool(tree.xpath(xpath, namespaces=namespaces))


def is_node(tree: t.Any, xpath: str, namespaces: dict[str, str]) -> bool:
    """Test if a given xpath matches anything and if that match is a node."""
    match = tree.xpath(xpath, namespaces=namespaces)
    return bool(match) and isinstance(match[0], etree._Element)


def get_matches(tree: t.Any, xpath: str, namespaces: dict[str, str]) -> tuple[list[str], str]:
    """Return matched XPath paths as (match_xpaths, message)."""
    match = tree.xpath(xpath, namespaces=namespaces)
    match_xpaths: list[str] = [tree.getpath(m) for m in match]
    match_str = json.dumps(match_xpaths)
    msg = f"selector '{xpath}' match: {match_str}"
    return match_xpaths, msg


def count_matches(tree: t.Any, xpath: str, namespaces: dict[str, str], *, count_mode: str = "match") -> tuple[int, str]:
    """Return the count of nodes matching the xpath as (count, message).

    When count_mode is "xpath", uses the XPath count() function for better memory efficiency.
    When count_mode is "match" (default), evaluates the expression and counts with len().
    """
    if count_mode == "xpath":
        hits = int(tree.xpath(f"count({xpath})", namespaces=namespaces))
    else:
        hits = len(tree.xpath(xpath, namespaces=namespaces))
    msg = f"found {hits} nodes"
    return hits, msg


def collect_element_text(tree: t.Any, xpath: str, namespaces: dict[str, str]) -> list[tuple[str, str | None]] | None:
    """Get text content of matched elements as (tag, text) tuples. Returns None if xpath does not match a node."""
    match = tree.xpath(xpath, namespaces=namespaces)
    if not match or not isinstance(match[0], etree._Element):
        return None
    return [(element.tag, element.text) for element in match]


def collect_element_attr(
    tree: t.Any, xpath: str, namespaces: dict[str, str]
) -> list[tuple[str, dict[str, str]]] | None:
    """Get attributes of matched elements as (tag, attributes) tuples. Returns None if xpath does not match a node."""
    match = tree.xpath(xpath, namespaces=namespaces)
    if not match or not isinstance(match[0], etree._Element):
        return None
    return [(element.tag, dict(element.attrib)) for element in match]

# -*- coding: utf-8 -*-
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

DOCUMENTATION = r"""
author: Unknown (!UNKNOWN)
name: yaml
type: stdout
short_description: YAML-ized Ansible screen output
deprecated:
  removed_in: 12.0.0
  why: Starting in ansible-core 2.13, the P(ansible.builtin.default#callback) callback has support for printing output in
    YAML format.
  alternative: Use O(ansible.builtin.default#callback:result_format=yaml).
description:
  - Ansible output that can be quite a bit easier to read than the default JSON formatting.
extends_documentation_fragment:
  - default_callback
requirements:
  - set as stdout in configuration
seealso:
  - plugin: ansible.builtin.default
    plugin_type: callback
    description: >-
      There is a parameter O(ansible.builtin.default#callback:result_format) in P(ansible.builtin.default#callback) that allows
      you to change the output format to YAML.
notes:
  - With ansible-core 2.13 or newer, you can instead specify V(yaml) for the parameter O(ansible.builtin.default#callback:result_format)
    in P(ansible.builtin.default#callback).
"""

import yaml
import json
import re
import string
from collections.abc import Mapping, Sequence

from ansible.module_utils.common.text.converters import to_text
from ansible.plugins.callback import strip_internal_keys, module_response_deepcopy
from ansible.plugins.callback.default import CallbackModule as Default


# from http://stackoverflow.com/a/15423007/115478
def should_use_block(value):
    """Returns true if string should be in block format"""
    for c in "\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
        if c in value:
            return True
    return False


def adjust_str_value_for_block(value):
    # we care more about readable than accuracy, so...
    # ...no trailing space
    value = value.rstrip()
    # ...and non-printable characters
    value = ''.join(x for x in value if x in string.printable or ord(x) >= 0xA0)
    # ...tabs prevent blocks from expanding
    value = value.expandtabs()
    # ...and odd bits of whitespace
    value = re.sub(r'[\x0b\x0c\r]', '', value)
    # ...as does trailing space
    value = re.sub(r' +\n', '\n', value)
    return value


def create_string_node(tag, value, style, default_style):
    if style is None:
        if should_use_block(value):
            style = '|'
            value = adjust_str_value_for_block(value)
        else:
            style = default_style
    return yaml.representer.ScalarNode(tag, value, style=style)


try:
    from ansible.module_utils.common.yaml import HAS_LIBYAML
    # import below was added in https://github.com/ansible/ansible/pull/85039,
    # first contained in ansible-core 2.19.0b2:
    from ansible.utils.vars import transform_to_native_types

    if HAS_LIBYAML:
        from yaml.cyaml import CSafeDumper as SafeDumper
    else:
        from yaml import SafeDumper

    class MyDumper(SafeDumper):
        def represent_scalar(self, tag, value, style=None):
            """Uses block style for multi-line strings"""
            node = create_string_node(tag, value, style, self.default_style)
            if self.alias_key is not None:
                self.represented_objects[self.alias_key] = node
            return node

except ImportError:
    # In case transform_to_native_types cannot be imported, we either have ansible-core 2.19.0b1
    # (or some random commit from the devel or stable-2.19 branch after merging the DT changes
    # and before transform_to_native_types was added), or we have a version without the DT changes.

    # Here we simply assume we have a version without the DT changes, and thus can continue as
    # with ansible-core 2.18 and before.

    transform_to_native_types = None

    from ansible.parsing.yaml.dumper import AnsibleDumper

    class MyDumper(AnsibleDumper):  # pylint: disable=inherit-non-class
        def represent_scalar(self, tag, value, style=None):
            """Uses block style for multi-line strings"""
            node = create_string_node(tag, value, style, self.default_style)
            if self.alias_key is not None:
                self.represented_objects[self.alias_key] = node
            return node


def transform_recursively(value, transform):
    # Since 2.19.0b7, this should no longer be needed:
    # https://github.com/ansible/ansible/issues/85325
    # https://github.com/ansible/ansible/pull/85389
    if isinstance(value, Mapping):
        return {transform(k): transform(v) for k, v in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [transform(e) for e in value]
    return transform(value)


class CallbackModule(Default):

    """
    Variation of the Default output which uses nicely readable YAML instead
    of JSON for printing results.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'community.general.yaml'

    def __init__(self):
        super(CallbackModule, self).__init__()

    def _dump_results(self, result, indent=None, sort_keys=True, keep_invocation=False):
        if result.get('_ansible_no_log', False):
            return json.dumps(dict(censored="The output has been hidden due to the fact that 'no_log: true' was specified for this result"))

        # All result keys stating with _ansible_ are internal, so remove them from the result before we output anything.
        abridged_result = strip_internal_keys(module_response_deepcopy(result))

        # remove invocation unless specifically wanting it
        if not keep_invocation and self._display.verbosity < 3 and 'invocation' in result:
            del abridged_result['invocation']

        # remove diff information from screen output
        if self._display.verbosity < 3 and 'diff' in result:
            del abridged_result['diff']

        # remove exception from screen output
        if 'exception' in abridged_result:
            del abridged_result['exception']

        dumped = ''

        # put changed and skipped into a header line
        if 'changed' in abridged_result:
            dumped += f"changed={str(abridged_result['changed']).lower()} "
            del abridged_result['changed']

        if 'skipped' in abridged_result:
            dumped += f"skipped={str(abridged_result['skipped']).lower()} "
            del abridged_result['skipped']

        # if we already have stdout, we don't need stdout_lines
        if 'stdout' in abridged_result and 'stdout_lines' in abridged_result:
            abridged_result['stdout_lines'] = '<omitted>'

        # if we already have stderr, we don't need stderr_lines
        if 'stderr' in abridged_result and 'stderr_lines' in abridged_result:
            abridged_result['stderr_lines'] = '<omitted>'

        if abridged_result:
            dumped += '\n'
            if transform_to_native_types is not None:
                abridged_result = transform_recursively(abridged_result, lambda v: transform_to_native_types(v, redact=False))
            dumped += to_text(yaml.dump(abridged_result, allow_unicode=True, width=1000, Dumper=MyDumper, default_flow_style=False))

        # indent by a couple of spaces
        dumped = '\n  '.join(dumped.split('\n')).rstrip()
        return dumped

    def _serialize_diff(self, diff):
        return to_text(yaml.dump(diff, allow_unicode=True, width=1000, Dumper=AnsibleDumper, default_flow_style=False))

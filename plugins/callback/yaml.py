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
  removed_in: 13.0.0
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

from ansible.module_utils.common.text.converters import to_text
from ansible.parsing.yaml.dumper import AnsibleDumper
from ansible.plugins.callback import strip_internal_keys, module_response_deepcopy
from ansible.plugins.callback.default import CallbackModule as Default


# from http://stackoverflow.com/a/15423007/115478
def should_use_block(value):
    """Returns true if string should be in block format"""
    for c in "\u000a\u000d\u001c\u001d\u001e\u0085\u2028\u2029":
        if c in value:
            return True
    return False


try:
    class MyDumper(AnsibleDumper):  # pylint: disable=inherit-non-class
        def represent_scalar(self, tag, value, style=None):
            """Uses block style for multi-line strings"""
            if style is None:
                if should_use_block(value):
                    style = '|'
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
                else:
                    style = self.default_style
            node = yaml.representer.ScalarNode(tag, value, style=style)
            if self.alias_key is not None:
                self.represented_objects[self.alias_key] = node
            return node
except:  # noqa: E722, pylint: disable=bare-except
    # This happens with Data Tagging, see https://github.com/ansible/ansible/issues/84781
    # Until there is a better solution we'll resort to using ansible-core internals.
    from ansible._internal._yaml import _dumper
    import typing as t

    class MyDumper(_dumper._BaseDumper):
        # This code is mostly taken from ansible._internal._yaml._dumper
        @classmethod
        def _register_representers(cls) -> None:
            cls.add_multi_representer(_dumper.AnsibleTaggedObject, cls.represent_ansible_tagged_object)
            cls.add_multi_representer(_dumper.Tripwire, cls.represent_tripwire)
            cls.add_multi_representer(_dumper.c.Mapping, _dumper.SafeRepresenter.represent_dict)
            cls.add_multi_representer(_dumper.c.Sequence, _dumper.SafeRepresenter.represent_list)

        def represent_ansible_tagged_object(self, data):
            if ciphertext := _dumper.VaultHelper.get_ciphertext(data, with_tags=False):
                return self.represent_scalar('!vault', ciphertext, style='|')

            return self.represent_data(_dumper.AnsibleTagHelper.as_native_type(data))  # automatically decrypts encrypted strings

        def represent_tripwire(self, data: _dumper.Tripwire) -> t.NoReturn:
            data.trip()

        # The following function is the same as in the try/except
        def represent_scalar(self, tag, value, style=None):
            """Uses block style for multi-line strings"""
            if style is None:
                if should_use_block(value):
                    style = '|'
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
                else:
                    style = self.default_style
            node = yaml.representer.ScalarNode(tag, value, style=style)
            if self.alias_key is not None:
                self.represented_objects[self.alias_key] = node
            return node


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
            dumped += to_text(yaml.dump(abridged_result, allow_unicode=True, width=1000, Dumper=MyDumper, default_flow_style=False))

        # indent by a couple of spaces
        dumped = '\n  '.join(dumped.split('\n')).rstrip()
        return dumped

    def _serialize_diff(self, diff):
        return to_text(yaml.dump(diff, allow_unicode=True, width=1000, Dumper=AnsibleDumper, default_flow_style=False))

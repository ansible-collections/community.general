# Copyright (c) 2023, Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

from ansible.module_utils.six import binary_type, text_type
from ansible.module_utils.common._collections_compat import Mapping, Set
from ansible.module_utils.common.collections import is_sequence
from ansible.utils.unsafe_proxy import (
    AnsibleUnsafe,
    wrap_var as _make_unsafe,
)

_RE_TEMPLATE_CHARS = re.compile(u'[{}]')
_RE_TEMPLATE_CHARS_BYTES = re.compile(b'[{}]')


def make_unsafe(value):
    if value is None or isinstance(value, AnsibleUnsafe):
        return value

    if isinstance(value, Mapping):
        return {make_unsafe(key): make_unsafe(val) for key, val in value.items()}
    elif isinstance(value, Set):
        return set(make_unsafe(elt) for elt in value)
    elif is_sequence(value):
        return type(value)(make_unsafe(elt) for elt in value)
    elif isinstance(value, binary_type):
        if _RE_TEMPLATE_CHARS_BYTES.search(value):
            value = _make_unsafe(value)
        return value
    elif isinstance(value, text_type):
        if _RE_TEMPLATE_CHARS.search(value):
            value = _make_unsafe(value)
        return value

    return value

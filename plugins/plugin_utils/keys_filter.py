# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# Copyright (c) 2024 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

from ansible.errors import AnsibleFilterError
from ansible.module_utils.six import string_types
from ansible.module_utils.common._collections_compat import Mapping, Sequence


def _keys_filter_params(data, matching_parameter):
    """test parameters:
       * data must be a list of dictionaries. All keys must be strings.
       * matching_parameter is member of a list.
    """

    mp = matching_parameter
    ml = ['equal', 'starts_with', 'ends_with', 'regex']

    if not isinstance(data, Sequence):
        msg = "First argument must be a list. %s is %s"
        raise AnsibleFilterError(msg % (data, type(data)))

    for elem in data:
        if not isinstance(elem, Mapping):
            msg = "The data items must be dictionaries. %s is %s"
            raise AnsibleFilterError(msg % (elem, type(elem)))

    for elem in data:
        if not all(isinstance(item, string_types) for item in elem.keys()):
            msg = "Top level keys must be strings. keys: %s"
            raise AnsibleFilterError(msg % elem.keys())

    if mp not in ml:
        msg = "The matching_parameter must be one of %s. matching_parameter=%s"
        raise AnsibleFilterError(msg % (ml, mp))

    return


def _keys_filter_target_str(target, matching_parameter):
    """
       Test:
       * target is a non-empty string or list.
       * If target is list all items are strings.
       * target is a string or list with single string if matching_parameter=regex.
       Convert target and return:
       * tuple of unique target items, or
       * tuple with single item, or
       * compiled regex if matching_parameter=regex.
    """

    if not isinstance(target, Sequence):
        msg = "The target must be a string or a list. target is %s."
        raise AnsibleFilterError(msg % type(target))

    if len(target) == 0:
        msg = "The target can't be empty."
        raise AnsibleFilterError(msg)

    if isinstance(target, list):
        for elem in target:
            if not isinstance(elem, string_types):
                msg = "The target items must be strings. %s is %s"
                raise AnsibleFilterError(msg % (elem, type(elem)))

    if matching_parameter == 'regex':
        if isinstance(target, string_types):
            r = target
        else:
            if len(target) > 1:
                msg = "Single item is required in the target list if matching_parameter=regex."
                raise AnsibleFilterError(msg)
            else:
                r = target[0]
        try:
            tt = re.compile(r)
        except re.error:
            msg = "The target must be a valid regex if matching_parameter=regex. target is %s"
            raise AnsibleFilterError(msg % r)
    elif isinstance(target, string_types):
        tt = (target, )
    else:
        tt = tuple(set(target))

    return tt


def _keys_filter_target_dict(target, matching_parameter):
    """
       Test:
       * target is a list of dictionaries with attributes 'after' and 'before'.
       * Attributes 'before' must be valid regex if matching_parameter=regex.
       * Otherwise, the attributes 'before' must be strings.
       Convert target and return:
       * iterator that aggregates attributes 'before' and 'after', or
       * iterator that aggregates compiled regex of attributes 'before' and 'after' if matching_parameter=regex.
    """

    if not isinstance(target, list):
        msg = "The target must be a list. target is %s."
        raise AnsibleFilterError(msg % (target, type(target)))

    if len(target) == 0:
        msg = "The target can't be empty."
        raise AnsibleFilterError(msg)

    for elem in target:
        if not isinstance(elem, Mapping):
            msg = "The target items must be dictionaries. %s is %s"
            raise AnsibleFilterError(msg % (elem, type(elem)))
        if not all(k in elem for k in ('before', 'after')):
            msg = "All dictionaries in target must include attributes: after, before."
            raise AnsibleFilterError(msg)
        if not isinstance(elem['before'], string_types):
            msg = "The attributes before must be strings. %s is %s"
            raise AnsibleFilterError(msg % (elem['before'], type(elem['before'])))
        if not isinstance(elem['after'], string_types):
            msg = "The attributes after must be strings. %s is %s"
            raise AnsibleFilterError(msg % (elem['after'], type(elem['after'])))

    before = [d['before'] for d in target]
    after = [d['after'] for d in target]

    if matching_parameter == 'regex':
        try:
            tr = map(re.compile, before)
            tz = list(zip(tr, after))
        except re.error:
            msg = ("The attributes before must be valid regex if matching_parameter=regex."
                   " Not all items are valid regex in: %s")
            raise AnsibleFilterError(msg % before)
    else:
        tz = list(zip(before, after))

    return tz

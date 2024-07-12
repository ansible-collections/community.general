# Copyright (c) 2024 Vladimir Botka <vbotka@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError
from ansible.module_utils.common._collections_compat import Mapping


def _atype(data, alias):
    """
    Returns the name of the type class.
    """

    data_type = type(data).__name__
    return alias.get(data_type, data_type)


def _ansible_type(data, alias):
    """
    Returns the Ansible data type.
    """

    if alias is None:
        alias = {}

    if not isinstance(alias, Mapping):
        msg = "The argument alias must be a dictionary. %s is %s"
        raise AnsibleFilterError(msg % (alias, type(alias)))

    data_type = _atype(data, alias)

    if data_type == 'list' and len(data) > 0:
        items = [_atype(i, alias) for i in data]
        items_type = '|'.join(sorted(set(items)))
        return ''.join((data_type, '[', items_type, ']'))

    if data_type == 'dict' and len(data) > 0:
        keys = [_atype(i, alias) for i in data.keys()]
        vals = [_atype(i, alias) for i in data.values()]
        keys_type = '|'.join(sorted(set(keys)))
        vals_type = '|'.join(sorted(set(vals)))
        return ''.join((data_type, '[', keys_type, ', ', vals_type, ']'))

    return data_type

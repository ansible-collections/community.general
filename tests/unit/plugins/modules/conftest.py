# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

import pytest

from ansible.module_utils.six import string_types
from ansible.module_utils.common.text.converters import to_bytes
from ansible.module_utils.common._collections_compat import MutableMapping

from ansible_collections.community.general.plugins.module_utils import deps


def fix_ansible_args(args):
    if isinstance(args, string_types):
        return args

    if isinstance(args, MutableMapping):
        if 'ANSIBLE_MODULE_ARGS' not in args:
            args = {'ANSIBLE_MODULE_ARGS': args}
        if '_ansible_remote_tmp' not in args['ANSIBLE_MODULE_ARGS']:
            args['ANSIBLE_MODULE_ARGS']['_ansible_remote_tmp'] = '/tmp'
        if '_ansible_keep_remote_files' not in args['ANSIBLE_MODULE_ARGS']:
            args['ANSIBLE_MODULE_ARGS']['_ansible_keep_remote_files'] = False
        args = json.dumps(args)
        return args

    else:
        raise Exception('Malformed data to the patch_ansible_module pytest fixture')


@pytest.fixture
def patch_ansible_module(request, mocker):
    if hasattr(request, "param"):
        args = fix_ansible_args(request.param)
        mocker.patch('ansible.module_utils.basic._ANSIBLE_ARGS', to_bytes(args))
    else:
        def _patch(args):
            args = fix_ansible_args(args)
            mocker.patch('ansible.module_utils.basic._ANSIBLE_ARGS', to_bytes(args))
        return _patch


@pytest.fixture(autouse=True)
def deps_cleanup():
    deps._deps.clear()

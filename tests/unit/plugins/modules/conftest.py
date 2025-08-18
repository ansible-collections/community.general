# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import contextlib as _contextlib
import json

import pytest

from ansible.module_utils.six import string_types
from ansible.module_utils.six.moves.collections_abc import MutableMapping

from ansible_collections.community.general.plugins.module_utils import deps
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import set_module_args as _set_module_args


def _fix_ansible_args(args):
    if isinstance(args, string_types):
        # This should be deprecated!
        return json.loads(args)

    if isinstance(args, MutableMapping):
        return args

    raise Exception('Malformed data to the patch_ansible_module pytest fixture')


@pytest.fixture
def patch_ansible_module(request):
    args = _fix_ansible_args(request.param)
    with _set_module_args(args):
        yield


@pytest.fixture
def patch_ansible_module_uthelper(request):
    @_contextlib.contextmanager
    def _patch(args):
        args = _fix_ansible_args(args)
        with _set_module_args(args):
            yield
    return _patch


@pytest.fixture(autouse=True)
def deps_cleanup():
    deps.clear()

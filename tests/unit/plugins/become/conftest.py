# Copyright (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright (c) 2017 Ansible Project
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible.cli.arguments import option_helpers as opt_help
from ansible.utils import context_objects as co


@pytest.fixture
def parser():
    parser = opt_help.create_base_parser('testparser')

    opt_help.add_runas_options(parser)
    opt_help.add_meta_options(parser)
    opt_help.add_runtask_options(parser)
    opt_help.add_vault_options(parser)
    opt_help.add_async_options(parser)
    opt_help.add_connect_options(parser)
    opt_help.add_subset_options(parser)
    opt_help.add_check_options(parser)
    opt_help.add_inventory_options(parser)

    return parser


@pytest.fixture
def reset_cli_args():
    co.GlobalCLIArgs._Singleton__instance = None
    yield
    co.GlobalCLIArgs._Singleton__instance = None

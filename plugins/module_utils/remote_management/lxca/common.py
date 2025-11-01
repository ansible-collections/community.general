# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by
# Ansible still belong to the author of the module, and may assign their
# own license to the complete work.
#
# Copyright (C) 2017 Lenovo, Inc.
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause
#
# Contains LXCA common class
# Lenovo xClarity Administrator (LXCA)

from __future__ import annotations

import traceback

try:
    from pylxca import connect, disconnect

    HAS_PYLXCA = True
except ImportError:
    HAS_PYLXCA = False


PYLXCA_REQUIRED = "Lenovo xClarity Administrator Python Client (Python package 'pylxca') is required for this module."


def has_pylxca(module):
    """
    Check pylxca is installed
    :param module:
    """
    if not HAS_PYLXCA:
        module.fail_json(msg=PYLXCA_REQUIRED)


LXCA_COMMON_ARGS = dict(
    login_user=dict(required=True),
    login_password=dict(required=True, no_log=True),
    auth_url=dict(required=True),
)


class connection_object:
    def __init__(self, module):
        self.module = module

    def __enter__(self):
        return setup_conn(self.module)

    def __exit__(self, type, value, traceback):
        close_conn()


def setup_conn(module):
    """
    this function create connection to LXCA
    :param module:
    :return:  lxca connection
    """
    lxca_con = None
    try:
        lxca_con = connect(
            module.params["auth_url"], module.params["login_user"], module.params["login_password"], "True"
        )
    except Exception as exception:
        error_msg = "; ".join(exception.args)
        module.fail_json(msg=error_msg, exception=traceback.format_exc())
    return lxca_con


def close_conn():
    """
    this function close connection to LXCA
    :param module:
    :return:  None
    """
    disconnect()

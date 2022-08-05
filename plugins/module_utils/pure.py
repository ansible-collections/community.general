# -*- coding: utf-8 -*-

# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Simon Dodsley <simon@purestorage.com>,2017
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

HAS_PURESTORAGE = True
try:
    from purestorage import purestorage
except ImportError:
    HAS_PURESTORAGE = False

HAS_PURITY_FB = True
try:
    from purity_fb import PurityFb, FileSystem, FileSystemSnapshot, SnapshotSuffix, rest
except ImportError:
    HAS_PURITY_FB = False

from functools import wraps
from os import environ
from os import path
import platform

VERSION = 1.2
USER_AGENT_BASE = 'Ansible'
API_AGENT_VERSION = 1.5


def get_system(module):
    """Return System Object or Fail"""
    user_agent = '%(base)s %(class)s/%(version)s (%(platform)s)' % {
        'base': USER_AGENT_BASE,
        'class': __name__,
        'version': VERSION,
        'platform': platform.platform()
    }
    array_name = module.params['fa_url']
    api = module.params['api_token']

    if array_name and api:
        system = purestorage.FlashArray(array_name, api_token=api, user_agent=user_agent)
    elif environ.get('PUREFA_URL') and environ.get('PUREFA_API'):
        system = purestorage.FlashArray(environ.get('PUREFA_URL'), api_token=(environ.get('PUREFA_API')), user_agent=user_agent)
    else:
        module.fail_json(msg="You must set PUREFA_URL and PUREFA_API environment variables or the fa_url and api_token module arguments")
    try:
        system.get()
    except Exception:
        module.fail_json(msg="Pure Storage FlashArray authentication failed. Check your credentials")
    return system


def get_blade(module):
    """Return System Object or Fail"""
    user_agent = '%(base)s %(class)s/%(version)s (%(platform)s)' % {
        'base': USER_AGENT_BASE,
        'class': __name__,
        'version': VERSION,
        'platform': platform.platform()
    }
    blade_name = module.params['fb_url']
    api = module.params['api_token']

    if blade_name and api:
        blade = PurityFb(blade_name)
        blade.disable_verify_ssl()
        try:
            blade.login(api)
            versions = blade.api_version.list_versions().versions
            if API_AGENT_VERSION in versions:
                blade._api_client.user_agent = user_agent
        except rest.ApiException as e:
            module.fail_json(msg="Pure Storage FlashBlade authentication failed. Check your credentials")
    elif environ.get('PUREFB_URL') and environ.get('PUREFB_API'):
        blade = PurityFb(environ.get('PUREFB_URL'))
        blade.disable_verify_ssl()
        try:
            blade.login(environ.get('PUREFB_API'))
            versions = blade.api_version.list_versions().versions
            if API_AGENT_VERSION in versions:
                blade._api_client.user_agent = user_agent
        except rest.ApiException as e:
            module.fail_json(msg="Pure Storage FlashBlade authentication failed. Check your credentials")
    else:
        module.fail_json(msg="You must set PUREFB_URL and PUREFB_API environment variables or the fb_url and api_token module arguments")
    return blade


def purefa_argument_spec():
    """Return standard base dictionary used for the argument_spec argument in AnsibleModule"""

    return dict(
        fa_url=dict(),
        api_token=dict(no_log=True),
    )


def purefb_argument_spec():
    """Return standard base dictionary used for the argument_spec argument in AnsibleModule"""

    return dict(
        fb_url=dict(),
        api_token=dict(no_log=True),
    )

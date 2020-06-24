# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Franck Cuny <franck.cuny@gmail.com>, 2014
#
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    from libcloud.compute.types import Provider
    from libcloud.compute.providers import get_driver
    HAS_LIBCLOUD_BASE = True
except ImportError:
    HAS_LIBCLOUD_BASE = False

from ansible_collections.community.general.plugins.module_utils.gcp import gcp_connect
from ansible_collections.community.general.plugins.module_utils.gcp import unexpected_error_msg as gcp_error

USER_AGENT_PRODUCT = "Ansible-gce"
USER_AGENT_VERSION = "v1"


def gce_connect(module, provider=None):
    """Return a GCP connection for Google Compute Engine."""
    if not HAS_LIBCLOUD_BASE:
        module.fail_json(msg='libcloud must be installed to use this module')
    provider = provider or Provider.GCE

    return gcp_connect(module, provider, get_driver, USER_AGENT_PRODUCT, USER_AGENT_VERSION)


def unexpected_error_msg(error):
    """Create an error string based on passed in error."""
    return gcp_error(error)

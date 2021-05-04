# Copyright (c) 2016-2017 Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from ansible_collections.community.general.tests.unit.compat.mock import Mock

# FIXME: These should be done inside of a fixture so that they're only mocked during
# these unittests
sys.modules['hpOneView'] = Mock()
sys.modules['hpOneView.oneview_client'] = Mock()

ONEVIEW_MODULE_UTILS_PATH = 'ansible_collections.community.general.plugins.module_utils.oneview'
from ansible_collections.community.general.plugins.module_utils.oneview import (OneViewModuleException,
                                                                                OneViewModuleTaskError,
                                                                                OneViewModuleResourceNotFound,
                                                                                OneViewModuleBase)

from ansible_collections.community.general.plugins.modules.remote_management.oneview.oneview_ethernet_network import EthernetNetworkModule
from ansible_collections.community.general.plugins.modules.remote_management.oneview.oneview_ethernet_network_info import EthernetNetworkInfoModule
from ansible_collections.community.general.plugins.modules.remote_management.oneview.oneview_fc_network import FcNetworkModule
from ansible_collections.community.general.plugins.modules.remote_management.oneview.oneview_fc_network_info import FcNetworkInfoModule
from ansible_collections.community.general.plugins.modules.remote_management.oneview.oneview_fcoe_network import FcoeNetworkModule
from ansible_collections.community.general.plugins.modules.remote_management.oneview.oneview_fcoe_network_info import FcoeNetworkInfoModule
from ansible_collections.community.general.plugins.modules.remote_management.oneview.oneview_network_set import NetworkSetModule
from ansible_collections.community.general.plugins.modules.remote_management.oneview.oneview_network_set_info import NetworkSetInfoModule
from ansible_collections.community.general.plugins.modules.remote_management.oneview.oneview_san_manager import SanManagerModule
from ansible_collections.community.general.plugins.modules.remote_management.oneview.oneview_san_manager_info import SanManagerInfoModule

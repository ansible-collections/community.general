# Copyright (c) 2016-2017 Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import sys
from unittest.mock import Mock

# FIXME: These should be done inside of a fixture so that they're only mocked during
# these unittests
if "hpOneView" not in sys.modules:
    sys.modules["hpOneView"] = Mock()
    sys.modules["hpOneView.oneview_client"] = Mock()

ONEVIEW_MODULE_UTILS_PATH = "ansible_collections.community.general.plugins.module_utils.oneview"
from ansible_collections.community.general.plugins.module_utils.oneview import (  # noqa: F401, pylint: disable=unused-import
    OneViewModuleException,
    OneViewModuleTaskError,
    OneViewModuleResourceNotFound,
    OneViewModuleBase,
)

from ansible_collections.community.general.plugins.modules.oneview_ethernet_network import EthernetNetworkModule  # noqa: F401, pylint: disable=unused-import
from ansible_collections.community.general.plugins.modules.oneview_ethernet_network_info import (  # noqa: F401, pylint: disable=unused-import
    EthernetNetworkInfoModule,
)
from ansible_collections.community.general.plugins.modules.oneview_fc_network import FcNetworkModule  # noqa: F401, pylint: disable=unused-import
from ansible_collections.community.general.plugins.modules.oneview_fc_network_info import FcNetworkInfoModule  # noqa: F401, pylint: disable=unused-import
from ansible_collections.community.general.plugins.modules.oneview_fcoe_network import FcoeNetworkModule  # noqa: F401, pylint: disable=unused-import
from ansible_collections.community.general.plugins.modules.oneview_fcoe_network_info import FcoeNetworkInfoModule  # noqa: F401, pylint: disable=unused-import
from ansible_collections.community.general.plugins.modules.oneview_network_set import NetworkSetModule  # noqa: F401, pylint: disable=unused-import
from ansible_collections.community.general.plugins.modules.oneview_network_set_info import NetworkSetInfoModule  # noqa: F401, pylint: disable=unused-import
from ansible_collections.community.general.plugins.modules.oneview_san_manager import SanManagerModule  # noqa: F401, pylint: disable=unused-import
from ansible_collections.community.general.plugins.modules.oneview_san_manager_info import SanManagerInfoModule  # noqa: F401, pylint: disable=unused-import

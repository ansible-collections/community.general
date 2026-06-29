# Copyright (c) 2025, IP2Location <support@ip2location.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import json
import unittest
from unittest.mock import Mock, patch

from ansible_collections.community.general.plugins.modules.ip2location_info import Ip2LocationInfo

IP2LOCATION_DATA = {
    "ip": "8.8.8.8",
    "country_code": "US",
    "country_name": "United States of America",
    "region_name": "California",
    "city_name": "Mountain View",
    "latitude": 37.386051,
    "longitude": -122.083855,
    "zip_code": "94035",
    "time_zone": "-07:00",
    "asn": "15169",
    "as": "Google LLC",
    "is_proxy": False,
}


class TestIp2LocationInfo(unittest.TestCase):
    def test_get_geo_data_with_ip(self):
        module = Mock()
        module.params = {"timeout": 10, "ip": "8.8.8.8"}
        module.from_json.side_effect = json.loads

        with patch(
            "ansible_collections.community.general.plugins.modules.ip2location_info.fetch_url"
        ) as mock_fetch_url:
            mock_response = Mock()
            mock_response.read.return_value = json.dumps(IP2LOCATION_DATA)
            mock_fetch_url.return_value = (mock_response, {"status": 200})

            ip2location_info = Ip2LocationInfo(module)
            result = ip2location_info.get_geo_data()

            self.assertEqual(result["country_code"], "US")
            mock_fetch_url.assert_called_once_with(module, "https://api.ip2location.io/?ip=8.8.8.8", timeout=10)

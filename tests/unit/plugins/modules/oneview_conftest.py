# Copyright (c) 2016-2017 Hewlett Packard Enterprise Development LP
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from .oneview_module_loader import ONEVIEW_MODULE_UTILS_PATH


@pytest.fixture
def mock_ov_client(mocker):
    mocker.patch(f"{ONEVIEW_MODULE_UTILS_PATH}.HAS_HPE_ONEVIEW", True)
    oneview_client_class = mocker.patch(f"{ONEVIEW_MODULE_UTILS_PATH}.OneViewClient", create=True)
    return oneview_client_class.from_json_file.return_value


@pytest.fixture
def mock_ansible_module():
    patcher_ansible = patch(f"{ONEVIEW_MODULE_UTILS_PATH}.AnsibleModule")
    patcher_ansible = patcher_ansible.start()
    ansible_module = Mock()
    patcher_ansible.return_value = ansible_module
    return ansible_module

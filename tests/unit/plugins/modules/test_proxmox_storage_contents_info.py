# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Julian Vanden Broeck <julian.vandenbroeck at dalibo.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

proxmoxer = pytest.importorskip("proxmoxer")

from ansible_collections.community.general.plugins.modules import proxmox_storage_contents_info
from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch
from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)
import ansible_collections.community.general.plugins.module_utils.proxmox as proxmox_utils

NODE1 = "pve"
RAW_LIST_OUTPUT = [
    {
        "content": "backup",
        "ctime": 1702528474,
        "format": "pbs-vm",
        "size": 273804166061,
        "subtype": "qemu",
        "vmid": 931,
        "volid": "datastore:backup/vm/931/2023-12-14T04:34:34Z",
    },
    {
        "content": "backup",
        "ctime": 1702582560,
        "format": "pbs-vm",
        "size": 273804166059,
        "subtype": "qemu",
        "vmid": 931,
        "volid": "datastore:backup/vm/931/2023-12-14T19:36:00Z",
    },
]


def get_module_args(node, storage, content="all", vmid=None):
    return {
        "api_host": "host",
        "api_user": "user",
        "api_password": "password",
        "node": node,
        "storage": storage,
        "content": content,
        "vmid": vmid,
    }


class TestProxmoxStorageContentsInfo(ModuleTestCase):
    def setUp(self):
        super(TestProxmoxStorageContentsInfo, self).setUp()
        proxmox_utils.HAS_PROXMOXER = True
        self.module = proxmox_storage_contents_info
        self.connect_mock = patch(
            "ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect",
        ).start()
        self.connect_mock.return_value.nodes.return_value.storage.return_value.content.return_value.get.return_value = (
            RAW_LIST_OUTPUT
        )
        self.connect_mock.return_value.nodes.get.return_value = [{"node": NODE1}]

    def tearDown(self):
        self.connect_mock.stop()
        super(TestProxmoxStorageContentsInfo, self).tearDown()

    def test_module_fail_when_required_args_missing(self):
        with pytest.raises(AnsibleFailJson) as exc_info:
            with set_module_args({}):
                self.module.main()

    def test_storage_contents_info(self):
        with pytest.raises(AnsibleExitJson) as exc_info:
            with set_module_args(get_module_args(node=NODE1, storage="datastore")):
                expected_output = {}
                self.module.main()

        result = exc_info.value.args[0]
        assert not result["changed"]
        assert result["proxmox_storage_content"] == RAW_LIST_OUTPUT

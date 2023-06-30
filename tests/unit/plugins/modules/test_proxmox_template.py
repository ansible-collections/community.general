# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, Sergei Antipov <greendayonfire at gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import sys

import pytest

proxmoxer = pytest.importorskip('proxmoxer')
mandatory_py_version = pytest.mark.skipif(
    sys.version_info < (2, 7),
    reason='The proxmoxer dependency requires python2.7 or higher'
)

from ansible_collections.community.general.plugins.modules import proxmox_template
from ansible_collections.community.general.tests.unit.compat.mock import patch, Mock
from ansible_collections.community.general.tests.unit.plugins.modules.utils import (
    AnsibleFailJson,
    ModuleTestCase,
    set_module_args,
)
import ansible_collections.community.general.plugins.module_utils.proxmox as proxmox_utils


class TestProxmoxTemplateModule(ModuleTestCase):
    def setUp(self):
        super(TestProxmoxTemplateModule, self).setUp()
        proxmox_utils.HAS_PROXMOXER = True
        self.module = proxmox_template
        self.connect_mock = patch(
            "ansible_collections.community.general.plugins.module_utils.proxmox.ProxmoxAnsible._connect"
        )
        self.connect_mock.start()

    def tearDown(self):
        self.connect_mock.stop()
        super(TestProxmoxTemplateModule, self).tearDown()

    @patch("os.stat")
    @patch.multiple(os.path, exists=Mock(return_value=True), isfile=Mock(return_value=True))
    def test_module_fail_when_toolbelt_not_installed_and_file_size_is_big(self, mock_stat):
        self.module.HAS_REQUESTS_TOOLBELT = False
        mock_stat.return_value.st_size = 268435460
        set_module_args(
            {
                "api_host": "host",
                "api_user": "user",
                "api_password": "password",
                "node": "pve",
                "src": "/tmp/mock.iso",
                "content_type": "iso"
            }
        )
        with pytest.raises(AnsibleFailJson) as exc_info:
            self.module.main()

        result = exc_info.value.args[0]
        assert result["failed"] is True
        assert result["msg"] == "'requests_toolbelt' module is required to upload files larger than 256MB"

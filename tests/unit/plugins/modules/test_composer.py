# Author: Alexei Znamensky (russoz@gmail.com)
#
# Copyright (c) Alexei Znamensky (russoz@gmail.com)
#
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ansible_collections.community.general.plugins.modules import composer

from .uthelper import RunCommandMock, TestCaseMock, UTHelper


class OsPathExistsMock(TestCaseMock):
    name = "os_path_exists"

    def setup(self, mocker):
        mocker.patch("os.path.exists", return_value=self.mock_specs.get("return_value", False))

    def check(self, test_case, results):
        pass


class OsPathIsfileMock(TestCaseMock):
    name = "os_path_isfile"

    def setup(self, mocker):
        mocker.patch("os.path.isfile", return_value=self.mock_specs.get("return_value", False))

    def check(self, test_case, results):
        pass


class Sha256Mock(TestCaseMock):
    name = "sha256"

    def setup(self, mocker):
        values = list(self.mock_specs.get("return_values", []))

        def _sha256_side_effect(path):
            if values:
                return values.pop(0)
            return "default_hash"

        mocker.patch("ansible.module_utils.basic.AnsibleModule.sha256", side_effect=_sha256_side_effect)

    def check(self, test_case, results):
        pass


UTHelper.from_module(composer, __name__, mocks=[RunCommandMock, OsPathExistsMock, OsPathIsfileMock, Sha256Mock])

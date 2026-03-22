# Copyright (c) 2026 Alexei Znamensky (russoz@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ansible_collections.community.general.plugins.modules import open_iscsi

from .uthelper import RunCommandMock, UTHelper
from .uthelper import TestCaseMock as MockBase

_MODULE = "ansible_collections.community.general.plugins.modules.open_iscsi"


class SocketMock(MockBase):
    name = "socket_getaddrinfo"

    def setup(self, mocker):
        ip = self.mock_specs["return"]
        mocker.patch(
            f"{_MODULE}.socket.getaddrinfo",
            return_value=[(None, None, None, None, (ip, None))],
        )

    def check(self, test_case, results):
        pass


class GlobMock(MockBase):
    name = "glob_glob"

    def setup(self, mocker):
        paths = self.mock_specs.get("return", [])
        mocker.patch(f"{_MODULE}.glob.glob", return_value=paths)
        mocker.patch(f"{_MODULE}.os.path.realpath", side_effect=lambda x: x)

    def check(self, test_case, results):
        pass


class TimeSleepMock(MockBase):
    name = "time_sleep"

    def setup(self, mocker):
        mocker.patch(f"{_MODULE}.time.sleep")

    def check(self, test_case, results):
        pass


UTHelper.from_module(open_iscsi, __name__, mocks=[RunCommandMock, SocketMock, GlobMock, TimeSleepMock])

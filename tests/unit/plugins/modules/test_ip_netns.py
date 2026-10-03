# Copyright (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ansible_collections.community.general.plugins.modules import ip_netns

from .uthelper import RunCommandMock, UTHelper

UTHelper.from_module(ip_netns, __name__, mocks=[RunCommandMock])

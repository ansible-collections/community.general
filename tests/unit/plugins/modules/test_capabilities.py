# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ansible_collections.community.general.plugins.modules import capabilities

from .uthelper import RunCommandMock, UTHelper

UTHelper.from_module(capabilities, __name__, mocks=[RunCommandMock])

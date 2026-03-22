# Copyright (c) 2026 Alexei Znamensky (russoz@gmail.com)
# Copyright (c) 2021 Abhijeet Kasurde <akasurde@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from ansible_collections.community.general.plugins.modules import npm

from .uthelper import RunCommandMock, UTHelper

UTHelper.from_module(npm, __name__, mocks=[RunCommandMock])

# -*- coding: utf-8 -*-
# Copyright (c) Alexei Znamensky (russoz@gmail.com)
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.community.general.plugins.modules import gio_mime
from .helper import Helper


helper = Helper.from_file(gio_mime.main, "tests/unit/plugins/modules/test_gio_mime.yaml")
patch_bin = helper.cmd_fixture
test_module = helper.test_module

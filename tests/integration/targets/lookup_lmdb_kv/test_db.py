# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import lmdb

map_size = 1024 * 100
env = lmdb.open("./jp.mdb", map_size=map_size)
with env.begin(write=True) as txn:
    txn.put(b"fr", b"France")
    txn.put(b"nl", b"Netherlands")
    txn.put(b"es", b"Spain")
    txn.put(b"be", b"Belgium")
    txn.put(b"lu", b"Luxembourg")

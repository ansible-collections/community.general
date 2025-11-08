#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later


from __future__ import annotations

import sys
from xmlrpc.client import ServerProxy
from urllib.parse import quote


proc = sys.argv[1]
value = sys.argv[2]
username = sys.argv[3]
password = sys.argv[4]

if username:
    url = 'http://%s:%s@127.0.0.1:9001/RPC2' % (quote(username, safe=''), quote(password, safe=''))
else:
    url = 'http://127.0.0.1:9001/RPC2'

server = ServerProxy(url, verbose=True)
server.supervisor.sendProcessStdin(proc, 'import sys; print(%s); sys.stdout.flush();\n' % value)

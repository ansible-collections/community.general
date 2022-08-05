#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import sys

if __name__ == '__main__':
    if sys.version_info[0] >= 3:
        import http.server
        import socketserver
        PORT = int(sys.argv[1])
        Handler = http.server.SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", PORT), Handler)
        httpd.serve_forever()
    else:
        import mimetypes
        mimetypes.init()
        mimetypes.add_type('application/json', '.json')
        import SimpleHTTPServer
        SimpleHTTPServer.test()

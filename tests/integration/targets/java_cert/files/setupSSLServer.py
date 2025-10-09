# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations
import ssl
import os
import sys

root_dir = sys.argv[1]
port = int(sys.argv[2])

try:
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler
except ModuleNotFoundError:
    from http.server import HTTPServer, SimpleHTTPRequestHandler

httpd = HTTPServer(('localhost', port), SimpleHTTPRequestHandler)
try:
    httpd.socket = ssl.wrap_socket(httpd.socket, server_side=True,
                                   certfile=os.path.join(root_dir, 'cert.pem'),
                                   keyfile=os.path.join(root_dir, 'key.pem'))
except AttributeError:
    # Python 3.12 or newer:
    context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=os.path.join(root_dir, 'cert.pem'),
                            keyfile=os.path.join(root_dir, 'key.pem'))
    httpd.socket = context.wrap_socket(httpd.socket)
httpd.handle_request()

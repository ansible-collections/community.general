#!/usr/bin/env python
# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import posixpath
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote

# Argument parsing
if len(sys.argv) != 4:
    print(f"Syntax: {sys.argv[0]} <bind> <port> <path>")
    sys.exit(-1)

HOST, PORT_str, PATH = sys.argv[1:4]
PORT = int(PORT_str)


# The HTTP request handler
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Modified from Python 3.6's version of SimpleHTTPRequestHandler
        # to support using another base directory than CWD.

        # abandon query parameters
        path = path.split("?", 1)[0]
        path = path.split("#", 1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith("/")
        try:
            path = unquote(path, errors="surrogatepass")
        except (UnicodeDecodeError, TypeError):
            path = unquote(path)
        path = posixpath.normpath(path)
        words = path.split("/")
        words = filter(None, words)
        path = PATH
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += "/"
        return path


# Run simple HTTP server
httpd = HTTPServer((HOST, PORT), Handler)

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

httpd.server_close()

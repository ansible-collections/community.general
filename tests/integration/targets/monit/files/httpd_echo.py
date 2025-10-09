# Copyright (c) 2020, Simon Kelly <simongdkelly@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import daemon

try:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

    def write_to_output(stream, content):
        stream.write(content)
except ImportError:
    from http.server import BaseHTTPRequestHandler, HTTPServer

    def write_to_output(stream, content):
        stream.write(bytes(content, "utf-8"))


hostname = "localhost"
server_port = 8082


class EchoServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        write_to_output(self.wfile, self.path)


def run_webserver():
    webServer = HTTPServer((hostname, server_port), EchoServer)
    print("Server started http://%s:%s" % (hostname, server_port))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


if __name__ == "__main__":
    context = daemon.DaemonContext()

    with context:
        run_webserver()

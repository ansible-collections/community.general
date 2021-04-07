from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
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
httpd.socket = ssl.wrap_socket(httpd.socket, server_side=True,
                               certfile=os.path.join(root_dir, 'cert.pem'),
                               keyfile=os.path.join(root_dir, 'key.pem'))
httpd.handle_request()

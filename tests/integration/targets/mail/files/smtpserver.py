#!/usr/bin/env python

# Copyright (c) 2018, Dag Wieers (@dagwieers) <dag@wieers.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Minimal SMTP server for testing, using only the Python standard library.
# The first port accepts plain SMTP and STARTTLS, the optional second port accepts SMTP over TLS.
# Messages are accepted and discarded.

from __future__ import annotations

import os.path
import socketserver
import ssl
import sys
import threading

# Handle custom ports
port = "25:465"
if len(sys.argv) > 1:
    port = sys.argv[1]
ports = port.split(":")
port1: int
port2: int | None
if len(ports) > 1:
    port1, port2 = int(ports[0]), int(ports[1])
else:
    port1, port2 = int(port), None

# Handle custom certificate
basename = os.path.splitext(sys.argv[0])[0]
certfile = basename + ".crt"
if len(sys.argv) > 2:
    certfile = sys.argv[2]

# Handle custom key
keyfile = basename + ".key"
if len(sys.argv) > 3:
    keyfile = sys.argv[3]

ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
print(f"Using {certfile} and {keyfile}")
ssl_ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)


class SMTPHandler(socketserver.BaseRequestHandler):
    implicit_tls = False

    def handle(self):
        self.tls_active = False
        if self.implicit_tls:
            self.start_tls()
        self.reply("220 localhost ESMTP test server")
        while True:
            line = self.reader.readline()
            if not line:
                break
            command, dummy, arg = line.decode("utf-8", "replace").rstrip("\r\n").partition(" ")
            command = command.upper()
            if command == "EHLO":
                extensions = ["localhost"]
                if not self.tls_active:
                    extensions.append("STARTTLS")
                extensions.append("8BITMIME")
                for extension in extensions[:-1]:
                    self.reply(f"250-{extension}")
                self.reply(f"250 {extensions[-1]}")
            elif command == "HELO":
                self.reply("250 localhost")
            elif command == "STARTTLS" and not self.tls_active:
                self.reply("220 Ready to start TLS")
                self.start_tls()
            elif command in ("MAIL", "RCPT", "RSET", "NOOP"):
                self.reply("250 OK")
            elif command == "DATA":
                self.reply("354 End data with <CR><LF>.<CR><LF>")
                self.read_data()
                self.reply("250 OK")
            elif command == "QUIT":
                self.reply("221 Bye")
                break
            else:
                self.reply(f"500 Command not recognized: {command}")

    def start_tls(self):
        self.request = ssl_ctx.wrap_socket(self.request, server_side=True)
        self.tls_active = True
        self.reader = self.request.makefile("rb")

    def setup(self):
        self.reader = self.request.makefile("rb")

    def reply(self, line):
        self.request.sendall(f"{line}\r\n".encode())

    def read_data(self):
        while True:
            line = self.reader.readline()
            if not line or line.rstrip(b"\r\n") == b".":
                return


class SMTPOverTLSHandler(SMTPHandler):
    implicit_tls = True


class SMTPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


print("Start SMTP server on port", port1)
servers = [SMTPServer(("127.0.0.1", port1), SMTPHandler)]
if port2:
    print("Start TLS SMTP server on port", port2)
    servers.append(SMTPServer(("127.0.0.1", port2), SMTPOverTLSHandler))

threads = [threading.Thread(target=server.serve_forever) for server in servers]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

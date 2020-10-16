import sys
from daemon import Daemon

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


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        write_to_output(self.wfile, self.path)


class MyDaemon(Daemon):
    def run(self):
        webServer = HTTPServer((hostname, server_port), MyServer)
        print("Server started http://%s:%s" % (hostname, server_port))

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass

        webServer.server_close()
        print("Server stopped.")


if __name__ == "__main__":
    daemon = MyDaemon('/tmp/httpd_echo.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)

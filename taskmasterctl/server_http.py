import http.server
import socketserver
import socket
import threading
import json
import urllib.parse
from Event import Event

from taskmasterctl.MyQueue import MyQueue

from HttpBuffer import HttpBuffer

import logging
logger = logging.getLogger(__name__)


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_POST(self):

        content_length = int(self.headers['Content-Length'])

        post_data = self.rfile.read(content_length).decode('utf-8')

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        post_data = urllib.parse.unquote(post_data)
        post_data = post_data.replace('+', ' ')

        command, process = post_data.split("=")
        process = urllib.parse.unquote(process)
        if command != "ping":
            MyQueue.put(Event(command, process))

        data = HttpBuffer.get_msg(timeout=0.1)
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        pass


class Myserver():
    def __init__(self) -> None:
        self.httpd = None

    def launch_server(self, port):
        server_address = ("", port)
        self.httpd = socketserver.TCPServer(server_address, MyHandler)
        self.httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        t = threading.Thread(target=self.httpd.serve_forever)
        t.start()
        logger.info(f"Serving HTTP on port {port}")

    def stop_server(self):
        self.httpd.shutdown()
        self.httpd.server_close()

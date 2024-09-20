import http.server
import socketserver
import sys
import threading
import json
import urllib.parse


from taskmasterctl.MyQueue import MyQueue

from HttpBuffer import HttpBuffer
dummy_data = {
    "cat:cat_0a": ["RUNNING", "12345"],
    "cat:cat_1a": ["RUNNING", "12346"],
    "dog:dog_2a": ["EXITED", "12347"],
    "dog:dog_3a": ["EXITED", "12348"],
    "dog:dog_4a": ["EXITED", "12349"],
    "dog:dog_5a": ["EXITED", "12350"],
    "dog:dog_6a": ["EXITED", "12351"],
    "dog:dog_7a": ["EXITED", "12352"],
    "dog:dog_8a": ["EXITED", "12353"],
    "dog:dog_9a": ["EXITED", "12354"]
}





class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(json.dumps(dummy_data).encode('utf-8'))

    def do_POST(self):

        content_length = int(self.headers['Content-Length'])

        post_data = self.rfile.read(content_length).decode('utf-8')

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # post_data = urllib.parse.quote(post_data)
        post_data = urllib.parse.unquote(post_data)
        post_data = post_data.replace('+', ' ')
        # post_data = urllib.parse.quo(post_data)

        command, process = post_data.split("=")
        process = urllib.parse.unquote(process)
        if command != "ping":
            MyQueue.put([command, process])
        
        data = HttpBuffer.get_msg(timeout=0.1)
        # data = dict(filter(lambda x: process in x[0], dummy_data.items()))
        # if process == "all":
        #     data = dummy_data
        if command != "ping":
            print(f"Received command: {command} on {process}")
        self.wfile.write(json.dumps(data).encode('utf-8'))


def launch_server(port):
    
    server_address = ("", port)
    httpd =  socketserver.TCPServer(server_address, MyHandler)
    # with socketserver.TCPServer(server_address, MyHandler) as httpd:
    print(f"Serving HTTP on port {port}")
    t = threading.Thread(target=httpd.serve_forever)
    t.start()
    print(f"Serving HTTP on port {port}")

        # httpd.shutdown()
        # t.join()

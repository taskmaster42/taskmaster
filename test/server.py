import socketserver
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s')


class TestSocketHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server) -> None:
        self.logger = logging.getLogger("TestSocketHandler")
        self.logger.debug("__init__")
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self) -> None:
        self.logger.debug("setup")
        socketserver.BaseRequestHandler.setup(self)
        return

    def handle(self) -> None:
        data_revc = self.request.recv(1024).strip()
        data_msg = data_revc.decode().upper()
        self.logger.debug("handle")
        self.logger.debug(f"Received: {data_revc}")
        self.request.send(data_msg.encode())
        self.logger.debug(f"Sent: {data_msg}")
        return


class TestServer(socketserver.TCPServer):
    def __init__(self, server_address: tuple[str, int], handler_class=TestSocketHandler) -> None:
        self.logger = logging.getLogger("TestServer")
        self.logger.debug("__init__")
        socketserver.TCPServer.__init__(self, server_address, handler_class)

    def server_activate(self) -> None:
        self.logger.debug("server_activate")
        socketserver.TCPServer.server_activate(self)
        return

    def serve_forever(self) -> None:
        self.logger.debug("waiting for request")
        self.logger.info("Handling requests, press <Ctrl-C> to quit")
        while True:
            self.handle_request()

    def handle_request(self) -> None:
        self.logger.debug("handle_request")
        return socketserver.TCPServer.handle_request(self)

    def verify_request(self, request, client_address) -> bool:
        self.logger.debug("verify_request")
        return socketserver.TCPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        self.logger.debug('process_request(%s, %s)', request, client_address)
        return socketserver.TCPServer.process_request(self, request, client_address)

    def server_close(self):
        self.logger.debug('server_close')
        return socketserver.TCPServer.server_close(self)

    def finish_request(self, request, client_address):
        self.logger.debug('finish_request(%s, %s)', request, client_address)
        return socketserver.TCPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        self.logger.debug('close_request(%s)', request_address)
        return socketserver.TCPServer.close_request(self, request_address)


def main() -> None:
    import threading

    address = ("localhost", 0)
    server = TestServer(address, TestSocketHandler)
    ip, port = server.server_address

    print(f"Server running on {ip}:{port}")

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    server.shutdown()


if __name__ == "__main__":
    main()

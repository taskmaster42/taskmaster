import socketserver


class TestSocketHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data_msg = "serveeeeeer answer"
        self.request.send(data_msg.encode())
        return


def main() -> None:
    import threading

    address = ("localhost", 0)
    server = socketserver.TCPServer(address, TestSocketHandler)
    ip, port = server.server_address

    print(f"Server running on {ip}:{port}")

    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()


if __name__ == "__main__":
    main()

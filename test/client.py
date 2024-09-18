import socket
import sys


class TestSocketClient:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))

    def send(self, message: bytes) -> bytes:
        self.socket.send(message)
        return self.socket.recv(1024)

    def close(self) -> None:
        self.socket.close()


def main() -> None:
    assert len(sys.argv) == 3, "Usage: python client.py <address> <port>"
    address = sys.argv[1]
    port = int(sys.argv[1])

    socketClient = TestSocketClient(address, port)
    message = b"Hello, world"
    print("Sending:", message)
    response = socketClient.send(message)
    print("Received:", response)
    socketClient.close()


if __name__ == "__main__":
    main()

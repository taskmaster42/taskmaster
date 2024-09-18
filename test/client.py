import socket
import sys
from Serializer import Serializer


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
    assert len(sys.argv) == 2, "Usage: python client.py <port>"
    port = int(sys.argv[1])

    socketClient = TestSocketClient("localhost", port)
    data = {"message": "Hello, World!", "code": 200}
    print("Sending:", Serializer.serialize(data))
    response = socketClient.send(Serializer.serialize(data))
    print("Received:", Serializer.deserialize(response))
    socketClient.close()


if __name__ == "__main__":
    main()

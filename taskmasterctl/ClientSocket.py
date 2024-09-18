import socket


class ClientSocket():
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

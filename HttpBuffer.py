import os
import select

class HttpBuffer():
    def __init__(self) -> None:
        self.fd_r, self.fd_w = os.pipe()
        self.data = []

    def put_msg(self, msg):
        self.data.append(msg)
        os.write(self.fd_w,b"YO")
    
    def get_msg(self, timeout=None):
        fd_r, _, _ = select.select([self.fd_r], [], [], timeout)
        if len(fd_r) > 0:
            _ = os.read(self.fd_r, 2)
            return self.data.pop(0)
        else:
            return {}
HttpBuffer = HttpBuffer()
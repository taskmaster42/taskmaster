import os
import threading


class FileManager():
    def __init__(self) -> None:
        self.current_file = {}
        self.lock = threading.Lock()

    def open_file(self, file_name, flags):
        self.lock.acquire()
        if file_name in self.current_file:
            self.current_file[file_name]["count"] += 1
        else:
            new_fd = os.open(file_name, flags )
            self.current_file[file_name] = {}
            self.current_file[file_name]["fd"] = new_fd
            self.current_file[file_name]["count"] = 1
        
        self.lock.release()
        return self.current_file[file_name]["fd"]
    

    def close(self, fd_close):
        self.lock.acquire()
        for name, fd in self.current_file.items():
            if fd_close == fd["fd"]:
                fd["count"] -= 1
                if fd["count"] <= 0:
                    os.close(fd_close)
                    del self.current_file[name]
                    break
        self.lock.release()


FileManager = FileManager()
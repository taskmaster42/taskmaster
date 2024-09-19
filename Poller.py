import select
TIMEOUT = 0.01


class Poller():
    def __init__(self) -> None:
        self._poll = select.poll()
        self.process_registered = {}

    def register_process(self, process):
        stdout = process.get_fd()
        self.process_registered[stdout] = process
        self._poll.register(stdout, select.EPOLLIN)

    def remove_process(self, process):
        stdout = process.get_fd()
        del self.process_registered[stdout]
        self._poll.unregister(stdout)

    def get_process_ready(self):
        fd_ready = self._poll.poll(TIMEOUT)
        if len(fd_ready) == 0:
            return []
        return [self.process_registered[fd[0]] for fd in fd_ready]

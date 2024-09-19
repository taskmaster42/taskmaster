import select
TIMEOUT = 0.01


class Poller():
    def __init__(self) -> None:
        self._poll = select.poll()
        self.process_registered = {}

    def register_process(self, process):
        stdout, stderr = process.get_fd()
        self.process_registered[stdout] = process
        self.process_registered[stderr] = process
        self._poll.register(stdout, select.EPOLLIN)
        self._poll.register(stderr, select.EPOLLIN)

    def remove_process(self, process):
        stdout, stderr = process.get_fd()
        del self.process_registered[stdout]
        del self.process_registered[stderr]
        self._poll.unregister(stdout)
        self._poll.unregister(stderr)

    def get_process_ready(self):
        fd_ready = self._poll.poll(TIMEOUT)
        if len(fd_ready) == 0:
            return []
        process_ready = []
        for fd in fd_ready:
            process_ready.append(self.process_registered[fd[0]])
            self.process_registered[fd[0]].set_fd_ready(fd[0])
        return process_ready

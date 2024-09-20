import select
TIMEOUT = 0.01


class Poller():
    def __init__(self, timeout=TIMEOUT) -> None:
        self._poll = select.poll()
        self.process_registered = {}
        self.timeout = timeout

    def register_process(self, process):
        stdout, stderr = process.get_fd()
        if stdout not in self.process_registered:
            self.process_registered[stdout] = process.get_name()
            self._poll.register(stdout, select.EPOLLIN)
        if stderr not in self.process_registered:
            self.process_registered[stderr] = process.get_name()
            self._poll.register(stderr, select.EPOLLIN)

    def remove_process(self, process):
        stdout, stderr = process.get_fd()

        del self.process_registered[stdout]

        del self.process_registered[stderr]
        self._poll.unregister(stdout)
        self._poll.unregister(stderr)

    def get_process_ready(self):
        fd_ready = self._poll.poll(self.timeout)
        if len(fd_ready) == 0:
            return []
        process_ready = {}
        for fd in fd_ready:
            if self.process_registered[fd[0]] in process_ready:
                process_ready[self.process_registered[fd[0]]].append(fd[0])
            else:
                 process_ready[self.process_registered[fd[0]]] = [fd[0]]
            # self.process_registered[fd[0]].set_fd_ready(fd[0])
        return process_ready


    def clear(self):
        for key , process in self.process_registered.items():
            self._poll.unregister(key)
        self.process_registered = {}
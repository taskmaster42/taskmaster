import select

TIMEOUT = 10 # milliseconds


class Poller():
    def __init__(self, timeout=TIMEOUT) -> None:
        self._poll = select.poll()
        self.process_registered = {}
        self.timeout = timeout

    def register_process(self, process):

        stdout, stderr = process.get_fd()
        if stdout not in self.process_registered and stdout > 0:
            self.process_registered[stdout] = process.get_name()
            self._poll.register(stdout, select.POLLIN)
        if stderr not in self.process_registered and stderr > 0:
            self.process_registered[stderr] = process.get_name()
            self._poll.register(stderr, select.POLLIN)

    def remove_process(self, process):
        stdout, stderr = process.get_fd()
        try:
            del self.process_registered[stdout]

            del self.process_registered[stderr]
        except KeyError:
            return
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

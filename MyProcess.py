from enum import Enum
import os
import subprocess
import threading
import time
import datetime
import signal
import logging
logger = logging.getLogger(__name__)
TIMEOUT = 0.01


class ProcessState(Enum):
    RUNNING = "RUNNING"
    SPAWNED = "SPAWNED"
    KILLED = "KILLED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"
    FINISH = "FAILED"


class MyProcess():
    def __init__(self, Config, name, task_name, q):
        self.Config = Config
        self.task_name = task_name
        self.open_pipe()
        self.cmd = [word for word in Config.get("cmd").split()]
        self.name = name
        self.q = q
        if Config.get("stdout") != 'None':
            self.stdout_log = os.open(Config.get("stdout"),
                                      os.O_WRONLY | os.O_CREAT)
        if Config.get("stderr") != 'None':
            if Config.get("stderr") == Config.get("stdout"):
                self.stderr_log = self.stdout_log
            else:
                self.stderr_log = os.open(Config.get("stderr"),
                                          os.O_WRONLY | os.O_CREAT)
        self.state = None
        self.got_killed = False
        self.attached = False
        self.th = threading.Thread(target=self.run, args=())
        self.fd_ready = []

    def open_pipe(self):
        self.stdin_read, self.stdin_write = os.pipe()
        self.stdout_read, self.stdout_write = os.pipe()
        self.stderr_read, self.stderr_write = os.pipe()
        self.stderr_log = -1
        self.stdout_log = -1

    def get_name(self):
        return self.name

    def write_data(self, data):
        os.write(self.stdin_write, data.encode())

    def launch_process(self):
        self.th.start()

    def start_suceed(self):
        time_finish = datetime.datetime.now()
        diff = time_finish - self.time_started
        return diff.seconds < self.Config.get("startsecs")

    def run(self):
        logger.info(f"Spawned {self.name}")
        self.state = ProcessState.SPAWNED
        self.time_started = datetime.datetime.now()
        self.proc = subprocess.Popen(self.cmd,
                                     stdin=self.stdin_read,
                                     stdout=self.stdout_write,
                                     stderr=self.stderr_write)
        self.state = ProcessState.RUNNING
        logger.info(f"Process {self.name} has entered a RUNNING" +
                    f" state with PID {self.proc.pid}")
        self.return_code = self.proc.wait()

        if self.start_suceed():
            self.state = ProcessState.FAILED
        elif self.got_killed:
            self.state = ProcessState.KILLED
        else:
            self.state = ProcessState.FINISH

        # process is finished we empty the pipe if needed
        if os.fstat(self.stdout_read).st_size > 0:
            self.read_fd(self.stdout_read, self.stdout_log, 'stdout')
        if os.fstat(self.stderr_read).st_size > 0:
            self.read_fd(self.stderr_read, self.stderr_log, 'stderr')
        self.clean_up()
        logger.info(f"Process {self.name} has finished with {self.return_code}" +
                    f"({'expected' if self.is_exit_expected() else 'unexpected'})")
        self.q.put(f"{self.name}")

    def clean_up(self):
        os.close(self.stderr_read)
        os.close(self.stdout_read)
        os.close(self.stdin_read)
        os.close(self.stderr_write)
        os.close(self.stdout_write)
        os.close(self.stdin_write)
        if self.Config.get("stdout") != 'None':
            os.close(self.stdout_log)
        if self.Config.get("stderr") != 'None' and self.Config.get("stderr") != self.Config.get("stdout"):
            os.close(self.stderr_log)

    def killed(self):
        return self.got_killed

    def is_exit_expected(self):
        if self.state == ProcessState.FAILED:
            return False
        return self.return_code in self.Config.get("exitcodes")

    def stop(self):
        th = threading.Thread(target=self._stop)
        th.start()

    def _stop(self):
        if self.state != ProcessState.RUNNING:
            return
        logger.info(f"Killing {self.name} with" +
                    f"{self.Config.get('stopsignal').get_num()}")
        self.got_killed = True
        os.kill(self.proc.pid, self.Config.get('stopsignal').get_num())
        time_before = datetime.datetime.now()
        while self.state == ProcessState.RUNNING:
            time.sleep(TIMEOUT)
            time_now = datetime.datetime.now()
            if time_now - time_before >\
                    datetime.timedelta(seconds=self.Config.get('stopwaitsecs')):
                break
        if self.state == ProcessState.RUNNING:
            os.kill(self.proc.pid, signal.SIGKILL)

    def read_fd(self, fd_read, fd_log, name):
        # We should probably buffer it and only write if we have a \n
        self.data = b''
        if self.Config.get(name) == 'None' and self.attached:
            # We empty the pipe if we dont capture
            self.data = os.read(fd_read, 65000)
            self.data = b''
            return
        self.data = os.read(fd_read, 65000)
        if self.Config.get(name) != 'None':
            os.write(fd_log, self.data)
        # Here we will probably send it to the client
        if self.attached:
            print(self.data)

    def handle_read(self):
        for fd in self.fd_ready:
            if fd == self.stdout_read:
                self.read_fd(fd, self.stdout_log, 'stdout')
            elif fd == self.stderr_read:
                self.read_fd(fd, self.stderr_log, 'stderr')
        self.fd_ready = []

    def get_fd(self):
        return self.stdout_read, self.stderr_read

    def attach(self):
        self.attached = True

    def detach(self):
        self.attached = False

    def set_fd_ready(self, fd_ready):
        self.fd_ready.append(fd_ready)

from MyProcess import MyProcess
from config_parser import Config
from config_types import AutoRestartType
import datetime
import logging

logger = logging.getLogger(__name__)


class Task():
    def __init__(self, task_name, config_file):
        self.task_name = task_name
        self.config = Config(config_file)

    def create_process_list(self, q):
        self.process_list = []
        self.process_history = {}
        self.process_history_last_restart = {}
        for i in range(0, self.config.get("numprocs")):
            process_name = self.task_name + ":" + str(i)
            new_process = MyProcess(self.config,
                                    process_name,
                                    self.task_name,
                                    q)
            self.process_list.append(new_process)
            self.process_history[process_name] = 0
            self.process_history_last_restart[process_name] = [datetime.datetime.now()]
        return self.process_list

    def check_fatal(self, process_history):
        # here we will if we tried to restart process too quickly
        # => max 3 retrie in less than 2 sec
        max_retrie = 3
        timeout = 2
        if len(process_history) <= max_retrie:
            return False
        if process_history[max_retrie - 1] - process_history[0] < datetime.timedelta(seconds=timeout):
            return True

        # we remove the oldest retry time
        process_history.pop(0)
        return False

    def renew_process(self, process, q):
        for i in range (0, len(self.process_list)):
            if self.process_list[i].name == process.get_name():
                self.process_list.pop(i)
        new_process = MyProcess(self.config, process.get_name(),
                             self.task_name, q)
        self.process_list.append(new_process)
        return new_process

    def recreate_process(self, process, q):
        if process.killed():
            return None

        self.process_history[process.get_name()] += 1
        self.process_history_last_restart[process.get_name()].append(datetime.datetime.now())

        if self.check_fatal(self.process_history_last_restart[process.get_name()]):
            logging.info(f"gave yup {process.get_name()} entered a FATAL state, too many start retries too quickly")
            return None
        if self.config.get("autorestart") == AutoRestartType('true'):
            return self.renew_process(process, q)
        if self.process_history[process.get_name()] >\
                self.config.get("startretries"):
            return None
        if not process.is_exit_expected() and\
                self.config.get("autorestart") == AutoRestartType('unexpected'):
            return self.renew_process(process, q)
        return None



    def get_status(self):
        process_status = {}
        for process in self.process_list:
            process_status[process.get_name()] = [process.get_status(), process.get_pid()]

        return process_status
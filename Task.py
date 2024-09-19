from MyProcess import MyProcess
from config_parser import Config
from config_types import AutoRestartType


class Task():
    def __init__(self, task_name, config_file):
        self.task_name = task_name
        self.config = Config(config_file)

    def create_process_list(self, q):
        self.process_list = []
        self.process_history = {}
        for i in range(0, self.config.get("numprocs")):
            process_name = self.task_name + ":" + str(i)
            new_process = MyProcess(self.config,
                                    process_name,
                                    self.task_name,
                                    q)
            self.process_list.append(new_process)
            self.process_history[process_name] = 0
        return self.process_list

    def recreate_process(self, process, q):
        if process.killed():
            return None
        self.process_history[process.get_name()] += 1
        if self.config.get("autorestart") == AutoRestartType('true'):
            return MyProcess(self.config, process.get_name(),
                             self.task_name, q)
        if self.process_history[process.get_name()] >\
                self.config.get("startretries"):
            return None
        if process.is_exit_expected() and\
                self.config.get("autorestart") == AutoRestartType('unexpected'):
            return MyProcess(self.config, process.get_name(),
                             self.task_name, q)
        return None

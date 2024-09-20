from MyProcess import MyProcess
from config_parser import Config
import datetime
import logging

logger = logging.getLogger(__name__)


class Task():
    def __init__(self, task_name, config_file):
        self.task_name = task_name
        self.config = Config(config_file)

    def __eq__(self, value: object) -> bool:
        return self.config == value.config

    def create_process_list(self, q):
        process_list = {}
        for i in range(0, self.config.get("numprocs")):
            process_name = self.task_name + ":" + str(i)
            new_process = MyProcess(self.config,
                                    process_name,
                                    self.task_name,
                                    q)
            process_list[new_process.get_name()] = new_process
        return process_list

    def get_task_name(self):
        return self.task_name


    def numproc_went_up(self, new_task):
        return new_task.config.get('numprocs') > self.config.get('numprocs')
    

    def need_despawn(self, new_task):
        key_change_despawn = [
            "cmd",
            "workingdir",
            "env",
            "umask"
        ]
        if not self.numproc_went_up(new_task):
            return True
        for key in key_change_despawn:
            if self.config.get(key) != new_task.config.get(key):
                return True
        return False
    
    def get_config(self):
        return self.config
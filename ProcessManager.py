from MyProcess import MyProcess, ProcessState

from Poller import Poller

import queue
import datetime
import logging



logger = logging.getLogger(__name__)
from config_types import AutoRestartType


class ProcessManager:
    def __init__(self, q) -> None:
        self.process_list = {}
        self.q = q
        self.process_history = {}
        self.process_history_last_restart = {}
        self.process_reloaded = {}
        pass

    def add_process_to_history(self, process):
        self.process_history[process.get_name()] = 0
        self.process_history_last_restart[process.get_name()] = [datetime.datetime.now()]
    
    
    def add_process_numproc_up(self, old_task, new_task):
        process_list = new_task.create_process_list(self.q)
        for process_name, process in process_list.items():
            if process_name not in self.process_list:
                self.process_list.update({process_name:process})
                self.add_process_to_history(process)
                process.launch_process()
    
    def stop_process_from_task(self, task):
        for _, process in self.process_list.items():
            if process.get_task_name() == task.get_task_name():
                process.stop()
                # del self.process_history[process_name]
                # del self.process_history_last_restart[process_name]


    def update_process_from_task(self, task):
        for _, process in self.process_list.items():
            if process.get_task_name() == task.get_task_name():
                process.update_config(task.get_config())
                self.add_process_to_history(process)

        
    def create_process_from_task_reload(self, task):
        new_process_list = task.create_process_list(self.q)
        self.process_reloaded.update(new_process_list)

    def create_process_from_task(self, task):
        new_process_list = task.create_process_list(self.q)
        self.process_list.update(new_process_list)

    def start_process_from_task(self, task):
        for _, process in self.process_list.items():
            if process.get_task_name() == task.get_task_name():
                process.launch_process()
                self.add_process_to_history(process)

    
    def start_all_process(self):
        for _, process in self.process_list.items():
            process.launch_process()
            self.add_process_to_history(process)

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
    

    def need_restart(self, process):            
        if process.killed():
            return None
        if process.get_config_key("autorestart") == AutoRestartType('true') and\
             process.is_exit_expected():
            return True
        
        # Here we check if we need to restart after it didnt stayed long enough
        if process.get_config_key("autorestart") != AutoRestartType('false') and\
            process.get_status() == ProcessState.FAILED and\
            self.check_fatal(self.process_history_last_restart[process.get_name()]):
            logging.info(f"gave up {process.get_name()} entered a FATAL state, too many start retries too quickly")
            return False
        
        if process.get_config_key("autorestart") == AutoRestartType('true'):
            return True
        
        if self.process_history[process.get_name()] >\
                process.get_config_key("startretries"):
            return False
        if not process.is_exit_expected() and\
                process.get_config_key("autorestart") == AutoRestartType('unexpected'):
            return True
        return False
    

    def handle_process_stopped(self, process_name, poller):
        self.process_list[process_name].clean_up()
        poller.remove_process(self.process_list[process_name])

        old_process = self.process_list[process_name]
        # special case for reloading conf => we launch new process with same name
        # after old process stopped
        if process_name in self.process_reloaded:
            new_process = self.process_reloaded[process_name]
            del self.process_list[process_name]
            del self.process_reloaded[process_name]
            self.process_list[new_process.get_name()] = new_process
            poller.register_process(new_process)
            new_process.launch_process()
            self.add_process_to_history(new_process)
            return
        self.process_history[old_process.get_name()] += 1
        self.process_history_last_restart[old_process.get_name()].append(datetime.datetime.now())

        if self.need_restart(old_process):
            new_process = old_process.clone()
            del self.process_list[process_name]
            self.process_list[new_process.get_name()] = new_process
            poller.register_process(new_process)
            new_process.launch_process()
        else:
            del self.process_list[process_name]

       
    
    def register_process(self, poller):
        for _, process in self.process_list.items():
            poller.register_process(process)


    def handle_read_event(self, process_list):
        for process_name, fd in process_list.items():
            self.process_list[process_name].set_fd_ready(fd)
            self.process_list[process_name].handle_read()

    def stop_all(self, poller):
        to_clean =  self.process_reloaded
        self.process_reloaded = {}
   
        for _, process in self.process_list.items():
            process.stop_wait()
        
        while self.process_list:
            item = self.q.get()
            self.handle_process_stopped(item, poller)

        for _, process in to_clean.items():
            process.clean_up()
import yaml

import queue
import logging

from Poller import Poller
from MyProcess import MyProcess
from Task import Task
logger = logging.getLogger(__name__)

TIMEOUT = 0.01

import gc
import sys


from ProcessManager import ProcessManager
# def is_task_different(task_a, task_b):



def main():
    logging.basicConfig(level=logging.INFO)
    with open('config_test.yml', 'r') as file:
        config = yaml.safe_load(file)
    task_list = {}
    for task_name, config in config["programs"].items():
        task_list[task_name] = Task(task_name, config)
    
    
    
    q = queue.Queue()
    poller = Poller()

    processManager = ProcessManager(q)
    for _, task in task_list.items():
        processManager.create_process_from_task(task)
    processManager.register_process(poller)
    processManager.start_all_process()

    while True:
        try:
            item = q.get(timeout=TIMEOUT)

            processManager.handle_process_stopped(item, poller)

        except Exception as e:
            item = None
        fd_ready = poller.get_process_ready()
        if len(fd_ready) > 0:
            processManager.handle_read_event(fd_ready)

if __name__ == "__main__":
    main()

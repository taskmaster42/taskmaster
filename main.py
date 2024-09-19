import yaml

import queue
import logging

from Poller import Poller
from Task import Task
logger = logging.getLogger(__name__)

TIMEOUT = 0.01


def main():
    logging.basicConfig(level=logging.INFO)
    with open('config_test.yml', 'r') as file:
        config = yaml.safe_load(file)
    task_list = {}
    for task_name, config in config["programs"].items():
        task_list[task_name] = Task(task_name, config)
    process_list = {}
    q = queue.Queue()
    poller = Poller()

    for _, task in task_list.items():
        for new_process in   task.create_process_list(q):
            process_list[new_process.get_name()] = new_process
            new_process.launch_process()
            poller.register_process(new_process)


    test_int = 0
    print (process_list["cat:0"])
    process_list["cat:0"].attach()
    while True:
        try:
            item = q.get(timeout=TIMEOUT)
        except Exception:
            item = None
        if item is not None:
            finished_process = process_list[item]
            poller.remove_process(finished_process)
            recreated_process =\
                task_list[finished_process.task_name].recreate_process(finished_process, q)
            process_list.pop(item)
            if recreated_process:
                process_list[item] = recreated_process
                recreated_process.launch_process()
                poller.register_process(recreated_process)
        
        process_event = poller.get_process_ready()
        for process in process_event:
            process.handle_read()
        if test_int > 30:
            test_int = -1
            process_list["cat:0"].detach()
            process_list["catch:0"].stop()
        if test_int >= 0:
            process_list["cat:0"].write_data("yoyoyoyo")

            test_int += 1


    for _, p in process_list.items():
        p.stop()


if __name__ == "__main__":
    main()

import yaml

import queue
import logging

from Poller import Poller
from Task import get_task_from_config_file

from taskmasterctl.server_http import Myserver

logger = logging.getLogger(__name__)

TIMEOUT = 0.01

import gc
import sys

from taskmasterctl.MyQueue import MyQueue

from ProcessManager import ProcessManager
from HttpBuffer import HttpBuffer

from Event import *

import signal
from taskmasterctl.server_http import Myserver

RUNNING = True

def stop_loop(signum, __):
    global RUNNING
    RUNNING = False
    print(f"Received signal {signum}. Exiting...")

def set_up_sig():
    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        if sig != signal.SIGCHLD:
            signal.signal(sig, stop_loop)  # Substitute handler of choice for `print`

def handle_cmd(event, process_manager, poller, task_list):
    cmd = event.get_cmd()
    process = event.get_args()
    if process != "all"\
        and cmd in ["debug", "stop", "start", "restart", "status", "update", "attach", "detach"]\
        and not process_manager.check_process_exist(process):
        logger.info(f"Unknown process {process}")
        HttpBuffer.put_msg(process_manager.get_all_state())
        return
 
    match cmd: 
        case "stop":
            event_stop(process, process_manager, poller)
        case "start":
            event_start(process, process_manager, poller)
        case "restart":
            event_restart(process, process_manager)
        case "status":
            event_status(process_manager)
        case "update":
            process_manager, task_list = event_update(process_manager, task_list, poller)
        case "attach":
            attach(process_manager, process)
        case "detach":
            detach(process_manager, process)
        case "attach_cmd":
            send_attached(process_manager, process)
        case "debug":
            debug()
        case _:
            logger.info(f"Unknown command {cmd}")
            return task_list
    return task_list


def run():
    set_up_sig()
    serv = Myserver()

    logging.basicConfig(level=logging.INFO)
    serv.launch_server(int (sys.argv[1]))
    task_list = get_task_from_config_file('config_test.yml')
    q = MyQueue
    poller = Poller()

    process_manager = ProcessManager(q)
    for _, task in task_list.items():
        process_manager.create_process_from_task(task)

    process_manager.start_all_process(poller, first_launch=True)
    
    do_reload = 0
    while RUNNING:
        try:
            item = q.get_nowait()
            if item.get_cmd() == EventType.DEAD:
                process_manager.handle_process_stopped(item.get_args(), poller)
            elif item.get_cmd() == EventType.DELETE:
                process_manager.forget_process(item.get_args())

            else:
                task_list = handle_cmd(item, process_manager, poller, task_list)
        except queue.Empty:
            pass
        fd_ready = poller.get_process_ready()
        if len(fd_ready) > 0:
            process_manager.handle_read_event(fd_ready)
        do_reload += 1
    
    process_manager.stop_all(poller)
    serv.stop_server()
    logger.info("Exiting")
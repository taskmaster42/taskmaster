import yaml

import queue
import logging

from Poller import Poller
from Task import get_task_from_config_file

from taskmasterctl.server_http import Myserver

logger = logging.getLogger(__name__)

TIMEOUT = 0.01

import sys

from taskmasterctl.MyQueue import MyQueue

from ProcessManager import ProcessManager
from HttpBuffer import HttpBuffer

from Event import *

import signal
from taskmasterctl.server_http import Myserver

import argparse


RUNNING = True

def stop_loop(signum, __):
    global RUNNING
    RUNNING = False
    logger.info(f"Received signal {signum}")

def set_up_sig():
    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        if sig != signal.SIGCHLD:
            signal.signal(sig, stop_loop)

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
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int)
    parser.add_argument("--config", type=str, default="config_test.yml")
    parser.add_argument("--out", action="store_true", dest="output")
    parser.add_argument("--log", type=str, default="./taskmasterd.log")
    args = parser.parse_args()

    set_up_sig()
    serv = Myserver()

    logging.basicConfig(level=logging.INFO, filename=args.log)
    if args.output:
        logging.getLogger().addHandler(logging.StreamHandler())
    serv.launch_server(args.port)
    try:
        task_list = get_task_from_config_file(args.config)
    except Exception as e:
        logger.error(f"Error while reading config file: {e}")
        serv.stop_server()
        return
    q = MyQueue
    poller = Poller()

    process_manager = ProcessManager(q)
    for _, task in task_list.items():
        process_manager.create_process_from_task(task)

    process_manager.start_all_process(poller, first_launch=True)
    
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
    
    process_manager.stop_all(poller)
    serv.stop_server()
    logger.info("Exiting")
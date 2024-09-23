
from enum import Enum
from HttpBuffer import HttpBuffer
import Task

import shutil
import subprocess
import os
import threading

import logging
logger = logging.getLogger(__name__)


class EventType(Enum):
    DEAD = "EventDead",
    DELETE = "EventDelete",
    SERVERQUERY = "EventServerQuery",


class Event():
    def __init__(self, cmd, args) -> None:
        self.cmd = cmd
        self.args = args

    def get_cmd(self):
        return self.cmd

    def get_args(self):
        return self.args

# When do we despawn all process:
    # -> process name change
    # -> cmd / workingdir / env / umask
    # numproc goes down
# We dont spawn / despawn process:
    # -> autostart / autorestart / exit code / start retries / stopsignal
    # -> stopwaitsec / stodut / stderr

# We spawn new process
#    -> numproc goes up

# We 'clear' process history if we have a change
# if we already have 2 restart failed and we change stdout -> we set nb of restart failed to 0

# if we have the same config we do nothing


def reload_conf(config_name, process_manager, old_task_list, poller):
    try:
        new_task_list = Task.get_task_from_config_file(config_name)
    except Exception as e:
        logging.warning(f"Error while loading config file: {e}")
        return old_task_list
    for old_task_name, old_task in old_task_list.items():
        # this task not in new config => despawn
        if old_task_name not in new_task_list:
            process_manager.stop_process_from_task(old_task)
            continue
        # exact same config => we do nothing
        if old_task == new_task_list[old_task_name]:
            continue
        # if we need a full despawn / respawn:
        if old_task.need_despawn(new_task_list[old_task_name]):
            process_manager.stop_process_from_task(old_task)
            process_manager.create_process_from_task_reload(new_task_list[old_task_name])
            continue

        # we need to add process because numproc went up
        if old_task.numproc_went_up(new_task_list[old_task_name]):
            process_manager.add_process_numproc_up(old_task, new_task_list[old_task_name])
        # last case no need to respawn we need to update process config
        # -> we might have a *small* window of time where process continue with old config
        process_manager.update_process_from_task(new_task_list[old_task_name])

    # new task in new config to spawn
    for new_task_name, new_task in new_task_list.items():
        if new_task_name not in old_task_list:
            process_manager.create_process_from_task(new_task)
            process_manager.start_process_from_task(new_task)

    process_manager.register_process(poller)

    return new_task_list


def event_stop(process, process_manager, poller):
    if process != "all":
        process_manager.stop_process(process)
    else:
        process_manager.stop_all(poller)
    HttpBuffer.put_msg(process_manager.get_all_state())


def event_start(process, process_manager, poller):
    if process != "all":
        process_manager.start_process(process, poller)
    else:
        process_manager.start_all_process(poller)
    HttpBuffer.put_msg(process_manager.get_all_state())


def event_restart(process, process_manager):
    process_manager.restart_process(process)
    HttpBuffer.put_msg(process_manager.get_all_state())


def event_status(process_manager):
    HttpBuffer.put_msg(process_manager.get_all_state())


def event_update(process_manager, task_list, poller):
    task_list = reload_conf('config_test.yml', process_manager,
                            task_list, poller)
    HttpBuffer.put_msg(process_manager.get_all_state())
    return process_manager, task_list


def attach(process_manager, process):
    process_manager.attach(process)
    HttpBuffer.put_msg(process_manager.get_all_state())


def detach(process_manager, process):
    process_manager.detach(process)
    HttpBuffer.put_msg(process_manager.get_all_state())


def send_attached(process_manager, process):
    process_manager.send_attached(process)


def debug():
    fds = get_fd()
    th_lst = get_treads()
    HttpBuffer.put_msg({
        "fds": fds,
        "thread": th_lst})


def get_fd():
    lsof_path = shutil.which("lsof")
    if lsof_path is None:
        raise NotImplementedError("Didn't handle unavailable lsof.")
    raw_procs = subprocess.check_output(
        [lsof_path, "-w", "-Ff", "-p", str(os.getpid())]
    )

    def filter_fds(lsof_entry: str) -> bool:
        return lsof_entry.startswith("f") and lsof_entry[1:].isdigit()

    fds = list(filter(filter_fds, raw_procs.decode().split(os.linesep)))
    return fds


def get_treads():
    lst = [str(th) for th in threading.enumerate()]
    return lst

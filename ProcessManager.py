from MyProcess import ProcessState
import datetime
import logging
from config_types import AutoRestartType

logger = logging.getLogger(__name__)


class ProcessManager:
    def __init__(self, q) -> None:
        self.process_list = {}
        self.q = q
        self.process_history = {}
        self.process_history_last_restart = {}
        self.process_reloaded = {}
        self.process_attached = None

    def add_process_to_history(self, process):
        self.process_history[process.get_name()] = 0
        current_time = datetime.datetime.now()
        self.process_history_last_restart[process.get_name()] = [current_time]

    def add_process_numproc_up(self, _, new_task):
        process_list = new_task.create_process_list(self.q)
        for process_name, process in process_list.items():
            if process_name not in self.process_list:
                self.process_list.update({process_name: process})
                self.add_process_to_history(process)
                process.launch_process()

    def stop_process_from_task(self, task):
        for _, process in self.process_list.items():
            if process.get_task_name() == task.get_task_name():
                process.stop(keep=False)

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

    def start_all_process(self, poller, first_launch=False):
        for process_name, process in self.process_list.items():
            if first_launch and not process.Config.get('autostart'):
                continue
            self.start_process(process_name, poller)

    def check_fatal(self, process_history):
        # here we will if we tried to restart process too quickly
        # => max 3 retrie in less than 2 sec
        max_retrie = 3
        timeout = 2
        if len(process_history) <= max_retrie:
            return False
        if process_history[max_retrie - 1] - process_history[0] < \
                datetime.timedelta(seconds=timeout):
            return True

        # we remove the oldest retry time
        process_history.pop(0)
        return False

    def need_restart(self, process):
        if process.killed():
            return None
        if process.get_config_key("autorestart") == AutoRestartType('true') \
                and process.is_exit_expected():
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

        self.process_list[process_name].drain_pipe()
        self.process_list[process_name].join_thread()
        poller.remove_process(self.process_list[process_name])
        self.process_list[process_name].clean_up()

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
            self.process_list[process_name] = None
            del self.process_list[process_name]
            self.process_list[new_process.get_name()] = new_process
            poller.register_process(new_process)
            new_process.launch_process()
        if not old_process.keep_process():
            try:
                self.process_list[process_name] = None
                del self.process_list[process_name]
            except KeyError:
                pass

    def register_process(self, poller):
        for _, process in self.process_list.items():
            poller.register_process(process)

    def handle_read_event(self, process_list):
        for process_name, fd in process_list.items():
            self.process_list[process_name].set_fd_ready(fd)
            self.process_list[process_name].handle_read()

    def stop_all(self, poller):
        for _, process in self.process_list.items():
            process.stop()

    def stop_process(self, process_name):
        try:
            self.process_list[process_name].stop()
        except KeyError:
            pass

    def start_process(self, process_name, poller):
        if process_name not in self.process_list:
            return
        if self.process_list[process_name].get_status() not in [
            ProcessState.NOTSTARTED,
            ProcessState.KILLED,
            ProcessState.STOPPED,
            ProcessState.FINISH,
            ProcessState.FAILED
        ]:
            return
        old_process = self.process_list[process_name]
        self.process_list[process_name] = self.process_list[process_name].clone()
        poller.register_process(self.process_list[process_name])
        self.add_process_to_history(self.process_list[process_name])
        self.process_list[process_name].set_started()
        self.process_list[process_name].launch_process()

        # old_process.clean_up()
        del old_process

    def restart_process(self, process_name):
        if self.process_list[process_name].get_status() == ProcessState.NOTSTARTED:
            self.process_list[process_name].launch_process()
            return
        if self.process_list[process_name].get_status() != ProcessState.RUNNING:
            return

        new_process = self.process_list[process_name].clone()
        self.process_reloaded.update({process_name: new_process})
        self.process_list[process_name].stop()

    def get_all_state(self):
        status = {}
        for process_name, process in self.process_list.items():
            status[process_name] = [process.get_status().value, process.get_pid()]
        return status

    def forget_process(self, process_name):
        try:
            del self.process_list[process_name]
            del self.process_history[process_name]
            del self.process_history_last_restart[process_name]
        except KeyError:
            pass

    def attach(self, process_name):
        if self.process_attached is not None:
            self.process_list[self.process_attached].detach()
        self.process_attached = process_name
        self.process_list[process_name].attach()

    def detach(self, process_name):
        self.process_attached = None
        self.process_list[process_name].detach()

    def send_attached(self, cmd):
        try:
            self.process_list[self.process_attached].write_data(cmd)
        except KeyError:
            self.process_attached = None
        except (OSError, ValueError):
            self.process_attached = None
            logger.info(f"Error while sending command to {self.process_attached}")

    def check_process_exist(self, process_name):
        return process_name in self.process_list

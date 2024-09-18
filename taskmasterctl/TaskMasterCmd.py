from cmd import Cmd


class TaskMasterCmd(Cmd):
    prompt = "taskmaster> "
    intro = "Welcome to TaskMaster!"

    def do_exit(self, line: str) -> bool:
        """exit	Exit the supervisor shell."""
        return True

    def do_quit(self, line: str) -> bool:
        """exit	Exit the supervisor shell."""
        return self.do_exit(line)

    def do_reload(self, line: str) -> None:
        """reload 		Restart the remote supervisord."""
        print("Reloading configuration")

    def do_restart(self, line: str) -> None:
        """restart <name>		Restart a process
restart <name> <name>	Restart multiple processes or groups
restart all		Restart all processes
Note: restart does not reread config files. For that, see reread and update."""
        print("Restarting task", line)

    def do_start(self, line: str) -> None:
        """start <name>		Start a process
start <name> <name>	Start multiple processes or groups
start all		Start all processes"""
        print("Starting task", line)

    def do_stop(self, line: str) -> None:
        """stop <name>		Stop a process
stop <name> <name>	Stop multiple processes or groups
stop all		Stop all processes"""
        print("Stopping task", line)

    def do_update(self, line: str) -> None:
        """update			Reload config and add/remove as necessary, \
            and will restart affected programs
update all		Reload config and add/remove as necessary, \
    and will restart affected programs"""
        print("Updating task", line)

    def do_status(self, line: str) -> None:
        """status <name>		Get status for a single process
status <name> <name>	Get status for multiple named processes
status			Get all process status info"""
        print("Getting status of task", line)

    do_EOF = do_exit
    do_q = do_quit

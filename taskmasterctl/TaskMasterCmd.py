from cmd import Cmd
from commands import Commands


class TaskMasterCmd(Cmd):
    prompt = "taskmaster> "
    intro = "Welcome to TaskMaster!"

    def __init__(self, port: int) -> None:
        super().__init__()
        self.commands = Commands(port)

    def do_exit(self, line: str) -> bool:
        """exit	Exit the supervisor shell."""
        if not self.commands.exit(line):
            print(self.do_exit.__doc__)

    def do_quit(self, line: str) -> bool:
        """exit	Exit the supervisor shell."""
        if not self.commands.quit(line):
            print(self.do_quit.__doc__)

    def do_restart(self, line: str) -> None:
        """restart <name>		Restart a process
restart <name> <name>	Restart multiple processes or groups
restart all		Restart all processes
Note: restart does not reread config files. For that, see reread and update."""
        if not self.commands.restart(line):
            print(self.do_restart.__doc__)

    def do_start(self, line: str) -> None:
        """start <name>		Start a process
start <name> <name>	Start multiple processes or groups
start all		Start all processes"""
        if not self.commands.start(line):
            print(self.do_start.__doc__)

    def do_stop(self, line: str) -> None:
        """stop <name>		Stop a process
stop <name> <name>	Stop multiple processes or groups
stop all		Stop all processes"""
        if not self.commands.stop(line):
            print(self.do_stop.__doc__)

    def do_update(self, line: str) -> None:
        """update			Reload config and add/remove as necessary, \
            and will restart affected programs"""
        if not self.commands.update(line):
            print(self.do_update.__doc__)

    def do_status(self, line: str) -> None:
        """status <name>		Get status for a single process
status <name> <name>	Get status for multiple named processes
status			Get all process status info"""
        if not self.commands.status(line):
            print(self.do_status.__doc__)
    
    def do_attach(self, line: str) -> None:
        """attach"""
        if not self.commands.attach(line):
            print(self.do_attach.__doc__)

    def do_debug(self, line: str) -> None:
        """debug"""
        if not self.commands.debug(line):
            print(self.do_attach.__doc__)

    do_EOF = do_exit
    do_q = do_quit

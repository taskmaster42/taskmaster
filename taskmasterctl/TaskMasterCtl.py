from TaskMasterCmd import TaskMasterCmd


class TaskMasterCtl:
    def __init__(self, port: int) -> None:
        self.cmd = TaskMasterCmd(port)

    def run(self) -> None:
        self.cmd.cmdloop()

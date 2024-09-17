import signal


class SignalType():
    def __init__(self, value) -> None:
        self.num = signal.Signals[value].value

    def get_num(self):
        return self.num

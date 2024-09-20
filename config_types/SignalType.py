import signal


class SignalType():
    def __init__(self, value) -> None:
        if isinstance(value, SignalType):
            self.num = value.get_num() 
        else:
            self.num = signal.Signals[value].value

    def get_num(self):
        return self.num
    
    def __eq__(self, value: object) -> bool:
        return self.num == value.get_num()

class AutoRestartType():
    def __init__(self, value):
        known_type = {'true': True, 'false': False, 'unexpected': 'unexpected'}
        if type(value) is AutoRestartType:
            self.value = value
        else:
            if value not in known_type:
                raise ValueError(f"unknown value got {value}")
            self.value = known_type[value]

    def get_value(self):
        return self.value

    def __eq__(self, value: object) -> bool:
        if self.value == value:
            return True
        return False

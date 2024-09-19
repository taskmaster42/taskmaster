class ConfigElement():
    def __init__(self, value, expected_type):
        self.value = expected_type(value)

    def get_value(self):
        return self.value

    def __eq__(self, value: object) -> bool:
        return self.value == value.value